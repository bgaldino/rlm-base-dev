# SFDMU Data-Shape Layering and Reload Safety

How the SFDMU data plans divide records between data shapes, how a plan reloads into a
built org without deleting anything, how to add a new shape, and the guardrails on the
destructive tasks that remain. This is the design record for the reload-safe conversions
of the qb pricing, rates and rating plans (PRs #659, #662) and the q3 plans (#666, #670,
#671). Plan-authoring rules live in the
[sfdmu-data-plans skill](../../.cursor/skills/sfdmu-data-plans/SKILL.md); this page explains
the model behind them.

## The problem this solved

Until late 2026 the pricing, rates and rating plans **deleted every record of a type and
re-inserted it** on each load. That worked on a fresh org and failed on a built one, because
the platform refuses most of those deletes once the org has activity:

| Object | Delete or rewrite blocked by |
|---|---|
| `PriceAdjustmentTier` | any write while its schedule is active |
| `AttributeAdjustmentCondition` | not deletable through the API at all |
| `PricebookEntry` | quote lines that reference it |
| `ProductUsageResource`, `ProductUsageGrant` | Active status |
| `RateCardEntry` | Active status, and `AssetRateCardEntry` records that reference it |

A failed delete left the old row in place, and the re-insert then created a duplicate or was
rejected. A reload could also do damage: an unscoped `deleteOldData` on qb-rating stripped every
policy from the Active usage resources. And because a reload was unsafe, a second data shape
couldn't safely be layered on an org that already had one.

These are platform rules, not SFDMU defects, so better-scoped deletes alone could not fix them.
The fix was to **stop deleting**: match existing rows on a stable key and update them in place.

## The model

### 1. A converted plan matches; it never deletes

In a converted plan, each writable object is `Upsert` (or `Update`) on an externalId that identifies the record
across orgs. A reload finds the existing row and updates it, or inserts it if it's missing.
The SFDMU v5.6.4 floor makes this possible for relationship-traversal keys (the historical
Upsert-matching bugs are fixed upstream; only Bug 4, `$$` in a lookup column, is still live).

The key must be **unique within what the object's query selects**. Where a natural key
collides, the key gains the part that disambiguates it:

- A plan whose `PricebookEntry` rows span more than one price book keys on the book too
  (q3-pricing, which loads the standard and Nonprofit books). The same SKU, selling model
  and currency exists in both, so without it an Upsert matches the other book's entry.
  qb-pricing scopes its query to the standard book and needs no book part.
- `RateCardEntry` in q3-rates keys on `ProductSellingModel.Name` too.
- A composite `$$` value drops its empty parts (`A;B;0`, not `A;B;0;`), as SFDMU builds
  the target key. A source value that keeps one never matches and duplicates on every
  reload.

### 2. Status is never sent to an existing record

Many RLM design-time objects can't be deleted while Active. Sending `Status` on update either
fails (`ProductUsageResource` rejects Active → Draft) or silently demotes the record
(`ProductUsageGrant`). Each object with a `Status` gets two passes:

1. **Pass 1:** `Upsert` + `skipExistingRecords: true` with the full CSV (Status = Draft).
   It inserts missing rows and never touches existing ones.
2. **Pass 2:** `Update` with `Status` removed from the query and from its
   `objectset_source/object-set-2/` CSV, so corrections to every other field still land.

Activation stays in Apex (`activate_rating_records`, `activate_rates`), which acts only on
non-Active records. `excludedFromUpdateFields` is not a substitute: in SFDMU 5.8.0 it strips
the field from inserts too.

### 3. Every lookup's parent is declared in every pass

An `Update` row whose lookup target isn't declared in the same pass is sent with that lookup
**null**. Each pass declares the parent, `Readonly` with no CSV if nothing else.

### 4. A child that can only match on its parent's composite key gets its own plan

On SFDMU 5.8.0 a child keyed on its parent's composite traversal key can't be matched
(upstream #1218). The child matches on the direct lookup instead, in a separate plan that
runs after the parent's: `qb-rating-entitlements` and `q3-rating-entitlements`. A
`parent_id_lookups.json` lets `LoadSFDMUData` resolve the target org's Ids from the CSV's
portable key columns into a temporary copy, and extraction turns them back into keys.
Tracked CSVs never carry Ids.

### 5. One object's rows can be split across passes

Some rows can't load in the same batch as others. Custom price book entries need their standard
entry to exist first (`STANDARD_PRICE_NOT_DEFINED`). The object is declared once per pass, and
each declaration's `sourceRecordsFilter` picks its rows from the one CSV. A `WHERE` in the query
scopes only the target, never CSV rows. Extraction merges such declarations back into one.

## Shape ownership

A **data shape** is a set of plans that seeds one demo dataset: qb (QuantumBit), q3, mfg, and
the qb/ja locale. The rule is that **a record has exactly one owning plan**. Other plans may
reference it, but only as `Readonly`.

**Two exceptions are written by every shape that uses them: price adjustment schedules and
currency types.** For both, the last load wins on shared fields.

Price adjustment schedules:

- **Platform-seeded:** on a USD-corporate org, three USD schedules, one per `ScheduleType`:
  'Standard Attribute Based Adjustment', 'Standard Bundle Based Adjustment', and 'Standard
  Price Adjustment Tier', which is the Volume type.
- **qb-pricing and q3-pricing** upsert the ones they use on `Name`. Even the first load matches
  the seeded record, so nothing is duplicated.
- **q3 adds two of its own:** 'Standard Tier Based Adjustment' and 'Standard Volume Based
  Adjustment'.
- **mfg-pricing** updates on `Name`. Its Tier Based row exists only after a q3 load. Without
  one, it matches nothing and doesn't load, because an `Update` never inserts.
- **qb/ja** updates on `Name;CurrencyIsoCode`. Its USD Price Adjustment Tier row matches the
  seeded one. Its three JPY rows match nothing, so they don't load either.
- **`EffectiveFrom`** ranges from 2023-01-01 (qb) to 2025-10-01 (qb/ja) across the shapes.

Currency types:

- **Every pricing plan upserts them on `IsoCode`,** so shared codes such as USD, EUR and JPY
  are written by each shape.
- **`ConversionRate` differs by shape.** CAD is 1.408989 in qb, 1.42 in q3 and 1.36 in mfg.
- **qb/ja's rates are on a JPY base.** JPY is the corporate currency and USD is 0.00663.
  qb/ja assumes a JPY-corporate org. Its rates are wrong on a USD-corporate org, and the other
  shapes' rates are wrong on a JPY-corporate one.

| Records | Owner | Other shapes |
|---|---|---|
| Legal entities, tax engine, tax treatments and policies | qb-tax | q3-tax maps the q3 products onto them |
| Accounting periods, billing policies and treatments, GL accounts, payment terms | qb-billing | q3-billing maps the q3 products onto them |
| Price adjustment schedules | platform-seeded; qb-pricing and q3-pricing upsert, and q3 adds two (above) | mfg-pricing and qb/ja still `Update` them |
| Currency types | every shape's pricing plan, on `IsoCode` (above) | a shape that adds a currency adds its prices too |
| Products, price book entries, rates, usage resources | the shape's own pcm, pricing, rates and rating plans, keyed on the shape's SKUs | |

Apart from those two, shapes don't collide because their keys don't: each shape's SKUs are
distinct, and shared design records (tax, billing) have a single owner. A shape that needs a
shared record references it by name rather than shipping its own copy. q3 used to carry its
own tax and billing objects, including two legal entities under qb's names with Canada in USD
rather than qb's CAD. They could not coexist with qb's, because a legal entity's currency can't
be changed.

**Shape-specific mapping plans.** When a shape reuses another shape's design records, its own
plan shrinks to a `Product2` `Update` that points its products at them, plus a `Readonly`
declaration of the referenced object (q3-tax, q3-billing). The same holds when the source org
has no design to copy: q3-dro only sets the products' decomposition fields, because the q3
source org has no fulfillment design and qb-dro's references QB SKUs.

**Extraction alignment.** A variant shape's extraction is aligned to its qb/en-US sibling's CSV
columns. A plan that keys an object differently from qb lists it in `$ownSchemaObjects`, so
alignment doesn't drop the extra key part.

## Adding a shape

1. **Decide what the shape owns and what it reuses.** Reuse a design another shape owns
   (tax, billing) whenever it fits, and map onto it, as q3 does. Give new owned records keys
   that can't collide with another shape's (distinct SKUs, distinct names).
2. **Author each plan by the model above.** That means stable-key `Upsert`, two passes for
   Status objects, parents declared in every pass, a separate plan where a child can only
   match its parent's composite key, and no `Insert` or `deleteOldData`.
3. **Gate the plans on the shape's flag** in `cumulusci.yml`, and give each one a
   `test_<shape>_<plan>_idempotency` task.
4. **If the shape reuses another's design, load that design on this shape's builds too.**
   `insert_tax_data` runs for qb or q3, for example. Check every later step that resolves
   records by name (Billing Settings, sequence policies) against what the build actually
   loaded.
5. **Verify on a fresh build of the shape.** The checks are no rejected rows, each plan
   reloaded twice with 0 diff, every idempotency task passing, and one correction per
   object that lands.
6. **Keep the validator's empty-CSV deferral list shrinking.** A new shape adds no
   header-only CSVs; an object with no data is left out of the plan.

## Destructive operations that remain

| Operation | Status | Guardrail |
|---|---|---|
| `delete_quantumbit_pricing_data`, `delete_q3_pricing_data` | manual full teardown only; no flow runs them | deletes every record of the plan's pricing types, org-wide |
| `delete_qb_rates_data`, `delete_q3_rates_data`, `delete_qb_rating_data`, `delete_q3_rating_data` | manual full teardown only; no flow runs them | Apex that deactivates Active records first, then deletes in dependency order |
| qb-dro `FulfillmentWorkspaceItem` | `Upsert` + `deleteOldData: true` in a flow plan | a pre-5.6.4 workaround; dropping it needs live verification and owner approval |
| mfg plans | 11 `Insert` or `deleteOldData` declarations across mfg-aaf, mfg-configflow, mfg-dro and mfg-pricing | converted with the mfg series (todo 111) |
| qb/ja qb-pricing | 7 `Insert` declarations, 6 of them live (one is `excluded`) | brought up to the en-US plan in the qb/ja refresh (todo 212) |

The rules for anything that stays destructive:

- **No `Insert` + `deleteOldData` change without explicit owner approval, per object**
  (AGENTS.md). Cite a current reason Upsert can't work; the fixed historical bugs don't count.
- **Scope any delete that must stay.** A per-object `deleteQuery` limits `deleteOldData` to the
  rows it selects; qb-rating used `WHERE Status != 'Active'` before it moved to matching.
- **Teardown tasks stay out of flows.** A flow reloads in place. A full teardown is a deliberate,
  manual step on a disposable org.
- **A rejected row fails the load** (`fail_on_row_errors`, default on). A plan that rejects rows
  on a fresh build today lists each object in `ignore_row_errors_for`. The task accepts a bare
  object name, but use the mapping form, `{Object: "expected error substring"}`, with a comment
  saying why. A rejection is then ignored only if every error contains the substring, so a new
  kind still fails.

## Options considered and rejected

- **Scoped deletes instead of matching.** The July 2026 analysis (issue #232) proposed
  WHERE-scoped deletes and literal-list scoping. They don't get past the platform rules above:
  an Active, referenced or undeletable record still can't be deleted, however narrow the delete.
- **Ownership tags on records** (a custom field naming the owning shape). It needs a schema
  change on every object and a field on every CSV. Distinct keys and single ownership give
  the same separation without either.
- **`excludedFromUpdateFields` for Status.** It strips the field from inserts too in 5.8.0.
- **A schema field to key children** (tried as option T3 on a test org). It removes the
  separate entitlements plan, but needs a custom field on a standard object. The Id-lookup
  pre-step (T1) needs no schema change and retires by deleting a step once upstream #1218 is
  fixed.

## Verification record

| Plans | Verified on | Result |
|---|---|---|
| qb-rating, qb-rating-entitlements | built `ent-sb0` scratch orgs, 2026-10-30 to 11-02 | 0 diff on reload; Active records untouched |
| qb-pricing, qb-rates | a fresh `ent-sb0` build, 2026-11-02 | 0 diff; idempotency tasks pass |
| every q3 plan | two fresh `ent-sb0` q3 builds, 2026-11-03 | no rejected rows; all 8 `test_q3_*` idempotency tasks pass |
| qb-tax and qb-billing, with the q3 mapping plans | fresh `ent-sb0` q3 and qb builds, 2026-11-03 | Billing Settings deploys on q3; qb tax and billing idempotency pass |
