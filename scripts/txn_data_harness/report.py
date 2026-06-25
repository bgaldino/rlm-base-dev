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

from .handlers import SCENARIO_HANDLERS
from .manifests import MANIFEST_DIR, write_json
from .models import Manifest

# Per-kind stage allowlist for the report's histogram. The handler's
# ``STEP_GRAPH`` keys are the stages a manifest can reach for that kind, in
# the order they're hit. ``(none)`` is appended so a manifest that never
# checkpointed a stage still buckets cleanly.
_STAGES_BY_KIND: dict[str, list[str]] = {
    "sales_transaction": [
        "opportunity", "quote", "order", "activate", "usage", "invoice", "post",
    ],
    "invoice_ingestion": ["invoice", "post"],
}

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
    """Summarize a batch of scenario manifests into a deterministic report dict.

    Mixed-kind batches (e.g. one config with both PST and ingestion scenarios)
    produce a kind-aware report:

    * ``kind_histogram`` -- per-kind totals at a glance.
    * ``stage_histogram_by_kind`` -- nested ``kind -> {stage: count}`` so the
      ``invoice`` bucket doesn't conflate "PST stopped at Draft generate_invoice"
      with "ingestion landed a Draft via ingest_invoice".

    Failure signatures stay one combined rollup -- failures cluster by error
    class, not by kind.
    """
    manifests = list(manifests)
    total = len(manifests)
    failed = [m for m in manifests if m.error]
    retried = [m for m in manifests if (m.attempts or 1) > 1]

    # Per-kind totals. Defaults to zero for every known handler so the report
    # shape is stable even when one kind is absent from this batch.
    kind_histogram: dict[str, int] = {kind: 0 for kind in SCENARIO_HANDLERS}
    for m in manifests:
        kind_histogram[m.kind] = kind_histogram.get(m.kind, 0) + 1

    # Per-kind stage histogram. Each kind only includes the stages it can
    # reach (the handler's step-graph keys + "(none)" for not-yet-started).
    stage_histogram_by_kind: dict[str, dict[str, int]] = {}
    for kind, stages in _STAGES_BY_KIND.items():
        if kind_histogram.get(kind):
            stage_histogram_by_kind[kind] = {s: 0 for s in stages}
            stage_histogram_by_kind[kind]["(none)"] = 0
    for m in manifests:
        per_kind = stage_histogram_by_kind.setdefault(
            m.kind,
            {s: 0 for s in _STAGES_BY_KIND.get(m.kind, [])} | {"(none)": 0},
        )
        reached = m.reached_stage or "(none)"
        per_kind[reached] = per_kind.get(reached, 0) + 1

    # Failure-signature rollup: signature -> {count, run_ids}.
    signatures: dict[str, dict[str, Any]] = {}
    for m in failed:
        sig = _signature(m)
        row = signatures.setdefault(sig, {"signature": sig, "count": 0, "run_ids": []})
        row["count"] += 1
        row["run_ids"].append(m.run_id)

    # Poll warnings: scenarios where asset poll did not converge cleanly.
    poll_warnings = sorted(
        (
            {"run_id": m.run_id, "status": m.asset_poll_status}
            for m in manifests
            if m.asset_poll_status and m.asset_poll_status != "converged"
        ),
        key=lambda r: r["run_id"],
    )
    link_warnings = sorted(
        (
            {
                "run_id": m.run_id,
                "status": m.invoice_order_link_status,
                "error": m.invoice_order_link_error,
            }
            for m in manifests
            if m.invoice_order_link_status == "failed"
        ),
        key=lambda r: r["run_id"],
    )

    return {
        "base_run_id": base_run_id,
        "total": total,
        "succeeded": total - len(failed),
        "failed": len(failed),
        "retried": len(retried),
        "kind_histogram": kind_histogram,
        "stage_histogram_by_kind": stage_histogram_by_kind,
        "failure_signatures": sorted(
            signatures.values(), key=lambda r: (-r["count"], r["signature"])
        ),
        "poll_warnings": poll_warnings,
        "link_warnings": link_warnings,
    }


_KIND_TITLES: dict[str, str] = {
    "sales_transaction": "Sales transaction",
    "invoice_ingestion": "Invoice ingestion",
}


def render_markdown(report: dict[str, Any]) -> str:
    """Render a short human-readable markdown summary of a batch report.

    Groups the stage histogram by kind so a mixed-kind batch surfaces each
    lifecycle's reached-stage shape on its own. Kinds with zero manifests in
    this batch are skipped entirely (no empty header).
    """
    kind_hist = report.get("kind_histogram", {})
    stage_by_kind = report.get("stage_histogram_by_kind", {})

    lines = [
        f"# Batch report — {report.get('base_run_id') or '(unknown)'}",
        "",
        f"- **Total:** {report['total']}",
        f"- **Succeeded:** {report['succeeded']}",
        f"- **Failed:** {report['failed']}",
        f"- **Retried:** {report['retried']}",
    ]
    if kind_hist:
        lines += ["", "## Kinds", ""]
        for kind in sorted(kind_hist):
            count = kind_hist[kind]
            if count:
                title = _KIND_TITLES.get(kind, kind)
                lines.append(f"- {title}: {count}")

    # Per-kind reached-stage sections; preserve lifecycle stage order from
    # _STAGES_BY_KIND so e.g. PST stays opportunity -> quote -> ... -> post.
    for kind in sorted(stage_by_kind):
        per_kind = stage_by_kind[kind]
        if not any(per_kind.values()):
            continue
        title = _KIND_TITLES.get(kind, kind)
        ordered_stages = [*_STAGES_BY_KIND.get(kind, sorted(per_kind)), "(none)"]
        lines += ["", f"## {title} — stages reached", ""]
        for stage in ordered_stages:
            count = per_kind.get(stage, 0)
            if count:
                lines.append(f"- {stage}: {count}")
        unknown_stages = [
            stage for stage in sorted(per_kind)
            if stage not in ordered_stages and per_kind.get(stage, 0)
        ]
        for stage in unknown_stages:
            lines.append(f"- {stage}: {per_kind[stage]} (unknown)")

    if report.get("poll_warnings"):
        lines += ["", "## Poll warnings", ""]
        for row in report["poll_warnings"]:
            lines.append(f"- {row['run_id']}: {row['status']}")

    if report.get("link_warnings"):
        lines += ["", "## Link warnings", ""]
        for row in report["link_warnings"]:
            suffix = f" — {row['error']}" if row.get("error") else ""
            lines.append(f"- {row['run_id']}: {row['status']}{suffix}")

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
