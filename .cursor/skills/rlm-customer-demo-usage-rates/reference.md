# Reference — customer demo usage & rates

## Directory map

| Plan | Path |
|------|------|
| PCM | `datasets/sfdmu/customer-template/en-US/customer-template-pcm` |
| Rating | `datasets/sfdmu/customer-template/en-US/customer-template-rating` |
| Rates | `datasets/sfdmu/customer-template/en-US/customer-template-rates` |
| Full QB (patterns) | `datasets/sfdmu/qb/en-US/qb-rating`, `qb-rates` |

## Snowflake template SKU prefixes (illustrative)

| Prefix | Meaning |
|--------|---------|
| `SF-USG-*` | Sellable **Pack** (quote these) |
| `SF-BLNG-*` | **Usage-definition** products (**UsageResource.UsageDefinitionProduct**) |
| `SF-UR-*` | **UsageResource.Code** (meters) |

## Rating CSV roles (customer-template-rating)

- **UsageResourceBillingPolicy.csv** — Upsert shared policies (**`monthlypeak`**, **`monthlytotal`**); not wiped by customer demo rating delete.
- **UsageResource.csv** — Meters; **Category = Usage**; links to **UsageDefinitionProduct**, **DefaultUnitOfMeasure**, **UnitOfMeasureClass**, **UsageResourceBillingPolicy**.
- **Product2.csv** — Update **UsageModelType** on sellable products.
- **ProductUsageResource.csv** — **`$$Product.StockKeepingUnit$UsageResource.Code`**; **Insert**; links Pack → UR.

**export.json:** object set pass 2 activates **UsageResource** from `objectset_source/object-set-2/`.

## Rates CSV roles (customer-template-rates)

- **RateCard.csv** — **CD-DEMO Base Rate Card**, **Type = Base**, effective window.
- **PriceBookRateCard.csv** — Link to **Standard Price Book**.
- **RateCardEntry.csv** — Composite key **Product;RateCard;UsageResource;RateUnitOfMeasure**; **Base** rates with **Negotiable**; **Draft** until **activate_rates**.

Lookup-only CSVs in the same folder (not always separate `objects` in export): **Pricebook2**, **ProductSellingModel**, **UsageResource**, **UnitOfMeasure**, **UnitOfMeasureClass**, **Product2** — must match org names.

## CumulusCI tasks (names)

- `insert_customer_demo_pcm_data`, `insert_customer_demo_rating_data`, `insert_customer_demo_rates_data`
- `delete_customer_demo_rating_data`, `delete_customer_demo_rates_data`
- `activate_rating_records`, `activate_rates`
- Flow: `prepare_customer_demo_catalog` with **`customer_demo_usage: true`** in project `custom`, or `prepare_customer_demo_usage` after catalog through pricebook + verify

## Quote / UX notes

- Quote **Pack** SKUs (**`SF-USG-*`**), not **`SF-BLNG-*`**, for normal usage demos.
- Product record UI: **ProductUsageResources** related list shows PUR wiring.

## Further reading

- `datasets/sfdmu/customer-template/en-US/customer-template-rating/README.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-rates/README.md`
- `datasets/sfdmu/qb/en-US/qb-rating/README.md`, `qb-rates/README.md`
