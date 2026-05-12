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
This task produces the markdown snapshot per release-area so the agents have
fast, surgical grounding material.

USAGE

In `cumulusci.yml`:

    snapshot_billing_help_262:
        description: Snapshot the 262 Billing area of Salesforce Help.
        class_path: tasks.rlm_snapshot_help.SnapshotSalesforceHelp
        group: Documentation
        options:
            release_version: "262"
            release_name: "Summer '26"
            area: billing
            root_article_id: ind.billing.htm
            article_id_prefix: ind.billing
            mode: all

Run with:

    cci task run snapshot_billing_help_262

MODES

    discover   Walk sidebar, emit manifest.json with discovered IDs as 'pending'.
               No body capture.
    capture    Read existing manifest, capture each 'pending' article.
    all        Discover then capture. Skips articles already captured. (default)
    refresh    Re-capture every article, overwriting existing files.

REQUIREMENTS

This project uses pyenv + a project-local `.venv` and pipx-installed CumulusCI
(see README §"macOS Environment Setup"). Playwright must be installed into
whichever Python environment runs the task — CCI's interpreter, not the
calling shell's.

If CCI is installed via pipx (the README-recommended path):

    pipx inject cumulusci playwright
    # Playwright isn't exposed as a pipx app by default, so run its CLI via
    # the cumulusci venv's Python directly:
    $(pipx environment --value PIPX_LOCAL_VENVS)/cumulusci/bin/python -m playwright install chromium

    # Or, if you'd rather have `playwright` on your PATH:
    #   pipx inject cumulusci playwright --include-apps --force
    #   playwright install chromium

If CCI is installed via `python -m pip install cumulusci` inside the project
venv (the alternative path in the README):

    source .venv/bin/activate
    python -m pip install playwright
    playwright install chromium

The browser runs headless by default. Set headless=false to watch it work.

VERIFY THE INSTALL

    cci task info snapshot_billing_help_262

If the task lists its options without error, registration is good. To verify
Playwright can be loaded in CCI's environment, dry-run with discover mode:

    cci task run snapshot_billing_help_262 -o mode discover

A successful discover run writes manifest.json with the discovered article IDs
in 'pending' status and exits cleanly.
"""

import asyncio
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
except ImportError:
    BaseTask = object  # type: ignore[misc,assignment]
    TaskOptionsError = Exception
    CommandException = Exception


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
        result.push({ id: id, title: a.innerText.trim().slice(0, 200) });
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


PLAYWRIGHT_INSTALL_HINT = """
Playwright is required for this task. Install with:
    pip install playwright
    playwright install chromium
