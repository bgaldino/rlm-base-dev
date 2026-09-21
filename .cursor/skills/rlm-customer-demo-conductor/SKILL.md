---
name: rlm-customer-demo-conductor
description: >-
  Orchestrates Revenue Cloud customer demo product onboarding as a multi-agent flow:
  intake, parallel research + org discovery, human vision gate, SKU contract authoring,
  parallel domain builders (PCM, billing, pricing, usage/rates, DRO, experience),
  series integration and SFDMU lint, human deploy gate, then prepare_customer_demo_catalog
  and verification. Use when a user asks to set up, onboard, or build products for a
  customer demonstration, demo catalog, or demo org, or mentions customer-template
  datasets, prepare_customer_demo_catalog, or a customer demo product vision.
---

# Customer demo onboarding — conductor

You are the conductor. You own the conversation, the human gates, and the CumulusCI
command. You do **not** author domain CSVs — specialists do, launched via the Task tool.

Full architecture: [reference.md](reference.md) (launch prompt templates, wave tables).
Contract schema: `docs/references/customer-demo-sku-contract.md`.

## Non-negotiable gates

1. **Vision gate** — no file is written until the user confirms the product vision.
2. **Deploy gate** — no `cci`, `sf sfdmu`, or `sf project deploy` runs without explicit approval.

### Activating the gate hook (optional)

`.cursor/hooks/onboarding-gate.sh` enforces the deploy gate mechanically, but only while
`.cursor/onboarding-gates.json` exists — otherwise normal repo work would be gated too.

```bash
cp .cursor/onboarding-gates.example.json .cursor/onboarding-gates.json   # Wave 0
```

Set `visionConfirmed: true` at Wave 2 and `deployApproved: true` at Wave 6. Delete the file
when the run finishes. Read-only `sf data query` is never gated.

## Wave 0 — intake (series)

On onboarding intent, ask for **either** a company description **or** a website URL.
Then collect, in the same turn:

- services, pricing motion, recurring vs one-time, add-ons, known SKUs
- billing expectations (payment terms, policy intent)
- whether usage metering, DRO, and branding are in scope (these set the flags)
- target org alias, and a logo URL/path if images are wanted
- **whether the org is dedicated to this customer or shared with other demos** — this sets
  `org.load_mode` and decides which flow runs at Wave 6

Do not proceed to research without at least a description or URL.

Do not take the user's word on dedicated-vs-shared. Org Discovery answers it in Wave 1 by
counting foreign demo SKUs; most "clean" demo orgs turn out to hold two or three older
customer catalogs.

## Wave 1 — research + org discovery (parallel)

Launch both in a single message. Neither writes into `datasets/`.

| Agent | subagent_type | Output |
|---|---|---|
| Researcher | `explore` | Draft vision: families, 3-6 categories, 10-15 SKUs, selling models, bundles, attributes, pricing, billing, image coverage |
| Org Discovery | `explore` | `datasets/sfdmu/customer-template/en-US/org-context.json` |

Org Discovery runs read-only SOQL once so builders never re-query. Use the **sf username**,
not the CCI org name — `sf data query --target-org` does not resolve CCI aliases.

Reference data the builders consume:

```bash
sf data query -q "SELECT Name, SellingModelType FROM ProductSellingModel" --target-org <user>
sf data query -q "SELECT Name FROM ProrationPolicy" --target-org <user>
sf data query -q "SELECT Code FROM UsageGrantRenewalPolicy" --target-org <user>
sf data query -q "SELECT Code FROM UsageGrantRolloverPolicy" --target-org <user>
sf data query -q "SELECT Name FROM UsageOveragePolicy" --target-org <user>
sf data query -q "SELECT Code, Name FROM UsageResourceBillingPolicy" --target-org <user>
sf data query -q "SELECT Id, Name FROM FulfillmentStepDefinitionGroup" --target-org <user>
```

**Units of measure must be captured with their class.** A `UnitOfMeasure` belongs to exactly
one `UnitOfMeasureClass` and cannot be moved. Capturing codes alone is what let a run get as
far as proposing `CRD` for a new customer's credits, when `CRD` is named "Snowflake Credit"
and is already owned by class `SNFCRED`:

```bash
sf data query -q "SELECT UnitCode, Name, UnitOfMeasureClass.Code FROM UnitOfMeasure" --target-org <user>
sf data query -q "SELECT Code, Name FROM UnitOfMeasureClass" --target-org <user>
```

**Existing names are as important as existing reference data.** Everything below loads via
Upsert on a name or code, so a contract that reuses one of these silently overwrites a live
org record instead of creating its own:

