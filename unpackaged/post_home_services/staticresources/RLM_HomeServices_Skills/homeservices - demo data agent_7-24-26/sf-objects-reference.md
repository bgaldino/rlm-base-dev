# Salesforce RLM Object & Field Reference

Field format: `API Name | Type | Notes`

> **Confirmed against live org.** Fields marked ⚠️ were incorrect in prior versions and have been corrected based on live run validation.
>
> **Environment note:** the "Cursor vs Claude" branch in `SKILL.md` is decided by tool availability (`GenerateImage` + canvas present = Cursor path), NOT by model identity. Opus, Sonnet, and GPT running in Cursor all follow the Cursor path.

---

## ProductCatalog
| API Name | Type | Value / Notes |
|---|---|---|
| `Name` | Text(255) | Company name + " Catalog" (e.g., "Brinks Home Catalog") |

> ⚠️ `IsActive` does **not** exist on `ProductCatalog` — omit it.

---

## ProductCategory
| API Name | Type | Value / Notes |
|---|---|---|
| `Name` | Text(255) | Always `"Offerings"` |
| `CatalogId` | Lookup(ProductCatalog) | ID of the catalog created above |

> ⚠️ `IsActive` does **not** exist on `ProductCategory` — omit it.

---

## ProductCategoryProduct
Junction object assigning a product to a category.

| API Name | Type | Value / Notes |
|---|---|---|
| `ProductId` | Lookup(Product2) | ID of the product |
| `ProductCategoryId` | Lookup(ProductCategory) | ID of the "Offerings" category |

---

## Billing Schedules (ALWAYS created — never skipped)

Create these via `scripts/setup-milestone-billing.py` (idempotent). The fields below are all **required** by the API — the records are rejected if any are omitted.

### BillingPolicy
| API Name | Type | Value / Notes |
|---|---|---|
| `Name` | Text(255) | `"Monthly Service - Home Services"` |
| `Status` | Picklist | Insert as `Draft` (⚠️ cannot insert as `Active`). Activate later. |
| `BillingTreatmentSelection` | Picklist | `Default` |
| `DefaultBillingTreatmentId` | Lookup(BillingTreatment) | Set at activation time to the treatment below |

> ⚠️ Activation requires `DefaultBillingTreatmentId` set **and** an active treatment. Set both `DefaultBillingTreatmentId` and `Status='Active'` in the activating update.

### BillingTreatment
| API Name | Type | Value / Notes |
|---|---|---|
| `Name` | Text(255) | `"Home Services Billing Treatment"` |
| `BillingPolicyId` | Lookup(BillingPolicy) | ID of the billing policy above |
| `Status` | Picklist | Insert as `Draft`; activate after items are active |
| `ExcludeFromBilling` | Picklist | `No` |
| `IsMilestoneBilling` | Checkbox | `true` |
| `CanChangeBillingFrequency` | Checkbox | `false` |

> ⚠️ A billable treatment must have **at least one Active item** before it can be activated.

### BillingTreatmentItem (12 items)
| API Name | Type | Value / Notes |
|---|---|---|
| `Name` | Text(255) | `"Month 1 Service"` through `"Month 12 Service"` |
| `BillingTreatmentId` | Master-Detail(BillingTreatment) | ID of the billing treatment |
| `ProcessingOrder` | Number | Month number (1–12) |
| `Type` | Picklist | `Percentage` for **all 12** items |
| `Percentage` | Percent | `8.333` for months 1–11; `8.337` for month 12 (sums to 100) |
| `BillingType` | Picklist | `None` |
| `Sequencing` | Picklist | `None` |
| `Controller` | Picklist | `None` |
| `Handling0Amount` | Picklist | `None` |
| `MilestoneType` | Picklist | `Event` |
| `Status` | Picklist | Insert as `Draft`, then update to `Active` |

> ⚠️ Field is `Percentage`, **not** `Percent`.
> ⚠️ For milestone billing, `Type='Remainder'` is **rejected** ("select percentage for type and enter a percentage") — every item must be `Percentage`.
> ⚠️ `BillingType` must be `None` for milestone billing ("Specify the billing type as None for milestone billing.").

