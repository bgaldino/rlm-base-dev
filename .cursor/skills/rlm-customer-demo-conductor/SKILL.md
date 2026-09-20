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

Do not proceed to research without at least a description or URL.

## Wave 1 — research + org discovery (parallel)

Launch both in a single message. Neither writes into `datasets/`.

| Agent | subagent_type | Output |
|---|---|---|
| Researcher | `explore` | Draft vision: families, 3-6 categories, 10-15 SKUs, selling models, bundles, attributes, pricing, billing, image coverage |
| Org Discovery | `explore` | `datasets/sfdmu/customer-template/en-US/org-context.json` |

Org Discovery runs read-only SOQL once so builders never re-query:

```bash
sf data query -q "SELECT Name, SellingModelType FROM ProductSellingModel" --target-org <alias>
sf data query -q "SELECT UnitCode, Name FROM UnitOfMeasure" --target-org <alias>
sf data query -q "SELECT Name FROM ProrationPolicy" --target-org <alias>
sf data query -q "SELECT Code FROM UsageGrantRenewalPolicy" --target-org <alias>
sf data query -q "SELECT Code FROM UsageGrantRolloverPolicy" --target-org <alias>
sf data query -q "SELECT Name FROM UsageOveragePolicy" --target-org <alias>
sf data query -q "SELECT Id, Name FROM FulfillmentStepDefinitionGroup" --target-org <alias>
```

If no org alias is available yet, Org Discovery writes an empty snapshot and the
Integrator flags every org-dependent value as unverified.

## Wave 2 — vision gate (human, series)

Present the vision with org-verified selling models. Ask the user to confirm or adjust.
**Stop here.** Do not write the contract until they confirm.

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
| Billing | `.cursor/skills/rlm-customer-demo-billing/SKILL.md` | `customer-template-billing/` | always |
| Pricing | `.cursor/skills/rlm-customer-demo-pricing/SKILL.md` | `customer-template-pricing/` + pricing Apex | `pricing_rules` non-empty |
| Usage-Rates | `.cursor/skills/rlm-customer-demo-usage-rates/SKILL.md` | `customer-template-rating/` + `customer-template-rates/` | `customer_demo_usage` |
| DRO | `.cursor/skills/rlm-customer-demo-dro/SKILL.md` | `customer-template-dro/` | `customer_demo_dro` |
| Experience | `.cursor/skills/rlm-customer-demo-experience/SKILL.md` | `customer-template-product-images/`, static resources, branding | images or branding in scope |

Keep usage and rates in **one** agent. Splitting them drifts `ProductSellingModel` and UOM
between `RateCardEntry` and the rating plan.

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

Summarize what will be created and ask for explicit approval. Only then:

```bash
cci flow run prepare_customer_demo_catalog --org <alias>
```

Never reorder the flow. Never parallelize CCI or SFDMU against a single org — SFDMU holds
state per plan directory and the load order encodes FK dependencies.

`cci task run <task> --org <alias>` fails with "No such option: --org" on some CCI versions.
Use `cci org default <alias>` first, or run the flow, which passes the org correctly.

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
