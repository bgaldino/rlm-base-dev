"""Structured batch reporting for Transaction Data Harness runs.

The build harness's ``reporting.py`` is tightly coupled to CCI step JSONL and
flag overrides, so this replicates only the *concept* on top of the data this
harness already produces: the list of ``Manifest`` records from a batch.

``build_batch_report`` returns a deterministic dict with totals, a per-stage
histogram of how far scenarios got, and a failure-signature rollup (mirroring
the build harness's ``signature_index``) so an operator or AI agent can see at a
glance which failures recurred and on which runs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .manifests import MANIFEST_DIR, write_json
from .models import STAGES, Manifest

# Errors are keyed by class + a truncated message so distinct transient blips
# don't fragment the rollup into dozens of singletons. The cap applies to the
# message portion; the class prefix (a short word) is always kept whole.
_MESSAGE_TRUNCATE = 160


def _signature(manifest: Manifest) -> str:
    """A stable rollup key for a failed manifest."""
    cls = manifest.failure_class or "unknown"
    message = (manifest.error or "").strip().replace("\n", " ")[:_MESSAGE_TRUNCATE]
    return f"{cls}: {message}" if message else cls


def build_batch_report(manifests: Iterable[Manifest], base_run_id: str = "") -> dict[str, Any]:
    """Summarize a batch of scenario manifests into a deterministic report dict."""
    manifests = list(manifests)
    total = len(manifests)
    failed = [m for m in manifests if m.error]
    retried = [m for m in manifests if (m.attempts or 1) > 1]

    # How far each scenario actually got. None (never started a stage) buckets
    # under "(none)" so the histogram always sums to total.
    stage_histogram: dict[str, int] = {stage: 0 for stage in STAGES}
    stage_histogram["(none)"] = 0
    for m in manifests:
        stage_histogram[m.reached_stage or "(none)"] += 1

    # Failure-signature rollup: signature -> {count, run_ids}.
    signatures: dict[str, dict[str, Any]] = {}
    for m in failed:
        sig = _signature(m)
        row = signatures.setdefault(sig, {"signature": sig, "count": 0, "run_ids": []})
        row["count"] += 1
        row["run_ids"].append(m.run_id)

    return {
        "base_run_id": base_run_id,
        "total": total,
        "succeeded": total - len(failed),
        "failed": len(failed),
        "retried": len(retried),
        "stage_histogram": stage_histogram,
        "failure_signatures": sorted(
            signatures.values(), key=lambda r: (-r["count"], r["signature"])
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render a short human-readable markdown summary of a batch report."""
    lines = [
        f"# Batch report — {report.get('base_run_id') or '(unknown)'}",
        "",
        f"- **Total:** {report['total']}",
        f"- **Succeeded:** {report['succeeded']}",
        f"- **Failed:** {report['failed']}",
        f"- **Retried:** {report['retried']}",
        "",
        "## Stages reached",
        "",
    ]
    # Show stages in lifecycle order, then the catch-all, skipping empty buckets.
    for stage in [*STAGES, "(none)"]:
        count = report["stage_histogram"].get(stage, 0)
        if count:
            lines.append(f"- {stage}: {count}")
    if report["failure_signatures"]:
        lines += ["", "## Failure signatures", ""]
        for row in report["failure_signatures"]:
            runs = ", ".join(row["run_ids"])
            lines.append(f"- ({row['count']}×) {row['signature']}  —  {runs}")
    return "\n".join(lines) + "\n"


def write_batch_report(
    report: dict[str, Any], manifest_dir: Path = MANIFEST_DIR
) -> tuple[Path, Path]:
    """Write the report JSON + markdown next to the manifests; return their paths."""
    base = report.get("base_run_id") or "batch"
    json_path = manifest_dir / f"{base}-report.json"
    md_path = manifest_dir / f"{base}-report.md"
    write_json(json_path, report)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path
