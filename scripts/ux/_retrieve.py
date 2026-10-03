"""
Retrieve live flexipages from an org into the UX output directory.

Replaces the assembled flexipages in ``unpackaged/post_ux/flexipages/`` with
the org's current state, as the first half of drift capture
(``ux_tool.py capture-drift`` = retrieve → diff).

The org is addressed by its sf CLI alias or username. Retrieval is
``sf project retrieve start --metadata FlexiPage:<name> ... --target-metadata-dir
<tmp> --unzip``: metadata format, so each file is the org's raw ``.flexipage``
XML, written here under its source-format name (``.flexipage-meta.xml``). The
sf CLI owns auth, polling and zip handling; no access token passes through
this module.

Scope defaults to every flexipage the assembler would deploy: base pages from
``templates/flexipages/base/`` plus standalone overrides whose feature flag is
active. Pass ``metadata_name`` to retrieve a single page.
"""
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

from scripts.ux._assemble import validate_selection
from scripts.ux._context import UxContext, UxError, UxOptionError
from scripts.ux._flags import FLEXIPAGE_SUFFIX, resolve_flexipage_sources
from scripts.ux._sf import cli_error, run_sf_json

#: Minutes sf waits for the retrieve to finish.
RETRIEVE_WAIT_MINUTES = 10


class UxRetriever:
    """Retrieves flexipages from ``target_org`` (sf CLI alias or username)."""

    def __init__(self, ctx: UxContext, target_org: str):
        if not target_org:
            raise UxOptionError("A target org (sf CLI alias or username) is required.")
        self.ctx = ctx
        self.logger = ctx.logger
        self.target_org = target_org

    def run(self, output_path: Path, metadata_name: Optional[str] = None) -> int:
        """Retrieve into ``output_path/flexipages``; return the number written."""
        validate_selection("flexipages", metadata_name, ("flexipages",))
        return self._retrieve_flexipages(Path(output_path), metadata_name)

    def _retrieve_flexipages(self, output_path: Path, filter_name: Optional[str]) -> int:
        templates_path = self.ctx.templates_path
        base_dir = templates_path / "flexipages" / "base"
        standalone_dir = templates_path / "flexipages" / "standalone"

        if filter_name:
            pages = [filter_name]
        else:
            if not base_dir.exists():
                self.logger.warning(f"Flexipage base directory not found: {base_dir}")
                return 0

            # Build page list using the shared resolver so retrieve scope always
            # matches what the assembler deploys (base + active standalone dirs).
            page_sources = resolve_flexipage_sources(base_dir, standalone_dir, self.ctx.features)
            pages = sorted(page_sources.keys())

        if not pages:
            self.logger.warning("No flexipages found to retrieve.")
            return 0

        # Extract API names from filenames
        api_names = [name.replace(FLEXIPAGE_SUFFIX, "") for name in pages]

        self.logger.info(
            f"Retrieving {len(api_names)} flexipage(s) from "
            f"'{self.target_org}': {', '.join(api_names)}"
        )

        dest_dir = output_path / "flexipages"
        with tempfile.TemporaryDirectory(prefix="ux_retrieve_") as tmp:
            # Retrieve before touching the output directory, so a bad alias or a
            # failed retrieve leaves the existing files in place.
            self._sf_retrieve(api_names, Path(tmp))
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Clear what this retrieve replaces (every page, or just the requested
            # one), so a page the org lacks cannot survive as a stale copy.
            stale = [dest_dir / filter_name] if filter_name else dest_dir.glob(f"*{FLEXIPAGE_SUFFIX}")
            for old_file in stale:
                old_file.unlink(missing_ok=True)

            retrieved = self._copy_flexipages(Path(tmp), dest_dir)

        if retrieved == 0:
            self.logger.warning(
                "No FlexiPage files found in retrieve result. "
                "The org may not have deployed flexipages for the requested names."
            )
        else:
            self.logger.info(f"Retrieved {retrieved} flexipage(s) written to {dest_dir}")
        return retrieved

    def _sf_retrieve(self, api_names: List[str], target_dir: Path) -> None:
        """``sf project retrieve start`` the flexipages into ``target_dir`` (metadata format)."""
        args = ["project", "retrieve", "start"]
        for name in api_names:
            args += ["--metadata", f"FlexiPage:{name}"]
        args += [
            "--target-metadata-dir", str(target_dir),
            "--unzip",
            "--api-version", self.ctx.api_version,
            "--wait", str(RETRIEVE_WAIT_MINUTES),
            "--target-org", self.target_org,
        ]
        output = run_sf_json(
            args,
            cwd=self.ctx.repo_root,
            timeout=RETRIEVE_WAIT_MINUTES * 60 + 60,
            logger=self.logger,
        )
        result = output.get("result") or {}
        status = result.get("status", "Unknown")
        if output.get("status", -1) != 0 or status != "Succeeded":
            detail = cli_error(output) or f"status={status}"
            raise UxError(f"Retrieve from '{self.target_org}' failed: {detail}")
        self.logger.info(f"  Retrieve complete: {status}")
        # Members the org does not have come back as warnings, not failures.
        messages = result.get("messages") or []
        if isinstance(messages, dict):
            messages = [messages]
        for msg in messages:
            problem = msg.get("problem") if isinstance(msg, dict) else msg
            if problem:
                self.logger.warning(f"  {problem}")

    def _copy_flexipages(self, retrieved_dir: Path, dest_dir: Path) -> int:
        """Copy retrieved ``*.flexipage`` files into ``dest_dir`` under source-format names."""
        count = 0
        for src in sorted(retrieved_dir.rglob("*.flexipage")):
            dest_name = src.name + "-meta.xml"
            dest = dest_dir / dest_name
            shutil.copyfile(src, dest)
            self.logger.info(f"  [retrieved] {dest_name} -> {self._rel(dest)}")
            count += 1
        return count

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.ctx.repo_root))
        except ValueError:
            return str(path)
