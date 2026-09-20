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

## Changing the contract mid-run

Editing the contract after builders have started invalidates their output. Stop the wave, edit, then re-launch the affected builders. The Integrator compares each dataset against the current contract and reports drift.
