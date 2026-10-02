"""Capture Salesforce Help articles as markdown for AI grounding.

Walks the Help portal sidebar from a root article URL, discovers all child
article IDs filtered by prefix, then captures each article body as a markdown
file with YAML frontmatter at `{output_dir}/articles/{article_id}.md`.

Also generates `manifest.json` (machine-readable index) and `index.md`
(human-readable area overview).

WHY THIS EXISTS

The Salesforce Help portal is an LWC SPA with shadow DOM. Plain `WebFetch`
or `curl` returns an unrendered shell. AI agents (and grep, glob, Read) work
much better against per-article markdown than against a 124 MB PDF compendium.
This module produces the markdown snapshot per release-area so the agents have
fast, surgical grounding material.

USAGE

Run through the CLI; named areas live in `presets.yaml`:

    python -m scripts.doc_snapshot help --release 264 --area billing
    python -m scripts.doc_snapshot help --release 264 --area billing --mode discover

MODES

    discover   Walk sidebar, emit manifest.json with discovered IDs as 'pending'.
               No body capture.
    capture    Read existing manifest, capture each 'pending' article.
    all        Discover then capture. Skips articles already captured. (default)
    refresh    Re-capture every article, overwriting existing files.

The browser runs headless by default; pass `--headless false` to watch it.
See scripts/doc_snapshot/README.md for install steps.
"""

import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from scripts.doc_snapshot._core import (
    OptionsError,
    SnapshotError,
    as_bool,
    as_int,
    compute_stats,
    get_logger,
    normalize_mode,
    raise_on_capture_errors,
    require_options,
    require_playwright,
    resolve_output_dir,
    run_browser,
)

CAPTURE_METHOD = "scripts/doc_snapshot help (Playwright + shadow-DOM walker)"


# ---------------------------------------------------------------------------
# JavaScript snippets executed inside the page (via page.evaluate).
# Both use a recursive shadow-DOM walker because Help articles render the
# article body and sidebar inside multiple shadow roots.
# ---------------------------------------------------------------------------

SIDEBAR_WALKER_JS = """
() => {
    function walk(root, pred, out=[]) {
        if (!root) return out;
        const all = root.querySelectorAll ? root.querySelectorAll('*') : [];
        all.forEach(el => {
            if (pred(el)) out.push(el);
            if (el.shadowRoot) walk(el.shadowRoot, pred, out);
        });
        return out;
    }

    // Best-effort parent extraction from the sidebar tree structure.
    // The Help portal sidebar typically uses <li><a>parent</a><ul><li><a>child</a>...
    // nesting, so for each link we walk up to its enclosing <li>, then
    // up the parent chain looking for the next ancestor <li>. The first
    // articleView <a> in that ancestor LI's label area is the parent
    // article. Returns null when no enclosing LI / parent link can be
    // identified (flat sidebar, cross-shadow nesting, or top-level
    // articles) — preserves any pre-existing parent_article values via
    // _merge_discovered (Python side), so partial extraction never
    // regresses manually-curated parents. Because null is ambiguous,
    // isTopLevel separately reports a positive tree-root signal: the
    // link's own LI carries aria-level="1".
    function isTopLevel(link) {
        const selfLi = link.closest && link.closest('li');
        return !!(selfLi && selfLi.getAttribute('aria-level') === '1');
    }

    function findParentArticleId(link) {
        if (!link.closest) return null;
        const selfLi = link.closest('li');
        if (!selfLi) return null;
        let p = selfLi.parentElement;
        while (p) {
            if (p.tagName === 'LI') {
                const candidate =
                    p.querySelector && p.querySelector('a[href*="articleView"]');
                if (candidate && candidate !== link) {
                    const m = candidate.href.match(/id=([^&]+)/);
                    if (m) return m[1];
                }
            }
            p = p.parentElement;
        }
        return null;
    }

    const links = walk(document, el =>
        el.tagName === 'A' &&
        el.href &&
        el.href.includes('articleView') &&
        el.innerText.trim() &&
        el.innerText.trim() !== 'Back'
    );
    const seen = new Set();
    const result = [];
    links.forEach(a => {
        const m = a.href.match(/id=([^&]+)/);
        if (!m) return;
        const id = m[1];
        if (seen.has(id)) return;
        seen.add(id);
        result.push({
            id: id,
            title: a.innerText.trim().slice(0, 200),
            parent_id: findParentArticleId(a) || null,
            top_level: isTopLevel(a),
        });
    });
    return result;
}
"""

