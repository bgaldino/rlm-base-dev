# SFDMU v5 Idempotency + Safe Data-Shape Layering

> Architecture analysis for [#232](../../232). Spun off from PR #182 review
> (`CostBookEntry` un-excluded in `qb-pricing` for PRM cost-parity, widening
> the org-wide delete set to a foundational object). Deletion scoping is
> **one** option evaluated here, not a pre-decided conclusion.

## 1. Problem statement

Several `datasets/sfdmu/**` plans use `operation: Insert` (+ `deleteOldData: true`,
or an external cleanup step) instead of `Upsert`, because SFDMU v5 cannot
reliably match records via composite `externalId`s that include relationship
traversals (see "The Five Confirmed v5 Bugs" in `AGENTS.md`). The cleanup
step that makes `Insert` idempotent — delete-then-reinsert — is currently
**shape-agnostic**: it deletes *every* record of the object type, with no
`WHERE` filtering, regardless of which plan or data shape produced it. On an
org where those object types hold records the plan didn't create, this wipes
them. The risk is proportional to how foundational the object is —
`CostBookEntry` and `PricebookEntry` are higher-stakes than QB-specific
adjustment types.

This doc surveys the current mechanisms, explains *why* full-type deletes
exist (which is not the same reason for every mechanism), and evaluates the
options in the issue against that reality.

## 2. Current state

There are **three independent full-type-delete mechanisms** in the repo, not
one. They differ in whether SFDMU v5's Upsert-matching bugs actually
constrain them — which matters a lot for what scoping is safe to add.

| Mechanism | Used by | Scoping today |
|---|---|---|
| **A. `DeleteSFDMUData`** (`tasks/rlm_sfdmu.py:424-609`) — custom Python task, hand-rolled REST `SELECT Id FROM {sobject}` + composite `DELETE` | `delete_quantumbit_pricing_data` (qb-pricing), `delete_quantumbit_prm_pricing_data` (qb-prm-pricing, currently a no-op — see §2.3) | None |
| **B. SFDMU-native `deleteOldData: true`** inline in `export.json`, executed by the `sf sfdmu run` CLI itself as part of `LoadSFDMUData` | qb-rates (`PriceBookRateCard`, `RateCardEntry`, `RateAdjustmentByTier`), qb-rating (`ProductUsageResource`, `ProductUsageResourcePolicy`, `ProductUsageGrant`) | None (no `deleteQuery` set) |
| **C. Anonymous Apex cleanup scripts** — hand-written SOQL + DML, deactivate-then-delete | `delete_qb_rates_data` → `scripts/apex/deleteQbRatesData.apex`, `delete_qb_rating_data` → `scripts/apex/deleteQbRatingData.apex` | None |

### 2.1 Mechanism A — `DeleteSFDMUData`

`tasks/rlm_sfdmu.py:424-438` docstring already states the tradeoff explicitly:
this was a **deliberate design choice**, not an oversight:

> "Shape-agnostic: no WHERE-clause filtering is applied. The full type is
> cleared regardless of which data shape populated it. The plan file is the
> authoritative definition of which object types are managed."

It reads `export.json`, collects every non-excluded `operation: Insert`
object (`rlm_sfdmu.py:508-519`), and deletes all records of each type in
reverse array order (`:526`) via `/composite/sobjects` batched deletes
(`:574-608`). No WHERE clause is possible today because it issues a bare
`SELECT Id FROM {sobject_name}` (`:550`).

**qb-pricing's current Insert set** (`datasets/sfdmu/qb/en-US/qb-pricing/export.json`,
verified directly — array order, reverse = delete order):
`PriceAdjustmentTier → AttributeAdjustmentCondition → AttributeBasedAdjustment
→ BundleBasedAdjustment → PricebookEntry → PricebookEntryDerivedPrice →
CostBookEntry`. `CostBookEntry` (line 98-101) has `excluded: false` — this is
the PR #182 change the issue references. Its `externalId` is
`CostBook.Name;Product.StockKeepingUnit;CurrencyIsoCode` — two traversal
components plus one direct field.

