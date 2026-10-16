"""Capture a Salesforce "atlas" Developer Guide as markdown for AI grounding.

Companion to ``help_portal`` (which captures the help.salesforce.com LWC
portal). The *developer* guide is a different documentation system — the
"atlas" viewer at ``developer.salesforce.com/docs/atlas.en-us.<deliverable>.meta``
— so it needs its own capture path.

HOW ATLAS WORKS

The atlas viewer is a JS SPA, but it is backed by a clean JSON content API:

    TOC / metadata:
        GET /docs/get_document/atlas.en-us.<deliverable>.meta
        -> { toc: [...nested...], version: {doc_version}, deliverable, doc_title, ... }

    Per-page content:
        GET /docs/get_document_content/<deliverable>/<page_id>/en-us/<doc_version>
        -> { id, title, content }   # content is an HTML fragment

Both endpoints sit behind Akamai bot protection — a plain ``requests``/``curl``
call returns HTTP 403. We therefore drive them from inside a real Playwright
browser context: navigate once to the guide (which passes the bot challenge and
sets cookies), then call the API with in-page ``fetch()`` so the requests carry
the browser's cookies and TLS fingerprint. The returned HTML fragment is
converted to markdown (``markdownify`` when available, else a built-in minimal
converter).

OUTPUT (mirrors the help snapshot layout)

    docs/salesforce/{release}/dev-guide/articles/{page_id}.md   # frontmatter + body
    docs/salesforce/{release}/dev-guide/manifest.json           # machine index
    docs/salesforce/{release}/dev-guide/index.md                # human index

Run through the CLI (``python -m scripts.doc_snapshot dev-guide ...``); named
guides live in ``presets.yaml``. scripts/doc_snapshot/README.md covers install,
modes and options.
"""

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scripts.doc_snapshot._core import (
    OptionsError,
    SnapshotError,
    as_bool,
    as_int,
    captured_table,
    compute_stats,
    get_logger,
    index_footer,
    log_done,
    normalize_mode,
    raise_on_capture_errors,
    read_manifest,
    require_playwright,
    require_positive,
    resolve_output_dir,
    run_browser,
    stats_table,
    today,
    utc_timestamp,
    validate_options,
    write_manifest,
    yaml_escape,
)

CAPTURE_METHOD = "scripts/doc_snapshot dev-guide (Playwright + atlas content API)"


DOCS_BASE = "https://developer.salesforce.com/docs"

# JS run in the page to fetch the atlas content API with the browser's cookies.
FETCH_TEXT_JS = """
async (url) => {
    const r = await fetch(url, { headers: { 'Accept': 'application/json' } });
    return { status: r.status, ok: r.ok, text: await r.text() };
}
"""

FETCH_BATCH_JS = """
async (args) => {
    const { base, deliverable, docVersion, ids } = args;
    return await Promise.all(ids.map(async (id) => {
        const url = `${base}/get_document_content/${deliverable}/${id}/en-us/${docVersion}`;
        try {
            const r = await fetch(url, { headers: { 'Accept': 'application/json' } });
            if (!r.ok) return { id, ok: false, status: r.status };
            const j = await r.json();
            return { id, ok: true, status: r.status, title: j.title, content: j.content };
        } catch (e) {
            return { id, ok: false, error: String(e) };
        }
    }));
}
"""


# ---------------------------------------------------------------------------
# HTML -> Markdown
# ---------------------------------------------------------------------------

_ANCHOR_RE = re.compile(r'<a\s+name="[^"]*">\s*(?:<!--.*?-->)?\s*</a>', re.IGNORECASE | re.DOTALL)
_MULTI_BLANK_RE = re.compile(r"\n{3,}")


def _atlas_link_re(deliverable: str) -> "re.Pattern":
    """Regex matching an atlas intra-guide page reference for ``deliverable``.

    Captures group 1 = page id (``<page>.htm``), group 2 = optional ``#anchor``.
    Optionally consumes a leading ``https://developer.salesforce.com/docs/`` so
    that *absolute* atlas URLs are matched and replaced whole — otherwise only
    the suffix would be rewritten, leaving a dangling ``…/docs/`` prefix (e.g.
    ``https://developer.salesforce.com/docs/./page.htm.md``).
    """
    d = re.escape(deliverable)
    return re.compile(
        r"(?:https?://developer\.salesforce\.com/docs/)?"
        r"(?:atlas\.en-us\.)?(?:[0-9.]+\.)?" + d + r"\.meta/" + d
        + r"/([A-Za-z0-9_.\-]+\.htm)(#[A-Za-z0-9_.\-]+)?"
    )


