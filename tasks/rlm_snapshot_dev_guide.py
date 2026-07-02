"""Capture a Salesforce "atlas" Developer Guide as markdown for AI grounding.

Companion to ``tasks/rlm_snapshot_help.py`` (which captures the help.salesforce.com
LWC portal). The *developer* guide is a different documentation system — the
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

USAGE (cumulusci.yml)

    snapshot_dev_guide_262:
        class_path: tasks.rlm_snapshot_dev_guide.SnapshotSalesforceDevGuide
        group: Documentation
        options:
            release_version: "262"
            release_name: "Summer '26"
            # deliverable defaults to revenue_lifecycle_management_dev_guide
            # doc_version defaults to the meta's version.doc_version
            mode: all

Capture only one section (e.g. just CML) with the ``section`` option:

    cci task run snapshot_dev_guide_262 -o section "Constraint Modeling Language"

MODES (same semantics as snapshot_help)

    discover   Fetch TOC, write manifest with pages as 'pending'. No body capture.
    capture    Read manifest, capture 'pending' pages.
    all        Discover then capture, skipping already-captured pages. (default)
    refresh    Re-capture every page, overwriting existing files.

REQUIREMENTS

Playwright must be installed into whichever Python runs the task (CCI's
interpreter, not the calling shell). This is the same requirement as
``snapshot_help`` — see that module's docstring / cumulusci.yml comment block:

    pipx inject cumulusci playwright
    ~/.local/pipx/venvs/cumulusci/bin/python -m playwright install chromium

Optional (better markdown for tables / nested lists):

    pipx inject cumulusci markdownify

Without ``markdownify`` the task falls back to a built-in converter that handles
headings, paragraphs, lists, links, inline/blocks of code, and br.
"""

import asyncio
import json
import os
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
except ImportError:
    BaseTask = object  # type: ignore[misc,assignment]

    class TaskOptionsError(Exception):
        """Fallback when CumulusCI is unavailable (e.g. stdlib-only test runs)."""

    class CommandException(Exception):
        """Fallback when CumulusCI is unavailable."""


DOCS_BASE = "https://developer.salesforce.com/docs"

PLAYWRIGHT_INSTALL_HINT = """
Playwright is required for this task. Install it into the SAME Python
environment that runs CCI (a plain `pip install playwright` only works if CCI
was installed via pip in that environment):

    pipx inject cumulusci playwright
    ~/.local/pipx/venvs/cumulusci/bin/python -m playwright install chromium

On Windows the venv python is
%USERPROFILE%\\pipx\\venvs\\cumulusci\\Scripts\\python.exe. If your pipx install
lives elsewhere, `pipx environment --value PIPX_LOCAL_VENVS` prints the base
directory that contains the cumulusci venv.
"""

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
        if self.in_pre:
            self._emit(data)
        else:
            self._emit(data)


# ---------------------------------------------------------------------------
# Markdown rendering (article file)
# ---------------------------------------------------------------------------

_FM_BAD = re.compile(r"[\r\n]+")