### 2.2 Mechanism B — SFDMU-native `deleteOldData`

`datasets/sfdmu/qb/en-US/qb-rates/export.json` and `qb-rating/export.json`
carry extensive inline `$comment*` blocks that already document, **per
object**, exactly which of the Five Bugs forced `Insert+deleteOldData`
instead of `Upsert` (e.g. qb-rating `$comment_composite_keys`,
`export.json:6`). This is some of the best in-repo bug-to-object attribution
available and should be treated as authoritative for any future Upsert
audit (§6.3).

Unlike Mechanism A, this delete runs as part of the SFDMU CLI's own load
pass — SFDMU v5 supports an optional `deleteQuery` override on any object
with `deleteOldData: true` (a native SFDMU config key, not currently used
anywhere in this repo — `grep -rn deleteQuery datasets/` returns nothing).

### 2.3 Mechanism C — Apex cleanup scripts

`scripts/apex/deleteQbRatesData.apex` and `deleteQbRatingData.apex` delete
**all** records of `RateCard`, `RateCardEntry`, `RateAdjustmentByTier`,
`PriceBookRateCard`, `ProductUsageGrant`, `ProductUsageResource(Policy)`,
`RatingFrequencyPolicy`, and 5 more usage-policy objects, with a
deactivate-before-delete pattern for anything with a `Status` field (Active
records reject direct deletion). No `WHERE` clause anywhere in either
script.

**These run *before* the same plan's own `deleteOldData: true` in Mechanism
B** — `prepare_rating` flow step 1/2 (`delete_qb_rates_data`,
`delete_qb_rating_data`) runs before step 5/6 (`insert_qb_rates_data`,
`insert_qb_rating_data`), and those `LoadSFDMUData` runs will *also* trigger
`deleteOldData` on `RateCardEntry`/`RateAdjustmentByTier`/`PriceBookRateCard`
and `ProductUsageResource`/`ProductUsageResourcePolicy`/`ProductUsageGrant`
per §2.2. The Apex step is a superset pre-clean (it also covers objects that
aren't part of the SFDMU plan at all, e.g. `RateCard` itself, `UsageResource`
policies), but the two mechanisms overlap on several objects — **both** need
scoping for a scoped-delete fix to actually bound the blast radius (this is
exactly what the deferred issue comment on this thread already concluded for
q3/qb rates+rating).

`delete_quantumbit_prm_pricing_data` (qb-prm-pricing) is currently a
**no-op**: the plan's `export.json` has zero `operation: Insert` objects
today (all `Upsert`/`Update`, see `datasets/sfdmu/qb/en-US/qb-prm-pricing/export.json`).
It exists as a standing safety mechanism for if/when an Insert object is
added to that plan, not as an active blast-radius risk today.

## 3. Why full-type delete exists (root cause, not a monolith)

Per `AGENTS.md` and the inline `$comment` blocks in qb-rates/qb-rating
`export.json`, the driving bugs are:

- **Bug 1** (all-multi-hop `externalId` fails validation) — forces a direct
  FK field into the `externalId` (e.g. PURP uses `ProductUsageResourceId`)
  *and* `deleteOldData`, since the direct field alone isn't a business key.
- **Bug 2** (2-hop traversal columns → invalid SOQL in Upsert's TARGET
  SELECT phase) — forces `Insert` (skips TARGET SELECT entirely) for any
  object whose externalId has a 2-hop component (e.g. `RateCardEntry.RateCard.Name`
  on `RateAdjustmentByTier`).
