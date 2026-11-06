# Release data-plan audit

Read this at the start of a release, after a platform patch that changes schema, or before calling a
data plan "audited for <release>". A plan that loads isn't audited: a load succeeds while it selects a
field the release removed, carries a value a restricted picklist dropped, or writes a column the
platform silently ignores. `scripts/audit_data_plans.py` checks every tracked plan's written
declarations against `sobject describe`.

## When to run it

- **Start of a release:** on the first `prepare_rlm_org` build of the new release, capture a snapshot,
  run the audit, triage, and commit the snapshot with the triage.
- **A plan change:** nothing to do. `pr_gate`'s `data_plan_audit` check runs the audit against the
  committed snapshot whenever `datasets/sfdmu/` changes.
- **Bumping `salesforce_release_active`:** the same PR must add `<release>-plan-describe.json`. Without
  it the audit exits 2, so `pr_gate` (and `tests/test_audit_data_plans.py`) fail on that PR and on
  every data-plan PR after it.
- **A suspected platform change mid-release:** audit live against a fresh build and compare with the
  committed snapshot's result.

## Steps

1. **Build a feature-complete org.** Use the build harness on the usual shape with every optional data
   plan on (for qb: `clm_data`, `inapp`, `quote_est_tax` on top of the defaults). An object a feature
   doesn't enable is missing from the describe; the report lists it under *Objects not in the
   describe* rather than auditing it.
2. **Capture the snapshot.** Read-only:
   ```bash
   python scripts/audit_data_plans.py snapshot --target-org <sf alias or username> \
       --out scripts/erd/schema_diff/<release>-plan-describe.json
   ```
   For objects that org lacks (q3's or mfg's features, a different edition), capture a second org and
   add it: `snapshot --target-org <other> --merge <release>-plan-describe.json --out <same path>`. The
   merge adds objects, fields and picklist values; the first org's attributes win.
3. **Run the audit.**
   ```bash
   python scripts/audit_data_plans.py audit --out /tmp/<release>-plan-audit.md
   ```
   With no `--target-org` or `--snapshot` it reads the active release's snapshot
   (`salesforce_release_active` in `.claude/skill-manifest.yml`) and the newest
   `scripts/erd/schema_diff/*-vs-<release>-diff.json` for the release's new fields and values.
   `--plans qb/en-US` limits it to some plans; an allowlist entry is reported stale only for a plan it audited.
4. **Triage each gating finding.** Fix the plan, or add an entry to `KNOWN_FINDINGS` in the script with
   the reason it stands and the todo that owns it. The run fails on any finding not listed, and on any
   listed entry no longer found.
5. **Review the informational sections** (they never fail the run):
   - *Columns that never land*: values in fields that are neither createable nor updateable. Usually
     derived fields an extraction copied (`PricingTerm` on adjustments, `ChildProductRole`); check none
     is a value the plan means to set, and drop real dead columns when the plan is next touched.
   - *Values outside an unrestricted picklist's defined values*: they load. Decide whether the org's
     picklist should define them.
   - *Picklist values the release added*: values a plan could now use.
   - *Writable fields no plan writes*, with the release's new fields in bold: candidates for the
     release's enablement, not defects.
6. **Record the run.** Commit the snapshot and the `KNOWN_FINDINGS` triage together, and log the
   report's counts in the release's todo pack.

## Checks

| Check | Gating | Meaning |
|---|---|---|
| `unknown-field` | yes | The query selects, or the `externalId` names, a field the object doesn't have, or a relationship path that doesn't resolve (followed through `referenceTo` where the target is in the snapshot; a target that isn't is left unchecked). SFDMU drops it and the load still succeeds |
| `picklist` | yes | A CSV value outside a restricted picklist's active values. `CurrencyIsoCode` is skipped: it is the org's currency set, not the release's |
| `required` | yes | A creating declaration leaves out, or blanks on the rows it creates, a field that is createable, not nillable and not defaulted on create. A row an earlier creating pass of the plan created (same key) is only patched, so it isn't re-checked. Booleans are skipped (they default to false) |
| dead columns, undefined values, release values, unwritten fields | no | See step 5 |

## Gotchas

- **Org shape is not release.** A field or value missing from one org may be feature-gated or
  currency-set dependent. Before calling a finding a release change, check it on a second shape or
  in the release diff (`scripts/erd/schema_diff/`), as the rest of this skill does for the ERD.
- **`required` reads describe, and describe can overstate it.** Some fields report not nillable and
  not defaulted yet are filled by the platform (qb-billing's `BillingTreatmentItem` fields load
  without them). Confirm on a load before adding the field; list it in `KNOWN_FINDINGS` with that
  evidence if it stands.
- **Custom fields are audited too.** A plan's `RLM_*__c` column is checked against the org it was
  captured on, so capture on an org with the plan's metadata deployed (the feature flags in step 1).
- **The snapshot holds no Ids or org identity**, only describe attributes. Some picklists list org
  records by Id (`DocumentClauseSet.Category`; `ProcedurePlanDefinitionVersion.ContextDefinition`
  lists custom context definitions by Id beside the standard ones). The snapshot drops those values
  (an 18-character Id is recognised by its case checksum, so object names such as
  `Pricebook2Share` stay), marks the field `orgValues`, and the audit doesn't value-check it.
- **`required` assumes a creating declaration creates.** An Upsert that only fills a few
  fields on records another plan created is flagged for every required field it leaves out. List it
  in `KNOWN_FINDINGS` with that reason rather than adding columns.
- **A feature-complete build can fail on the plans you are auditing.** The 264 run's `clm_data`
  build failed at `prepare_clm` (qb-clm, todo 346). Record the failure as a finding, advance the
  harness checkpoint past the step (`checkpoint.json`: `failed_step` null, `last_successful_step`
  the failed step) and `harness.py resume`, so the remaining plans load and are audited.
- **mfg-only objects** (AAF, rebates) aren't on a qb build. Merge a snapshot from an org that has them,
  or they stay under *Objects not in the describe*.
- **SFDMU's polymorphic `Field$Type`** (`AssignedToId$User`) is checked as `Field`.
- **An unsupported `sourceRecordsFilter`** (`Name IN (...)`) exits 2 rather than skipping the declaration; rewrite it as `[col] LIKE`, `=` or `<>`.
- **`--plans` and a feature-incomplete org:** an allowlist entry for an object the describe lacks is never reported stale, since it wasn't checked.

## 264 run (todo 321)

Fresh `ent-sb0` qb build with `clm_data`, `inapp` and `quote_est_tax` on; 135 objects. 15 gating
findings, all triaged into `KNOWN_FINDINGS`:
- `AttributePicklist.Code` in four pcm plans and the PRM deal fields (todo 345);
- qb-clm's `DocumentClauseSet.Category` and `ReferenceRecordAccessType` (todo 346);
- four in mfg-guidedselling (the mfg rebase list, todo 332);
- qb-accounting's `BillingBatchFilterCriteria` externalId (`JournalEntryRuleName`, copied from the previous object; todo 341).

Seven mfg-aaf/mfg-rebates objects weren't in the describe.

## Related

- `scripts/erd/schema_diff/` — the release schema snapshots and diffs this reads for new fields.
- `.cursor/skills/sfdmu-data-plans/SKILL.md` — the plan rules; `validate_sfdmu_v5_datasets.py` checks
  them offline, without a describe.
- `scripts/ai/check_sfdmu_layering.py` — the cross-plan layering gate whose plan and CSV helpers the
  audit reuses.
