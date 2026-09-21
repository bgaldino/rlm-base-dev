# Agent Operating Rules

## Customer Demo Product Onboarding UX

When a user asks to set up, onboard, or build products for a customer demonstration, you are
the **conductor** of a multi-agent flow. Read
[`.cursor/skills/rlm-customer-demo-conductor/SKILL.md`](.cursor/skills/rlm-customer-demo-conductor/SKILL.md)
and follow it. This section is the contract that skill implements; the skill holds the
operational detail.

Domain pitfalls (SFDMU shapes, Apex constraints, org quirks) intentionally live in the
specialist skills and in file-scoped rules under [`.cursor/rules/`](.cursor/rules/), not here.
Loading them all into every conversation is what this architecture exists to avoid.

### The two hard gates

1. **Vision gate** — do not create or modify any file until the user confirms the product
   vision.
2. **Deploy gate** — do not run deployment or import steps (`cci`, `sf sfdmu`,
   `sf project deploy`) without explicit user approval.

### Flow

| Wave | Mode | What happens |
|---|---|---|
| 0 Intake | series | Ask for a company description **or** website URL. Also collect services, pricing motion, recurring vs one-time, add-ons, known SKUs, billing expectations, image/logo preferences, target org alias, whether usage metering, DRO, and branding are in scope, and whether the org is dedicated or shared with other demos. |
| 1 Research + Org Discovery | **parallel** | Researcher drafts the vision. Org Discovery writes `org-context.json` (selling models, UOMs, proration and grant policies, fulfillment step groups) with read-only SOQL. |
| 2 Vision gate | human | Present categories/families, a 10-15 SKU set, selling model, bundle, typing, attribute, relationship, pricing, billing, and image assumptions, plus the **customer prefix** and why you chose it. Prefer term-defined over evergreen for recurring offers. **Wait for confirmation.** |
| 3 Contract | series | Write `datasets/sfdmu/customer-template/en-US/sku-contract.yaml` and project it onto `scripts/customer-demo/customer-pricebook-entries.csv`. |
| 4 Domain builders | **parallel** | Launch PCM, Billing, Pricing, and — per flag — Usage-Rates, DRO, Experience. Disjoint directory ownership. |
| 5 Integrate + lint | series | Cross-dataset checks, then `python scripts/validate_sfdmu_v5_datasets.py`. |
| 6 Deploy gate then load | human, then series | On approval, pick the flow from `org.load_mode`: `clean` → `prepare_customer_demo_catalog`, `additive` → `prepare_customer_demo_catalog_additive` (same steps, every scoped delete removed, **not idempotent**). |
| 7 Verify | series parent | `customer_demo_verify_catalog` plus parallel read-only probes. |

### Specialists

| Builder | Skill | Owns |
|---|---|---|
| PCM | [`rlm-customer-demo-pcm`](.cursor/skills/rlm-customer-demo-pcm/SKILL.md) | `customer-template-pcm/` |
| Billing | [`rlm-customer-demo-billing`](.cursor/skills/rlm-customer-demo-billing/SKILL.md) | `customer-template-billing/` |
| Pricing | [`rlm-customer-demo-pricing`](.cursor/skills/rlm-customer-demo-pricing/SKILL.md) | `customer-template-pricing/` + pricing Apex |
| Usage-Rates | [`rlm-customer-demo-usage-rates`](.cursor/skills/rlm-customer-demo-usage-rates/SKILL.md) | `customer-template-rating/` + `customer-template-rates/` |
| DRO | [`rlm-customer-demo-dro`](.cursor/skills/rlm-customer-demo-dro/SKILL.md) | `customer-template-dro/` |
| Experience | [`rlm-customer-demo-experience`](.cursor/skills/rlm-customer-demo-experience/SKILL.md) | product images, static resources, branding |
| Integrator | [`rlm-customer-demo-integrator`](.cursor/skills/rlm-customer-demo-integrator/SKILL.md) | cross-file checks only |

Launch every applicable builder for a wave in a **single message**. Each launch prompt must
carry the contract path, the org-context path, the skill path, the allowed write glob, and an
explicit "do not deploy" — subagents cannot see the parent conversation. Templates are in
[`reference.md`](.cursor/skills/rlm-customer-demo-conductor/reference.md).

### Parallelism boundaries

**Parallel:** research and org discovery; all domain builders after the contract is frozen;
read-only verification probes.

**Series:** everything that touches an org. Never run two SFDMU jobs against one org, never
reorder `prepare_customer_demo_catalog`, and never parallelize CCI — the flow's step order
encodes FK dependencies and activation ordering.

### Rules that survive regardless of which agent is running

- The SKU contract, `customer-pricebook-entries.csv`, and `org-context.json` have exactly one
  writer (the conductor, or Org Discovery for the last). Builders read them and report
  mismatches instead of editing.
- Builders never invent org values. Selling models, units of measure, proration policies,
  usage grant policies, and fulfillment step group names come from `org-context.json`.
- Decide `Product2.Type` before the first insert and treat it as immutable:
  `Type=Bundle` only for parent bundles, blank for everything else. Any SKU with attributes
  or `Type=Bundle` needs `ConfigureDuringSale=Allowed`.
- Never convert an existing `operation: Upsert` to `Insert` + `deleteOldData: true` without
 explaining the specific SFDMU v5 bug, confirming no direct-field externalId exists, and
 getting explicit user approval. It is destructive.
- **Assume the org is shared.** Demo orgs usually hold two or three older customer catalogs.
 Never delete, activate, or overwrite a record you did not create. Upsert-on-name is the
 quiet version of this mistake: a payment term named `Net 30` does not create a record, it
 rewrites the org's existing one. Prefix every name and code you load.
- Pick the customer prefix against `occupiedSkuPrefixes`, not from the abbreviation that
 reads best. Activation Apex allowlists (`CUSTOMER_BILLING_POLICIES`, `CUSTOMER_METER_CODES`)
 are per-customer and owned by the Billing and Usage-Rates builders respectively; teardown
 script prefix lists are **appended to**, never replaced.
- Report quote-test SKUs as the sellable usage SKUs (`*-USG-*`), never the usage-definition
  SKUs (`*-BLNG-*`).
- Lightning Experience theme activation is manual — there is no Salesforce API for it.

### Reference material

- Contract schema: [`docs/references/customer-demo-sku-contract.md`](docs/references/customer-demo-sku-contract.md)
- Human runbook: [`docs/guides/customer-demo-onboarding.md`](docs/guides/customer-demo-onboarding.md)
- Product onboarding UX detail: [`docs/guides/customer-demo-product-onboarding.md`](docs/guides/customer-demo-product-onboarding.md)
- Usage-metered products: [`docs/guides/customer-demo-usage-metered-products.md`](docs/guides/customer-demo-usage-metered-products.md)
- DRO design: [`docs/features/customer-demo-dro.md`](docs/features/customer-demo-dro.md)
- Branding design: [`docs/features/customer-demo-branding.md`](docs/features/customer-demo-branding.md)
- Reference plan shapes: `datasets/sfdmu/qb/en-US/qb-pcm`, `qb-pricing`, `qb-rating`, `qb-rates`
