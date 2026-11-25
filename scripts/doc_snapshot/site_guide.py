"""Capture a server-rendered Salesforce developer guide as markdown.

Salesforce is moving developer guides off the "atlas" viewer (``dev_guide.py``)
onto server-rendered sites such as

    https://developer.salesforce.com/docs/revenue/revenue-management/guide/<slug>.html
    https://developer.salesforce.com/docs/industries/industries-common-dev/guide/<slug>.html

Atlas URLs 301 to these, and the atlas content API serves the new guides empty
or truncated, so ``dev_guide.py`` cannot capture them. These sites need neither
a browser nor the content API. Every page is plain HTML (``curl`` works):

    * the article is the markup inside ``<doc-content-layout ...> ... </doc-content-layout>``;
    * the full table of contents is the HTML-escaped JSON in that element's
      ``sidebar-content`` attribute (nodes with ``label``, ``name`` = page path,
      ``children``), identical on every page of the guide.

Two site-specific elements are rewritten before conversion: ``<doc-heading>``
becomes a heading and ``<dx-code-block code-block="...">`` a ``<pre>`` block.
The result goes through the same HTML -> markdown converter as atlas pages.

NO VERSION SELECTOR. The site serves one release at a time (API 68.0 = release
264 when this was written); older releases exist only as PDFs. A capture
therefore counts the ``/services/data/vNN.0`` versions in the pages it fetched
and refuses, before writing anything, when the dominant one is not the preset's
``api_version``. Without that check a run after the next GA would write the new
release's text into the old release's tree.

LEGACY IDS. Atlas page ids (``rlm_get_started.htm``) become slugs
(``rlm-get-started``). The manifest's ``legacy_id_map`` maps old ids to new
slugs: a TOC match on the usual rename (``_`` to ``-``, ``.htm`` dropped), else
the atlas URL's redirect target. Ids neither finds are keys of
``unmapped_legacy_ids`` instead of being guessed. The old ids come from the
prior atlas manifest of the same output directory.

OUTPUT (same layout as the atlas corpus, files named by slug)

    <output_dir>/articles/<slug>.md
    <output_dir>/manifest.json
    <output_dir>/index.md

Run through ``python -m scripts.doc_snapshot dev-guide`` with a preset that
sets ``source: site``. scripts/doc_snapshot/README.md covers options.
"""

import html as html_lib
import http.client
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from scripts.doc_snapshot._core import (
    OptionsError,
    SnapshotError,
    as_id_set,
    as_int,
    attribution_note,
    captured_table,
    compute_stats,
    get_logger,
    index_footer,
    log_done,
    normalize_mode,
    raise_on_capture_errors,
    read_manifest,
    require_positive,
    resolve_output_dir,
    stats_table,
    today,
    utc_timestamp,
    validate_options,
    write_manifest,
    yaml_escape,
)
from scripts.doc_snapshot.dev_guide import html_to_markdown
from scripts.doc_snapshot.guard import (
    read_prior,
    refusal_reason,
    report_orphans,
    report_refusals,
)

CAPTURE_METHOD = "scripts/doc_snapshot dev-guide (server-rendered site, HTTP)"
SITE_HOST = "https://developer.salesforce.com"
USER_AGENT = "rlm-base-dev doc_snapshot (+https://github.com/bgaldino/rlm-base-dev)"

# A page id (slug) is a bare filename: it names a local file.
_SAFE_SLUG_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")
_API_VERSION_RE = re.compile(r"/services/data/v(\d+\.\d+)")
# Tag attributes, quote-aware: a literal ">" inside a quoted value (``Map<String>``,
# ``->``) does not end the tag.
_ATTRS = r'((?:[^>"]|"[^"]*")*)'
_CONTENT_RE = re.compile(r"<doc-content-layout\b" + _ATTRS + r">(.*)</doc-content-layout>", re.DOTALL)
_ATTR_RE = re.compile(r'([\w:-]+)="([^"]*)"')
_DOC_HEADING_RE = re.compile(
    r"<doc-heading\b" + _ATTRS + r">(?:\s*</doc-heading>)?", re.DOTALL
)
_CODE_BLOCK_RE = re.compile(
    r"<dx-code-block\b" + _ATTRS + r">(?:\s*</dx-code-block>)?", re.DOTALL
)
_CALLOUT_RE = re.compile(r"<doc-content-callout\b" + _ATTRS + r">(.*?)</doc-content-callout>", re.DOTALL)
_CUSTOM_TAG_RE = re.compile(r"</?((?:doc|dx)-[a-z0-9-]+)")
_HREF_RE = re.compile(r'href="([^"]*)"')
_H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.DOTALL)

# (status, body text, final url); status 0 = the request never completed.
Fetcher = Callable[[str], Tuple[int, str, str]]


# ---------------------------------------------------------------------------
# Page parsing (pure functions; the unit tests drive these with saved HTML)
# ---------------------------------------------------------------------------


def normalize_key(value: str) -> str:
    """Section / id key: lower case, ``_`` as ``-``, no ``.htm``/``.html``."""
    key = value.strip().lower().rsplit("/", 1)[-1]
    key = re.sub(r"\.html?$", "", key)
    return key.replace("_", "-")


def slug_of(path: str, guide_path: str) -> Optional[str]:
    """The page slug of a TOC ``name``/href under ``guide_path``, else None.

    ``guide_path`` is e.g. ``/docs/revenue/revenue-management/guide/``. Fragments
    and queries are dropped; anything that is not a flat ``<slug>.html`` under
    the guide (another guide, a path separator, ``..``) is rejected.
    """
    if not path:
        return None
    if path.startswith(SITE_HOST):
        path = path[len(SITE_HOST):]
    path = path.split("#", 1)[0].split("?", 1)[0]
    if not path.startswith(guide_path) or not path.endswith(".html"):
        return None
    slug = path[len(guide_path):-len(".html")]
    if not slug or ".." in slug or not _SAFE_SLUG_RE.match(slug):
        return None
    return slug


def parse_page(page_html: str) -> Optional[Dict[str, Any]]:
    """Split a fetched page into ``{attrs, body}``; None when it is not a guide page.

    A soft error page (HTTP 200 with the site's 404 shell) has no
    ``<doc-content-layout>``, so it is not mistaken for content.
    """
    m = _CONTENT_RE.search(page_html or "")
    if not m:
        return None
    return {"attrs": dict(_ATTR_RE.findall(m.group(1))), "body": m.group(2)}


def parse_toc(attrs: Dict[str, str]) -> List[Dict[str, Any]]:
    """The TOC tree from a page's ``sidebar-content`` attribute."""
    raw = attrs.get("sidebar-content")
    if not raw:
        raise SnapshotError(
            "the page has no sidebar-content attribute, so the guide's table of "
            "contents cannot be read (the site layout may have changed)"
        )
    try:
        toc = json.loads(html_lib.unescape(raw))
    except json.JSONDecodeError as exc:
        raise SnapshotError(f"sidebar-content is not valid JSON: {exc}") from exc
    if not isinstance(toc, list):
        raise SnapshotError("sidebar-content is not a list of nodes")
    return toc


