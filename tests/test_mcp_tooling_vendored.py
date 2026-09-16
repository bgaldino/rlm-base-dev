#!/usr/bin/env python3
"""
Offline invariants for the vendored MCP client tooling in scripts/mcp/.

    python tests/test_mcp_tooling_vendored.py

No org needed. The byte-identity checks need a resolvable ramp-demo-kit clone; without
one they report SKIP rather than failing, so this passes in CI and on a workstation that
has only Foundations checked out.

Why this file exists
--------------------
Three scripts in scripts/mcp/ are byte-identical copies of ramp-demo-kit's, kept under
their original filenames precisely so drift is a one-line diff (see scripts/mcp/README.md).
Nothing about a copy announces itself as a copy, though. Someone reformats one, or fixes a
bug in one repo only, and the two silently diverge -- at which point "vendored" is a lie in
the README and the next person to re-vendor either clobbers a real fix or reintroduces a
fixed bug.

So: assert identity while the kit is reachable, and assert the structural claims that hold
regardless -- that the vendored set is exactly what the README lists, that the one adapted
script is not passed off as vendored, and that .mcp.json cannot be committed.
"""
import ast
import hashlib
import io
import os
import sys
import tokenize
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

MCP_DIR = REPO / "scripts" / "mcp"

# filename here -> path within the kit
VENDORED = {
    "ramp_org.py": "tools/ramp_org.py",
    "ramp_auth.py": "tools/ramp_auth.py",
    "mcp_multiplex_proxy.py": "tools/mcp_multiplex_proxy.py",
}
ADAPTED = "write_connector_config.py"

RESULTS = []


def check(name, ok, detail="", skipped=False):
    RESULTS.append((name, None if skipped else bool(ok), detail))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def executable_code(source):
    """
    Strip docstrings and comments, keeping other string literals.

    The checks below ask what the code *does*, and this file's own subject matter is a
    directory layout it must not use -- so the script explains `demos/native` at length
    in its module docstring. Searching raw text reads that explanation as the defect.
    Other string literals stay, because a hardcoded path in a live literal would be a
    real finding.
    """
    without_comments = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type != tokenize.COMMENT:
                without_comments.append(token)
        stripped = tokenize.untokenize(without_comments)
    except (tokenize.TokenError, IndentationError):
        stripped = source

    try:
        tree = ast.parse(stripped)
    except SyntaxError:
        return stripped

    docstring_lines = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        body = getattr(node, "body", [])
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            first = body[0]
            docstring_lines.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))

    return "\n".join(
        "" if number in docstring_lines else line
        for number, line in enumerate(stripped.splitlines(), start=1)
    )


def kit_root():
    """Resolve the kit clone through the manifest, falling back to env/sibling hints."""
    try:
        from scripts.ai.skill_manifest import load_manifest, resolve_repo_root

        root = resolve_repo_root(load_manifest(), "ramp_demo_kit")
        if root:
            return Path(root)
    except Exception:
        pass

    for candidate in (
        os.environ.get("RAMP_DEMO_KIT_ROOT"),
        REPO.parent / "ramp-demo-kit",
    ):
        if candidate and Path(candidate).is_dir():
            return Path(candidate)
    return None


def main():
    # ── The set of files is exactly what the README documents ───────────────────
    present = sorted(p.name for p in MCP_DIR.glob("*.py"))
    expected = sorted(list(VENDORED) + [ADAPTED])
    check(
        "scripts/mcp contains exactly the documented scripts",
        present == expected,
        f"found {', '.join(present)}",
    )
    check("README documents the vendoring", (MCP_DIR / "README.md").exists())

    readme = (MCP_DIR / "README.md").read_text(encoding="utf-8")
    check(
        "README does not claim the adapted script is vendored",
        f"`{ADAPTED}`" in readme and "this repo" in readme,
        "the one file we own must be marked as ours",
    )

    # ── The adapted script must not depend on the kit's demo layout ─────────────
    adapted_source = (MCP_DIR / ADAPTED).read_text(encoding="utf-8")
    adapted_code = executable_code(adapted_source)
    check(
        "adapted script has no hardcoded demo folders",
        "demos/native" not in adapted_code and "demos/cohort" not in adapted_code,
        "Foundations has no demos/ tree",
    )
    check(
        "adapted script points at the vendored proxy",
        "mcp_multiplex_proxy.py" in adapted_code,
        "otherwise it writes a connector to nothing",
    )

    # ── A connector config must be uncommittable ────────────────────────────────
    gitignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    check(
        ".mcp.json is gitignored",
        ".mcp.json" in gitignore,
        "it embeds a consumer key, and a secret in client_credentials mode",
    )

    # ── Byte identity against the kit, when it is reachable ─────────────────────
    kit = kit_root()
    if kit is None:
        for name in VENDORED:
            check(
                f"{name} matches the kit byte for byte",
                None,
                "SKIP — no ramp-demo-kit clone resolved",
                skipped=True,
            )
    else:
        for name, relative in VENDORED.items():
            here = MCP_DIR / name
            there = kit / relative
            if not there.exists():
                check(
                    f"{name} matches the kit byte for byte",
                    None,
                    f"SKIP — {relative} missing from the clone",
                    skipped=True,
                )
                continue
            same = digest(here) == digest(there)
            check(
                f"{name} matches the kit byte for byte",
                same,
                "identical"
                if same
                else f"DRIFT — diff {there} {here}",
            )

    width = max(len(name) for name, _, _ in RESULTS)
    failed = sum(1 for _, ok, _ in RESULTS if ok is False)
    skipped = sum(1 for _, ok, _ in RESULTS if ok is None)
    print("MCP client tooling vendoring\n" + "=" * (width + 60))
    for name, ok, detail in RESULTS:
        label = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
        print(f"  {label}  {name:<{width}}  {detail}")
    print("=" * (width + 60))
    print(
        f"{len(RESULTS) - failed - skipped}/{len(RESULTS) - skipped} checks passed"
        + (f", {skipped} skipped" if skipped else "")
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
