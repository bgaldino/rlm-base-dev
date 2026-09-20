# SKU Contract — schema

The SKU contract is the single shared interface for the multi-agent customer demo onboarding flow. The conductor writes it once after the user confirms the product vision; every domain builder reads it and writes only its own dataset directory.

- **Example:** [`datasets/sfdmu/customer-template/en-US/sku-contract.example.yaml`](../../datasets/sfdmu/customer-template/en-US/sku-contract.example.yaml)
- **Working path:** `datasets/sfdmu/customer-template/en-US/sku-contract.yaml`
- **Orchestration:** [`.cursor/skills/rlm-customer-demo-conductor/SKILL.md`](../../.cursor/skills/rlm-customer-demo-conductor/SKILL.md)

## Why it exists

Domain builders run in parallel as separate subagents. They do not share a conversation, so they cannot negotiate SKU names, selling models, or category codes at runtime. Without a frozen contract, the rates builder picks one `ProductSellingModel` and the pricebook picks another — the exact mismatch called out in [`customer-template-rate-card-entry.md`](customer-template-rate-card-entry.md).

The contract makes every cross-domain value a read, not a decision.

## Ownership

One writer per path. Builders never edit files outside their own column.

| Section | Written by | Consumed by |
|---|---|---|
| `customer`, `flags`, `categories`, `skus`, `bundles`, `attributes`, `pricing_rules`, `uom`, `usage`, `dro`, `experience` | Conductor (Contract Author) | all builders |
| `org` + `org-context.json` | Org Discovery | all builders |

## Field reference

### `customer`

| Field | Rule |
|---|---|
| `name` | Display name. |
| `prefix` | Org-unique. Scopes `AttributeDefinition.DeveloperName`, `AttributeBasedAdjRule.Name`, PFDR/PFS names, and every scoped Apex delete (`WHERE Name LIKE 'ACME-%'`). |
| `website` | Research source; optional after the vision gate. |

### `flags`

Mirror the CumulusCI `project → custom` flags. They gate which builders launch at all: `customer_demo_usage`, `customer_demo_dro`, `customer_demo_branding`.

### `catalog`

`name` and `code` for the `ProductCatalog` row the PCM builder creates. Without it the PCM
builder has to invent a catalog name, which then disagrees with anything referencing it.

### `billing`

`legal_entity`, `payment_terms`, and `policies` are what the Billing builder needs to create
`LegalEntity`, `PaymentTerm`/`PaymentTermItem`, and the `BillingPolicy` /
`BillingTreatment` / `BillingTreatmentItem` chain. Every `skus[].billing_policy_name` must
appear in `billing.policies[].name` — otherwise the Product2 billing assignment points at a
policy that was never created, and the load reports a misleading "Same data" success.

All three billing objects load as `Draft`; `activate_customer_demo_billing` promotes them.

### `org`

`alias` is the CCI/sf org alias. `context_file` points at the Org Discovery snapshot (`org-context.json`) holding real org values: available `ProductSellingModel` names and types, `UnitOfMeasure` codes, existing grant policy names, `FulfillmentStepDefinitionGroup` names, `ProrationPolicy` names. **Builders read org facts from this file. They do not invent them and do not re-query.**

### `skus`

This list projects 1:1 onto [`scripts/customer-demo/customer-pricebook-entries.csv`](../../scripts/customer-demo/customer-pricebook-entries.csv):

| Contract field | CSV column |
|---|---|
| `sku` | `SKU` |
| `unit_price` | `UnitPrice` |
| `currency` | `CurrencyIsoCode` |
| `psm_name` | `PSMName` |
| `psm_selling_model_type` | `PSMSellingModelType` |
| — (always `true`) | `IsActive` |
| `category_code` | `CategoryCode` |
| `image_required` | `ImageRequired` |
| `billing_required` | `BillingRequired` |
| `billing_policy_name` | `BillingPolicyName` |
| `product_type_expected` | `ProductTypeExpected` |
| `expected_pricing_rules` | `ExpectedPricingRules` |

Constraints the Integrator enforces:

- `type` is `Bundle` only for parent bundle SKUs; blank for everything else.
- `configure_during_sale: Allowed` is required when `type: Bundle` **or** the SKU appears in `attributes.definitions[].applies_to_skus`.
- `category_code` must be non-empty and exist in `categories`, or `customer_demo_verify_catalog` reports a missing `ProductCategoryProduct` on every row.
- `psm_name` + `psm_selling_model_type` must exist in `org-context.json`.
- `usage.role` is `sellable`, `definition`, or `none`. Sellable usage SKUs carry `usage_model_type: Anchor`; `Pack` breaks `ProductUsageResourcePolicy`.

### `attributes`

`picklists[].values[].code` is a **global** externalId across every picklist in the org — always prefix it. `definitions[].developer_name` is org-unique and must carry the customer prefix.

### `pricing_rules`

Drives both the SFDMU `AttributeBasedAdjRule` load and the Apex `AttributeAdjustmentCondition` + `AttributeBasedAdjustment` insert. `operator` is the word `equals`. The count of rules per SKU must equal that SKU's `expected_pricing_rules`.

### `uom`, `usage`, `dro`, `experience`

Read only when the matching flag is true. Two hard rules:

- `usage.grant_policies` must name policies that **already exist** in the org — SFDMU silently fails to create `UsageGrantRenewalPolicy`, `UsageGrantRolloverPolicy`, and `UsageOveragePolicy`.
- `dro.scenarios[].step_group` must be a name read from `org-context.json`. A wrong name makes SFDMU set `FulfillmentStepDefnGroupId = null` with no error and an empty Fulfillment tab.

## Validation

```bash
python scripts/customer-demo/validate_sku_contract.py [contract.yaml] [--org-context org-context.json]
python scripts/customer-demo/validate_sku_contract.py --emit-pricebook > scripts/customer-demo/customer-pricebook-entries.csv
```

Checks the mechanical half of the Integrator's list: selling model existence and type,
category coverage, `ConfigureDuringSale` on bundle and attribute SKUs, `ProductTypeExpected`
agreement, pricing rule counts and `equals` operator, globally unique
`AttributePicklistValue.Code`, prefixed `AttributeDefinition.DeveloperName`, billing policy
and payment term resolution, `Anchor` on sellable usage SKUs, usage resource UOM stitching,
grant policies present in the org, Base vs Tier rate card shape, `RateCardEntry` selling
model agreement with the pricebook, and DRO step group existence.

Org-dependent checks are skipped when `org-context.json` is missing or reports
`"reachable": false`; everything else still runs. Requires PyYAML — use the CumulusCI
interpreter if the system `python3` lacks it.

## UOM declaration semantics

In `uom.units`, a unit with a `class_code` is **created** by the PCM builder. A unit with an
empty `class_code` (e.g. `EACH`) is a **reference** to an org-native UOM and must already
exist. The validator enforces only the latter against the org.

## Changing the contract mid-run

Editing the contract after builders have started invalidates their output. Stop the wave, edit, then re-launch the affected builders. The Integrator compares each dataset against the current contract and reports drift.