def flatten_toc(
    toc: List[Dict[str, Any]], guide_path: str, section_filters: Optional[List[str]]
) -> Tuple[List[Dict[str, Any]], int]:
    """Ordered, de-duplicated page records from the TOC tree, plus a skipped count.

    Each record is ``{page_id, title, section, parent_page, ancestors, alt_ancestors}``; ``page_id`` is the
    slug and ``section`` the top-level ancestor's label. With ``section_filters``
    only those subtrees (each matched by label or slug, ``_``/``-`` and the
    ``.htm`` suffix ignored, so an atlas id works) are returned. ``skipped`` counts
    nodes whose target is not a page of this guide.
    """
    pages: List[Dict[str, Any]] = []
    seen = set()
    by_slug: Dict[str, Dict[str, Any]] = {}
    skipped = 0

    def walk(nodes, section, parent, anc=()):
        nonlocal skipped
        for node in nodes or []:
            if not isinstance(node, dict):
                continue
            slug, label = _node_ident(node, guide_path)
            if not slug and node.get("name"):
                skipped += 1
            this_section = section if section is not None else label
            # Every way a section filter can name this node (label, slug key), kept
            # for the node and its ancestors so a later --mode capture can resolve
            # label-only and nested sections without a TOC walk.
            here = anc + (_node_entry(label, slug),)
            if slug and slug not in seen:
                seen.add(slug)
                by_slug[slug] = {
                    "page_id": slug, "title": label,
                    "section": this_section, "parent_page": parent, "ancestors": list(here),
                    "alt_ancestors": [],
                }
                pages.append(by_slug[slug])
            elif slug and list(here) != by_slug[slug]["ancestors"] and list(here) not in by_slug[slug]["alt_ancestors"]:
                # A page listed under another TOC branch: keep that path apart from the first.
                by_slug[slug]["alt_ancestors"].append(list(here))
            walk(node.get("children"), this_section, slug or parent, here)

    if section_filters:
        for needle in section_filters:
            nodes = _find_sections(toc, needle, guide_path)
            if not nodes:
                raise OptionsError(f"section {needle!r} not found in the guide TOC")
            # A page listed twice is one page (its first listing wins); only distinct pages are ambiguous.
            listings, distinct, seen_slugs = nodes, [], set()
            for n_ in nodes:
                sl = _node_ident(n_, guide_path)[0]
                if sl and sl in seen_slugs:
                    continue
                seen_slugs.add(sl)
                distinct.append(n_)
            nodes = distinct
            if len(nodes) > 1:
                raise OptionsError(
                    f"section {needle!r} names {len(nodes)} different TOC nodes; name one by its page id"
                )
            node = nodes[0]
            # Walk every listing of the page: a later listing may carry children the first lacks.
            for n_ in listings:
                walk([n_], node.get("label") or needle, None, _ancestor_entries(toc, n_, guide_path))
    else:
        walk(toc, None, None)
    return pages, skipped


def _legacy_map(manifest) -> Dict[str, str]:
    """``legacy_id_map`` as {old id: slug}; a hand-edited non-string entry is ignored."""
    raw = manifest.get("legacy_id_map")
    return {k: v for k, v in raw.items() if isinstance(k, str) and isinstance(v, str)} if isinstance(raw, dict) else {}


def _record_section_paths(rec, d) -> None:
    """Fold a section walk's listing ``d`` of a page into its stored record: the first path stays
    canonical and every other branch (this walk's own, then its alternates) accumulates, since a
    section walk sees only the branches under its section."""
    rec.setdefault("ancestors", d["ancestors"])
    rec["alt_ancestors"] = _merge_paths(
        rec.get("alt_ancestors"), [d["ancestors"]] + list(d.get("alt_ancestors") or []), rec["ancestors"])


def _paths_of(rec) -> list:
    """Every recorded TOC path of a page record: the first listing, then the alternates.
    Tolerates a legacy or hand-edited record (missing or non-list fields, non-string entries)."""
    out = []
    first = rec.get("ancestors")
    alts = rec.get("alt_ancestors")
    for path in [first] + (alts if isinstance(alts, list) else []):
        if isinstance(path, list) and path and all(isinstance(e, str) for e in path):
            out.append(path)
    return out


def _merge_paths(stored, new, canonical) -> list:
    """Union of alternate paths, without the canonical one and without duplicates."""
    out = []
    for path in list(stored if isinstance(stored, list) else []) + list(new or []):
        if isinstance(path, list) and path != canonical and path not in out:
            out.append(path)
    return out


def _node_ident(node, guide_path: str):
    """A TOC node's slug and label, derived once for the walk, the paths and the matcher."""
    slug = slug_of(node.get("name") or (node.get("link") or {}).get("href") or "", guide_path)
    return slug, node.get("label") or slug or ""


def _node_entry(label: str, slug: Optional[str]) -> str:
    """One TOC node as a path entry: its label and slug key (what a filter may name)."""
    return f"{(label or '').strip().lower()}\t{normalize_key(slug) if slug else ''}"


def _ancestor_entries(nodes, target, guide_path: str, anc=()) -> tuple:
    """Path entries of ``target``'s ancestors from the top of the TOC (not ``target``)."""
    for node in nodes or []:
        if not isinstance(node, dict):
            continue
        if node is target:
            return anc
        slug, label = _node_ident(node, guide_path)
        found = _ancestor_entries(node.get("children"), target, guide_path, anc + (_node_entry(label, slug),))
        if found is not None:
            return found
    return None


def _entry_matches(label: str, slug_key: str, needle: str) -> bool:
    """One matcher for a section filter: the node's label or its slug key (``_``/``-``, ``.htm`` ignored)."""
    n = needle.strip()
    if (label or "").strip().lower() == n.lower():
        return True
    # A label with spaces or a slash is never a page id (normalize_key would keep only
    # the text after the last slash and match an unrelated page).
    return bool(slug_key) and not re.search(r"[\s/]", n) and slug_key == normalize_key(n)


def _find_sections(nodes, needle: str, guide_path: str) -> List[Dict[str, Any]]:
    """Every TOC node a filter names (a match's own subtree is not searched again)."""
    found: List[Dict[str, Any]] = []
    for node in nodes or []:
        if not isinstance(node, dict):
            continue
        slug, label = _node_ident(node, guide_path)
        if _entry_matches(label, normalize_key(slug) if slug else "", needle):
            found.append(node)
        else:
            found.extend(_find_sections(node.get("children"), needle, guide_path))
    return found


def page_title(body: str, fallback: str) -> str:
    """The page's own H1 text, else ``fallback``."""
    m = _H1_RE.search(body or "")
    if m:
        text = html_lib.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
        text = " ".join(text.split())
        if text:
            return text
    return fallback