def html_to_markdown(
    html: str,
    deliverable: Optional[str] = None,
    known_ids: Optional[set] = None,
) -> str:
    """Convert an atlas HTML content fragment to markdown.

    Prefers ``markdownify`` (best fidelity for tables / nested lists); falls
    back to a built-in converter when it isn't installed. When ``deliverable``
    is given, intra-guide cross-references are rewritten: to a sibling
    ``./<page_id>.md`` when the target was captured (``known_ids``), otherwise
    to an absolute developer.salesforce.com URL so the link is never dead.
    """
    if not html:
        return ""
    html = _ANCHOR_RE.sub("", html)
    try:
        from markdownify import markdownify as _md  # type: ignore

        text = _md(html, heading_style="ATX", bullets="-")
    except ImportError:
        text = _MinimalMarkdownParser.convert(html)
    if deliverable:
        text = _rewrite_internal_links(text, deliverable, known_ids)
    text = _MULTI_BLANK_RE.sub("\n\n", text).strip()
    return text


def _rewrite_internal_links(
    text: str, deliverable: str, known_ids: Optional[set] = None
) -> str:
    """Rewrite atlas intra-guide page links so none are dead.

    ``atlas.en-us.<deliverable>.meta/<deliverable>/<page>.htm[#anchor]`` becomes:
      * ``./<page>.htm.md`` when ``<page>`` was captured (in ``known_ids``), so the
        corpus is self-navigable; or
      * the absolute ``https://developer.salesforce.com/docs/...`` URL when it was
        not captured (e.g. a reference page outside the captured set), so the link
        resolves online instead of pointing at a missing file.
    When ``known_ids`` is None, every match is rewritten to a sibling (legacy
    behavior). Cross-product (help.salesforce.com) and other absolute links are
    left untouched.
    """
    pat = _atlas_link_re(deliverable)

    def repl(m):
        page_id, anchor = m.group(1), m.group(2) or ""
        if known_ids is None or page_id in known_ids:
            return f"./{page_id}.md{anchor}"  # keep the #fragment on local links too
        return f"{DOCS_BASE}/atlas.en-us.{deliverable}.meta/{deliverable}/{page_id}{anchor}"

    return pat.sub(repl, text)


def extract_link_targets(html: str, deliverable: str) -> set:
    """Return the set of intra-guide page ids (``<page>.htm``) linked from ``html``.

    Used to follow links beyond the TOC so pages that are linked from a captured
    page but not listed in the TOC (e.g. per-class Apex reference pages) are also
    captured.
    """
    if not html:
        return set()
    return {m.group(1) for m in _atlas_link_re(deliverable).finditer(html)}


class _MinimalMarkdownParser(HTMLParser):
    """A small, dependency-free HTML->markdown converter for atlas content.

    Handles the tag set atlas pages actually use: h1-h6, p, ul/ol/li (nested),
    pre/code/samp/kbd, table (rendered as pipe rows), a, strong/b, em/i, br,
    dl/dt/dd. Unknown wrapper tags pass their text through. Good enough as a
    fallback when markdownify is absent.
    """

    HEADINGS = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####", "h6": "######"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: List[str] = []
        self.list_stack: List[str] = []  # 'ul' | 'ol'
        self.ol_counters: List[int] = []
        self.in_pre = 0
        self.in_code = 0
        self.href: Optional[str] = None
        self.link_text: List[str] = []
        self.cell_buf: Optional[List[str]] = None
        self.row: Optional[List[str]] = None
        self.table_rows: Optional[List[List[str]]] = None
        self.suppress = 0  # depth of tags whose text we drop (e.g. <a name>)

    @classmethod
    def convert(cls, html: str) -> str:
        p = cls()
        p.feed(html)
        p.close()
        return "".join(p.out)

    # -- helpers --
    def _emit(self, s: str):
        if self.link_text and self.href is not None:
            self.link_text.append(s)
        elif self.cell_buf is not None:
            self.cell_buf.append(s)
        else:
            self.out.append(s)

    def _block(self):
        if self.out and not "".join(self.out[-2:]).endswith("\n\n"):
            self.out.append("\n\n")

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.HEADINGS:
            self._block()
            self.out.append(self.HEADINGS[tag] + " ")
        elif tag == "p":
            self._block()
        elif tag == "br":
            self._emit("  \n")
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("*")
        elif tag == "ul":
            self.list_stack.append("ul")
        elif tag == "ol":
            self.list_stack.append("ol")
            self.ol_counters.append(0)
        elif tag == "li":
            depth = max(0, len(self.list_stack) - 1)
            indent = "  " * depth
            if self.list_stack and self.list_stack[-1] == "ol":
                self.ol_counters[-1] += 1
                marker = f"{self.ol_counters[-1]}. "
            else:
                marker = "- "
            self.out.append("\n" + indent + marker)
        elif tag == "pre":
            self._block()
            self.out.append("```\n")
            self.in_pre += 1
        elif tag in ("code", "samp", "kbd"):
            if not self.in_pre:
                self._emit("`")
            self.in_code += 1
        elif tag == "a":
            self.href = a.get("href")
            self.link_text = [""] if self.href else []
        elif tag == "table":
            self._block()
            self.table_rows = []
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.cell_buf = []
        elif tag in ("dt",):
            self._block()
            self._emit("**")
        elif tag == "dd":
            self.out.append("\n: ")

    def handle_endtag(self, tag):
        if tag in self.HEADINGS:
            self.out.append("\n\n")
        elif tag == "p":
            self.out.append("\n\n")
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("*")
        elif tag in ("ul", "ol"):
            if self.list_stack:
                popped = self.list_stack.pop()
                if popped == "ol" and self.ol_counters:
                    self.ol_counters.pop()
            if not self.list_stack:
                self.out.append("\n")
        elif tag == "pre":
            self.in_pre = max(0, self.in_pre - 1)
            self.out.append("\n```\n\n")
        elif tag in ("code", "samp", "kbd"):
            self.in_code = max(0, self.in_code - 1)
            if not self.in_pre:
                self._emit("`")
        elif tag == "a":
            text = "".join(self.link_text).strip()
            href = self.href
            self.href = None
            self.link_text = []
            if href and text:
                self._emit(f"[{text}]({href})")
            elif text:
                self._emit(text)
        elif tag in ("td", "th"):
            if self.row is not None and self.cell_buf is not None:
                self.row.append(" ".join("".join(self.cell_buf).split()))
            self.cell_buf = None
        elif tag == "tr":
            if self.table_rows is not None and self.row is not None:
                self.table_rows.append(self.row)
            self.row = None
        elif tag == "table":
            self._flush_table()
        elif tag == "dt":
            self._emit("**")

    def _flush_table(self):
        rows = self.table_rows or []
        self.table_rows = None
        if not rows:
            return
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        lines = ["| " + " | ".join(c for c in rows[0]) + " |"]
        lines.append("| " + " | ".join("---" for _ in range(width)) + " |")
        for r in rows[1:]:
            lines.append("| " + " | ".join(c for c in r) + " |")
        self.out.append("\n" + "\n".join(lines) + "\n\n")

    def handle_data(self, data):
        self._emit(data)