ARTICLE_BODY_JS = """
() => {
    function walk(root, pred, out=[]) {
        if (!root) return out;
        const all = root.querySelectorAll ? root.querySelectorAll('*') : [];
        all.forEach(el => {
            if (pred(el)) out.push(el);
            if (el.shadowRoot) walk(el.shadowRoot, pred, out);
        });
        return out;
    }
    const h1s = walk(document, el => el.tagName === 'H1');
    if (h1s.length === 0) return { title: null, body: null, breadcrumb: null };
    const h1 = h1s[0];
    const title = h1.innerText.trim();
    const container = h1.closest('article') || h1.parentElement;
    let body = container ? container.innerText : '';

    // Strip the Help-portal breadcrumb prefix:
    //   "You are here:\\n\\nSALESFORCE HELP\\nDOCS\\nAGENTFORCE REVENUE MANAGEMENT\\n<title>\\n\\n<body>"
    // We find the first occurrence of the title (which appears at the end of
    // the breadcrumb path) and keep everything after it. If the breadcrumb
    // signature isn't present, leave the body untouched.
    if (body.indexOf('You are here') !== -1) {
        const idx = body.indexOf(title);
        if (idx >= 0) {
            body = body.substring(idx + title.length).trim();
        }
    }

    // Try to capture a structured breadcrumb separately for downstream use.
    const breadcrumbEl = walk(document, el =>
        (el.tagName === 'NAV' || (el.className && String(el.className).toLowerCase().includes('breadcrumb')))
        && el.innerText && el.innerText.length < 500
    )[0];

    return {
        title: title,
        body: body,
        breadcrumb: breadcrumbEl ? breadcrumbEl.innerText.trim() : null,
    };
}
"""


# The Help portal serves this exact H1 for a broken/retired article ID
# instead of a 404 status — it renders fine (has an H1, extracts a "body")
# so the generic "no H1 found" guard below never sees it. Caught live on
# ind.dro_create_custom_context_definition_and_map_attribute_to_field.htm
# (PR #409 review).
NOT_FOUND_TITLE_PREFIX = "We looked high and low"


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

FORBIDDEN_FRONTMATTER_CHARS = re.compile(r"[\r\n]+")


def _yaml_escape(value: str) -> str:
    """Escape a string for safe inclusion in YAML frontmatter."""
    if value is None:
        return ""
    value = FORBIDDEN_FRONTMATTER_CHARS.sub(" ", value)
    if '"' in value or ":" in value or value.startswith(("-", "*", "&", "?", "|", ">", "%", "@", "`")):
        value = '"' + value.replace('"', '\\"') + '"'
    return value


def render_article_markdown(
    article_id: str,
    title: str,
    body: str,
    source_url: str,
    release_version: str,
    release_name: str,
    area: str,
    parent_article_id: Optional[str],
    fetched_at: str,
) -> str:
    """Render an article body as markdown with YAML frontmatter.

    The body is preserved verbatim — innerText already gives us paragraph
    breaks where the rendered HTML had them. Downstream formatting passes
    (bullet detection, table reconstruction) are out of scope for the
    snapshot — we want the captured text to be as close to source as
    possible so future passes can format from a known good baseline.
    """
    fm_lines = [
        "---",
        f"article_id: {article_id}",
        f"title: {_yaml_escape(title)}",
        f"source_url: {source_url}",
        f"release: {_yaml_escape(release_version)}",
        f"release_name: {_yaml_escape(release_name)}",
        f"area: {_yaml_escape(area)}",
    ]
    if parent_article_id:
        fm_lines.append(f"parent_article: {parent_article_id}")
    fm_lines.append(f"fetched_at: {_yaml_escape(fetched_at)}")
    fm_lines.append("---")

    parts = ["\n".join(fm_lines), "", f"# {title}", "", body.strip(), ""]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Snapshotter
# ---------------------------------------------------------------------------