**Activation order:** create all 12 items (Draft) → set each item `Status='Active'` → set treatment `Status='Active'` → set policy `DefaultBillingTreatmentId` + `Status='Active'`.

---

## Product2
| API Name | Type | Value / Notes |
|---|---|---|
| `Name` | Text(255) | Full product name |
| `ProductCode` | Text(255) | Format: `HS-KEYWORD-TYPE` (e.g., `HS-PEST-MON`) |
| `Description` | Text Area(4000) | 2–3 sentence description — use Python REST API, not `--values` |
| `IsActive` | Checkbox | Always `true` |
| `IsAssetizable` | Checkbox | Always `true` |
| `CurrencyIsoCode` | Picklist | Always `USD` |
| `DisplayUrl` | URL(1000) | `/resource/<sanitizedResourceName>`; the Home Services UI normalizes this path for authenticated and guest pages |
| `Type` | Picklist | `Bundle` — bundle parent products only; omit for all others |
| `ConfigureDuringSale` | Picklist | `Allowed` — bundle parent products only; omit for all others |
| `TaxPolicyId` | Lookup(TaxPolicy) | ID of "Default Tax Policy" record |
| `BillingPolicyId` | Lookup(BillingPolicy) | ID of "Monthly Service - Home Services" billing policy (always set — billing is mandatory) |

> `DisplayUrl` is the single source for product imagery. Do not create or populate a separate custom image-resource-name field.

> ⚠️ Do NOT use `sf data create record --body <file>` — the `--body` flag does not exist in SF CLI versions prior to 2.130. Use the **Python REST API approach** for all product creation.

**Static resource name sanitization rule**: Replace spaces and hyphens with underscores; strip all other special characters. Salesforce static resource names must be alphanumeric + underscores only.

---

## ProductSellingModelOption
| API Name | Type | Value / Notes |
|---|---|---|
| `Product2Id` | Lookup(Product2) | ID of the product |
| `ProductSellingModelId` | Master-Detail(ProductSellingModel) | ID of the "Term Monthly" record |
| `ProrationPolicyId` | Lookup(ProrationPolicy) | ID of the "Default Proration Policy" record |
| `IsDefault` | Checkbox | **Required — always set `true`** so the selling model option resolves for pricing |

> ⚠️ Field is `Product2Id`, **not** `ProductId`.

---

## PricebookEntry
| API Name | Type | Value / Notes |
|---|---|---|
| `Product2Id` | Lookup(Product2) | ID of the product |
| `Pricebook2Id` | Lookup(Pricebook2) | ID of the Standard Price Book (`IsStandard=true`) |
| `UnitPrice` | Currency | Monthly price proposed for this product |
| `IsActive` | Checkbox | Always `true` |
| `ProductSellingModelId` | Lookup(ProductSellingModel) | ID of the "Term Monthly" record |
| `CurrencyIsoCode` | Picklist | Always `USD` |

---

## ProductRelationshipType
Pre-fetch the correct relationship type ID before creating bundle components:

```soql
SELECT Id, Name FROM ProductRelationshipType
WHERE Name = 'Bundle to Bundle Component Relationship'
```

Store as `$BUNDLE_REL_TYPE_ID`. This ID is required on every `ProductRelatedComponent` record.

---

## ProductComponentGroup
Intermediate layer between a bundle parent and its add-on children.

| API Name | Type | Value / Notes |
|---|---|---|
| `Name` | Text(255) | `"Optional Add-ons"` |
| `ParentProductId` | Lookup(Product2) | ID of the bundle parent product |
| `MinBundleComponents` | Number | `0` (add-ons are optional) |
| `MaxBundleComponents` | Number | Total number of available add-on children |
| `Sequence` | Number | `1` |

> ⚠️ Fields are `MinBundleComponents` / `MaxBundleComponents`, **not** `MinQty` / `MaxQty`.

---

## ProductRelatedComponent
Links each add-on child product to the component group.