- **Bug 3** (Upsert can't match on relationship-traversal externalId, even
  1-hop — always inserts, causing duplicates) — this is the broadest bug: it
  forces `Insert+deleteOldData` for objects whose *only* natural key includes
  **any** parent traversal, 1-hop or more. Most objects in this survey hit
  this one (`PricebookEntry`, `CostBookEntry`, `ProductUsageResource`, etc.
  all have a direct field *and* a traversal in their externalId — the
  traversal alone is enough to break Upsert per Bug 3, so the presence of a
  direct field doesn't save them).

**Important distinction:** these are bugs in **SFDMU's own Upsert
target-matching logic** (its internal "TARGET SELECT" + externalId
comparison). They say nothing about hand-written SOQL. Mechanism A
(`DeleteSFDMUData`) and Mechanism C (Apex) don't go through SFDMU's Upsert
matching at all — they're plain REST/SOQL queries. **A `WHERE` clause added
to either is not subject to Bugs 1/2/3.** This is the key fact that makes
scoping viable without waiting on an SFDMU upstream fix (see §6.1).

Mechanism B's `deleteOldData` deletion phase is *SFDMU's own* delete query —
whether its optional `deleteQuery` override is itself affected by the
traversal bugs is unconfirmed (no plan in this repo uses it yet). This is
listed as an open verification item in §7.

## 4. Risk / blast-radius assessment

| Object | Mechanism | Foundational? | Notes |
|---|---|---|---|
| `CostBookEntry`, `PricebookEntry` | A | **High** — standard platform pricing objects, not QB-specific | Any org-wide `CostBook`/`Pricebook2` usage outside the QB demo dataset is at risk on every `delete_quantumbit_pricing_data` run |
| `PriceAdjustmentTier`, `AttributeAdjustmentCondition`, `AttributeBasedAdjustment`, `BundleBasedAdjustment`, `PricebookEntryDerivedPrice` | A | Medium — QB-pattern-specific but still platform objects | Lower risk only because non-QB adjustment authoring is less common on these orgs today |
| `RateCard`, `RateCardEntry`, `RateAdjustmentByTier`, `PriceBookRateCard` | B + C | Medium-High — foundational rating/pricing objects | Confirmed **not currently active** on any committed org (q3/mfg gated off); qb path is live |
| `ProductUsageGrant`, `ProductUsageResource(Policy)`, usage policies | B + C | Medium-High — foundational usage/rating objects | Same qb/q3 gating as above |

The issue's framing is correct: risk scales with how "foundational"
(non-QB-owned) the object type is, and `CostBookEntry`/`PricebookEntry` are
the sharpest current example because PR #182 just widened Mechanism A's
blast radius to include one of them.

## 5. Options evaluated

### 5.1 Scope deletions to dataset-owned rows

**Viable for Mechanisms A and C today, without any schema change**, because
(per §3) they're plain SOQL, unaffected by the Upsert-matching bugs.
`qb-prm-pricing/export.json` already establishes the pattern in this repo —
its source queries scope with `WHERE Name IN ('Apex Dynamics', 'Cloud
Distributors', 'Robot Resellers')` (`export.json:9`) and `WHERE Program.Name
IN (...)` (`:19`). The same idea — filter the delete `SELECT Id FROM X` by a
literal list or a parent-relationship match on **known QB-owned parent
record names** (`Pricebook2.Name`, `CostBook.Name`, `RateCard.Name`) — works
identically for Mechanism A/C's delete queries.

**Caveat:** this only bounds the blast radius to "records under a
QB-named parent," not to "records this specific plan run created." It's a
naming-convention control, not a strong ownership guarantee — see 5.2.

For **Mechanism B**, the equivalent is SFDMU's native `deleteQuery` override
on `deleteOldData: true` objects. This is exactly what the deferred
issue-comment on this thread already recommends for qb/q3 rates+rating.
Whether `deleteQuery` itself is subject to the traversal-matching bugs needs
a small confirmation test before relying on it (§7, open item).

### 5.2 Ownership tagging (managed marker)

A dedicated marker (custom field or a stable naming convention already
enforced at insert time) would give a *real* ownership guarantee instead of
a name-matching heuristic. Highest rigor, but it's a **data-model change**
— not a pure tooling fix — and per bgaldino's June-30 comment on this issue,
the QB/Q3 demo records aren't edition-tagged today, so this is nontrivial:
"enumerating specific names/SKUs or adding an edition marker — a data-model
change." Recommended as a **follow-up issue**, not part of the immediate fix
(§8).

### 5.3 Upsert-where-possible audit

Per §3, Bug 3 alone (not just Bug 1) forces `Insert` for essentially every
object surveyed here, because **any** traversal component in the externalId
— even a single 1-hop one — breaks Upsert matching, and every affected
object's only real-world business key includes at least one parent
traversal (e.g. `PricebookEntry` needs `Product2.StockKeepingUnit` to be
unique). Restructuring these to a pure-direct-field externalId would require
adding a synthetic unique field (e.g. a formula/text field populated at
insert time) to each object — itself a schema change with the same
data-tagging cost as 5.2, for a smaller payoff (it doesn't reduce blast
radius, only removes the delete-then-reinsert pattern). **Low priority**
relative to 5.1/5.4/5.5.

### 5.4 Per-shape isolation (separate pricebooks/cost books/rate cards)

Partially true already — QB creates specifically-named `Pricebook2`/
`CostBook`/`RateCard` parents (`Upsert` on `Name`), so shapes loaded under
different parent names don't collide at the parent level. The problem is
purely at the **child** level (`PricebookEntry`, `CostBookEntry`,
`RateCardEntry`, etc.), which the current full-type delete does not
distinguish by parent. This option and 5.1 converge: scoping the child
delete by parent name **is** per-shape isolation, implemented via a `WHERE`
filter rather than separate object types. No additional design needed beyond
5.1.

### 5.5 Guardrails on `DeleteSFDMUData` (and the Apex/Mechanism-B paths)

Independent of scoping, and cheapest to ship immediately:

- **Org-type gating** — `org_config.org_type` is already used elsewhere in
  this repo for edition detection (`AGENTS.md` → Edition flags); the same
  property can gate `DeleteSFDMUData`/`delete_qb_rates_data`/
  `delete_qb_rating_data` to scratch/demo org types only, refusing to run
  (or requiring an explicit override flag) against a persistent/production-like
  org.
- **Dry-run / simulate** — log record counts per object without issuing the
  DELETE, mirroring `LoadSFDMUData`'s existing `simulation: true` option
  (`rlm_sfdmu.py:390-391`).
- **Max-rows safety cap** — abort (or require `--force`) if a query returns
  more records than a sane demo-data ceiling, catching the "this org has
  real production-scale data in this object" case even without ownership
  scoping.

These don't require a data-model change and directly reduce risk on every
plan using Mechanism A/B/C today, including ones not otherwise addressed by
this analysis.

### 5.6 `deleteOldData` ordering vs. external delete-step trade-offs

Already correctly handled today: `AGENTS.md` documents the parent→child
array-order rule, and both qb-rates/qb-rating `export.json` comments confirm
the reverse-order deletion satisfies FK constraints (§2.2). No open problem
here — noted for completeness since the issue asked for it to be weighed.

## 6. Recommendation

Layer the fixes by cost and rigor rather than picking one option:

1. **Ship now (this issue's own follow-up, tooling-only, no data-model
   change):** guardrails (5.5) on `DeleteSFDMUData` and the Apex cleanup
   tasks — org-type gating, dry-run, max-rows cap. Directly de-risks every
   plan using Mechanisms A/B/C today, independent of everything else.
2. **Ship next (tooling + literal-list scoping, no schema change):** extend
   `DeleteSFDMUData` to accept an optional per-object scoping filter (e.g. a
   `deleteWhere` key read from `export.json`, mirrored in the Apex scripts as
   `WHERE Pricebook2.Name IN (...)` / `WHERE RateCard.Name IN (...)` /
   `WHERE Product.StockKeepingUnit IN (...)`), sourced from the same literal
   list pattern `qb-prm-pricing/export.json` already uses. Apply to
   `CostBookEntry`/`PricebookEntry` first (highest current risk per §4),
   then qb-rates/qb-rating (§8). This is 5.1 + 5.4, requires no field
   additions, and is backward-compatible (omit the key → today's unscoped
   behavior, so plans not yet audited keep working).
3. **Confirm before relying on it:** whether SFDMU v5's `deleteQuery`
   override (Mechanism B) is itself subject to the traversal-matching bugs —
   a small isolated test against qb-rates' `RateCardEntry` object is enough
   to answer this (§7).
4. **Longer-term, separate issue (data-model change):** ownership/edition
   tagging (5.2) for a real guarantee instead of name-matching, if/when QB/Q3
   coexistence on the same org becomes a real scenario (today it's gated off
   — see §8). The Upsert-restoration audit (5.3) is lower priority — it
   doesn't reduce blast radius and carries the same schema cost as 5.2.

## 7. Open verification items

- Does SFDMU v5's `deleteQuery` override (used with `deleteOldData: true`)
  correctly handle a `WHERE` clause referencing the same relationship-path
  fields that break Upsert matching (Bugs 2/3)? Untested in this repo.
  Needed before scoping Mechanism B (qb-rates/qb-rating inline
  `deleteOldData`) the same way as Mechanism A.
- Confirm `delete_quantumbit_prm_pricing_data` stays a no-op (§2.3) as
  `qb-prm-pricing/export.json` evolves — if an `Insert` object is ever added
  there, it inherits the same unscoped-by-default risk and should get
  scoping applied at the same time, not after the fact.

## 8. qb/q3 rating+rates blanket cleanup (deferred item, carried from this
   issue's June-30 comment)

Captured here for completeness — this is the concrete instance of §5.1/§5.4
for the rating/rates domain, already scoped by bgaldino's comment on this
issue:

- **Targets:** `scripts/apex/deleteQbRatesData.apex`, `deleteQbRatingData.apex`
  (Mechanism C), and the inline `deleteOldData` blocks in qb-rates/qb-rating
  `export.json` (Mechanism B) — **both** need scoping, for **both** qb and
  q3 (q3 mirrors qb's pattern; q3-rates/q3-rating currently use `Upsert`
  throughout with no `deleteOldData`, so today's actual risk is
  qb-only, but a fix should cover both to avoid the same trap re-appearing
  when q3 goes active).
- **Why deferred rather than a quick fix:** the demo records aren't
  edition-tagged (q3 rate cards/SKUs aren't marked `q3`), so real
  "plan-owned" scoping needs either a literal name/SKU list (5.1 — doable
  now) or an edition marker (5.2 — data-model change).
- **Currently safe:** q3/mfg are not active on any committed org, and the
  qb/q3 mutual-exclusivity guard in `prepare_rating` (q3 tasks only run when
  `project_config.project__custom__q3` is set, which excludes `qb`'s own
  path being simultaneously live in the same run) prevents coexistence
  collisions today.
- **Action when taken up:** apply recommendation #2 (§6) — literal-list
  `WHERE`/`deleteQuery` scoping — to both the Apex scripts and the
  export.json `deleteOldData` blocks, for qb and q3 together, before any
  q3/mfg org goes active.

## 9. Suggested follow-up issues

Not created as part of this analysis (scope of this issue was investigation
+ design doc) — recommended for the user to open, matching §6:

1. **Guardrails on destructive SFDMU cleanup tasks** — org-type gating,
   dry-run, max-rows cap for `DeleteSFDMUData` + `delete_qb_rates_data` +
   `delete_qb_rating_data` (§5.5, §6.1).
2. **Scope `qb-pricing`/`qb-prm-pricing` deletes to dataset-owned parents**
   — add `deleteWhere`/literal-list scoping to `DeleteSFDMUData`, applied
   first to `CostBookEntry`/`PricebookEntry` (§4, §6.2).
3. **Scope qb/q3 rating+rates blanket cleanup** — Apex scripts +
   `deleteOldData` export.json blocks, both editions, before q3/mfg goes
   active (§8).
4. **Confirm SFDMU v5 `deleteQuery` behavior under traversal externalIds** —
   small isolated test, blocks issue 3's Mechanism-B half (§7).
5. *(Lower priority, separate track)* **Ownership/edition tagging for QB/Q3
   demo data** — data-model change, only needed if QB/Q3 coexistence on one
   org becomes a real requirement (§5.2, §6.4).
