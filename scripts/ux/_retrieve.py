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

from scripts.ux._assemble import validate_selection, write_org_state
from scripts.ux._context import UxContext, UxError, UxOptionError
from scripts.ux._flags import FLEXIPAGE_SUFFIX, resolve_flexipage_sources
from scripts.ux._sf import cli_error, run_sf_json

#: Minutes sf waits for the retrieve to finish.
RETRIEVE_WAIT_MINUTES = 10


def retrieve(
    ctx: UxContext,
    target_org: str,
    output_path: Path,
    metadata_name: Optional[str] = None,
) -> int:
    """Retrieve flexipages from ``target_org`` (sf CLI alias or username) into
    ``output_path/flexipages``; return the number written."""
    if not target_org:
        raise UxOptionError("A target org (sf CLI alias or username) is required.")
    validate_selection("flexipages", metadata_name, ("flexipages",))
    logger = ctx.logger
    output_path = Path(output_path)

    if metadata_name:
        pages = [metadata_name]
    else:
        base_dir = ctx.templates_path / "flexipages" / "base"
        standalone_dir = ctx.templates_path / "flexipages" / "standalone"
        if not base_dir.exists():
            logger.warning(f"Flexipage base directory not found: {base_dir}")
            return 0
        # The shared resolver keeps retrieve scope equal to what the assembler
        # deploys (base + active standalone dirs).
        pages = sorted(resolve_flexipage_sources(base_dir, standalone_dir, ctx.features))

    if not pages:
        logger.warning("No flexipages found to retrieve.")
        return 0

    api_names = [name[: -len(FLEXIPAGE_SUFFIX)] for name in pages]
    logger.info(
        f"Retrieving {len(api_names)} flexipage(s) from "
        f"'{target_org}': {', '.join(api_names)}"
    )

    dest_dir = output_path / "flexipages"
    with tempfile.TemporaryDirectory(prefix="ux_retrieve_") as tmp:
        # Retrieve before touching the output directory, so a bad alias or a
        # failed retrieve leaves the existing files in place.
        _sf_retrieve(ctx, target_org, api_names, Path(tmp))
        dest_dir.mkdir(parents=True, exist_ok=True)
        # Until the copy below finishes, the directory is neither the old
        # files nor the org's: deploy, diff and writeback must refuse it.
        write_org_state(output_path, pages, incomplete=True)

        # Clear what this retrieve replaces (every page, or just the requested
        # one), so a page the org lacks cannot survive as a stale copy.
        stale = [dest_dir / metadata_name] if metadata_name else dest_dir.glob(f"*{FLEXIPAGE_SUFFIX}")
        for old_file in stale:
            old_file.unlink(missing_ok=True)

        retrieved = _copy_flexipages(ctx, Path(tmp), dest_dir)

    # Record which pages are org state (a requested page the org lacks is too:
    # its absence). The rest of a scoped retrieve's directory is not, and none
    # of it is assembled output that deploy may send.
    write_org_state(output_path, pages)

    if retrieved == 0:
        logger.warning(
            "No FlexiPage files found in retrieve result. "
            "The org may not have deployed flexipages for the requested names."
        )
    else:
        logger.info(f"Retrieved {retrieved} flexipage(s) written to {dest_dir}")
    return retrieved


def _sf_retrieve(ctx: UxContext, target_org: str, api_names: List[str], target_dir: Path) -> None:
    """``sf project retrieve start`` the flexipages into ``target_dir`` (metadata format)."""
    args = ["project", "retrieve", "start"]
    for name in api_names:
        args += ["--metadata", f"FlexiPage:{name}"]
    args += [
        "--target-metadata-dir", str(target_dir),
        "--unzip",
        "--api-version", ctx.api_version,
        "--wait", str(RETRIEVE_WAIT_MINUTES),
        "--target-org", target_org,
    ]
    output = run_sf_json(
        args,
        cwd=ctx.repo_root,
        timeout=RETRIEVE_WAIT_MINUTES * 60 + 60,
        logger=ctx.logger,
    )
    result = output.get("result") or {}
    status = result.get("status", "Unknown")
    if output.get("status", -1) != 0 or status != "Succeeded":
        detail = cli_error(output) or f"status={status}"
        raise UxError(f"Retrieve from '{target_org}' failed: {detail}")
    ctx.logger.info(f"  Retrieve complete: {status}")
    # Members the org does not have come back as warnings, not failures.
    messages = result.get("messages") or []
    if isinstance(messages, dict):
        messages = [messages]
    for msg in messages:
        problem = msg.get("problem") if isinstance(msg, dict) else msg
        if problem:
            ctx.logger.warning(f"  {problem}")


def _copy_flexipages(ctx: UxContext, retrieved_dir: Path, dest_dir: Path) -> int:
    """Copy retrieved ``*.flexipage`` files into ``dest_dir`` under source-format names."""
    count = 0
    for src in sorted(retrieved_dir.rglob("*.flexipage")):
        dest = dest_dir / (src.name + "-meta.xml")
        shutil.copyfile(src, dest)
        try:
            shown = dest.relative_to(ctx.repo_root)
        except ValueError:
            shown = dest
        ctx.logger.info(f"  [retrieved] {dest.name} -> {shown}")
        count += 1
    return count