"""


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
# Task
# ---------------------------------------------------------------------------


class SnapshotSalesforceHelp(BaseTask):
    """Capture Salesforce Help articles as markdown for AI grounding.

    See module docstring for usage. This task does not require an org
    connection — it's a pure web scrape against the public Help portal.
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "release_version": {
            "description": "Salesforce release version (used in URL release param and as a path component), e.g. '262'.",
            "required": True,
        },
        "release_name": {
            "description": "Human-readable release name, e.g. \"Summer '26\".",
            "required": True,
        },
        "area": {
            "description": "Functional area name for grouping, e.g. 'billing'.",
            "required": True,
        },
        "root_article_id": {
            "description": "Article ID of the area root, e.g. 'ind.billing.htm'. The sidebar of this article seeds discovery.",
            "required": True,
        },
        "article_id_prefix": {
            "description": "Only capture articles whose IDs start with this prefix, e.g. 'ind.billing'.",
            "required": True,
        },
        "output_dir": {
            "description": "Output directory. Defaults to docs/salesforce/{release_version}/help.",
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
            "description": "Number of articles to capture in parallel. Defaults to 4.",
            "required": False,
        },
        "wait_ms": {
            "description": "Milliseconds to wait after each navigation for SPA hydration. Defaults to 3000.",
            "required": False,
        },
        "include_release_param": {
            "description": "Append &release={release_version} to article URLs. Defaults to true.",
            "required": False,
        },
    }

    BASE_URL = "https://help.salesforce.com/s/articleView"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _init_options(self, kwargs):
        if hasattr(super(), "_init_options"):
            super()._init_options(kwargs)

        if not self.options.get("output_dir"):
            self.options["output_dir"] = (
                f"docs/salesforce/{self.options['release_version']}/help"
            )
        self.options["mode"] = str(self.options.get("mode", "all")).lower()
        self.options["headless"] = (
            str(self.options.get("headless", "true")).lower() == "true"
        )
        self.options["concurrency"] = int(self.options.get("concurrency", 4))
        self.options["wait_ms"] = int(self.options.get("wait_ms", 3000))
        self.options["include_release_param"] = (
            str(self.options.get("include_release_param", "true")).lower() == "true"
        )

        valid_modes = ("discover", "capture", "all", "refresh")
        if self.options["mode"] not in valid_modes:
            raise TaskOptionsError(
                f"mode must be one of {valid_modes}, got {self.options['mode']!r}"
            )

    def _run_task(self):
        # Lazy-import Playwright so the error message is clearer when it's missing.
        try:
            from playwright.async_api import async_playwright  # noqa: F401
        except ImportError:
            self.logger.error(PLAYWRIGHT_INSTALL_HINT)
            raise CommandException("Playwright not installed")

        cwd = os.getcwd()
        output_dir = Path(cwd) / self.options["output_dir"]
        articles_dir = output_dir / "articles"
        manifest_path = output_dir / "manifest.json"
        index_path = output_dir / "index.md"

        articles_dir.mkdir(parents=True, exist_ok=True)

        asyncio.run(
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
        # The required top-level keys this task writes and the index builder reads.
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
            "capture_method": "tasks.rlm_snapshot_help.SnapshotSalesforceHelp (Playwright + shadow-DOM walker)",
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
                areas[i] = area_entry
                replaced = True
                break
        if not replaced:
            area_entry["snapshot_started"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            areas.append(area_entry)

    @staticmethod
    def _compute_stats(manifest: Dict[str, Any]) -> Dict[str, Any]:
        articles = manifest.get("articles", [])
        captured = [a for a in articles if a.get("status") == "captured"]
        pending = [a for a in articles if a.get("status") == "pending"]
        errored = [a for a in articles if a.get("status") == "error"]
        total_chars = sum(a.get("body_length", 0) for a in captured)
        return {
            "discovered": len(articles),
            "captured": len(captured),
            "pending": len(pending),
            "errored": len(errored),
            "total_captured_body_chars": total_chars,
        }

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
            if article_id in existing_by_id:
                # Update title if the existing one is empty
                if not existing_by_id[article_id].get("title"):
                    existing_by_id[article_id]["title"] = title
                # Backfill area if missing (handles articles from older manifest
                # versions that pre-date per-article area tagging)
                if not existing_by_id[article_id].get("area"):
                    existing_by_id[article_id]["area"] = current_area
            else:
                existing_by_id[article_id] = {
                    "article_id": article_id,
                    "title": title,
                    "status": "pending",
                    "area": current_area,
                }
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
                discovered = await self._discover_articles(page)
                await context.close()

                kept = [
                    d for d in discovered
                    if d["id"].startswith(self.options["article_id_prefix"])
                ]
                self.logger.info(
                    f"Discovered {len(kept)} unique articles "
                    f"({len(discovered)} total before prefix filter)"
                )
                manifest = self._merge_discovered(manifest, kept)
                self._save_manifest(manifest_path, manifest)

            # Phase 2: Capture
            if mode in ("capture", "all", "refresh"):
                to_capture = self._select_articles_to_capture(manifest, mode)
                self.logger.info(f"Capture: {len(to_capture)} articles queued")

                if to_capture:
                    await self._capture_articles(
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

    async def _discover_articles(self, page) -> List[Dict[str, str]]:
        url = self._article_url(self.options["root_article_id"])
        self.logger.info(f"  GET {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(self.options["wait_ms"])
        try:
            discovered = await page.evaluate(SIDEBAR_WALKER_JS)
        except Exception as e:
            self.logger.error(f"  Discovery JS failed: {e}")
            return []
        return discovered or []

    async def _capture_articles(
        self,
        browser,
        articles: List[Dict[str, Any]],
        articles_dir: Path,
        manifest: Dict[str, Any],
        manifest_path: Path,
    ) -> None:
        concurrency = max(1, int(self.options["concurrency"]))
        semaphore = asyncio.Semaphore(concurrency)
        manifest_lock = asyncio.Lock()
        saved_count = 0

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
                    if captured.get("error"):
                        record["status"] = "error"
                        record["error"] = captured["error"]
                        self.logger.warning(
                            f"  [skip] {article_id}: {captured['error']}"
                        )
                    elif not captured.get("body"):
                        record["status"] = "error"
                        record["error"] = "Empty body"
                        self.logger.warning(f"  [skip] {article_id}: empty body")
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
            f"*Generated by `tasks.rlm_snapshot_help.SnapshotSalesforceHelp` "
            f"on {manifest.get('last_updated', 'n/a')}.*"
        )

        index_path.write_text("\n".join(lines), encoding="utf-8")
