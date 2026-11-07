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
   doesn't enable is missing from the describe; it isn't audited and the run reports it as
   `object-missing` (gating; step 4 triages it).
2. **Capture the snapshot.** Read-only; it queries the API version in `api_version_active` and records it in the snapshot's metadata (a `--merge` base whose metadata records another release or version, or lacks them, is refused):
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
   the reason it stands and the todo that owns it. A `picklist` entry also lists its offending values in `TRIAGED_VALUES`; a different bad value in the same field is a new finding. A triaged value that no longer appears makes the entry stale. The run fails on any finding not listed, and on any
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
| `unknown-field` | yes | The query selects, the CSV writes (every column the declaration writes: plain, `Rel.Field`, and each part of a composite `Rel.$$A$B`; under `SELECT all` that is every CSV header not in `excludedFields`), or the `externalId` names, a field the object doesn't have, or a relationship path that doesn't resolve; only `Id` is exempt, every other system field (`LastActivityDate`, …) must be in the describe (followed through `referenceTo` where the target is in the snapshot; a target that isn't is left unchecked). SFDMU drops it and the load still succeeds |
| `picklist` | yes | A CSV value outside a restricted picklist's active values. `CurrencyIsoCode` is skipped: it is the org's currency set, not the release's. Dead columns (neither createable nor updateable, and not a key) aren't value-checked |
| `required` | yes | A creating declaration leaves out, or blanks on the rows it creates, a field that is createable, not nillable and not defaulted on create. An Upsert row whose value for this declaration's `externalId` matches a row an earlier creating pass created is only patched, so it isn't re-checked; an Insert row is always checked. Booleans are skipped (they default to false) |
| `object-missing` | yes | A plan declares an object the describe lacks, so nothing on it is audited. Triage it in `KNOWN_FINDINGS` (field `""`) with the reason, or capture a snapshot from an org that has it |
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
- **`required` reads rows, not the org.** An Upsert row counts as already created when an earlier creating
  pass of the plan loaded the same `externalId` value, whatever the org holds, and a repeat of a key in
  one pass patches the first row that passes the required check, so row order inside a CSV can decide which row is checked.
  A declaration with no `externalId` is matched on the plan's first creating declaration's key. A pass
  whose CSV lacks one of the key's columns can't be matched, either side, so its rows count as created.
  A key value is matched as written: a later pass that rewrites a key field of an existing record
  doesn't retire the value an earlier pass wrote, so a third pass keyed on the old value still counts
  as patching. For a plan that does this, run the audit on its final pass alone.
  A pass with `deleteOldData: true` clears the object's earlier rows first, so its own rows are all
  treated as created.
  A row the platform would reject for a required field (blank, or the pass doesn't load it) isn't
  persisted, so a later pass on its key re-checks it; describe can overstate `required`, in which case
  the field is in `KNOWN_FINDINGS` and the later pass's finding is the same entry.
- **`required` assumes a creating declaration creates.** An Upsert that only fills a few
  fields on records another plan created is flagged for every required field it leaves out. List it
  in `KNOWN_FINDINGS` with that reason rather than adding columns.
- **A feature-complete build can fail on the plans you are auditing.** The 264 run's `clm_data`
  build failed at `prepare_clm` (qb-clm, todo 346). Record the failure as a finding, advance the
  harness checkpoint past the step (`checkpoint.json`: `failed_step` null, `last_successful_step`
  the failed step) and `harness.py resume`, so the remaining plans load and are audited.
- **mfg-only objects** (AAF, rebates) aren't on a qb build. Merge a snapshot from an org that has them;
  until then they are triaged as `object-missing` in `KNOWN_FINDINGS`, and a new plan object the
  describe lacks fails the audit.
- **The snapshot must match the active release and API version.** `audit` exits 2 on a snapshot whose
  `metadata` records another `release` or `api_version`, or lacks either; recapture it with `snapshot`
  (a stale schema would pass plans the release breaks). A `--target-org` audit always describes at the
  active version.
- **SFDMU's polymorphic `Rel$Type`** (`Who$Contact.Name`) is resolved through that target only; an untyped polymorphic path passes if any target has the rest; a typed lookup field (`WhoId$Contact`) must reference that type. Which columns a declaration writes ignores the type (a `Who$Lead.Name` header counts as written for a query selecting `Who$Contact.Name`), and the layering checker's shared-record merge treats `Who$Contact` and `Who` as different lookups.
- **An unsupported `sourceRecordsFilter`** (`Name IN (...)`) exits 2 rather than skipping the declaration; rewrite it as `[col] LIKE`, `=` or `<>`.
- **`--plans` and a feature-incomplete org:** an allowlist entry for an object the describe lacks is never reported stale, since it wasn't checked, and an object the plan declares but the org lacks is a new gating `object-missing` finding. Conversely, a live audit on an org that has the mfg objects reports their `object-missing` entries stale until they are removed.

## 264 run (todo 321)

Fresh `ent-sb0` qb build with `clm_data`, `inapp` and `quote_est_tax` on; 135 objects. 15 gating
findings, all triaged into `KNOWN_FINDINGS`:
- `AttributePicklist.Code` in four pcm plans and the PRM deal fields (todo 345);
- qb-clm's `DocumentClauseSet.Category` and `ReferenceRecordAccessType` (todo 346);
- four in mfg-guidedselling (the mfg rebase list, todo 332);
- qb-accounting's `BillingBatchFilterCriteria` externalId (`JournalEntryRuleName`, copied from the previous object; todo 341).

Seven mfg-aaf/mfg-rebates objects weren't in the describe; they are triaged as `object-missing` (22 known entries in all).

## Related

- `scripts/erd/schema_diff/` — the release schema snapshots and diffs this reads for new fields.
- `.cursor/skills/sfdmu-data-plans/SKILL.md` — the plan rules; `validate_sfdmu_v5_datasets.py` checks
  them offline, without a describe.
- `scripts/ai/check_sfdmu_layering.py` — the cross-plan layering gate whose plan and CSV helpers the
  audit reuses.