def normalize_body(body: str) -> str:
    """Rewrite the site's custom elements into plain HTML the converter handles.

    ``<doc-heading header= aria-level=>`` -> ``<hN>``; ``<dx-code-block
    code-block="...">`` -> ``<pre><code>`` (the code is an attribute, entity
    escaped). Other ``doc-*``/``dx-*`` elements are left alone; ``unhandled_tags``
    reports them.
    """
    def heading(m):
        attrs = dict(_ATTR_RE.findall(m.group(1)))
        text = html_lib.unescape(attrs.get("header", "")).strip()
        level = attrs.get("aria-level", "2")
        level = level if level in ("1", "2", "3", "4", "5", "6") else "2"
        return f"<h{level}>{html_lib.escape(text, quote=True)}</h{level}>" if text else ""

    def code(m):
        attrs = dict(_ATTR_RE.findall(m.group(1)))
        text = html_lib.unescape(attrs.get("code-block", "")).strip("\n")
        return f"<pre><code>{html_lib.escape(text, quote=True)}</code></pre>"

    def callout(m):
        attrs = dict(_ATTR_RE.findall(m.group(1)))
        label = html_lib.unescape(attrs.get("header") or attrs.get("variant") or "").strip()
        lead = f"<p><strong>{html_lib.escape(label, quote=True)}:</strong></p>" if label else ""
        return lead + m.group(2)

    body = _CALLOUT_RE.sub(callout, body)
    body = _DOC_HEADING_RE.sub(heading, body)
    return _CODE_BLOCK_RE.sub(code, body)


def unhandled_tags(body: str) -> List[str]:
    """Custom ``doc-*``/``dx-*`` element names left after ``normalize_body``."""
    return sorted(set(_CUSTOM_TAG_RE.findall(normalize_body(body))))


def rewrite_links(body: str, guide_path: str, known: set) -> str:
    """Point intra-guide links at sibling files, and make every other link absolute.

    A link to a captured page becomes ``./<slug>.md[#frag]``; a link to a page
    that was not captured keeps its online URL, so no link is dead.
    """
    def repl(m):
        href = html_lib.unescape(m.group(1))
        slug = slug_of(href, guide_path)
        frag = "#" + href.split("#", 1)[1] if "#" in href else ""
        if slug and slug in known:
            new = f"./{slug}.md{frag}"
        elif href.startswith("/") and not href.startswith("//"):
            new = SITE_HOST + href
        else:
            return m.group(0)
        return f'href="{html_lib.escape(new, quote=True)}"'

    return _HREF_RE.sub(repl, body)


def api_versions(page_html: str) -> List[str]:
    """Every ``/services/data/vNN.N`` version the page mentions."""
    return [f"v{v}" for v in _API_VERSION_RE.findall(html_lib.unescape(page_html or ""))]


def observed_version(votes: Counter) -> Optional[str]:
    """The dominant API version among ``votes``, as ``68.0``; None without votes."""
    if not votes:
        return None
    def rank(item):  # most pages first; a tie goes to the newer version (deterministic)
        version, count = item
        return count, tuple(int(n) for n in version.lstrip("v").split("."))
    return max(votes.items(), key=rank)[0].lstrip("v")


def guess_slug(legacy_id: str) -> str:
    """The usual rename of an atlas page id: ``rlm_get_started.htm`` -> ``rlm-get-started``."""
    return normalize_key(legacy_id)


def render_page_markdown(
    *, slug: str, title: str, body_md: str, source_url: str, release_version: str,
    release_name: str, deliverable: str, section: Optional[str],
    parent_page: Optional[str], legacy_page_id: Optional[str], api_version: str,
    fetched_at: str,
) -> str:
    fm = [
        "---",
        f"page_id: {slug}",
        f"title: {yaml_escape(title)}",
        f"source_url: {source_url}",
        f"release: {yaml_escape(release_version)}",
        f"release_name: {yaml_escape(release_name)}",
        f"deliverable: {yaml_escape(deliverable)}",
        f"api_version: {yaml_escape(api_version)}",
    ]
    if section:
        fm.append(f"section: {yaml_escape(section)}")
    if parent_page:
        fm.append(f"parent_page: {parent_page}")
    if legacy_page_id:
        fm.append(f"legacy_page_id: {legacy_page_id}")
    fm.append(f"fetched_at: {yaml_escape(fetched_at)}")
    fm.append("---")
    return (
        "\n".join(fm) + "\n\n" + body_md.strip() + "\n\n"
        + attribution_note(source_url, "Salesforce developer documentation") + "\n"
    )


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # noqa: D401 - urllib hook
        return None


def http_fetch(url: str, timeout: int = 60) -> Tuple[int, str, str]:
    """GET ``url`` following redirects; returns (status, text, final url)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace"), resp.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, "", url
    except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError, ValueError):
        return 0, "", url


def http_redirect_target(url: str, timeout: int = 30) -> Optional[str]:
    """The ``Location`` of ``url``'s redirect (not followed), or None."""
    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        opener.open(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        if exc.code in (301, 302, 303, 307, 308):
            return exc.headers.get("Location")
    except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError, ValueError):
        pass
    return None


# ---------------------------------------------------------------------------
# Snapshotter
# ---------------------------------------------------------------------------