# ---------------------------------------------------------------------------
# Markdown rendering (article file)
# ---------------------------------------------------------------------------

def render_page_markdown(
    *,
    page_id: str,
    title: str,
    body_md: str,
    source_url: str,
    release_version: str,
    release_name: str,
    deliverable: str,
    section: Optional[str],
    parent_page_id: Optional[str],
    fetched_at: str,
) -> str:
    fm = [
        "---",
        f"page_id: {page_id}",
        f"title: {yaml_escape(title)}",
        f"source_url: {source_url}",
        f"release: {yaml_escape(release_version)}",
        f"release_name: {yaml_escape(release_name)}",
        f"deliverable: {yaml_escape(deliverable)}",
    ]
    if section:
        fm.append(f"section: {yaml_escape(section)}")
    if parent_page_id:
        fm.append(f"parent_page: {parent_page_id}")
    fm.append(f"fetched_at: {yaml_escape(fetched_at)}")
    fm.append("---")
    # Body already begins with the page's own H1 (from the atlas content
    # fragment), so we don't prepend another title.
    return "\n".join(fm) + "\n\n" + body_md.strip() + "\n"


# ---------------------------------------------------------------------------
# Snapshotter
# ---------------------------------------------------------------------------


class DevGuideSnapshot:
    """Capture an atlas developer guide as per-page markdown for AI grounding.

    Pure web scrape — no org connection required.

    Options (snake_case; the CLI maps --kebab-case flags onto them):

        release_version  required; path component, e.g. '264'
        release_name     required; e.g. "Winter '27"
        deliverable      atlas slug (default revenue_lifecycle_management_dev_guide)
        doc_version      atlas doc version, e.g. '264.0' (default: the guide meta's value)
        sections         capture only these TOC subtrees, each named by title or page_id
        output_dir       default docs/salesforce/{release_version}/dev-guide (repo-relative)
        mode             discover | capture | all | refresh (default all)
        headless         default true
        concurrency      pages fetched per batch (default 6)
        wait_ms          ms to wait after the bootstrap navigation (default 3000)
        batch_delay_ms   ms between fetch batches (default 400)
        follow_links     follow intra-guide links beyond the TOC (default true for a
                         whole-guide run, false when sections are given)
        max_pages        safety cap on total pages captured (default 5000)
    """

    DEFAULT_DELIVERABLE = "revenue_lifecycle_management_dev_guide"

    def __init__(self, options: Dict[str, Any], logger=None):
        self.options = dict(options)
        self.logger = logger or get_logger()
        self._init_options()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _init_options(self) -> None:
        validate_options(
            self.options, "release_version", "release_name", list_options=("sections",)
        )
        # YAML reads `output_dir: 266` or `doc_version: 264.0` as a number.
        for name in ("release_version", "release_name", "deliverable", "output_dir",
                     "doc_version"):
            if self.options.get(name) is not None:
                self.options[name] = str(self.options[name])
        self.options["deliverable"] = (
            self.options.get("deliverable") or self.DEFAULT_DELIVERABLE
        )
        if not self.options.get("output_dir"):
            self.options["output_dir"] = (
                f"docs/salesforce/{self.options['release_version']}/dev-guide"
            )
        self.options["mode"] = normalize_mode(self.options.get("mode"))
        self.options["headless"] = as_bool(self.options.get("headless"), True)
        self.options["concurrency"] = as_int(self.options.get("concurrency"), 6)
        self.options["wait_ms"] = as_int(self.options.get("wait_ms"), 3000)
        self.options["batch_delay_ms"] = as_int(self.options.get("batch_delay_ms"), 400)
        # Each section is a TOC title or a page_id; use the page_id when a
        # title is ambiguous. validate_options() has rejected blank items.
        sections = self.options.get("sections")
        if sections is not None and not isinstance(sections, (list, tuple)):
            sections = [sections]
        self.options["section_filters"] = (
            [str(section).strip() for section in sections] if sections else None
        )
        self.options["doc_version"] = self.options.get("doc_version") or None
        self.options["max_pages"] = as_int(self.options.get("max_pages"), 5000)
        require_positive(self.options, "concurrency", "wait_ms", "max_pages")
        # Follow links by default for a whole-guide run; default off when specific
        # sections are requested (so a section capture stays scoped). Override with
        # follow_links: true to also pull in in-scope pages linked from a section
        # but absent from its TOC subtree.
        self.options["follow_links"] = as_bool(
            self.options.get("follow_links"), self.options["section_filters"] is None
        )

    def preflight(self) -> None:
        """Raise the conflicts detectable offline, before any target of a batch runs.

        Only a pinned doc_version can be checked here; an unpinned one is
        resolved from the guide's meta during the run, which checks it again.
        """
        if not self.options.get("doc_version"):
            return
        manifest_path = self._manifest_path(resolve_output_dir(self.options["output_dir"]))
        # Load it silently: run() loads (and logs) it again. A manifest it
        # can't read comes back empty, so it has nothing to conflict with.
        manifest = read_manifest(manifest_path, {"pages": []}, "pages")
        self._check_doc_version_change(
            manifest, manifest.get("doc_version"), self.options["mode"]
        )

    def run(self) -> Dict[str, Any]:
        """Run the snapshot; returns the manifest's stats."""
        require_playwright(self.logger)

        output_dir = resolve_output_dir(self.options["output_dir"])
        (output_dir / "articles").mkdir(parents=True, exist_ok=True)
        return run_browser(self._async_run(output_dir))

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    def _meta_url(self) -> str:
        return f"{DOCS_BASE}/get_document/atlas.en-us.{self.options['deliverable']}.meta"

    def _bootstrap_url(self) -> str:
        # Navigating the bare deliverable URL redirects to the first page,
        # passes the Akamai challenge, and sets cookies for the API fetches.
        return f"{DOCS_BASE}/atlas.en-us.{self.options['deliverable']}.meta"

    def _page_source_url(self, page_id: str) -> str:
        d = self.options["deliverable"]
        return f"{DOCS_BASE}/atlas.en-us.{d}.meta/{d}/{page_id}"

    # ------------------------------------------------------------------
    # Manifest I/O
    # ------------------------------------------------------------------

    def _manifest_path(self, output_dir: Path) -> Path:
        return output_dir / "manifest.json"

    def _load_or_init_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        base = {
            "deliverable": self.options["deliverable"],
            "release": self.options["release_version"],
            "release_name": self.options["release_name"],
            "doc_version": self.options.get("doc_version"),
            "guide_title": None,
            "source_meta_url": self._meta_url(),
            "capture_method": CAPTURE_METHOD,
            "snapshot_started": today(),
            "pages": [],
        }
        manifest = read_manifest(manifest_path, base, "pages", self.logger)
        # Label the manifest with the tool that last wrote it.
        manifest["capture_method"] = CAPTURE_METHOD
        return manifest

    def _save_manifest(self, manifest_path: Path, manifest: Dict[str, Any]) -> None:
        manifest["last_updated"] = utc_timestamp()
        manifest["stats"] = compute_stats(manifest, "pages")
        write_manifest(manifest_path, manifest)

    # ------------------------------------------------------------------
    # TOC walk
    # ------------------------------------------------------------------

    # A page id must be a bare ``<name>.htm`` filename — no path separators or
    # parent refs — because it is used to build a local file path. This guards
    # against path traversal from a malformed/hostile TOC or link href.
    _SAFE_PAGE_ID_RE = re.compile(r"^[A-Za-z0-9_.\-]+\.htm$")

    @classmethod
    def _safe_page_id(cls, href: Optional[str]) -> Optional[str]:
        """Return a safe intra-guide page id from ``href``, else None.

        Strips any ``#fragment`` / ``?query`` first (so a page with an anchored
        TOC href isn't skipped), then rejects path separators / parent refs.
        """
        if not href or href.startswith("http://") or href.startswith("https://"):
            return None  # missing or external (e.g. help.salesforce.com cross-ref)
        href = href.split("#", 1)[0].split("?", 1)[0]  # drop #fragment / ?query
        if "/" in href or "\\" in href or ".." in href:
            return None  # path separators / parent refs — not a flat page id
        return href if cls._SAFE_PAGE_ID_RE.match(href) else None

    @classmethod
    def _node_page_id(cls, node: Dict[str, Any]) -> Optional[str]:
        href = (node.get("a_attr") or {}).get("href") or node.get("href")
        return cls._safe_page_id(href)

    def _flatten_toc(
        self, toc: List[Dict[str, Any]], section_filters: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Return ordered, de-duped page records from the TOC tree.

        Each record: {page_id, title, section, parent_page}. ``section`` is the
        top-level ancestor's title. When ``section_filters`` is a non-empty list,
        only those subtrees (each matched by title or page_id, case-insensitive)
        are returned; a page is attributed to the first matching section.
        """
        pages: List[Dict[str, Any]] = []
        seen = set()

        def walk(nodes, section, parent_pid):
            for node in nodes or []:
                if not isinstance(node, dict):
                    continue
                pid = self._node_page_id(node)
                title = node.get("text") or node.get("title") or pid or ""
                this_section = section if section is not None else title
                if pid and pid not in seen:
                    seen.add(pid)
                    pages.append({
                        "page_id": pid,
                        "title": title,
                        "section": this_section,
                        "parent_page": parent_pid,
                    })
                walk(node.get("children"), this_section, pid or parent_pid)

        if section_filters:
            for needle in section_filters:
                sub = self._find_section(toc, needle)
                if sub is None:
                    raise OptionsError(
                        f"section {needle!r} not found in the guide TOC"
                    )
                # The matched node's own title seeds the section label for its subtree.
                seed_section = sub.get("text") or sub.get("title") or needle
                walk([sub], seed_section, None)
        else:
            walk(toc, None, None)
        return pages

    def _find_section(
        self, nodes: List[Dict[str, Any]], needle: str
    ) -> Optional[Dict[str, Any]]:
        target = needle.strip().lower()
        for node in nodes or []:
            if not isinstance(node, dict):
                continue
            title = (node.get("text") or node.get("title") or "").strip().lower()
            pid = self._node_page_id(node) or ""
            if title == target or pid.lower() == target or pid.lower() == target + ".htm":
                return node
            found = self._find_section(node.get("children"), needle)
            if found:
                return found
        return None

    def _merge_discovered(
        self, manifest: Dict[str, Any], discovered: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        by_id = {p["page_id"]: p for p in manifest.get("pages", [])}
        for d in discovered:
            pid = d["page_id"]
            if pid in by_id:
                rec = by_id[pid]
                if not rec.get("title"):
                    rec["title"] = d.get("title")
                rec.setdefault("section", d.get("section"))
                if d.get("parent_page") and not rec.get("parent_page"):
                    rec["parent_page"] = d["parent_page"]
            else:
                by_id[pid] = {
                    "page_id": pid,
                    "title": d.get("title"),
                    "section": d.get("section"),
                    "parent_page": d.get("parent_page"),
                    "status": "pending",
                }
        manifest["pages"] = sorted(by_id.values(), key=lambda p: p["page_id"])
        return manifest

    # ------------------------------------------------------------------
    # Async pipeline
    # ------------------------------------------------------------------

    async def _async_run(self, output_dir: Path) -> None:
        from playwright.async_api import async_playwright

        mode = self.options["mode"]
        manifest_path = self._manifest_path(output_dir)
        articles_dir = output_dir / "articles"
        manifest = self._load_or_init_manifest(manifest_path)
        # Captured before anything below mutates it, so the guard further down can
        # tell "the version this manifest's articles were actually fetched at" from
        # "the version we're about to claim" — those two can diverge (see guard).
        previous_doc_version = manifest.get("doc_version")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.options["headless"])
            # Derive the user agent from the actual bundled Chromium (rather than
            # hardcoding a version that can go stale) and drop the "Headless"
            # marker so requests look like a normal browser — the atlas API sits
            # behind bot protection. Falls back to Playwright's default UA.
            probe = await browser.new_context()
            try:
                default_ua = await (await probe.new_page()).evaluate(
                    "() => navigator.userAgent"
                )
            finally:
                await probe.close()
            user_agent = (default_ua or "").replace("HeadlessChrome", "Chrome").replace(
                "Headless", ""
            ).strip()
            context = await browser.new_context(user_agent=user_agent or None)
            page = await context.new_page()

            self.logger.info(f"Bootstrapping session: {self._bootstrap_url()}")
            await page.goto(self._bootstrap_url(), wait_until="domcontentloaded", timeout=60_000)
            await page.wait_for_timeout(self.options["wait_ms"])

            # Discovery
            if mode in ("discover", "all", "refresh"):
                meta = await self._fetch_meta(page)
                version = (meta.get("version") or {})
                if not self.options.get("doc_version"):
                    self.options["doc_version"] = version.get("doc_version")
                # Validate the resolved version BEFORE mutating the manifest:
                # capture/all raise outright on a mislabeling conflict (see
                # _check_doc_version_change); discover is allowed to preview
                # without raising but must not merge/save the other version's
                # TOC in the same conflict case it already defers the
                # doc_version write for (see _may_record_doc_version) — else the
                # foreign-version pages land as 'pending' even though the label
                # doesn't change.
                self._check_doc_version_change(manifest, previous_doc_version, mode)
                if mode != "discover" or self._may_record_doc_version(
                    manifest, previous_doc_version, mode
                ):
                    manifest["guide_title"] = meta.get("doc_title") or meta.get("title")
                    discovered = self._flatten_toc(meta.get("toc") or [], self.options["section_filters"])
                    self.logger.info(
                        f"TOC: {len(discovered)} page(s)"
                        + (f" in section(s) {', '.join(self.options['section_filters'])}"
                           if self.options["section_filters"] else "")
                        + f" (doc_version={self.options['doc_version']})"
                    )
                    manifest = self._merge_discovered(manifest, discovered)
                    self._save_manifest(manifest_path, manifest)
                else:
                    self.logger.warning(
                        f"Skipping discovery merge: doc_version would change "
                        f"({previous_doc_version!r} -> {self.options['doc_version']!r}) "
                        "over already-captured pages. Re-run with --mode refresh to force a "
                        "re-fetch, or pass --doc-version to confirm the intended version."
                    )

            if not self.options.get("doc_version"):
                # capture-only mode relies on a previously-discovered version
                self.options["doc_version"] = manifest.get("doc_version")
                if not self.options["doc_version"]:
                    raise OptionsError(
                        "doc_version unknown; run --mode discover or pass --doc-version"
                    )
            self._check_doc_version_change(manifest, previous_doc_version, mode)
            if self._may_record_doc_version(manifest, previous_doc_version, mode):
                manifest["doc_version"] = self.options["doc_version"]

            # Capture
            failed: List[str] = []
            attempted = 0
            if mode in ("capture", "all", "refresh"):
                to_capture = self._select_to_capture(manifest, mode)
                self.logger.info(f"Capture: {len(to_capture)} page(s) queued")
                if to_capture:
                    failed, attempted = await self._capture_pages(
                        page, to_capture, articles_dir, manifest, manifest_path
                    )

            await browser.close()

        self._save_manifest(manifest_path, manifest)
        self._build_index(output_dir / "index.md", manifest)
        stats = manifest.get("stats", {})
        log_done(self.logger, stats, manifest_path)
        raise_on_capture_errors(failed, attempted, "pages")
        return stats

    async def _fetch_meta(self, page) -> Dict[str, Any]:
        self.logger.info(f"  GET {self._meta_url()}")
        res = await page.evaluate(FETCH_TEXT_JS, self._meta_url())
        if not res.get("ok"):
            raise SnapshotError(
                f"TOC fetch failed (HTTP {res.get('status')}). The atlas API may "
                "have blocked the session or the deliverable slug is wrong."
            )
        try:
            return json.loads(res.get("text") or "{}")
        except json.JSONDecodeError as e:
            raise SnapshotError(f"TOC response was not JSON: {e}")

    def _check_doc_version_change(
        self, manifest: Dict[str, Any], previous_doc_version: Optional[str], mode: str
    ) -> None:
        """Refuse a doc_version change that mode=capture/all would not honor.

        _select_to_capture skips already-captured pages for every mode except
        `refresh`, so recording a new doc_version on the manifest without refetching
        would mislabel old-version files as the new one. `discover` never fetches
        page bodies at all, so it's exempt too — it's meant to be a safe preview.
        """
        if mode not in ("capture", "all") or not self._doc_version_conflicts(
            manifest, previous_doc_version
        ):
            return
        raise OptionsError(
            f"doc_version changed ({previous_doc_version!r} -> "
            f"{self.options['doc_version']!r}) but "
            f"mode={mode!r} would not recapture already-captured pages, mislabeling "
            "their content as the new version. Use --mode refresh to force a re-fetch."
        )

    def _may_record_doc_version(
        self, manifest: Dict[str, Any], previous_doc_version: Optional[str], mode: str
    ) -> bool:
        """Whether it's safe to stamp the resolved doc_version onto the manifest now.

        `discover` is exempt from _check_doc_version_change's raise (it never
        fetches bodies), but writing the new version to the manifest here would
        still launder it past that guard: a later capture/all run reads the
        manifest as `previous_doc_version`, sees no change, and skips already-
        captured pages that were never refetched. So discover defers the write
        in the same conflict case the guard would otherwise raise on.
        """
        return mode != "discover" or not self._doc_version_conflicts(
            manifest, previous_doc_version
        )

    def _doc_version_conflicts(
        self, manifest: Dict[str, Any], previous_doc_version: Optional[str]
    ) -> bool:
        """The requested doc_version differs from one pages were already captured at."""
        requested = self.options["doc_version"]
        if not previous_doc_version or requested == previous_doc_version:
            return False
        return any(p.get("status") == "captured" for p in manifest.get("pages", []))

    def _select_to_capture(self, manifest: Dict[str, Any], mode: str) -> List[Dict[str, Any]]:
        pages = [p for p in manifest.get("pages", []) if p.get("page_id")]
        # When a section is requested, restrict to that section's pages even if
        # the manifest already holds other (e.g. previously discovered) pages, so
        # a single-section run never captures unrelated guide pages. Pages are
        # tagged with their TOC section by _merge_discovered; match that, or the
        # requested value given as the section's own page id.
        filters = self.options.get("section_filters")
        if filters:
            # A section may be given as a TOC title OR a page id (matching
            # _find_section). Pages are tagged with their section *title*, so if a
            # page id was supplied, resolve it to that page's stored section title
            # and filter by that — otherwise only the root page would match and
            # the subtree's children would be missed.
            by_pid = {(p.get("page_id") or "").lower(): p for p in pages}
            want_titles = set()
            for f in filters:
                want = f.strip().lower()
                root = by_pid.get(want) or by_pid.get(want + ".htm")
                want_titles.add(
                    (root.get("section") or want).strip().lower() if root else want
                )
            pages = [
                p for p in pages
                if (p.get("section") or "").strip().lower() in want_titles
            ]
        if mode == "refresh":
            return pages
        return [p for p in pages if p.get("status") != "captured"]

    async def _capture_pages(
        self,
        page,
        pages: List[Dict[str, Any]],
        articles_dir: Path,
        manifest: Dict[str, Any],
        manifest_path: Path,
    ) -> Tuple[List[str], int]:
        """Fetch and write ``pages``; returns (page ids that failed, pages attempted)."""
        concurrency = self.options["concurrency"]
        deliverable = self.options["deliverable"]
        doc_version = self.options["doc_version"]
        follow = self.options["follow_links"]
        max_pages = self.options["max_pages"]
        fetched_at = today()

        # Per-page metadata (section/parent), seeded from the TOC manifest.
        meta = {
            p["page_id"]: {"section": p.get("section"), "parent": p.get("parent_page")}
            for p in manifest.get("pages", []) if p.get("page_id")
        }

        # --- Phase 1: fetch (and, when follow_links, crawl) to closure ---------
        # Cache HTML in memory so Phase 2 can rewrite links against the FULL
        # captured set (a link is rewritten to a sibling only if its target was
        # captured; otherwise it falls back to an absolute URL — never a dead
        # local link). Following links also captures pages reachable from the
        # TOC pages but not listed in the TOC (e.g. per-class Apex reference).
        fetched: Dict[str, Dict[str, Any]] = {}   # pid -> {title, html}
        errors: Dict[str, str] = {}               # pid -> error
        seen = {p["page_id"] for p in pages}
        frontier = [p["page_id"] for p in pages]
        round_no = 0
        while frontier and len(fetched) < max_pages:
            round_no += 1
            new_targets: List[str] = []
            for start in range(0, len(frontier), concurrency):
                if len(fetched) >= max_pages:
                    break
                # Cap the final batch to the remaining allowance so the total
                # fetched never exceeds max_pages (the slice would otherwise grab
                # a full `concurrency` and overshoot by up to concurrency-1).
                remaining = max_pages - len(fetched)
                batch = frontier[start:start + min(concurrency, remaining)]
                results = await page.evaluate(
                    FETCH_BATCH_JS,
                    {"base": DOCS_BASE, "deliverable": deliverable,
                     "docVersion": doc_version, "ids": batch},
                )
                for res in results:
                    pid = res.get("id")
                    if not res.get("ok"):
                        errors[pid] = res.get("error") or f"HTTP {res.get('status')}"
                        continue
                    html = res.get("content") or ""
                    if not html:
                        errors[pid] = "empty body"
                        continue
                    fetched[pid] = {"title": res.get("title"), "html": html}
                    errors.pop(pid, None)
                    if follow:
                        linker_section = (meta.get(pid) or {}).get("section")
                        for t in extract_link_targets(html, deliverable):
                            if t not in seen:
                                seen.add(t)
                                meta.setdefault(t, {"section": linker_section, "parent": pid})
                                new_targets.append(t)
                if start + concurrency < len(frontier):
                    await page.wait_for_timeout(self.options["batch_delay_ms"])
            self.logger.info(
                f"  round {round_no}: {len(fetched)} fetched, "
                f"{len(errors)} error(s), {len(new_targets)} newly discovered"
            )
            room = max_pages - len(fetched)
            frontier = new_targets[:room] if room > 0 else []

        # Pages discovered (queued in `seen`) but never fetched — dropped when the
        # max_pages cap was hit (loop break, or new_targets[:room] truncation).
        # `frontier` alone misses these, so compute from `seen` and record them as
        # 'pending' below so they aren't silently lost.
        unfetched = [pid for pid in seen if pid not in fetched and pid not in errors]
        if unfetched:
            self.logger.warning(
                f"  Hit max_pages={max_pages}: {len(unfetched)} discovered page(s) "
                "left uncaptured (recorded as 'pending'). Raise --max-pages or "
                "re-run with --mode capture to fetch them."
            )

        # --- Phase 2: write every fetched page with the full set known ---------
        known_ids = set(fetched)
        by_id = {p["page_id"]: p for p in manifest.get("pages", [])}

        def record(pid: str) -> Dict[str, Any]:
            """The manifest record for ``pid``, backfilled from crawl metadata."""
            rec = by_id.setdefault(pid, {"page_id": pid})
            page_meta = meta.get(pid) or {}
            rec.setdefault("section", page_meta.get("section"))
            if page_meta.get("parent") and not rec.get("parent_page"):
                rec["parent_page"] = page_meta["parent"]
            return rec

        written = 0
        empty: List[str] = []   # fetched, but converted to an empty body
        for pid, data in fetched.items():
            body_md = html_to_markdown(data["html"], deliverable=deliverable, known_ids=known_ids)
            rec = record(pid)
            if not body_md:
                rec["status"] = "error"
                rec["error"] = "empty body"
                empty.append(pid)
            else:
                title = data["title"] or rec.get("title") or pid
                (articles_dir / f"{pid}.md").write_text(
                    render_page_markdown(
                        page_id=pid, title=title, body_md=body_md,
                        source_url=self._page_source_url(pid),
                        release_version=self.options["release_version"],
                        release_name=self.options["release_name"],
                        deliverable=deliverable,
                        section=rec.get("section"),
                        parent_page_id=rec.get("parent_page"),
                        fetched_at=fetched_at,
                    ),
                    encoding="utf-8",
                )
                rec.update(title=title, status="captured",
                           body_length=len(body_md), file=f"articles/{pid}.md")
                rec.pop("error", None)
                written += 1
        for pid, err in errors.items():
            rec = record(pid)
            rec["status"] = "error"
            rec["error"] = err
        # Record discovered-but-unfetched pages as 'pending' so they survive in the
        # manifest and a later mode=capture run can fetch them (don't downgrade a
        # page already captured in a prior run).
        for pid in unfetched:
            rec = record(pid)
            if rec.get("status") != "captured":
                rec["status"] = "pending"

        manifest["pages"] = sorted(by_id.values(), key=lambda p: p["page_id"])
        self._save_manifest(manifest_path, manifest)
        self.logger.info(f"  wrote {written} page(s); {len(errors) + len(empty)} error(s)")
        return list(errors) + empty, len(fetched) + len(errors)

    # ------------------------------------------------------------------
    # Index rendering
    # ------------------------------------------------------------------

    def _build_index(self, index_path: Path, manifest: Dict[str, Any]) -> None:
        pages = manifest.get("pages", [])
        captured = [p for p in pages if p.get("status") == "captured"]
        errored = [p for p in pages if p.get("status") == "error"]
        stats = manifest.get("stats", {})

        lines = [
            f"# {manifest.get('guide_title') or self.options['deliverable']} — Snapshot",
            "",
            f"**Deliverable:** `{manifest.get('deliverable')}`  ",
            f"**Release:** {manifest.get('release_name')} ({manifest.get('release')}, "
            f"doc_version {manifest.get('doc_version')})  ",
            f"**Last updated:** {manifest.get('last_updated', 'n/a')}",
            "",
            "## Stats",
            "",
            *stats_table(stats),
        ]

        if captured:
            by_section: Dict[str, List[Dict[str, Any]]] = {}
            for p in captured:
                by_section.setdefault(p.get("section") or "(uncategorized)", []).append(p)
            for section in sorted(by_section):
                items = by_section[section]
                lines.extend(captured_table(
                    f"## {section} ({len(items)})", items, "page_id", "Page", "Chars"
                ))

        if errored:
            lines.append(f"## Errored ({len(errored)})")
            lines.append("")
            for p in sorted(errored, key=lambda x: x["page_id"]):
                lines.append(f"- `{p['page_id']}` — {p.get('error', 'unknown')}")
            lines.append("")

        lines.extend(index_footer("dev-guide", manifest))
        index_path.write_text("\n".join(lines), encoding="utf-8")