| API Name | Type | Value / Notes |
|---|---|---|
| `ProductComponentGroupId` | Lookup(ProductComponentGroup) | ID of the component group |
| `ParentProductId` | Lookup(Product2) | ID of the bundle parent product — **required** |
| `ChildProductId` | Lookup(Product2) | ID of the add-on child product |
| `ProductRelationshipTypeId` | Lookup(ProductRelationshipType) | ID of "Bundle to Bundle Component Relationship" — **required** |
| `IsDefaultComponent` | Checkbox | `false` — add-ons are optional, not pre-selected |
| `DoesBundlePriceIncludeChild` | Checkbox | `false` — child priced separately; must be set explicitly (defaults to `true` if omitted) |
| `Quantity` | Number | `1` |
| `Sequence` | Number | Sequential integer per child (1, 2, 3…) |

> ⚠️ Field is `ProductComponentGroupId`, **not** `ParentProductComponentGroupId`.
> ⚠️ Field is `IsDefaultComponent`, **not** `IsDefault`.
> ⚠️ Both `IsDefaultComponent` and `DoesBundlePriceIncludeChild` must **always** be set to `False`. `DoesBundlePriceIncludeChild` defaults to `True` when omitted, so set it explicitly.
> ⚠️ `ParentProductId` is **required** — include the bundle parent's product ID.
> ⚠️ `ProductRelationshipTypeId` is **required** — pre-fetch in Phase 3.
> ⚠️ `ParentProductRole` and `ChildProductRole` are **read-only** (auto-set by the system) — do not attempt to set them; you will get an `INVALID_FIELD_FOR_INSERT_UPDATE` error.

---

## StaticResource (image upload via REST API)

> ⚠️ Do **not** use `sf project deploy start --metadata` for static resource upload — it requires an SFDX project scaffold and does not reliably package binary files ("Required field is missing: content"). Use the REST API approach below (no scaffold needed).

> ⚠️ Do **not** use `curl` with a command-line `-d` argument containing the base64 body — large images produce base64 strings that exceed shell argument length limits (`argument list too long`). Use Python's `urllib` instead.

The `scripts/upload-static-resource.sh` helper does this: it fetches org credentials from `sf org display --json`, base64-encodes the image, and POSTs to `<instanceUrl>/services/data/v<apiVersion>/sobjects/StaticResource` with body `{Name, Body, ContentType, CacheControl}`. It is idempotent (skips resources that already exist). Pass the **absolute image path returned by `GenerateImage`**.

```bash
bash scripts/upload-static-resource.sh "<absoluteImagePath>" "<sanitizedResourceName>"
```

---

## Documentation References

- [RLM Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/) — primary object reference for all RLM-specific objects
- [Product Catalog Data Model Gallery](https://developer.salesforce.com/docs/platform/data-models/guide/product-catalog-mgmt.html) — full data model including `ProductComponentGroup`, `ProductRelatedComponent`, `ProductRelationshipType`
- [Salesforce Pricing Data Model](https://developer.salesforce.com/docs/platform/data-models/guide/salesforce-pricing.html) — `ProductSellingModel`, `ProductSellingModelOption`, `PricebookEntry` relationships
- [Trailhead: Create a Product Bundle](https://trailhead.salesforce.com/content/learn/modules/product-catalog-management-with-revenue-cloud/create-a-product-bundle) — step-by-step configurable bundle setup with component groups
- [Trailhead: Get Started with Product Catalog Management](https://trailhead.salesforce.com/content/learn/modules/product-catalog-management-with-revenue-cloud/get-started-with-product-catalog-management) — catalog/category foundational context
- [Salesforce Help: Product Catalog Products](https://help.salesforce.com/s/articleView?id=ind.product_catalog_products.htm&type=5) — product types including bundle parent
- [Salesforce Help: Milestone Billing Methods](https://help.salesforce.com/s/articleView?id=ind.billing_milestone_methods.htm&type=5) — milestone billing Method 1 reference
- [SF CLI Command Reference](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_top.htm) — `sf data create record`, `sf data query` syntax
- [PricebookEntry Object Reference](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_pricebookentry.htm) — field-level reference