def _yaml_escape(value: Optional[str]) -> str:
    if value is None:
        return ""
    value = _FM_BAD.sub(" ", value)
    if '"' in value or ":" in value or value.startswith(("-", "*", "&", "?", "|", ">", "%", "@", "`", "#")):
        value = '"' + value.replace('"', '\\"') + '"'
    return value


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
        f"title: {_yaml_escape(title)}",
        f"source_url: {source_url}",
        f"release: {_yaml_escape(release_version)}",
        f"release_name: {_yaml_escape(release_name)}",
        f"deliverable: {_yaml_escape(deliverable)}",
    ]
    if section:
        fm.append(f"section: {_yaml_escape(section)}")
    if parent_page_id:
        fm.append(f"parent_page: {parent_page_id}")
    fm.append(f"fetched_at: {_yaml_escape(fetched_at)}")
    fm.append("---")
    # Body already begins with the page's own H1 (from the atlas content
    # fragment), so we don't prepend another title.
    return "\n".join(fm) + "\n\n" + body_md.strip() + "\n"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class SnapshotSalesforceDevGuide(BaseTask):
    """Capture an atlas developer guide as per-page markdown for AI grounding.

    Pure web scrape — no org connection required.
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "release_version": {
            "description": "Release version, used as a path component, e.g. '262'.",
            "required": True,
        },
        "release_name": {
            "description": "Human-readable release name, e.g. \"Summer '26\".",
            "required": True,
        },
        "deliverable": {
            "description": "Atlas deliverable slug. Defaults to 'revenue_lifecycle_management_dev_guide'.",
            "required": False,
        },
        "doc_version": {
            "description": "Atlas doc version (e.g. '262.0'). Defaults to the value reported by the guide's metadata.",
            "required": False,
        },
        "section": {
            "description": "Optional. Capture only the TOC subtree whose title or page_id matches (e.g. 'Constraint Modeling Language'). Default: whole guide.",
            "required": False,
        },
        "sections": {
            "description": "Optional. Comma-separated list of TOC sections (title or page_id) to capture in one run, e.g. 'business_rules_engine, context_service_overview'. Use page_ids when a section title contains commas. Supersedes 'section'.",
            "required": False,
        },
        "output_dir": {
            "description": "Output directory. Defaults to docs/salesforce/{release_version}/dev-guide.",
            "required": False,
        },
        "mode": {
            "description": "discover | capture | all | refresh. Defaults to 'all'.",
            "required": False,
        },
        "headless": {
            "description": "Run browser headless. Defaults to true. Set 'false' to watch.",
            "required": False,
        },
        "concurrency": {
            "description": "Pages fetched per batch. Defaults to 6.",
            "required": False,
        },
        "wait_ms": {
            "description": "Milliseconds to wait after the bootstrap navigation for cookies/hydration. Defaults to 3000.",
            "required": False,
        },
        "batch_delay_ms": {
            "description": "Milliseconds to pause between fetch batches (politeness/rate-limit). Defaults to 400.",
            "required": False,
        },
        "follow_links": {
            "description": "Follow intra-guide links beyond the TOC so linked-but-not-listed pages (e.g. per-class Apex reference) are also captured. Defaults to true for a whole-guide run, false when a 'section' is given.",
            "required": False,
        },
        "max_pages": {
            "description": "Safety cap on total pages captured (prevents runaway crawls). Defaults to 5000.",
            "required": False,
        },
    }

    DEFAULT_DELIVERABLE = "revenue_lifecycle_management_dev_guide"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _init_options(self, kwargs):
        if hasattr(super(), "_init_options"):
            super()._init_options(kwargs)

        self.options["deliverable"] = (
            self.options.get("deliverable") or self.DEFAULT_DELIVERABLE
        )
        if not self.options.get("output_dir"):
            self.options["output_dir"] = (
                f"docs/salesforce/{self.options['release_version']}/dev-guide"
            )
        self.options["mode"] = str(self.options.get("mode", "all")).lower()
        self.options["headless"] = (
            str(self.options.get("headless", "true")).lower() == "true"
        )
        self.options["concurrency"] = max(1, int(self.options.get("concurrency", 6)))
        self.options["wait_ms"] = int(self.options.get("wait_ms", 3000))
        self.options["batch_delay_ms"] = int(self.options.get("batch_delay_ms", 400))
        self.options["section"] = self.options.get("section") or None
        # `sections` (comma-separated) captures several named TOC sections in one
        # run; `section` (singular) stays supported. A section identifier may be a
        # TOC title OR a page_id — use page_ids when a title itself contains commas
        # (e.g. the Data Processing Engine section).
        raw_sections = self.options.get("sections")
        if raw_sections:
            if isinstance(raw_sections, (list, tuple)):
                filters = [str(s).strip() for s in raw_sections if str(s).strip()]
            else:
                filters = [s.strip() for s in str(raw_sections).split(",") if s.strip()]
        elif self.options["section"]:
            filters = [self.options["section"]]
        else:
            filters = None
        self.options["section_filters"] = filters
        self.options["doc_version"] = self.options.get("doc_version") or None
        self.options["max_pages"] = int(self.options.get("max_pages", 5000))
        # Follow links by default for a whole-guide run; default off when specific
        # sections are requested (so a section capture stays scoped). Override with
        # follow_links: true to also pull in in-scope pages linked from a section
        # but absent from its TOC subtree.
        if self.options.get("follow_links") is None:
            self.options["follow_links"] = self.options["section_filters"] is None
        else:
            self.options["follow_links"] = (
                str(self.options.get("follow_links")).lower() == "true"
            )

        valid_modes = ("discover", "capture", "all", "refresh")
        if self.options["mode"] not in valid_modes:
            raise TaskOptionsError(
                f"mode must be one of {valid_modes}, got {self.options['mode']!r}"
            )

    def _run_task(self):
        try:
            from playwright.async_api import async_playwright  # noqa: F401
        except ImportError:
            self.logger.error(PLAYWRIGHT_INSTALL_HINT)
            raise CommandException("Playwright not installed")

        output_dir = Path(os.getcwd()) / self.options["output_dir"]
        (output_dir / "articles").mkdir(parents=True, exist_ok=True)
        asyncio.run(self._async_run(output_dir))

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
            "capture_method": "tasks.rlm_snapshot_dev_guide.SnapshotSalesforceDevGuide (Playwright + atlas content API)",
            "snapshot_started": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "pages": [],
        }
        if manifest_path.exists():
            try:
                existing = json.loads(manifest_path.read_text(encoding="utf-8"))
                for k, v in base.items():
                    existing.setdefault(k, v)
                self.logger.info(
                    f"Loaded existing manifest with {len(existing.get('pages', []))} pages"
                )
                return existing
            except (json.JSONDecodeError, OSError) as e:
                self.logger.warning(f"Could not load manifest ({e}); starting fresh")
        return base

    def _save_manifest(self, manifest_path: Path, manifest: Dict[str, Any]) -> None:
        manifest["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        manifest["stats"] = self._compute_stats(manifest)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @staticmethod
    def _compute_stats(manifest: Dict[str, Any]) -> Dict[str, Any]:
        pages = manifest.get("pages", [])
        captured = [p for p in pages if p.get("status") == "captured"]
        return {
            "discovered": len(pages),
            "captured": len(captured),
            "pending": len([p for p in pages if p.get("status") == "pending"]),
            "errored": len([p for p in pages if p.get("status") == "error"]),
            "total_captured_body_chars": sum(p.get("body_length", 0) for p in captured),
        }

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
                    raise TaskOptionsError(
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
                manifest["doc_version"] = self.options.get("doc_version")
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

            if not self.options.get("doc_version"):
                # capture-only mode relies on a previously-discovered version
                self.options["doc_version"] = manifest.get("doc_version")
                if not self.options["doc_version"]:
                    raise TaskOptionsError(
                        "doc_version unknown; run mode=discover or pass -o doc_version"
                    )

            # Capture
            if mode in ("capture", "all", "refresh"):
                to_capture = self._select_to_capture(manifest, mode)
                self.logger.info(f"Capture: {len(to_capture)} page(s) queued")
                if to_capture:
                    await self._capture_pages(
                        page, to_capture, articles_dir, manifest, manifest_path
                    )

            await browser.close()

        self._save_manifest(manifest_path, manifest)
        self._build_index(output_dir / "index.md", manifest)
        stats = manifest.get("stats", {})
        self.logger.info(
            f"Done. discovered={stats.get('discovered', 0)} "
            f"captured={stats.get('captured', 0)} "
            f"pending={stats.get('pending', 0)} errored={stats.get('errored', 0)}"
        )
        self.logger.info(f"Manifest: {manifest_path}")

    async def _fetch_meta(self, page) -> Dict[str, Any]:
        self.logger.info(f"  GET {self._meta_url()}")
        res = await page.evaluate(FETCH_TEXT_JS, self._meta_url())
        if not res.get("ok"):
            raise CommandException(
                f"TOC fetch failed (HTTP {res.get('status')}). The atlas API may "
                "have blocked the session or the deliverable slug is wrong."
            )
        try:
            return json.loads(res.get("text") or "{}")
        except json.JSONDecodeError as e:
            raise CommandException(f"TOC response was not JSON: {e}")

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
    ) -> None:
        concurrency = self.options["concurrency"]
        deliverable = self.options["deliverable"]
        doc_version = self.options["doc_version"]
        follow = self.options["follow_links"]
        max_pages = self.options["max_pages"]
        fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")

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
                "left uncaptured (recorded as 'pending'). Raise -o max_pages or "
                "re-run mode=capture to fetch them."
            )

        # --- Phase 2: write every fetched page with the full set known ---------
        known_ids = set(fetched)
        by_id = {p["page_id"]: p for p in manifest.get("pages", [])}
        written = 0
        for pid, data in fetched.items():
            body_md = html_to_markdown(data["html"], deliverable=deliverable, known_ids=known_ids)
            rec = by_id.get(pid, {"page_id": pid})
            rec.setdefault("section", (meta.get(pid) or {}).get("section"))
            if (meta.get(pid) or {}).get("parent") and not rec.get("parent_page"):
                rec["parent_page"] = meta[pid]["parent"]
            if not body_md:
                rec["status"] = "error"
                rec["error"] = "empty body"
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
            by_id[pid] = rec
        for pid, err in errors.items():
            rec = by_id.get(pid, {"page_id": pid})
            rec.setdefault("section", (meta.get(pid) or {}).get("section"))
            rec["status"] = "error"
            rec["error"] = err
            by_id[pid] = rec
        # Record discovered-but-unfetched pages as 'pending' so they survive in the
        # manifest and a later mode=capture run can fetch them (don't downgrade a
        # page already captured in a prior run).
        for pid in unfetched:
            rec = by_id.get(pid, {"page_id": pid})
            rec.setdefault("section", (meta.get(pid) or {}).get("section"))
            if (meta.get(pid) or {}).get("parent") and not rec.get("parent_page"):
                rec["parent_page"] = meta[pid]["parent"]
            if rec.get("status") != "captured":
                rec["status"] = "pending"
            by_id[pid] = rec

        manifest["pages"] = sorted(by_id.values(), key=lambda p: p["page_id"])
        self._save_manifest(manifest_path, manifest)
        self.logger.info(f"  wrote {written} page(s); {len(errors)} error(s)")

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
            "| Metric | Value |",
            "|:--|--:|",
            f"| Discovered | {stats.get('discovered', 0)} |",
            f"| Captured | {stats.get('captured', 0)} |",
            f"| Pending | {stats.get('pending', 0)} |",
            f"| Errored | {stats.get('errored', 0)} |",
            f"| Total body chars | {stats.get('total_captured_body_chars', 0):,} |",
            "",
        ]

        if captured:
            by_section: Dict[str, List[Dict[str, Any]]] = {}
            for p in captured:
                by_section.setdefault(p.get("section") or "(uncategorized)", []).append(p)
            for section in sorted(by_section):
                items = by_section[section]
                lines.append(f"## {section} ({len(items)})")
                lines.append("")
                lines.append("| Page | ID | Chars |")
                lines.append("|:--|:--|--:|")
                for p in sorted(items, key=lambda x: x["page_id"]):
                    pid = p["page_id"]
                    title = p.get("title", pid)
                    file_path = p.get("file", f"articles/{pid}.md")
                    lines.append(f"| [{title}](./{file_path}) | `{pid}` | {p.get('body_length', 0):,} |")
                lines.append("")

        if errored:
            lines.append(f"## Errored ({len(errored)})")
            lines.append("")
            for p in sorted(errored, key=lambda x: x["page_id"]):
                lines.append(f"- `{p['page_id']}` — {p.get('error', 'unknown')}")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append(
            f"*Generated by `tasks.rlm_snapshot_dev_guide.SnapshotSalesforceDevGuide` "
            f"on {manifest.get('last_updated', 'n/a')}.*"
        )
        index_path.write_text("\n".join(lines), encoding="utf-8")
