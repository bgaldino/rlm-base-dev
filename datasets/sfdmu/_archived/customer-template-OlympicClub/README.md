# Customer template SFDMU plans (blank scaffold)

The plans under `en-US/` default to **structure-only** (headers + `export.json`). The **Olympic Club** customer demo ships **fully populated** rows in `customer-template-pcm`, billing, product-images, rating, and rates, plus `scripts/customer-demo/customer-pricebook-entries.csv`. Replace or fork those CSVs when onboarding a different customer.

The previous populated Snowflake-style sample (including SFDMU `source/`, `target/`, and `reports/MissingParentRecordsReport.csv`, which are normally gitignored under active plans) is preserved under **`datasets/sfdmu/_archived/customer-template-Snowflake/`** for reference only. Do not point CCI tasks at that path unless you intend to reload that snapshot.

## What to fill in

| Area | Path | Also update |
|------|------|-------------|
| PCM (products, catalog, bundles, UoM) | `en-US/customer-template-pcm/` | — |
| Product images (`DisplayUrl`) | `en-US/customer-template-product-images/` | Static resources under `unpackaged/post_customer_demo/staticresources/` if needed |
| Billing assignment | `en-US/customer-template-billing/` | Align policy and legal entity names with the org |
| Usage / rating | `en-US/customer-template-rating/` | After PCM + UoM exist; see subfolder README |
| Rate cards | `en-US/customer-template-rates/` | After rating load and `activate_rating_records` |
| Standard pricebook API step | — | `scripts/customer-demo/customer-pricebook-entries.csv` (header-only until you add SKUs) |

## References

- Runbook: `docs/guides/customer-demo-onboarding.md`
- Agent workflow: `AGENTS.md` (Customer Demo Product Onboarding UX)
- Advanced PCM shape: `datasets/sfdmu/qb/en-US/qb-pcm`
- Usage and rates skill: `.cursor/skills/rlm-customer-demo-usage-rates/`

Until rows exist, `insert_*` tasks for these plans are effectively no-ops for empty objects; pricebook recreation and catalog verification require populated PCM and `customer-pricebook-entries.csv`.