class HelpSnapshot:
    """Capture Salesforce Help articles as markdown for AI grounding.

    See module docstring for usage. No org connection is needed: it's a
    pure web scrape against the public Help portal.

    Options (all keys snake_case; the CLI maps --kebab-case flags onto them):

        release_version       required; URL release param and path component, e.g. '264'
        release_name          required; e.g. "Winter '27"
        area                  required; functional area tag, e.g. 'billing'
        root_article_id       required; area root whose sidebar seeds discovery
        article_id_prefix     required; only capture IDs with this prefix
        output_dir            default docs/salesforce/{release_version}/help (repo-relative)
        mode                  discover | capture | all | refresh (default all)
        headless              default true
        concurrency           articles captured in parallel (default 4)
        wait_ms               ms between sidebar reads, and the per-article settle (default 3000)
        discover_timeout_ms   max ms to poll the sidebar for a stable count (default 20000)
        expect_min_articles   fail discovery below this many prefix matches
        include_release_param append &release= to article URLs (default true)
        subtree_only          keep only root_article_id's sidebar descendants (default false);
                              a validated walk also prunes this area's records whose complete
                              parent chain places them in another sidebar branch
    """

    BASE_URL = "https://help.salesforce.com/s/articleView"

    def __init__(self, options: Dict[str, Any], logger=None):
        self.options = dict(options)
        self.logger = logger or get_logger()
        self._init_options()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _init_options(self) -> None:
        require_options(
            self.options,
            "release_version", "release_name", "area",
            "root_article_id", "article_id_prefix",
        )
        self.options["release_version"] = str(self.options["release_version"])
        if not self.options.get("output_dir"):
            self.options["output_dir"] = (
                f"docs/salesforce/{self.options['release_version']}/help"
            )
        self.options["mode"] = normalize_mode(self.options.get("mode"))
        self.options["headless"] = as_bool(self.options.get("headless"), True)
        self.options["concurrency"] = as_int(self.options.get("concurrency"), 4)
        self.options["wait_ms"] = as_int(self.options.get("wait_ms"), 3000)
        self.options["discover_timeout_ms"] = as_int(
            self.options.get("discover_timeout_ms"), 20000
        )
        self._validate_timing_options()
        self.options["expect_min_articles"] = (
            as_int(self.options.get("expect_min_articles"), None) or None
        )
        self.options["include_release_param"] = as_bool(
            self.options.get("include_release_param"), True
        )
        self.options["subtree_only"] = as_bool(self.options.get("subtree_only"), False)

    def run(self) -> Dict[str, Any]:
        """Run the snapshot; returns the manifest's overall stats."""
        require_playwright(self.logger)

        output_dir = resolve_output_dir(self.options["output_dir"])
        articles_dir = output_dir / "articles"
        manifest_path = output_dir / "manifest.json"
        index_path = output_dir / "index.md"

        articles_dir.mkdir(parents=True, exist_ok=True)

        return run_browser(
            self._async_run(
                output_dir=output_dir,
                articles_dir=articles_dir,
                manifest_path=manifest_path,
                index_path=index_path,
            )
        )

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    def _article_url(self, article_id: str) -> str:
        url = f"{self.BASE_URL}?id={article_id}&type=5"
        if self.options["include_release_param"]:
            url += f"&release={self.options['release_version']}"
        return url

    # ------------------------------------------------------------------
    # Manifest I/O
    # ------------------------------------------------------------------

    def _load_or_init_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        # The required top-level keys this module writes and the index builder reads.
        # Older or hand-written manifests may be missing some of these — backfill
        # from the current options so we don't crash later.
        #
        # The top-level `area` / `root_article_id` / `article_id_prefix` fields
        # reflect the MOST RECENT run that wrote to this manifest. When the same
        # manifest is shared across multiple area snapshots (e.g., all RC
        # functional areas under docs/salesforce/{release}/help/manifest.json),
        # those top-level fields aren't authoritative — the `areas` array is.
        # Per-article `area` tags are the source of truth for which run captured
        # each article.
        required_defaults = {
            "release": self.options["release_version"],
            "release_name": self.options["release_name"],
            "area": self.options["area"],
            "source_root_url": self._article_url(self.options["root_article_id"]),
            "root_article_id": self.options["root_article_id"],
            "article_id_prefix": self.options["article_id_prefix"],
            "snapshot_started": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "capture_method": CAPTURE_METHOD,
            "areas": [],   # accumulated per-area run metadata (this run + prior runs)
            "articles": [],
        }

        if manifest_path.exists():
            try:
                with manifest_path.open() as f:
                    existing = json.load(f)
                self.logger.info(
                    f"Loaded existing manifest with {len(existing.get('articles', []))} articles"
                )
                # Backfill any missing required keys without clobbering existing values
                for key, default in required_defaults.items():
                    existing.setdefault(key, default)
                # Refresh the top-level pointers to reflect THIS run. The `areas`
                # array preserves prior-run metadata; these top-level fields are
                # just convenience pointers to the most recent run.
                existing["area"] = self.options["area"]
                existing["root_article_id"] = self.options["root_article_id"]
                existing["article_id_prefix"] = self.options["article_id_prefix"]
                existing["source_root_url"] = self._article_url(self.options["root_article_id"])
                # Label the manifest with the tool that last wrote it.
                existing["capture_method"] = CAPTURE_METHOD
                return existing
            except (json.JSONDecodeError, OSError) as e:
                self.logger.warning(f"Could not load existing manifest: {e}. Starting fresh.")
        return required_defaults

    def _save_manifest(self, manifest_path: Path, manifest: Dict[str, Any]) -> None:
        manifest["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        manifest["stats"] = self._compute_stats(manifest)
        self._update_area_entry(manifest)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with manifest_path.open("w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    def _update_area_entry(self, manifest: Dict[str, Any]) -> None:
        """Sync this run's per-area metadata into the manifest['areas'] array."""
        current_area = self.options["area"]
        articles = manifest.get("articles", [])
        # Per-area stats: only count articles tagged with this area
        area_articles = [a for a in articles if a.get("area") == current_area]
        area_captured = [a for a in area_articles if a.get("status") == "captured"]
        area_entry = {
            "area": current_area,
            "root_article_id": self.options["root_article_id"],
            "article_id_prefix": self.options["article_id_prefix"],
            "source_root_url": self._article_url(self.options["root_article_id"]),
            "last_updated": manifest["last_updated"],
            "stats": {
                "discovered": len(area_articles),
                "captured": len(area_captured),
                "pending": len([a for a in area_articles if a.get("status") == "pending"]),
                "errored": len([a for a in area_articles if a.get("status") == "error"]),
                "total_captured_body_chars": sum(a.get("body_length", 0) for a in area_captured),
            },
        }
        # Only set on runs that actually performed discovery this call;
        # capture-only runs fall through to the "preserve existing" branch
        # below so the field survives across a discover-then-capture pair.
        last_kept = getattr(self, "_last_discover_kept", None)
        if last_kept is not None:
            area_entry["last_run_discovered"] = {
                "kept": last_kept,
                "before_prefix_filter": getattr(self, "_last_discover_total", None),
            }
        # Replace existing entry for this area, or append a new one
        areas = manifest.setdefault("areas", [])
        replaced = False
        for i, existing in enumerate(areas):
            if existing.get("area") == current_area:
                # Preserve the original snapshot_started if it's there
                if "snapshot_started" in existing:
                    area_entry["snapshot_started"] = existing["snapshot_started"]
                else:
                    area_entry["snapshot_started"] = manifest.get("snapshot_started")
                if "last_run_discovered" not in area_entry and "last_run_discovered" in existing:
                    area_entry["last_run_discovered"] = existing["last_run_discovered"]
                areas[i] = area_entry
                replaced = True
                break
        if not replaced:
            area_entry["snapshot_started"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            areas.append(area_entry)

    @staticmethod
    def _compute_stats(manifest: Dict[str, Any]) -> Dict[str, Any]:
        return compute_stats(manifest, "articles")

    def _prune_moved_out(
        self, manifest: Dict[str, Any], moved_out: Set[str]
    ) -> List[str]:
        """Drop this area's records that `_classify_subtree` placed outside the root.

        With subtree_only, an article that left the root's subtree (pre-GA
        release notes move between sections) must leave this area's snapshot
        too, or mode=refresh selects the stale record and recaptures it.
        `moved_out` holds only IDs placed conclusively outside the subtree: a
        record merely absent from the walk, or one whose ancestry is
        incomplete, is kept, because a partial walk can stabilize above
        expect_min_articles. Other areas' records sharing the manifest are
        untouched. Returns the pruned IDs; `_save_then_delete` removes the
        files only after the pruned manifest is saved.
        """
        if not self.options.get("subtree_only") or not moved_out:
            return []
        current_area = self.options["area"]
        kept_records, pruned = [], []
        for record in manifest.get("articles", []):
            article_id = record.get("article_id")
            if article_id in moved_out and (
                not record.get("area") or record.get("area") == current_area
            ):
                pruned.append(article_id)
                self.logger.info(f"Pruned {article_id}: no longer under the root subtree")
            else:
                kept_records.append(record)
        manifest["articles"] = kept_records
        return pruned

    def _save_then_delete(
        self,
        manifest_path: Path,
        manifest: Dict[str, Any],
        articles_dir: Path,
        moved_out: Set[str],
    ) -> None:
        """Save the pruned manifest, then delete moved-out article files.

        In this order an interrupted run leaves an orphan file, never a
        captured record whose file is gone. The delete covers every
        moved-out ID with no manifest record left, not only the IDs pruned
        this run, so the next validated walk removes a file an earlier run
        orphaned after its save. A moved-out ID that another area still
        records keeps its file.
        """
        self._save_manifest(manifest_path, manifest)
        recorded = {a.get("article_id") for a in manifest.get("articles", [])}
        for article_id in sorted(moved_out - recorded):
            (articles_dir / f"{article_id}.md").unlink(missing_ok=True)

    def _merge_discovered(
        self,
        manifest: Dict[str, Any],
        discovered: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        existing_by_id: Dict[str, Dict[str, Any]] = {
            a["article_id"]: a for a in manifest.get("articles", [])
        }
        current_area = self.options["area"]
        for d in discovered:
            article_id = d["id"]
            title = d.get("title", "")
            parent_id = d.get("parent_id")
            if article_id in existing_by_id:
                # Update title if the existing one is empty
                if not existing_by_id[article_id].get("title"):
                    existing_by_id[article_id]["title"] = title
                # Backfill area if missing (handles articles from older manifest
                # versions that pre-date per-article area tagging)
                if not existing_by_id[article_id].get("area"):
                    existing_by_id[article_id]["area"] = current_area
                # Backfill parent_article if the discovery walker found one
                # and the existing record doesn't already have it. Never
                # overwrite — preserves manually-set or previously-extracted
                # values across re-runs.
                if parent_id and not existing_by_id[article_id].get("parent_article"):
                    existing_by_id[article_id]["parent_article"] = parent_id
            else:
                record = {
                    "article_id": article_id,
                    "title": title,
                    "status": "pending",
                    "area": current_area,
                }
                if parent_id:
                    record["parent_article"] = parent_id
                existing_by_id[article_id] = record
        manifest["articles"] = sorted(
            existing_by_id.values(), key=lambda a: a["article_id"]
        )
        return manifest

    def _select_articles_to_capture(
        self,
        manifest: Dict[str, Any],
        mode: str,
    ) -> List[Dict[str, Any]]:
        articles = manifest.get("articles", [])

        # Per-area scoping: the shared manifest accumulates articles across
        # every area that has ever been run against this release directory.
        # An area-specific run (e.g. the 262 pricing preset) must only
        # operate on its own area — otherwise mode=refresh would silently
        # re-capture other areas' articles (and re-tag them with the wrong
        # `area` value via render_article_markdown). Articles with no `area`
        # field still pass through so legacy single-area manifests captured
        # before per-article area tagging continue to work.
        current_area = self.options.get("area")
        if current_area:
            articles = [
                a for a in articles
                if not a.get("area") or a.get("area") == current_area
            ]

        if mode == "refresh":
            return [a for a in articles if a.get("article_id")]
        return [a for a in articles if a.get("status") != "captured"]

    # ------------------------------------------------------------------
    # Pipeline phases (async)
    # ------------------------------------------------------------------

    async def _async_run(
        self,
        output_dir: Path,
        articles_dir: Path,
        manifest_path: Path,
        index_path: Path,
    ) -> None:
        from playwright.async_api import async_playwright

        mode = self.options["mode"]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.options["headless"])

            manifest = self._load_or_init_manifest(manifest_path)

            # Phase 1: Discovery
            if mode in ("discover", "all", "refresh"):
                self.logger.info(
                    f"Discovery: walking sidebar from {self.options['root_article_id']}"
                )
                context = await browser.new_context()
                page = await context.new_page()
                discovered, stabilized = await self._discover_articles(page)
                await context.close()

                kept = self._filter_discovered(discovered)
                total_before_filter = len(discovered)
                self.logger.info(
                    f"Discovered {len(kept)} unique articles "
                    f"({total_before_filter} total before prefix filter)"
                )
                # Persist this attempt's counters before validating — a raise
                # below must still leave `last_run_discovered` reflecting the
                # failed walk, not a stale success from a prior run.
                self._last_discover_kept = len(kept)
                self._last_discover_total = total_before_filter
                self._save_manifest(manifest_path, manifest)
                self._validate_discovery(
                    len(kept), total_before_filter, stabilized,
                    only_root=[d["id"] for d in kept] == [self.options["root_article_id"]],
                )
                moved_out = {
                    article_id
                    for article_id, where in self._classify_subtree(discovered).items()
                    if where == "out"
                } if self.options.get("subtree_only") else set()
                self._prune_moved_out(manifest, moved_out)
                manifest = self._merge_discovered(manifest, kept)
                self._save_then_delete(manifest_path, manifest, articles_dir, moved_out)

            # Phase 2: Capture
            to_capture: List[Dict[str, Any]] = []
            failed: List[str] = []
            if mode in ("capture", "all", "refresh"):
                to_capture = self._select_articles_to_capture(manifest, mode)
                self.logger.info(f"Capture: {len(to_capture)} articles queued")

                if to_capture:
                    failed = await self._capture_articles(
                        browser=browser,
                        articles=to_capture,
                        articles_dir=articles_dir,
                        manifest=manifest,
                        manifest_path=manifest_path,
                    )

            await browser.close()

        # Phase 3: Refresh index.md and final manifest
        self._save_manifest(manifest_path, manifest)
        self._build_index(index_path, manifest)
        stats = manifest.get("stats", {})
        self.logger.info(
            f"Done. "
            f"discovered={stats.get('discovered', 0)} "
            f"captured={stats.get('captured', 0)} "
            f"pending={stats.get('pending', 0)} "
            f"errored={stats.get('errored', 0)}"
        )
        self.logger.info(f"Manifest: {manifest_path}")
        self.logger.info(f"Index:    {index_path}")
        raise_on_capture_errors(failed, len(to_capture), "articles")
        # The manifest's stats sum every area; a caller's summary wants this one.
        for entry in manifest.get("areas", []):
            if entry.get("area") == self.options["area"]:
                return entry.get("stats", stats)
        return stats

    def _validate_timing_options(self) -> None:
        """Reject non-positive wait_ms/discover_timeout_ms before the discovery loop runs.

        `_discover_articles` accumulates elapsed time as `elapsed_ms += wait_ms` each
        read, so `wait_ms <= 0` never advances it — an empty or never-stabilizing walk
        would then poll forever instead of reaching `discover_timeout_ms` and failing
        loudly via `_validate_discovery`. Pure option check, no browser state needed.
        """
        if self.options["wait_ms"] <= 0:
            raise OptionsError(
                f"wait_ms must be positive, got {self.options['wait_ms']!r} — "
                "the discovery loop's elapsed-time counter is wait_ms * reads, "
                "so a non-positive value never reaches discover_timeout_ms."
            )
        if self.options["discover_timeout_ms"] <= 0:
            raise OptionsError(
                f"discover_timeout_ms must be positive, got "
                f"{self.options['discover_timeout_ms']!r}"
            )

    def _validate_discovery(
        self,
        kept_count: int,
        total_before_filter: int,
        stabilized: bool,
        only_root: bool = False,
    ) -> None:
        """Fail loud on a thin or unstable walk instead of silently writing a partial manifest.

        A 1-of-83 walk previously merged fine (add-only merge) and exited 0 —
        the bug this guards against. No browser state needed, so this is a
        pure function of the counts/options plus `_discover_articles`'s
        `stabilized` flag; kept separate from `_discover_articles` so it's
        unit-testable without Playwright.
        """
        if not kept_count:
            raise SnapshotError(
                f"Discovery found 0 articles matching prefix "
                f"{self.options['article_id_prefix']!r} under root "
                f"{self.options['root_article_id']!r} "
                f"({total_before_filter} links seen before prefix filter). "
                "The sidebar likely didn't finish rendering before "
                "discover_timeout_ms — rerun, or raise "
                "--discover-timeout-ms / --wait-ms."
            )
        if only_root:
            # A nonexistent id still renders the portal shell, and the root
            # matches its own prefix, so a wrong root "discovers" one article.
            raise SnapshotError(
                f"Discovery found only the root article "
                f"{self.options['root_article_id']!r} itself, with no child "
                f"articles matching prefix {self.options['article_id_prefix']!r} "
                f"({total_before_filter} links seen before prefix filter). "
                "Check that the root id exists and is a section landing page."
            )
        expect_min = self.options["expect_min_articles"]
        if expect_min and kept_count < expect_min:
            raise SnapshotError(
                f"Discovery found only {kept_count} articles matching prefix "
                f"{self.options['article_id_prefix']!r}, below "
                f"expect_min_articles={expect_min} "
                f"({total_before_filter} links seen before prefix filter). "
                "The sidebar may not have fully rendered — rerun, or raise "
                "--discover-timeout-ms."
            )
        if not stabilized:
            raise SnapshotError(
                f"Discovery hit discover_timeout_ms with the matching-article "
                f"count (or, with subtree_only, the whole walk) still changing "
                f"between reads (last read: {kept_count} matching, "
                f"{total_before_filter} total before prefix filter) — the walk "
                "never went two consecutive reads without changing, so "
                "this count is not reliably the full tree even though it clears "
                "any configured expect_min_articles floor. Rerun, or raise "
                "--discover-timeout-ms."
            )

    def _filter_discovered(
        self, discovered: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Apply the prefix filter and, with `subtree_only`, the root-subtree filter."""
        prefix = self.options["article_id_prefix"]
        kept = [d for d in discovered if d["id"].startswith(prefix)]
        if not self.options.get("subtree_only"):
            return kept
        membership = self._classify_subtree(discovered)
        return [d for d in kept if membership[d["id"]] == "in"]

    def _classify_subtree(self, discovered: List[Dict[str, str]]) -> Dict[str, str]:
        """Classify each walked ID as "in", "out" or "unknown" relative to root_article_id.

        "in": the parent chain reaches the root. "out": the chain, with every
        link present in the walk, reaches an ancestor of the root or ends at
        a different sidebar tree root (`top_level`, from aria-level="1"), so
        the article sits in another branch. Anything else (a parent missing
        from the walk, a null parent on a non-top-level item, a cycle) is
        "unknown": parent extraction is best-effort, and pruning treats only
        "out" as moved. On the live 264 release notes the Revenue root has no
        parent, and the other 1,470 IDs chain to the top-level
        release-notes.salesforce_release_notes.htm.
        """
        root = self.options["root_article_id"]
        parent_of = {d["id"]: d.get("parent_id") for d in discovered}
        top_level = {d["id"] for d in discovered if d.get("top_level")}
        root_ancestors = set()
        node, seen = parent_of.get(root), {root}
        while node and node not in seen:
            root_ancestors.add(node)
            seen.add(node)
            node = parent_of.get(node)

        def classify(article_id: str) -> str:
            seen = set()
            while article_id and article_id not in seen:
                if article_id == root:
                    return "in"
                if article_id in root_ancestors:
                    return "out"
                if article_id not in parent_of:
                    return "unknown"
                seen.add(article_id)
                if parent_of[article_id] is None:
                    return "out" if article_id in top_level else "unknown"
                article_id = parent_of[article_id]
            return "unknown"

        return {d["id"]: classify(d["id"]) for d in discovered}

    async def _discover_articles(self, page) -> Tuple[List[Dict[str, str]], bool]:
        """Walk the sidebar, polling until the matching-article count stabilizes.

        The Help portal SPA hydrates the sidebar tree at variable speed —
        live probing showed the same page taking anywhere from ~3s to >6s,
        with 3 of 4 single-read trials at a fixed 3s wait succeeding and one
        catching the tree mid-hydration (1 article instead of ~80). A single
        fixed wait is therefore a race; poll every wait_ms up to
        discover_timeout_ms and stop once the prefix-matching count holds
        steady across two consecutive reads (with subtree_only, the whole
        walk's id, parent and top_level signature must also repeat, because
        the prune reads the whole walk) — unless that count sits below
        expect_min_articles (when set), in which case keep polling: the same
        SPA can plateau at a partial count for a read or two before the rest
        of the tree hydrates, and stopping there would fail a walk that just
        needed more time within its own budget.

        Returns `(discovered, stabilized)` — `stabilized` is False when the
        loop only ended because `discover_timeout_ms` was reached without ever
        seeing two equal consecutive reads, so the caller can distinguish "the
        full tree" from "whatever the last, possibly-still-growing, read saw."
        """
        url = self._article_url(self.options["root_article_id"])
        self.logger.info(f"  GET {url}")
        await page.goto(url, wait_until="domcontentloaded")

        wait_ms = self.options["wait_ms"]
        timeout_ms = self.options["discover_timeout_ms"]
        expect_min = self.options["expect_min_articles"]

        discovered: List[Dict[str, str]] = []
        prev_kept = -1
        prev_walk = None
        elapsed_ms = 0
        stabilized = False
        while True:
            sleep_ms = min(wait_ms, timeout_ms - elapsed_ms)
            await page.wait_for_timeout(sleep_ms)
            elapsed_ms += sleep_ms
            discovered = await page.evaluate(SIDEBAR_WALKER_JS) or []
            kept = len(self._filter_discovered(discovered))
            self.logger.info(
                f"  ...read at {elapsed_ms}ms: {kept} matching articles "
                f"({len(discovered)} total)"
            )
            # subtree_only prunes from the whole walk, not just the kept
            # subset, so the out-of-subtree branches must also have stopped
            # hydrating: require every field _classify_subtree reads (id,
            # parent, top_level) to repeat.
            walk = (
                frozenset(
                    (d["id"], d.get("parent_id"), bool(d.get("top_level")))
                    for d in discovered
                )
                if self.options.get("subtree_only") else None
            )
            if (
                kept > 0 and kept == prev_kept and walk == prev_walk
                and (not expect_min or kept >= expect_min)
            ):
                stabilized = True
                break
            prev_kept = kept
            prev_walk = walk
            if elapsed_ms >= timeout_ms:
                break
        return discovered, stabilized

    async def _capture_articles(
        self,
        browser,
        articles: List[Dict[str, Any]],
        articles_dir: Path,
        manifest: Dict[str, Any],
        manifest_path: Path,
    ) -> List[str]:
        """Capture ``articles``; returns the ids that failed this run."""
        concurrency = max(1, int(self.options["concurrency"]))
        semaphore = asyncio.Semaphore(concurrency)
        manifest_lock = asyncio.Lock()
        saved_count = 0
        failed: List[str] = []

        # Index articles by id for in-place updates
        articles_by_id = {a["article_id"]: a for a in manifest["articles"]}

        async def _one(article: Dict[str, Any]) -> None:
            nonlocal saved_count
            async with semaphore:
                article_id = article["article_id"]
                ctx = await browser.new_context()
                try:
                    page = await ctx.new_page()
                    captured = await self._capture_one(page, article_id)
                finally:
                    await ctx.close()

                async with manifest_lock:
                    record = articles_by_id.get(article_id, {})
                    # Backfill required fields for legacy records that
                    # pre-date per-article tagging (area, article_id).
                    # setdefault preserves any existing value, so this is
                    # safe to run on every capture — only fills gaps.
                    # Without this, per-area stats / filtering / future
                    # area-scoped refreshes would silently skip legacy
                    # records (whose frontmatter still gets the current
                    # area via render_article_markdown below).
                    record.setdefault("area", self.options["area"])
                    record.setdefault("article_id", article_id)
                    if captured.get("error") or not captured.get("body"):
                        # A refresh can turn a previously-captured article into
                        # an error (e.g. it's since become a not-found shell —
                        # PR #409 review round 2). Drop the stale file/metadata
                        # from the prior successful capture rather than leaving
                        # it on disk and in the manifest, still marked
                        # `captured`-looking except for `status`, where a
                        # directory scan (not filtering on `status`) would
                        # still surface it. `title` is untouched here — it's
                        # only ever set by a successful capture (below), so on
                        # error it already stays whatever discovery/a prior
                        # capture last put there.
                        error = captured.get("error") or "Empty body"
                        record["status"] = "error"
                        record["error"] = error
                        if record.pop("file", None):
                            (articles_dir / f"{article_id}.md").unlink(missing_ok=True)
                        record.pop("body_length", None)
                        failed.append(article_id)
                        self.logger.warning(f"  [skip] {article_id}: {error}")
                    else:
                        body = captured["body"]
                        title = captured.get("title") or record.get("title") or article_id
                        path = articles_dir / f"{article_id}.md"
                        path.write_text(
                            render_article_markdown(
                                article_id=article_id,
                                title=title,
                                body=body,
                                source_url=self._article_url(article_id),
                                release_version=self.options["release_version"],
                                release_name=self.options["release_name"],
                                area=self.options["area"],
                                parent_article_id=record.get("parent_article"),
                                fetched_at=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                            ),
                            encoding="utf-8",
                        )
                        record["title"] = title
                        record["status"] = "captured"
                        record["body_length"] = len(body)
                        record["file"] = f"articles/{article_id}.md"
                        record.pop("error", None)
                        saved_count += 1
                        if saved_count % 10 == 0 or saved_count == 1:
                            self.logger.info(
                                f"  [{saved_count}/{len(articles)}] {article_id} "
                                f"({len(body)} chars)"
                            )

                    articles_by_id[article_id] = record

                    # Periodic flush so a crash doesn't lose progress
                    if saved_count and saved_count % 25 == 0:
                        manifest["articles"] = sorted(
                            articles_by_id.values(), key=lambda a: a["article_id"]
                        )
                        self._save_manifest(manifest_path, manifest)

        await asyncio.gather(*[_one(a) for a in articles])

        # Final sync
        manifest["articles"] = sorted(
            articles_by_id.values(), key=lambda a: a["article_id"]
        )
        self._save_manifest(manifest_path, manifest)
        return failed

    async def _capture_one(self, page, article_id: str) -> Dict[str, Any]:
        url = self._article_url(article_id)
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        except Exception as e:
            return {"error": f"navigate failed: {e}"}
        await page.wait_for_timeout(self.options["wait_ms"])

        try:
            result = await page.evaluate(ARTICLE_BODY_JS)
        except Exception as e:
            return {"error": f"extract JS failed: {e}"}

        if not result or not result.get("title"):
            return {"error": "no H1 found (article may be 404 or unrendered)"}

        if result["title"].strip().startswith(NOT_FOUND_TITLE_PREFIX):
            return {"error": "portal returned its generic not-found page (rendered, but no article behind this id)"}

        return result

    # ------------------------------------------------------------------
    # Index rendering
    # ------------------------------------------------------------------

    def _build_index(self, index_path: Path, manifest: Dict[str, Any]) -> None:
        stats = manifest.get("stats", {})
        all_articles = manifest.get("articles", [])
        captured = [a for a in all_articles if a.get("status") == "captured"]
        pending = [a for a in all_articles if a.get("status") == "pending"]
        errored = [a for a in all_articles if a.get("status") == "error"]

        # Use .get() with safe defaults throughout — a hand-written or older
        # manifest may be missing some top-level keys.
        release_name = manifest.get("release_name", self.options.get("release_name", "?"))
        release = manifest.get("release", self.options.get("release_version", "?"))
        areas = manifest.get("areas", [])
        # Sort areas by name for stable rendering across runs
        areas = sorted(areas, key=lambda x: x.get("area", ""))

        lines: List[str] = []
        # Title: if manifest covers multiple areas, use the cross-area header;
        # otherwise use the single-area header for backward compatibility.
        if len(areas) > 1:
            lines.append(f"# {release_name} Salesforce Help Snapshot")
            lines.append("")
            lines.append(
                f"Captures **{len(areas)} functional areas** of Revenue Cloud "
                f"Help: {', '.join(a.get('area', '?') for a in areas)}."
            )
        else:
            single_area = (areas[0].get("area") if areas else manifest.get("area", "?"))
            lines.append(f"# {release_name} Salesforce Help Snapshot — {single_area.title()} Area")
        lines.append("")
        lines.append(f"**Release:** {release_name} ({release})")
        lines.append(f"**Last updated:** {manifest.get('last_updated', 'n/a')}")
        lines.append("")

        # Overall stats (across all areas)
        lines.append("## Overall Stats")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|:--|--:|")
        lines.append(f"| Discovered | {stats.get('discovered', 0)} |")
        lines.append(f"| Captured | {stats.get('captured', 0)} |")
        lines.append(f"| Pending | {stats.get('pending', 0)} |")
        lines.append(f"| Errored | {stats.get('errored', 0)} |")
        lines.append(
            f"| Total captured body chars | "
            f"{stats.get('total_captured_body_chars', 0):,} |"
        )
        lines.append("")

        # Per-area summary table (only renders when manifest covers multiple areas)
        if len(areas) > 1:
            lines.append("## Per-Area Coverage")
            lines.append("")
            lines.append("| Area | Root Article | Prefix | Captured | Last Updated |")
            lines.append("|:--|:--|:--|--:|:--|")
            for area_entry in areas:
                a_name = area_entry.get("area", "?")
                a_root = area_entry.get("root_article_id", "?")
                a_url = area_entry.get("source_root_url", "")
                a_prefix = area_entry.get("article_id_prefix", "?")
                a_stats = area_entry.get("stats", {})
                a_captured = a_stats.get("captured", 0)
                a_updated = area_entry.get("last_updated", "n/a")
                root_cell = f"[{a_root}]({a_url})" if a_url else f"`{a_root}`"
                lines.append(
                    f"| **{a_name}** | {root_cell} | `{a_prefix}` | {a_captured} | {a_updated} |"
                )
            lines.append("")

        # Captured articles — group by area when multiple areas exist
        if captured:
            if len(areas) > 1:
                # Group by area
                captured_by_area: Dict[str, List[Dict[str, Any]]] = {}
                for a in captured:
                    captured_by_area.setdefault(a.get("area", "untagged"), []).append(a)
                for area_name in sorted(captured_by_area.keys()):
                    area_articles = captured_by_area[area_name]
                    lines.append(f"## Captured — {area_name} ({len(area_articles)})")
                    lines.append("")
                    lines.append("| Article | ID | Bytes |")
                    lines.append("|:--|:--|--:|")
                    for a in sorted(area_articles, key=lambda x: x["article_id"]):
                        article_id = a["article_id"]
                        title = a.get("title", article_id)
                        file_path = a.get("file", f"articles/{article_id}.md")
                        body_len = a.get("body_length", 0)
                        lines.append(
                            f"| [{title}](./{file_path}) | `{article_id}` | {body_len:,} |"
                        )
                    lines.append("")
            else:
                lines.append("## Captured")
                lines.append("")
                lines.append("| Article | ID | Bytes |")
                lines.append("|:--|:--|--:|")
                for a in sorted(captured, key=lambda x: x["article_id"]):
                    article_id = a["article_id"]
                    title = a.get("title", article_id)
                    file_path = a.get("file", f"articles/{article_id}.md")
                    body_len = a.get("body_length", 0)
                    lines.append(
                        f"| [{title}](./{file_path}) | `{article_id}` | {body_len:,} |"
                    )
                lines.append("")

        if pending:
            lines.append(f"## Pending ({len(pending)})")
            lines.append("")
            for a in sorted(pending, key=lambda a: a["article_id"]):
                title = a.get("title") or a["article_id"]
                lines.append(f"- `{a['article_id']}` — {title}")
            lines.append("")

        if errored:
            lines.append(f"## Errored ({len(errored)})")
            lines.append("")
            for a in sorted(errored, key=lambda a: a["article_id"]):
                title = a.get("title") or a["article_id"]
                err = a.get("error", "unknown")
                lines.append(f"- `{a['article_id']}` — {title} — _{err}_")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append(
            f"*Generated by `scripts/doc_snapshot help` "
            f"on {manifest.get('last_updated', 'n/a')}.*"
        )

        index_path.write_text("\n".join(lines), encoding="utf-8")