```bash
sf data query -q "SELECT Name FROM PaymentTerm" --target-org <user>
sf data query -q "SELECT Name FROM BillingPolicy" --target-org <user>
sf data query -q "SELECT Name FROM BillingTreatment" --target-org <user>
sf data query -q "SELECT Name FROM LegalEntity" --target-org <user>
sf data query -q "SELECT Name, Code FROM ProductCatalog" --target-org <user>
sf data query -q "SELECT Code FROM ProductClassification" --target-org <user>
sf data query -q "SELECT DeveloperName FROM AttributeDefinition" --target-org <user>
sf data query -q "SELECT Code FROM AttributePicklistValue" --target-org <user>
```

**Occupied SKU prefixes** decide whether the customer prefix is usable. Sample the SKU space
and record every distinct leading token:

```bash
sf data query -q "SELECT StockKeepingUnit FROM Product2 WHERE StockKeepingUnit != null" --target-org <user>
```

Write all of it to `org-context.json` under `unitsOfMeasure[].ClassCode`, `existingNames`,
and `occupiedSkuPrefixes`. Schema: `docs/references/customer-demo-sku-contract.md`.

**Capture the snapshot before the load, once, and do not refresh it afterward.** The whole
point of `existingNames` and `occupiedSkuPrefixes` is to describe what the org held *before*
this customer existed. Re-capturing after a load fills them with the contract's own output,
at which point the collision checks are comparing the contract against itself and can no
longer see a foreign record. The validator detects that case and downgrades to
`prefix-collision-self` / `name-collision-self` so the contract still passes, but the
protection is gone until a clean pre-load snapshot exists.

If you must refresh mid-project, exclude the customer's own prefix and namespace from
`existingNames` and `occupiedSkuPrefixes` as you write them.

If no org alias is available yet, Org Discovery writes an empty snapshot and the
Integrator flags every org-dependent value as unverified.

## Wave 2 — vision gate (human, series)

Present the vision with org-verified selling models. Ask the user to confirm or adjust.
**Stop here.** Do not write the contract until they confirm.

### Choosing the customer prefix

Pick it yourself from `occupiedSkuPrefixes`; do not accept the researcher's suggestion
unchecked. The obvious abbreviation is usually the one already taken — a Salesforce run had
to use `SFDC` because `SF-` belonged to an existing Snowflake catalog in the same org.

The prefix scopes `AttributeDefinition.DeveloperName`, `AttributePicklistValue.Code`,
billing record names, PFDR/PFS names, and every scoped Apex delete. State it in the vision
so the user sees it before it is baked into 14 SKUs, and say why you picked it if the
natural choice was unavailable.

Watch for near-misses in both directions. `SFDC-` is safe alongside `SF-` because the
literal SOQL pattern `SF-%` cannot match `SFDC-FOO`, but a prefix that is a strict prefix of
an occupied one (or vice versa) makes every scoped `LIKE` ambiguous.

## Wave 3 — contract (series)

Write `datasets/sfdmu/customer-template/en-US/sku-contract.yaml`, then project its `skus`
list onto `scripts/customer-demo/customer-pricebook-entries.csv`. You do this yourself —
it is small, and a single writer prevents SKU drift.

Validate the contract before launching any builder — a bad contract multiplies across six
parallel agents:

```bash
python scripts/customer-demo/validate_sku_contract.py
python scripts/customer-demo/validate_sku_contract.py --emit-pricebook \
  > scripts/customer-demo/customer-pricebook-entries.csv
```

## Wave 4 — domain builders (parallel)

Launch every applicable builder in **one message**. Each gets its own directory; the file
ownership is disjoint, which is what makes the parallelism safe.

| Builder | Skill | Owns | Launch when |
|---|---|---|---|
| PCM | `.cursor/skills/rlm-customer-demo-pcm/SKILL.md` | `customer-template-pcm/` | always |
| Billing | `.cursor/skills/rlm-customer-demo-billing/SKILL.md` | `customer-template-billing/` + `scripts/apex/activateCustomerDemoBilling.apex` | always |
| Pricing | `.cursor/skills/rlm-customer-demo-pricing/SKILL.md` | `customer-template-pricing/` + pricing Apex | `pricing_rules` non-empty |
| Usage-Rates | `.cursor/skills/rlm-customer-demo-usage-rates/SKILL.md` | `customer-template-rating/` + `customer-template-rates/` + `scripts/apex/activateCustomerDemoRatingRecords.apex` | `customer_demo_usage` |
| DRO | `.cursor/skills/rlm-customer-demo-dro/SKILL.md` | `customer-template-dro/` | `customer_demo_dro` |
| Experience | `.cursor/skills/rlm-customer-demo-experience/SKILL.md` | `customer-template-product-images/`, static resources, branding | images or branding in scope |

