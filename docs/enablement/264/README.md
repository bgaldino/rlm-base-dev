# Release 264 (Winter '27) — Enablement Extracts

**Status: scaffold — no 264 artifacts authored yet.** Created with the `264`
branch cut so the per-release directory exists; authoring starts once the 264
feature inventory does.

Per-release directories hold two different kinds of artifact, and they have
different prerequisites:

| Kind | Files | Prerequisite |
|---|---|---|
| **Per-area Hands-On extracts** | `264-{area}-hands-on.md` | A populated [`docs/salesforce/264/feature-index.md`](../../salesforce/264/feature-index.md), plus master sign-off in [`../master/`](../master/) |
| **SE/partner artifacts** | `qb-demo-script.md` | Its own authoring skill — [`.cursor/skills/qb-demo-script/SKILL.md`](../../../.cursor/skills/qb-demo-script/SKILL.md) |

Extracts are filtered views of the living master catalog in
[`../master/`](../master/) — author there first, then extract. Use
[`../_template/exercise-template.md`](../_template/exercise-template.md) as the
canonical exercise shape and follow
[`.cursor/skills/release-enablement/SKILL.md`](../../../.cursor/skills/release-enablement/SKILL.md).

Blocking dependency: the 264 feature index is itself a scaffold, because 264
release notes have not published (feature freeze 2026-08-14; GA waves
2026-09-05 → 2026-10-10). Do not author 264 exercises against 262 content and
relabel it — the point of a per-release extract is that it reflects that
release.

Track status for this release in
[`../coverage-matrix.md`](../coverage-matrix.md).
