# Customer Demo Product Onboarding

This guide covers customer-specific demo onboarding **after environment setup is complete**.
It is separate from machine/tool installation.

## Outcome

Use this process to research a customer, build a focused product record book, create required records, push them to Salesforce, and verify demo readiness.

## Conversation UX Contract

Use this contract whenever a user says they want to set up products for a customer demo.

1. Detect onboarding intent from natural requests such as:
   - "I want to set up products for my customer demonstration."
   - "Help me onboard customer demo products."
2. First response must ask for **either**:
   - a company description, or
   - the company website URL.
3. Encourage richer input (the more the user shares, the better):
   - service lines, pricing motions, known SKUs, bundles, add-ons, annual/monthly offers.
   - billing expectations (payment terms, invoice timing, billing policies by SKU).
   - product image preferences/sources (which SKUs need images, customer logo URL source).
4. Produce a draft product vision:
   - product families, categories, 10-15 SKU proposal, expected selling models, pricing assumptions, billing assumptions, and image coverage assumptions.
5. Ask the user to confirm or adjust the proposal before any record creation/deploy.
6. After confirmation, build datasets and run the onboarding tasks/flow.

## Operator Prompt Contract

Use this sequence as a standard user experience:

- **User:** "I want to set up products for my customer demonstration."
- **Assistant:** "Share either a company description or website URL. If possible include service lines, pricing model, and known offerings."
- **Assistant:** Researches inputs and returns proposed categories/SKUs/PSMs.
- **Assistant:** "Please confirm this product vision or tell me changes."
- **User:** Confirms.
- **Assistant:** Builds customer records from templates and runs deployment + verification commands.

Do not run deploy/import commands until explicit user confirmation is provided.

## Phase 1: Research and record book

For each customer:

1. Research public service lines and commercial motions:
   - One-time project work
   - Recurring monthly services
   - Annual service plans
   - Emergency/surcharge add-ons
2. Convert motions into product families and categories.
3. Build a demo SKU set with **10-15 SKUs**.
4. Keep categories to a practical **3-6 categories**.
5. Build the SKU matrix (record book) with:
   - `SKU`, `Name`, `CategoryCode`, `Family`, `PSMName`, `PSMSellingModelType`, `UnitPrice`, `CurrencyIsoCode`, `Description`
6. Prefer recurring SKUs to use **term-defined** selling models (typically monthly or annual) instead of evergreen:
   - default recurring offers to `SellingModelType=TermDefined` where possible
   - use org-native term model names in `PSMName` (for example "Term Monthly" / "Term Annual")
   - use evergreen only as a fallback when term models are unavailable, and document that this limits proration and amend/cancel/replace demo scenarios

If the plan needs more than 15 SKUs or more than 6 categories, document why and approve an exception before build.

## Phase 2: Build records locally

1. Copy the template plan:
   - `datasets/sfdmu/customer-template/en-US/customer-template-pcm`
2. Create your customer plan (example):
   - `datasets/sfdmu/acme/en-US/acme-pcm`
3. Populate customer CSVs from the SKU matrix:
   - `ProductSellingModel.csv`
   - `Product2.csv`
   - `ProductSellingModelOption.csv` (default option required)
   - `ProductCatalog.csv`
   - `ProductCategory.csv`
   - `ProductCategoryProduct.csv`
4. Populate `scripts/customer-demo/customer-pricebook-entries.csv`.
   - for recurring SKUs, keep `PSMSellingModelType=TermDefined` unless fallback is required
5. Populate customer image dataset CSV:
   - `datasets/sfdmu/customer-template/en-US/customer-template-product-images/Product2.csv`
6. Prepare customer logo static resource files:
   - `python3 scripts/customer-demo/prepare_customer_logo_static_resource.py --company-name "<Customer Name>" --logo-url "<Logo URL>"`
7. Populate customer billing dataset CSVs (as needed for your billing model):
   - `datasets/sfdmu/customer-template/en-US/customer-template-billing/*.csv`

## Phase 3: Push records to Salesforce

Example command sequence:

```bash
# 1) Optional hard reset
cci task run customer_demo_purge_records --org <org-alias>

# 2) Load customer PCM records
cci task run insert_customer_demo_pcm_data --org <org-alias>

# 3) Deploy customer static resources (logo assets)
cci task run deploy_customer_demo_staticresources --org <org-alias>

# 4) Apply product images by SKU
cci task run insert_customer_demo_product_images_data --org <org-alias>

# 5) Load lightweight billing foundation + product billing assignments
cci task run insert_customer_demo_billing_data --org <org-alias>

# 6) Recreate Standard PricebookEntry rows through API (with ProductSellingModelId)
cci task run customer_demo_recreate_pricebook_via_api --org <org-alias>

# 7) Verify go/no-go checks
cci task run customer_demo_verify_catalog --org <org-alias>
```

Or run as one flow:

```bash
cci flow run prepare_customer_demo_catalog --org <org-alias>
```

## Verification checklist

For every SKU:

- Product exists and is active.
- Product Type field is populated.
- Product image URL is populated when required for demo UX.
- Billing policy assignment exists when SKU is billable.
- Default `ProductSellingModelOption` exists.
- Standard `PricebookEntry` exists and is active.
- `PricebookEntry.ProductSellingModelId` matches expected model.
- Category mapping exists (`ProductCategoryProduct`).

If any check fails, do not proceed to demo execution.