Keep usage and rates in **one** agent. Splitting them drifts `ProductSellingModel` and UOM
between `RateCardEntry` and the rating plan.

### Activation Apex carries a per-customer allowlist

Two activation scripts name the current customer's records explicitly, and the owning
builder must update them every run or activation silently targets the wrong org records:

| Script | Owner | Holds |
|---|---|---|
| `activateCustomerDemoBilling.apex` | Billing | `CUSTOMER_BILLING_POLICIES` |
| `activateCustomerDemoRatingRecords.apex` | Usage-Rates | `CUSTOMER_METER_CODES` |

They are allowlists rather than broad "activate everything Draft" queries for a reason. The
broad form activated three other customers' billing stacks in a shared org, and the org-wide
rating equivalent aborts entirely on one pre-existing malformed record. Details in
`.cursor/rules/customer-demo-apex.mdc`.

Teardown scripts scoped by prefix (`deleteCustomerDemo*.apex`,
`customer-purge-and-reimport.apex`) accumulate customer prefixes rather than replacing them,
so older demos stay removable. Add the new prefix; never swap out the previous one.

Every launch prompt must carry the contract path, the org-context path, the skill path, the
allowed write glob, and an explicit "do not deploy, do not run cci or sf". Subagents cannot
see this conversation. Templates: [reference.md](reference.md).

## Wave 5 — integrate + lint (series)

Run the Integrator (`.cursor/skills/rlm-customer-demo-integrator/SKILL.md`) for
cross-dataset checks, then:

```bash
python scripts/customer-demo/validate_sku_contract.py
python scripts/validate_sfdmu_v5_datasets.py
```

All must pass before you ask to deploy. Fix by re-launching the owning builder, not by
editing another builder's files yourself.

## Wave 6 — deploy gate (human, series)

Summarize what will be created and ask for explicit approval. Then pick the flow from
`org.load_mode`:

| `load_mode` | Flow | Deletes |
|---|---|---|
| `clean` | `prepare_customer_demo_catalog` | five scoped-delete steps run |
| `additive` | `prepare_customer_demo_catalog_additive` | none |

```bash
cci flow run prepare_customer_demo_catalog_additive --org <alias>
```

The additive flow is the same steps in the same order with `customer_demo_purge_records`,
`delete_customer_demo_pricing_data`, `delete_customer_demo_rates_data`,
`delete_customer_demo_rating_data`, and `delete_customer_demo_dro_data` removed. The
trade-off is that it is **not idempotent**: seven objects load via `Insert` because SFDMU v5
cannot Upsert relationship-traversal external ids, so a second run duplicates the usage,
rate-card, and pricing-adjustment rows. Say this out loud at the gate.

Before running, confirm the `cumulusci.yml` feature flags match the contract. `customer_demo_usage`
in particular defaults to `false`, and a mismatch makes the flow skip whole waves of work
with no error.

Never reorder the flow. Never parallelize CCI or SFDMU against a single org — SFDMU holds
state per plan directory and the load order encodes FK dependencies.

`cci task run <task> --org <alias>` fails with "No such option: --org" on some CCI versions.
Use `cci org default <alias>` first, or run the flow, which passes the org correctly.

### When a step fails mid-flow

CCI has no `--skip` and no resume. Fix the cause, then either re-run the whole flow (safe
only when the completed steps are Upsert/Update/Deploy — which is true for steps 1-5 of the
additive flow) or run the remaining tasks individually with `cci task run` in flow order.

## Wave 7 — verify (series parent, parallel probes)

Run `customer_demo_verify_catalog`, then fan out read-only probes in parallel and merge:

- `ProductUsageGrant` existence per usage SKU (SFDMU v5 reports success and persists nothing)
- `ProductFulfillmentScenario` rows with `FulfillmentStepDefnGroupId = null`
- `reports/MissingParentRecordsReport.csv` in each plan directory

Report quote-test SKUs as the **sellable** usage SKUs (`*-USG-*`), never the usage-definition
SKUs. Remind the user that Lightning theme activation is manual.

## Re-runs

If a dataset already matches the current contract, skip that builder. PCM, billing, DRO, and
pricebook steps are Upsert-idempotent; rates and rating require their scoped deletes first.