class SiteGuideSnapshot:
    """Capture a server-rendered developer guide as per-page markdown.

    Options (snake_case; the CLI maps --kebab-case flags onto them):

        release_version  required; path component, e.g. '264'
        release_name     required; e.g. "Winter '27"
        site_url         required; any page of the guide, e.g.
                         https://developer.salesforce.com/docs/revenue/revenue-management/guide/rlm-get-started.html
        api_version      required; the API version the preset's release serves, e.g.
                         '68.0'. A capture refuses when the site shows another one.
        deliverable      the guide's legacy atlas id (default: the guide's last path
                         segment). Names the frontmatter and builds the atlas URLs the
                         legacy-id redirect lookup uses.
        sections         capture only these TOC subtrees, each named by label or slug
                         (an atlas page id works too)
        output_dir       default docs/salesforce/{release_version}/dev-guide
        mode             discover | capture | all | refresh (default all)
        concurrency      pages fetched per batch (default 4)
        batch_delay_ms   ms between batches (default 500)
        max_pages        safety cap on pages fetched (default 5000)
        probe_page       slug of a page that shows /services/data/vNN.0, fetched only when
                         the captured pages show no version (e.g. a metadata-only section)
        accept_shrinkage page ids whose capture may shrink past the guard's stub threshold
        accept_uncovered atlas page ids (with .htm) a sectioned atlas-to-site switch may leave
                         on atlas because the section's site pages do not replace them
    """

    def __init__(self, options: Dict[str, Any], logger=None, fetcher: Optional[Fetcher] = None,
                 redirect_resolver: Optional[Callable[[str], Optional[str]]] = None,
                 sleep: Callable[[float], None] = time.sleep):
        self.options = dict(options)
        self.logger = logger or get_logger()
        self._version_verified = False
        self._switching = False
        self._start_votes: Counter = Counter()
        self._fetch_once = fetcher or http_fetch
        self._redirect = redirect_resolver or http_redirect_target
        self._sleep = sleep
        self.refused: List[Tuple[str, str]] = []
        self.accepted: List[str] = []
        self.orphaned: List[str] = []
        self._toc_ids: Optional[set] = None
        self._section_ids: Optional[set] = None
        self._init_options()

    # -- options ----------------------------------------------------------

    def _init_options(self) -> None:
        o = self.options
        validate_options(
            o, "release_version", "release_name", "site_url", "api_version",
            list_options=("sections", "accept_shrinkage", "accept_uncovered"),
        )
        for name in ("release_version", "release_name", "deliverable", "output_dir",
                     "site_url", "api_version", "probe_page"):
            if o.get(name) is not None:
                o[name] = str(o[name])
        if o.get("doc_version"):
            raise OptionsError(
                "doc_version applies to atlas guides; a site guide pins api_version instead"
            )
        parsed = urllib.parse.urlparse(o["site_url"])
        m = self._GUIDE_RE.match(parsed.path)
        if f"{parsed.scheme}://{parsed.netloc}" != SITE_HOST or not m:
            raise OptionsError(
                f"site_url must be a page of a developer.salesforce.com guide, like "
                f"{SITE_HOST}/docs/<area>/<guide>/guide/<slug>.html; got {o['site_url']!r}"
            )
        self.guide_path = m.group(1)
        self.start_slug = slug_of(parsed.path, self.guide_path)
        if not self.start_slug:
            raise OptionsError(f"site_url does not name a guide page slug: {o['site_url']!r}")
        if not re.match(r"^\d+\.\d+$", o["api_version"]):
            raise OptionsError(f"api_version must look like '68.0', got {o['api_version']!r}")
        o["deliverable"] = o.get("deliverable") or self.guide_path.split("/")[3]
        o.setdefault("output_dir", f"docs/salesforce/{o['release_version']}/dev-guide")
        o["mode"] = normalize_mode(o.get("mode"))
        o["concurrency"] = as_int(o.get("concurrency"), 4)
        o["batch_delay_ms"] = as_int(o.get("batch_delay_ms"), 500)
        o["max_pages"] = as_int(o.get("max_pages"), 5000)
        require_positive(o, "concurrency", "max_pages")
        if o["batch_delay_ms"] < 0:
            raise OptionsError(f"batch_delay_ms must be >= 0, got {o['batch_delay_ms']}")
        sections = o.get("sections")
        if sections is not None and not isinstance(sections, (list, tuple)):
            sections = [sections]
        o["section_filters"] = [str(s).strip() for s in sections] if sections else None
        o["accept_shrinkage"] = as_id_set(o.get("accept_shrinkage"))
        o["accept_uncovered"] = as_id_set(o.get("accept_uncovered"))

    def preflight(self) -> None:
        """Raise offline-detectable conflicts before any target of a batch runs."""
        path = self._manifest_path(resolve_output_dir(self.options["output_dir"]))
        self._check_switch(path, self.options["mode"])
        self._check_identity_change(path, self.options["mode"])
        if self.options["mode"] == "capture" and self.options.get("section_filters") and path.exists():
            self._stored_section_ids(
                read_manifest(path, {"pages": []}, "pages").get("pages", []),
                self.options["section_filters"])

    def run(self) -> Dict[str, Any]:
        output_dir = resolve_output_dir(self.options["output_dir"])
        return self._run(output_dir)

    # -- helpers ----------------------------------------------------------

    def _manifest_path(self, output_dir: Path) -> Path:
        return output_dir / "manifest.json"

    def _page_url(self, slug: str) -> str:
        return f"{SITE_HOST}{self.guide_path}{slug}.html"

    @staticmethod
    def _file_is_site(path: Path) -> bool:
        """True when the manifest file is missing, unreadable, or written by this tool."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return True
        return not isinstance(data, dict) or data.get("source") == "site" or "pages" not in data

    def _check_switch(self, path: Path, mode: str) -> None:
        """An atlas corpus is replaced only by a refresh, like a doc_version change."""
        if self._file_is_site(path):
            return
        if mode == "refresh":
            # A sectioned switch is allowed; _check_covered refuses it once the site's pages are
            # known, unless they cover every atlas article already captured.
            return
        manifest = read_manifest(path, {"pages": []}, "pages")
        if any(self._has_article(path, p) for p in manifest.get("pages", [])):
            raise OptionsError(
                "the output directory holds an atlas capture; recording the site's "
                "pages over it would orphan its files. Use --mode refresh to switch "
                "the corpus to the site (its atlas ids become legacy_id_map entries)."
            )

    _GUIDE_RE = re.compile(r"^(/docs/[^/]+/[^/]+/guide/)[^/]+\.html$")

    @staticmethod
    def _describe(changes) -> str:
        return "; ".join(f"{k} {a!r} -> {b!r}" for k, (a, b) in changes.items())

    @staticmethod
    def _has_article(path: Path, page: Dict[str, Any]) -> bool:
        """The page has an article on disk (captured, or a failed refetch of one)."""
        return page.get("status") == "captured" or (
            bool(page.get("page_id")) and (path.parent / "articles" / f"{page['page_id']}.md").exists())

    def _identity_changes(self, raw: Dict[str, Any]) -> Dict[str, Tuple[Any, Any]]:
        """What a stored site manifest records about its corpus that this run changes.

        Keys: ``guide`` (the guide path of ``site_url``), ``deliverable``, ``release``,
        ``api_version``; each maps to (stored, requested). ``release_name`` and the
        start page within the same guide are labels and do not count.
        """
        o = self.options
        m = self._GUIDE_RE.match(urllib.parse.urlparse(str(raw.get("site_url") or "")).path)
        want = {
            "guide": (m.group(1) if m else None, self.guide_path),
            "deliverable": (raw.get("deliverable"), o["deliverable"]),
            "release": (raw.get("release"), o["release_version"]),
            "api_version": (raw.get("api_version"), o["api_version"]),
        }
        # Only a recorded value that differs counts (a missing one is not a change).
        return {k: (a, b) for k, (a, b) in want.items() if a and str(a) != str(b)}

    def _check_identity_change(self, path: Path, mode: str) -> None:
        """A corpus captured for one guide, release or API version is replaced whole or not at all.

        Relabelling the manifest while keeping its captured articles would claim the
        new identity over old text (or mix two guides' pages), so any change needs a
        full ``--mode refresh`` (or a separate output_dir).
        """
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(raw, dict) or raw.get("source") != "site":
            return
        changes = self._identity_changes(raw)
        if not changes:
            return
        if not any(self._has_article(path, p) for p in raw.get("pages", []) if isinstance(p, dict)):
            return
        if mode != "refresh" or self.options.get("section_filters"):
            what = self._describe(changes)
            raise OptionsError(
                f"the output directory holds a different capture ({what}); its articles would "
                "be kept under the new identity. Run the whole guide with --mode refresh "
                "(no --section), or use a separate output_dir."
            )

    def _load_or_init_manifest(self, path: Path) -> Dict[str, Any]:
        o = self.options
        base = {
            "source": "site",
            "deliverable": o["deliverable"],
            "release": o["release_version"],
            "release_name": o["release_name"],
            "api_version": o["api_version"],
            "observed_api_version": None,
            "site_url": o["site_url"],
            "guide_title": None,
            "capture_method": CAPTURE_METHOD,
            "snapshot_started": today(),
            "legacy_id_map": {},
            "unmapped_legacy_ids": {},
            "pages": [],
        }
        manifest = read_manifest(path, base, "pages", self.logger)
        # read_manifest backfills `source` from the defaults, so ask the file itself.
        if not self._file_is_site(path):
            # Atlas manifest: keep only what maps its ids; the pages restart.
            legacy = sorted(
                p["page_id"] for p in manifest.get("pages", [])
                if str(p.get("page_id", "")).endswith(".htm")
            )
            self.logger.info(f"Atlas manifest found: {len(legacy)} legacy page id(s) to map")
            fresh = dict(base)
            fresh["_legacy_ids"] = legacy
            old_files = sorted(
                f"articles/{p['page_id']}.md" for p in manifest.get("pages", [])
                if str(p.get("page_id", "")).endswith(".htm") and self._has_article(path, p)
            )
            if old_files:
                fresh["superseded_files"] = old_files
                self.logger.warning(
                    f"  {len(old_files)} atlas article file(s) are candidates for removal and stay on disk; "
                    "only those whose site page was captured end up under superseded_files in the "
                    "saved manifest. Remove just those with the re-capture commit"
                )
            return fresh
        changes = self._identity_changes(manifest)
        if "guide" in changes:
            # Another guide's pages are not this guide's: start the page list over (a full
            # refresh follows); its article files stay on disk, listed as superseded
            # (a file the refresh recaptures is dropped from the list when saved).
            old_files = sorted(
                f"articles/{p['page_id']}.md" for p in manifest.get("pages", [])
                if self._has_article(path, p)
            )
            # Atlas files held back from the list (their page was never captured) belong to the
            # old guide too: list every one still on disk.
            ids = [o for key in ("legacy_id_map", "unmapped_legacy_ids")
                   for o in (manifest.get(key) if isinstance(manifest.get(key), dict) else {})]
            old_files = sorted(set(old_files) | {
                f for f in (f"articles/{o}.md" for o in ids) if (path.parent / f).is_file()})
            self.logger.warning(
                f"  the manifest describes a different guide ({self._describe(changes)}): "
                f"{len(manifest.get('pages', []))} page record(s) are dropped"
            )
            fresh = dict(base)
            prior_list = manifest.get("superseded_files")
            superseded = sorted({f for f in (prior_list if isinstance(prior_list, list) else []) if isinstance(f, str)}
                                | set(old_files))
            if superseded:
                fresh["superseded_files"] = superseded
            return fresh
        if changes:
            # Same guide, another release, deliverable or API version: nothing is current
            # until it is recaptured, so a capped or failed run leaves pages pending.
            stale = [p["page_id"] for p in manifest.get("pages", []) if self._has_article(path, p)]
            for page in manifest.get("pages", []):
                page["status"] = "pending"
            if stale:
                self.logger.warning(
                    f"  {self._describe(changes)}: {len(stale)} "
                    "captured page(s) are reset to pending; their old article files stay on disk "
                    "until each is recaptured"
                )
        manifest.update(
            api_version=o["api_version"], site_url=o["site_url"], release=o["release_version"],
            release_name=o["release_name"], deliverable=o["deliverable"], capture_method=CAPTURE_METHOD,
        )
        return manifest

    @staticmethod
    def _settle_superseded(path: Path, manifest: Dict[str, Any]) -> None:
        """List an atlas article as superseded only once the site page it maps to has an article.

        A refused, failed or not-yet-captured replacement leaves the atlas file as the only
        copy, and an id that maps to nothing has no replacement at all, so neither is offered
        for removal (unmapped ids are reported under ``unmapped_legacy_ids``). A file is
        listed again when its page gets an article. Entries for files already removed are
        pruned.
        """
        pages = [p for p in manifest.get("pages", []) if isinstance(p, dict) and p.get("page_id")]
        out = path.parent
        captured = {p["page_id"] for p in pages if p.get("status") == "captured"}
        # A page has an article when its file is on disk (a refused refetch keeps the old one).
        have = {p["page_id"] for p in pages if (out / "articles" / f"{p['page_id']}.md").is_file()}
        mapped = _legacy_map(manifest)
        unmapped = manifest.get("unmapped_legacy_ids")
        unmapped = unmapped if isinstance(unmapped, dict) else {}
        replacement = {f"articles/{old}.md": slug for old, slug in mapped.items()}
        held = {f"articles/{old}.md" for old in unmapped}
        stored = manifest.get("superseded_files")
        stored = [f for f in stored if isinstance(f, str)] if isinstance(stored, list) else []
        keep = {f for f in stored
                if f not in {f"articles/{pid}.md" for pid in captured} and f not in held
                and (f not in replacement or replacement[f] in have) and (out / f).is_file()}
        for f, slug in replacement.items():  # (re)list a mapped atlas file whose page has an article
            if slug in have and (out / f).is_file():
                keep.add(f)
        if keep:
            manifest["superseded_files"] = sorted(keep)
        else:
            manifest.pop("superseded_files", None)

    def _save_manifest(self, path: Path, manifest: Dict[str, Any]) -> None:
        if self._switching and not self._version_verified:
            raise SnapshotError(
                "switching an atlas capture to the site needs a confirmed API version, and "
                "none was confirmed; the atlas manifest was kept. Rerun with --mode all or "
                "refresh while the site is reachable (set probe_page if its pages show no version)."
            )
        self._settle_superseded(path, manifest)
        manifest["last_updated"] = utc_timestamp()
        manifest["stats"] = compute_stats(manifest, "pages")
        write_manifest(path, {k: v for k, v in manifest.items() if k != "_legacy_ids"})

    # -- fetching ---------------------------------------------------------

    def _get(self, url: str, attempts: int = 3) -> Tuple[int, str, str]:
        """GET with retries on a failed connection, 429 and 5xx (backoff 2s, 4s)."""
        status, text, final = 0, "", url
        for attempt in range(attempts):
            status, text, final = self._fetch_once(url)
            if status == 200 or 400 <= status < 500 and status != 429:
                break
            if attempt + 1 < attempts:
                self._sleep(2 ** (attempt + 1))
        return status, text, final

    def _fetch_page(self, slug: str) -> Dict[str, Any]:
        url = self._page_url(slug)
        status, text, final = self._get(url)
        if status != 200:
            return {"id": slug, "error": f"HTTP {status}" if status else "connection failed"}
        if slug_of(final, self.guide_path) != slug:
            return {"id": slug, "error": f"redirected away to {final}"}
        parsed = parse_page(text)
        if parsed is None:
            return {"id": slug, "error": "no doc-content-layout (not a guide page)"}
        return {"id": slug, "html": text, "attrs": parsed["attrs"], "body": parsed["body"]}

    # -- run --------------------------------------------------------------

    def _run(self, output_dir: Path) -> Dict[str, Any]:
        o = self.options
        mode = o["mode"]
        manifest_path = self._manifest_path(output_dir)
        self._check_switch(manifest_path, mode)
        self._check_identity_change(manifest_path, mode)
        manifest = self._load_or_init_manifest(manifest_path)
        legacy_ids = manifest.get("_legacy_ids")
        self._version_verified = False
        self._switching = "_legacy_ids" in manifest
        self._start_votes = Counter()
        self._toc_ids = None
        self._section_ids = None
        self.refused, self.accepted, self.orphaned = [], [], []

        if o["accept_uncovered"] and not (self._switching and o["section_filters"]):
            self.logger.warning(
                "  --accept-uncovered has no effect here: it applies only to a sectioned "
                "atlas-to-site switch (--mode refresh with sections over an atlas corpus)")
        if mode in ("discover", "all", "refresh"):
            self._discover(manifest, manifest_path, legacy_ids, save=mode == "discover")
        (output_dir / "articles").mkdir(parents=True, exist_ok=True)
        failed: List[str] = []
        attempted = 0
        if mode in ("capture", "all", "refresh"):
            to_capture = self._select_to_capture(manifest, mode)
            self.logger.info(f"Capture: {len(to_capture)} page(s) queued")
            if to_capture:
                failed, attempted = self._capture_pages(to_capture, output_dir, manifest, manifest_path)

        if not self._version_verified and self._start_votes and not self._switching:
            # No capture settled the version (nothing queued or fetched): the start page still must not
            # let a moved site's TOC be saved.
            self._verify_version(self._start_votes, manifest, require=False, weak=True)
        self._save_manifest(manifest_path, manifest)
        self._build_index(output_dir / "index.md", manifest)
        stats = manifest.get("stats", {})
        log_done(self.logger, stats, manifest_path)
        raise_on_capture_errors(
            failed, attempted, "pages", refused=self.refused, orphaned=self.orphaned
        )
        return stats

    def _discover(self, manifest, manifest_path, legacy_ids, save: bool = True) -> None:
        o = self.options
        start = self._fetch_page(self.start_slug)
        if "error" in start:
            raise SnapshotError(f"TOC fetch failed for {self._page_url(self.start_slug)}: {start['error']}")
        # Settle the API version before the manifest is touched or saved, so a
        # refusal leaves the corpus (and an atlas manifest being switched) intact.
        votes: Counter = Counter(set(api_versions(start["body"])))
        self._start_votes = votes
        if save and not self._switching:
            # Discover-only: the start page decides. With a capture to follow, capture
            # settles the version over many pages before any save.
            self._verify_version(votes, manifest, require=False, weak=True)
        toc = parse_toc(start["attrs"])
        discovered, skipped = flatten_toc(toc, self.guide_path, o["section_filters"])
        if skipped:
            self.logger.warning(f"  {skipped} TOC node(s) point outside this guide and were skipped")
        header = re.search(r"<doc-header\b" + _ATTRS + ">", start["html"], re.DOTALL)
        subtitle = dict(_ATTR_RE.findall(header.group(1))).get("subtitle") if header else None
        manifest["guide_title"] = html_lib.unescape(subtitle) if subtitle else None
        self.logger.info(
            f"TOC: {len(discovered)} page(s)"
            + (f" in section(s) {', '.join(o['section_filters'])}" if o["section_filters"] else "")
        )
        if not discovered:
            raise SnapshotError("the TOC walk found no pages")
        if o["section_filters"]:
            # The filtered TOC walk is the section's subtree; stored records keep the
            # top-level label from a full-guide capture, so select by id, not label.
            self._section_ids = {d["page_id"] for d in discovered}
        else:
            self._toc_ids = {d["page_id"] for d in discovered}
        by_id = {p["page_id"]: p for p in manifest.get("pages", [])}
        for d in discovered:
            rec = by_id.setdefault(d["page_id"], {"page_id": d["page_id"], "status": "pending"})
            rec["title"] = rec.get("title") or d["title"]
            rec.setdefault("section", d["section"])
            rec["toc_label"] = d["title"]  # the title field becomes the page's H1 once captured
            if o["section_filters"]:
                if d["parent_page"]:
                    rec.setdefault("parent_page", d["parent_page"])
                _record_section_paths(rec, d)
            else:  # the whole TOC is authoritative: follow a restructure
                rec["parent_page"] = d["parent_page"]
                rec["section"] = d["section"]
                rec["ancestors"] = d["ancestors"]
                rec["alt_ancestors"] = d.get("alt_ancestors") or []
            rec["source_url"] = self._page_url(d["page_id"])
        manifest["pages"] = sorted(by_id.values(), key=lambda p: p["page_id"])
        # The legacy map needs the whole guide's slugs, not just a section's.
        all_slugs = {d["page_id"] for d in flatten_toc(toc, self.guide_path, None)[0]}
        if not legacy_ids and not o["section_filters"]:
            # A rerun (an interrupted switch, a redirect that failed) retries what stayed unmapped.
            legacy_ids = sorted(manifest.get("unmapped_legacy_ids") or {})
        if legacy_ids:
            self._map_legacy(manifest, legacy_ids, all_slugs)
            if self._switching and o["section_filters"]:
                self._check_covered(manifest_path, manifest, legacy_ids)
        if save:  # with a capture to follow, the one save comes after the version check
            self._save_manifest(manifest_path, manifest)

    def _check_covered(self, path: Path, manifest, legacy_ids: List[str]) -> None:
        """Refuse a sectioned atlas-to-site switch that would silently drop captured pages.

        The site pages of the selected sections must replace every atlas article on disk:
        each such id has to map (by rename or redirect) to a slug inside the sections. An id
        that does not stays on atlas only if the operator names it in ``accept_uncovered``.
        Raised before anything is saved, so the atlas manifest is left intact.
        """
        mapping = _legacy_map(manifest)
        section = self._section_ids or set()
        articles = path.parent / "articles"
        uncovered = sorted(
            old for old in legacy_ids
            if (articles / f"{old}.md").is_file() and mapping.get(old) not in section)
        accepted = self.options["accept_uncovered"]
        refused = [old for old in uncovered if old not in accepted]
        if refused:
            shown = ", ".join(refused[:20]) + (f", ... ({len(refused) - 20} more)" if len(refused) > 20 else "")
            raise OptionsError(
                f"switching to the site would leave {len(refused)} captured atlas page(s) with no "
                f"replacement in the selected section(s): {shown}. Their articles would be the only "
                "copy. Name them with --accept-uncovered ID[,ID...] to keep them on atlas, or widen "
                "the sections."
            )
        if uncovered:
            self.logger.warning(
                f"  {len(uncovered)} captured atlas page(s) have no site replacement in the selected "
                "section(s) and stay on atlas (--accept-uncovered)")
        unused = sorted(accepted - set(uncovered))
        if unused:
            self.logger.warning(
                f"  --accept-uncovered named {', '.join(unused)}, not uncovered in this switch (covered, "
                "no atlas article, or an id meant for another target)")

    def _map_legacy(self, manifest, legacy_ids: List[str], slugs: set) -> None:
        """Fill ``legacy_id_map``/``unmapped_legacy_ids`` for atlas ids ``legacy_ids``."""
        mapping = _legacy_map(manifest)
        unmapped: List[str] = []
        by_rename = by_redirect = 0
        for old in legacy_ids:
            guess = guess_slug(old)
            if guess in slugs:
                mapping[old] = guess
                by_rename += 1
                continue
            d = self.options["deliverable"]
            target = self._redirect(f"{SITE_HOST}/docs/atlas.en-us.{d}.meta/{d}/{old}")
            slug = slug_of(urllib.parse.urljoin(SITE_HOST, target), self.guide_path) if target else None
            if slug and slug in slugs:
                mapping[old] = slug
                by_redirect += 1
            else:
                unmapped.append(old)
            self._sleep(self.options["batch_delay_ms"] / 1000.0 / 4)
        manifest["legacy_id_map"] = dict(sorted(mapping.items()))
        manifest["unmapped_legacy_ids"] = {
            old: "no slug by rename or by the atlas redirect" for old in sorted(unmapped)
        }
        self.logger.info(
            f"Legacy ids: {by_rename} by rename, {by_redirect} by redirect, "
            f"{len(unmapped)} unmapped (listed in the manifest)"
        )

    def _select_to_capture(self, manifest, mode: str) -> List[Dict[str, Any]]:
        pages = [p for p in manifest.get("pages", []) if p.get("page_id")]
        filters = self.options.get("section_filters")
        if filters:
            ids = self._section_ids if self._section_ids is not None else self._stored_section_ids(pages, filters)
            pages = [p for p in pages if p["page_id"] in ids]
        return pages if mode == "refresh" else [p for p in pages if p.get("status") != "captured"]

    @staticmethod
    def _stored_section_ids(pages, filters) -> set:
        """Section pages from the manifest's recorded TOC paths (``--mode capture``: no TOC walk).

        A filter names a page id (``_``/``-``, ``.htm`` ignored) or a TOC label; it
        selects every page whose path from the top of the TOC passes through that
        node. A manifest written before paths were recorded needs one discover.
        """
        ids: set = set()
        for f in filters:
            hit, nodes = set(), set()
            for p in pages:
                # the first listing plus every other branch the page is listed under
                for path in _paths_of(p):
                    for i, entry in enumerate(path):
                        label, _, slug_key = entry.partition("\t")
                        if _entry_matches(label, slug_key, f):
                            hit.add(p["page_id"])
                            # the matched node's identity: its page (a page listed twice is one node), else its path
                            nodes.add(slug_key or tuple(path[: i + 1]))
                            break
            if not hit:
                raise OptionsError(
                    f"section {f!r} is not in the manifest; run --mode discover (or all) first"
                )
            if len(nodes) > 1:
                raise OptionsError(
                    f"section {f!r} names {len(nodes)} different TOC nodes; name one by its page id"
                )
            ids |= hit
        return ids

    def _verify_version(self, votes: Counter, manifest, require: bool = True,
                        weak: bool = False) -> None:
        """Refuse unless the site's observed API version is the preset's.

        ``votes`` counts pages (not mentions) per ``/services/data/vNN.0``; when
        they show nothing, the preset's ``probe_page`` is fetched for evidence.
        """
        o = self.options
        votes = Counter(votes)
        seen = observed_version(votes)
        if weak and votes:
            # One page is thin evidence: it may cite older versions ("v62.0 and later").
            # It refuses only when a newer version appears; it passes when the preset's version is present, and is otherwise undecided.
            want = tuple(int(n) for n in o["api_version"].split("."))
            newer = any(tuple(int(n) for n in v.lstrip("v").split(".")) > want for v in votes)
            if not newer:
                seen = o["api_version"] if f"v{o['api_version']}" in votes else None
        if seen is None and o.get("probe_page"):
            probe = self._fetch_page(str(o["probe_page"]))
            if "error" not in probe:
                votes.update(set(api_versions(probe["body"])))
                seen = observed_version(votes)
        if seen is None and not require:
            return  # discover alone may lack evidence; capture settles it before writing
        manifest["observed_api_version"] = seen
        manifest["api_version_votes"] = dict(votes)
        if seen is None:
            raise SnapshotError(
                "cannot confirm the site's API version: none of the fetched pages "
                "(nor the preset's probe_page) shows a /services/data/vNN.0 version. "
                "Nothing was written. Set probe_page to a REST or Connect page of the guide."
            )
        if seen != o["api_version"]:
            raise SnapshotError(
                f"the site now serves API {seen} ({dict(votes)}), but this preset is "
                f"for API {o['api_version']}. Nothing was written: the site has moved "
                "to a newer release and no per-release copy is served. Compare the "
                "pages against the PDF archive, or update the preset on purpose."
            )
        self._version_verified = True
        self.logger.info(f"  API version check: site serves {seen} (matches the preset)")

    def _capture_pages(self, pages, output_dir: Path, manifest, manifest_path) -> Tuple[List[str], int]:
        o = self.options
        articles_dir = output_dir / "articles"
        fetched: Dict[str, Dict[str, Any]] = {}
        errors: Dict[str, str] = {}
        votes: Counter = Counter()
        queue = [p["page_id"] for p in pages][: o["max_pages"]]
        capped = len(pages) - len(queue)
        if capped:
            self.logger.warning(f"  max_pages={o['max_pages']}: {capped} page(s) left pending")

        for start in range(0, len(queue), o["concurrency"]):
            batch = queue[start:start + o["concurrency"]]
            with ThreadPoolExecutor(max_workers=len(batch)) as pool:
                results = list(pool.map(self._fetch_page, batch))
            for res in results:
                if "error" in res:
                    errors[res["id"]] = res["error"]
                    continue
                votes.update(set(api_versions(res["body"])))  # one vote per page
                fetched[res["id"]] = res
            if start + o["concurrency"] < len(queue):
                self._sleep(o["batch_delay_ms"] / 1000.0)
        # With nothing fetched, the start page's votes (if any) are the evidence.
        if votes or self._switching:
            self._verify_version(votes, manifest)  # a switch needs captured evidence
        else:
            self._verify_version(self._start_votes, manifest, require=bool(fetched), weak=True)

        extra = Counter(t for r in fetched.values() for t in unhandled_tags(r["body"]))
        if extra:
            self.logger.warning(f"  custom elements left unconverted: {dict(extra)}")

        by_id = {p["page_id"]: p for p in manifest.get("pages", [])}
        legacy_by_slug: Dict[str, List[str]] = {}
        for old, slug in sorted(_legacy_map(manifest).items()):
            legacy_by_slug.setdefault(slug, []).append(old)
        accept = o["accept_shrinkage"]
        def prior_for(pid: str) -> Optional[str]:
            """What a capture would replace: the page's site article, else (a corpus switched from the
            atlas) the longest atlas article mapped to it, so the shrinkage guard sees the real prior."""
            text = read_prior(articles_dir / f"{pid}.md")
            if text is None:
                texts = [t for old in legacy_by_slug.get(pid, ())
                         if (t := read_prior(articles_dir / f"{old}.md")) is not None]
                text = max(texts, key=len) if texts else None
            return text

        prior_texts = {pid: prior_for(pid) for pid in fetched}
        has_site_file = {pid: (articles_dir / f"{pid}.md").is_file() for pid in fetched}
        self.accepted = []
        refusals: Dict[str, str] = {}

        def convert(pid: str, known: set) -> Tuple[str, str]:
            body = rewrite_links(normalize_body(fetched[pid]["body"]), self.guide_path, known)
            title = page_title(body, by_id.get(pid, {}).get("title") or pid)
            return title, html_to_markdown(body)

        # Links to pages captured by an earlier run stay local.
        earlier = {pid for pid, rec in by_id.items()
                   if rec.get("status") == "captured" and (articles_dir / f"{pid}.md").is_file()}
        all_ids = set(fetched) | earlier
        no_article: set = set()  # converted to nothing: no file is written for these
        for pid in fetched:
            title, body_md = convert(pid, all_ids)
            if not body_md:
                no_article.add(pid)
            if body_md and (reason := refusal_reason(
                title, body_md, prior_texts[pid], pid, accept,
                lambda why, p=pid: (self.accepted.append(p), self.logger.warning(f"  [accepted] {p}: {why}")),
            )):
                refusals[pid] = reason
        # A link stays local only when the target has (or keeps) an article file: a refused
        # or empty page with no earlier file would leave a dead ./slug.md.
        known = all_ids - {p for p in (set(refusals) | no_article) if not has_site_file[p]}

        written = 0
        empty: List[str] = []
        self.refused = []
        fetched_at = today()
        for pid in fetched:
            title, body_md = convert(pid, known)
            rec = by_id.setdefault(pid, {"page_id": pid})
            rec["source_url"] = self._page_url(pid)
            if not body_md:
                rec.update(status="error", error="empty body")
                empty.append(pid)
            elif pid in refusals:
                rec.update(status="error", error=f"refused: {refusals[pid]}")
                self.refused.append((pid, refusals[pid]))
                self.logger.warning(f"  [refused] {pid}: {refusals[pid]}")
            else:
                legacy = (legacy_by_slug.get(pid) or [None])[0]
                (articles_dir / f"{pid}.md").write_text(render_page_markdown(
                    slug=pid, title=title, body_md=body_md, source_url=self._page_url(pid),
                    release_version=o["release_version"], release_name=o["release_name"],
                    deliverable=o["deliverable"], section=rec.get("section"),
                    parent_page=rec.get("parent_page"), legacy_page_id=legacy,
                    api_version=manifest.get("observed_api_version") or o["api_version"],
                    fetched_at=fetched_at,
                ), encoding="utf-8")
                rec.update(title=title, status="captured", body_length=len(body_md),
                           file=f"articles/{pid}.md")
                if legacy:
                    rec["legacy_page_id"] = legacy
                rec.pop("error", None)
                written += 1
        for pid, err in errors.items():
            rec = by_id.setdefault(pid, {"page_id": pid})
            rec.update(status="error", error=err)
        manifest["pages"] = sorted(by_id.values(), key=lambda p: p["page_id"])
        self._save_manifest(manifest_path, manifest)
        self.logger.info(f"  wrote {written} page(s); {len(errors) + len(empty) + len(self.refused)} error(s)")
        report_refusals(self.logger, self.refused)
        self.orphaned = sorted(
            pid for pid in list(errors) + empty
            if self._toc_ids is not None and pid not in self._toc_ids
        )
        report_orphans(self.logger, self.orphaned, "page")
        return list(errors) + empty + [p for p, _ in self.refused], len(fetched) + len(errors)

    # -- index ------------------------------------------------------------

    def _build_index(self, index_path: Path, manifest: Dict[str, Any]) -> None:
        pages = manifest.get("pages", [])
        captured = [p for p in pages if p.get("status") == "captured"]
        errored = [p for p in pages if p.get("status") == "error"]
        lines = [
            f"# {manifest.get('guide_title') or self.options['deliverable']} — Snapshot",
            "",
            f"**Source:** {manifest.get('site_url')}  ",
            f"**Release:** {manifest.get('release_name')} ({manifest.get('release')}, "
            f"API {manifest.get('api_version')}, observed {manifest.get('observed_api_version')})  ",
            f"**Last updated:** {manifest.get('last_updated', 'n/a')}",
            "",
            "## Stats",
            "",
            *stats_table(manifest.get("stats", {})),
        ]
        unmapped = manifest.get("unmapped_legacy_ids") or {}
        mapped = _legacy_map(manifest)
        if mapped or unmapped:
            lines += [
                "## Legacy atlas ids", "",
                f"{len(mapped)} mapped to a site slug (`legacy_id_map` in the manifest), "
                f"{len(unmapped)} unmapped.", "",
            ]
        by_section: Dict[str, List[Dict[str, Any]]] = {}
        for p in captured:
            by_section.setdefault(p.get("section") or "(uncategorized)", []).append(p)
        for section in sorted(by_section):
            items = by_section[section]
            lines.extend(captured_table(f"## {section} ({len(items)})", items, "page_id", "Page", "Chars"))
        if errored:
            lines += [f"## Errored ({len(errored)})", ""]
            lines += [f"- `{p['page_id']}` — {p.get('error', 'unknown')}"
                      for p in sorted(errored, key=lambda x: x["page_id"])]
            lines.append("")
        lines.extend(index_footer("dev-guide", manifest))
        index_path.write_text("\n".join(lines), encoding="utf-8")
