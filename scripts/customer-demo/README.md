# Customer Demo Scripts

This directory contains reusable templates for customer-specific product onboarding.

- `customer-seed-products.apex`: optional Apex hook for product/catalog support records.
- `customer-purge-and-reimport.apex`: hard reset script template.
- `customer-pricebook-entries.csv`: input for API-based PricebookEntry recreation and verification checks.
- `prepare_customer_logo_static_resource.py`: downloads a customer logo URL and generates a square static resource payload/metadata.

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
