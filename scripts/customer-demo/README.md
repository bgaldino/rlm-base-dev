# Customer Demo Scripts

This directory contains reusable templates for customer-specific product onboarding.

## Chicago Bulls Demo — Quick Start

The customer-template datasets are pre-populated with the Chicago Bulls product catalog (13 SKUs).
Run the following commands to prepare branding, then deploy the full catalog:

```bash
# 1. Generate Bulls logo static resource (requires requests: pip install requests)
python3 scripts/customer-demo/prepare_customer_logo_static_resource.py \
  --company-name "Chicago Bulls" \
  --logo-url "https://cdn.nba.com/logos/nba/1610612741/global/L/logo.svg" \
  --resource-name "ChicagoBullsLogo"

# 2. Generate Bulls Lightning Experience Theme (requires Pillow: pip install Pillow requests)
python3 scripts/customer-demo/prepare_customer_branding.py \
  --company-name "Chicago Bulls" \
  --logo-url "https://cdn.nba.com/logos/nba/1610612741/global/L/logo.svg" \
  --brand-color "#CE1141" \
  --bg-color "#000000"

# 3. Deploy and run the full catalog flow (set org alias as appropriate)
cci flow run prepare_customer_demo_catalog --org <org-alias>

# After deploy: manually activate the theme at Setup → Themes and Branding
```

### Bulls SKU Summary

| SKU | Name | Model | Price |
|-----|------|-------|-------|
| `BULLS-ST-FULL` | Full Season Ticket (82 Games) | Term Annual | $5,000/seat/yr |
| `BULLS-ST-20` | 20-Game Plan | Term Annual | $2,500/seat/yr |
| `BULLS-ST-10` | 10-Game Plan | Term Annual | $1,200/seat/yr |
| `BULLS-MBR-PRO` | Bulls Pro Digital Membership | Term Monthly | $19.99/mo |
| `BULLS-YTH-ELITE` | Youth Elite Training Program | Term Monthly | $49.99/mo |
| `BULLS-SUITE-LOWER` | Lower Level Suite Rental | One-Time | $16,075/event |
| `BULLS-SUITE-CLUB` | Club Level Suite Rental | One-Time | $12,500/event |
| `BULLS-EXP-TUNNEL` | Tunnel Experience | One-Time | $10,000/event |
| `BULLS-EXP-ANTHEM` | Anthem Buddies | One-Time | $10,000/event |
| `BULLS-EXP-BENCH` | Benchwarmers Warm-Up Access | One-Time | $6,000/event |
| `BULLS-CAMP-SUMMER` | Youth Hoops Summer Camp | One-Time | $399/session |
| `BULLS-FAM-PACK` | Family Fun Pack | One-Time | $89/ticket |
| `BULLS-CORP-PKG` | Corporate Hospitality Package *(Bundle)* | One-Time | $29,500/event |

Bundle components: Club Level Suite (required) + Tunnel Experience (optional) + Anthem Buddies (optional).

Attributes configured: **Seat Section** (Lower Bowl / Upper Bowl / Courtside), **Seats Per Game** (1/2/4/6), **Game Package Theme** (All-Star / Weekender / Weeknight) on 10-Game Plan, **Suite Capacity** (read-only, 20) on suite products.

Billing: **Bulls Standard Billing** (advance, Net 30) assigned to all 13 SKUs via **Chicago Bulls LLC** legal entity.

- `customer-seed-products.apex`: optional Apex hook for product/catalog support records.
- `customer-purge-and-reimport.apex`: step-1 cleanup for `prepare_customer_demo_catalog` — deletes **QuotLineItmUseRsrcGrant** / **OrderItemUsageRsrcGrant** on **`SF-UR-*`** meters so rating delete is not blocked by **QLIURG** / order grants.
- `customer-pricebook-entries.csv`: input for API-based PricebookEntry recreation and verification checks.
- `prepare_customer_logo_static_resource.py`: downloads a customer logo URL and generates a square static resource payload/metadata.
- `validate_sku_contract.py`: validates the SKU contract that drives the multi-agent onboarding flow, and can emit `customer-pricebook-entries.csv` from it. See `docs/references/customer-demo-sku-contract.md`.

## SKU contract (multi-agent onboarding)

Onboarding runs as a conductor plus parallel domain builders coordinated by a **SKU contract**
(`datasets/sfdmu/customer-template/en-US/sku-contract.yaml`). The contract is the single
source for SKUs, selling models, categories, attributes, pricing rules, billing policies, and
usage wiring; `customer-pricebook-entries.csv` is a projection of it.

```bash
# validate before launching builders (org checks run when org-context.json exists)
python3 scripts/customer-demo/validate_sku_contract.py

# regenerate the pricebook CSV from the contract
python3 scripts/customer-demo/validate_sku_contract.py --emit-pricebook \
  > scripts/customer-demo/customer-pricebook-entries.csv
```

Requires PyYAML; if the system `python3` lacks it, use the CumulusCI interpreter
(`~/.local/pipx/venvs/cumulusci/bin/python3`). Orchestration:
`.cursor/skills/rlm-customer-demo-conductor/SKILL.md`.

## Product2 bootstrap rules for onboarding

Set Product2 structure fields correctly on the initial import:

- `Product2.Type` should be treated as a one-time onboarding decision per SKU.
- Use `Type=Bundle` for parent bundle SKUs.
- Use blank/null `Type` for component or standalone SKUs unless target-org rules require a specific value.
- For SKUs inserted with `Type=Bundle`, set `Product2.ConfigureDuringSale=Allowed` on initial insert.

Light discovery from active demo orgs:
- `ConfigureDuringSale` commonly appears as `Allowed` or null.
- Bundle relationship validation may reject child SKUs typed as `Base`/`Set`; null child type is safer.

## Customer logo static resource

Use this script to create a deployable static resource for customer demo product images:

```bash
python3 scripts/customer-demo/prepare_customer_logo_static_resource.py \
  --company-name "Acme" \
  --logo-url "https://example.com/logo.png"
```

Optional flags:

- `--resource-name RLM_customer_acme_logo_sq` to force a specific resource name
- `--output-dir <path>` to write files to a different staticresources folder

Then deploy:

```bash
cci task run deploy_customer_demo_staticresources --org <org-alias>
```

## `customer-pricebook-entries.csv` columns

- Core pricing fields: `SKU`, `UnitPrice`, `CurrencyIsoCode`, `PSMName`, `PSMSellingModelType`, `IsActive`, `CategoryCode`
- Recurring-model recommendation:
  - prefer `PSMSellingModelType=TermDefined` for recurring offers (monthly/annual)
  - this keeps proration and amend/cancel/replace scenarios demonstrable in customer demos
  - use evergreen only when the target org does not provide compatible term-based models
- Optional verification controls:
  - `ImageRequired` (default `true`) - when `true`, verify `Product2.DisplayUrl` exists
  - `BillingRequired` (default `true`) - when `true`, verify `Product2.BillingPolicyId` exists
  - `BillingPolicyName` (optional) - if provided, verify assigned billing policy name matches

Use these templates to create customer-specific files (for example `acme-seed-products.apex`) and wire them into your flow if you need per-customer variants.
