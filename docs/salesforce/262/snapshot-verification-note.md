# 262 Help-Corpora Verification Note

Final verification of the captured Salesforce Help / Developer-Guide snapshots under
`docs/salesforce/262/`, ahead of the 264 branch cut. This is the known-good baseline the
264 refresh (`revenue-cloud-docs` skill → *Refresh workflow* → `diff -u`) reads against.

**Verified:** 2026-08-04 (todo pack 100). Owning skill: `.cursor/skills/revenue-cloud-docs/SKILL.md`.

## State — all three sub-corpora complete, 0 errored

| Sub-corpus | Path | Captured / Discovered | Errored | Files on disk |
|---|---|---|---|---|
| Help | `help/` | 935 / 935 | 0 | 935 ✓ |
| Dev-Guide (RLM atlas) | `dev-guide/` | 1388 / 1389 | 1 (upstream-broken, logged below) | 1388 ✓ |
| Dev-Guide (Industries common) | `dev-guide-industries/` | 571 / 571 | 0 | 571 ✓ |

Body totals: help ~2.07 MB / 4.3 MB on disk; corpus captured 2026-05-11/12 (collections
2026-06-21; final 3 collections articles recaptured 2026-08-04).

## Checks (per the skill's Refresh-workflow validation)

1. **File count == manifest `captured` count** — ✓ all three (935 / 1388 / 571).
2. **Breadcrumb-noise grep** (`grep -l "^You are here:"` across every `articles/` tree) — ✓ 0.
3. **Errored count** — Help 0, Industries 0, RLM dev-guide 1 (logged as upstream-broken, below).
4. **`help/manifest.json` `notes[]` stale-reference items** — verified accurate and carried
   forward (see below); they target downstream Trailhead content, not a corpus defect.

## Recaptured 2026-08-04

3 Collections help articles that had errored at original capture ("no H1 found — 404 or
unrendered") were recaptured cleanly via `cci task run snapshot_collections_help_262 -o mode
capture` (after `playwright install chromium` in the CCI venv):

- `ind.collections_customize_omniscript_for_direct_debit.htm`
- `ind.collections_customize_page_check_compliance.htm`
- `ind.collections_customize_page_hierarchical_view.htm`

Help is now 935/935, 0 errored. The original "no H1" errors were transient (page unrendered at
first capture), not genuine 404s.

## Known upstream-broken — carry forward, do NOT re-investigate

- **`connect_resources_rating_waterfall_post.htm`** (RLM dev-guide, section "Salesforce
  Pricing"). Fails on every capture with `SyntaxError: Failed to execute 'json' on 'Response':
  Unexpected end of JSON input` — the atlas content API returns an empty body for this page ID.
  Retried 2026-08-04, still empty. Its siblings (`..._rating_waterfall_fetch.htm`,
  `..._pricing_waterfall_post.htm`) capture fine, so this is one broken upstream page, not a
  task defect. Recapture only if upstream fixes it. **A bare `capture`/`refresh` retry rewrites
  the manifest/index timestamp with no content gain — revert that churn if it's the only diff.**

## Manifest `notes[]` — verified accurate, carry forward

The `help/manifest.json` note about Module 2 v2 Trailhead references is correct against the
corpus and should stay until that downstream content is synced:

- "Define Billing Policies and Billability Rules" = `ind.billing_policies_and_treatments.htm`
  (NOT `ind.billing_payment_terms.htm`, which is titled "Create Payment Terms").
- "Configure Milestone Billing" = `ind.billing_milestone_plans.htm`
  (`ind.billing_milestone.htm` is gone — a 260→262 rename).

Both target IDs resolve correctly in the 262 corpus; the note is a pointer for fixing the
Trailhead module, not a snapshot error.

## Stale-stat sweep (fixed 2026-08-04)

The recapture moved help 932→935 / collections 94→97 / errored 3→0. Every hardcoded copy of
the old numbers was updated: `revenue-cloud-docs/SKILL.md` (4 spots incl. a wrong BRE
errored-page claim), `cumulusci.yml` (area-snapshot comment block), `docs/enablement/README.md`,
`docs/enablement/coverage-matrix.md`, `datasets/sfdmu/inapp/convert_from_legacy.py`.
