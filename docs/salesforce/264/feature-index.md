# Release 264 (Winter '27) — Feature Index

**Status: scaffold — not yet populated.** This file was created with the `264`
branch cut so the per-release corpus has a home. It intentionally contains no
feature inventory yet, because the source material does not exist:

- Feature freeze **passed on 2026-08-14 01:00 UTC**; GA waves run **2026-09-05 →
  2026-10-10**. Production is still on 262.
- No 264 release notes have been published, and there is no Metadata Coverage
  Report entry for **API v68.0**.
- No official 264 ERD documentation has been published either, so
  [`docs/erds/erd-data.json`](../../erds/erd-data.json) — refreshed to 264 from
  live-org describe — has nothing to reconcile against. It is *ahead of* the
  published doc for this release, not behind it.

Until those land, the ground truth for 264 behavior is a **live 264 org** (the dev
hub is on API 68.0, so every scratch org it creates is a 264 org), not
documentation. Findings gathered that way belong in
`.agents/artifacts/upgrades/264-upgrade-plan.md` until they can be cited to a
published source.

## How to populate this file

1. **Capture the Help portal corpus.** The 13 `snapshot_*_264` tasks in
   `cumulusci.yml` are twins of the 262 tasks, but their `root_article_id`
   values are **inherited from 262 and unverified** — Help article IDs are not
   stable across release reorgs. Validate each area's root first:

   ```bash
   cci task run snapshot_pcm_help_264 -o mode discover 2>&1 | grep 'unique articles'
   cci task run snapshot_pcm_help_264   # only if that line reports a non-zero count
   ```

   Captures land in `docs/salesforce/264/help/` and
   `docs/salesforce/264/dev-guide{,-industries}/`.

   **`discover` does not fail on a bad root** — it exits 0 with zero discovered
   articles, so the `Discovered N unique articles` line it logs is the only
   signal that the root and prefix are right. Read that line, not the manifest:
   `stats.discovered` sums every area and keeps prior runs, so it stays positive
   through a failed re-walk (and on a first 264 run the manifest does not exist
   yet). And even a non-zero count says nothing about whether 264 content
   was *written*: the articles behind a valid root can still be 262 text, so a
   capture can spend 10–15 minutes writing last release's content under a 264
   path. Per-area readiness and capture order are assessed in the private
   artifacts repo (todo 145); check it before committing a run to an area.

2. **Add the release-notes and Solution Overview sources** to the table below as
   they publish, following the 262 pattern. Internal decks are CONFIDENTIAL and
   stay gitignored — reference them by filename only.

3. **Write the per-area inventory** using
   [`../262/feature-index.md`](../262/feature-index.md) as the structural model
   (one `##` section per RC functional area; a `Feature | Tier | Description |
   Demo` table per section).

4. **Preserve preview status.** While 264 is pre-GA, carry the Salesforce
   Release Notes preview disclaimer that the 262 index uses, and mark tiers
   (GA / Beta / Pilot) explicitly.

## Sources

| File | Description |
|---|---|
| *(none yet)* | Populate as 264 release notes, Solution Overview decks, and the Help snapshot become available. |

## Related

- [`.cursor/skills/revenue-cloud-docs/SKILL.md`](../../../.cursor/skills/revenue-cloud-docs/SKILL.md) — grounding product claims against the Help snapshot
- [`.cursor/skills/release-enablement/SKILL.md`](../../../.cursor/skills/release-enablement/SKILL.md) — how this index feeds `docs/enablement/264/`
- [`../262/feature-index.md`](../262/feature-index.md) — prior-release reference and structural model
