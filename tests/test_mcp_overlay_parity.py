#!/usr/bin/env python3
"""
Offline invariants for the two copies of RampCloneSalesTransaction.

    python tests/test_mcp_overlay_parity.py

No org and no CumulusCI install required -- every check is text and YAML handling
against files in the working tree.

Why this file exists
--------------------
The MCP clone invocable is deliberately duplicated. `unpackaged/post_mcp` carries a
67.0, synchronous-only copy because the async members simply are not on the 262
representations -- a compile probe against a 262 org reports `Variable does not exist`
for input.contextId, options.contextId, and output.trackerId -- and ConnectApi input
types reject JSON.serialize/deserialize, so a 67.0 class has no reflective path to
them either. `unpackaged/post_mcp_264` therefore carries a 68.0 copy that adds the
async path, overlaid only on orgs that can compile it.

Two copies of one class is a drift hazard, and the dangerous direction is specific:
someone edits the base copy, reaches for the async fields because the 264 copy has
them, and every 262 org in the fleet starts failing its deploy. Or the reverse -- the
async members get dropped from the overlay, it deploys clean, and the async path
vanishes silently because nothing at runtime asserts a tracker handle is reachable.
Neither shows up in an org build's exit code, so both need asserting on the source.

These checks are cheap and blunt on purpose: same class name, opposite async-member
sets, the api versions the gate assumes, and a flow that deploys base before overlay.
They are also the retirement checklist -- when Foundations' baseline reaches 264, this
file, the overlay, and the DeployMcpOverlay task all go away together.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

BASE_DIR = REPO / "unpackaged" / "post_mcp"
OVERLAY_DIR = REPO / "unpackaged" / "post_mcp_264"
CLASS_NAME = "RampCloneSalesTransaction"

# Members that exist only on 264 / v68.0. The base copy must not reference any of
# them; the overlay must reference all of them.
ASYNC_MEMBERS = ("contextId", "trackerId", "trackerUrl", "isAsync")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def strip_comments(source):
    """
    Drop Apex block and line comments.

    The async-member checks below have to run on code, not prose. Both copies discuss
    contextId and trackerId at length in their header comments -- explaining the split
    is the whole point of those comments -- and a raw substring search would read that
    explanation as the very defect it is meant to catch.
    """
    without_blocks = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", without_blocks)


def api_version(meta_path):
    match = re.search(r"<apiVersion>([\d.]+)</apiVersion>", read(meta_path))
    return match.group(1) if match else None


def main():
    base_cls = BASE_DIR / "classes" / f"{CLASS_NAME}.cls"
    overlay_cls = OVERLAY_DIR / "classes" / f"{CLASS_NAME}.cls"

    # ── Both copies are present, with their meta and their tests ────────────────
    for label, directory in (("base", BASE_DIR), ("overlay", OVERLAY_DIR)):
        for suffix in ("", "Test"):
            stem = f"{CLASS_NAME}{suffix}"
            cls = directory / "classes" / f"{stem}.cls"
            meta = directory / "classes" / f"{stem}.cls-meta.xml"
            check(f"{label} has {stem}.cls", cls.exists(), str(cls.relative_to(REPO)))
            check(
                f"{label} has {stem}.cls-meta.xml",
                meta.exists(),
                str(meta.relative_to(REPO)),
            )

    base_source = read(base_cls)
    overlay_source = read(overlay_cls)

    # ── Same class, so the overlay replaces rather than adds a second tool ──────
    # The CLASSIC binding points at /actions/custom/apex/RampCloneSalesTransaction.
    # A renamed overlay would deploy fine and bind nothing.
    for label, source in (("base", base_source), ("overlay", overlay_source)):
        check(
            f"{label} declares class {CLASS_NAME}",
            re.search(rf"\bclass\s+{CLASS_NAME}\b", source) is not None,
            "the CLASSIC binding resolves this class by name",
        )
        check(
            f"{label} declares the invocable entry point",
            "@InvocableMethod" in source and "cloneSegments" in source,
            "CLASSIC binding needs an @InvocableMethod",
        )
        check(
            f"{label} declares a sharing keyword",
            re.search(r"\b(with|without|inherited)\s+sharing\b", source) is not None,
            "repo Apex rule: sharing keyword is mandatory",
        )

    # ── The load-bearing asymmetry ─────────────────────────────────────────────
    base_code = strip_comments(base_source)
    overlay_code = strip_comments(overlay_source)

    leaked = [m for m in ASYNC_MEMBERS if m in base_code]
    check(
        "base copy references no async members",
        not leaked,
        "clean"
        if not leaked
        else f"{', '.join(leaked)} present -- will not compile on 262 / v67.0",
    )

    missing = [m for m in ASYNC_MEMBERS if m not in overlay_code]
    check(
        "overlay copy references every async member",
        not missing,
        "clean"
        if not missing
        else f"{', '.join(missing)} absent -- async path silently lost",
    )

    # The overlay's test must touch the async members too, so a deploy to an org
    # that lacks them fails at validation instead of compiling a degraded contract.
    overlay_test = strip_comments(
        read(OVERLAY_DIR / "classes" / f"{CLASS_NAME}Test.cls")
    )
    untested = [m for m in ASYNC_MEMBERS if m not in overlay_test]
    check(
        "overlay test exercises the async members",
        not untested,
        "clean" if not untested else f"{', '.join(untested)} unreferenced",
    )

    # ── The api versions the version gate assumes ──────────────────────────────
    base_version = api_version(BASE_DIR / "classes" / f"{CLASS_NAME}.cls-meta.xml")
    overlay_version = api_version(OVERLAY_DIR / "classes" / f"{CLASS_NAME}.cls-meta.xml")
    check("base copy is 67.0", base_version == "67.0", f"got {base_version}")
    check("overlay copy is 68.0", overlay_version == "68.0", f"got {overlay_version}")

    # ── Wiring: gated task, and base deploys before the overlay ────────────────
    cumulusci = read(REPO / "cumulusci.yml")
    check(
        "overlay task uses the version-gated deploy class",
        "tasks.rlm_mcp.DeployMcpOverlay" in cumulusci,
        "a plain Deploy here hard-fails every 262 org",
    )
    check(
        "overlay task declares min_api_version",
        re.search(r"min_api_version:\s*68\.0", cumulusci) is not None,
        "the gate needs a floor to compare against",
    )

    order = [
        cumulusci.find("task: deploy_post_mcp\n"),
        cumulusci.find("task: deploy_post_mcp_264"),
        cumulusci.find("task: configure_mcp_servers"),
    ]
    check(
        "prepare_mcp orders base -> overlay -> configure",
        all(position != -1 for position in order) and order == sorted(order),
        f"positions {order}",
    )

    width = max(len(name) for name, _, _ in RESULTS)
    failed = 0
    print("MCP clone-invocable overlay parity\n" + "=" * (width + 60))
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
        failed += 0 if ok else 1
    print("=" * (width + 60))
    print(f"{len(RESULTS) - failed}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
