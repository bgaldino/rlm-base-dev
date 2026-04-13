# customer-template-product-images Data Plan

Template SFDMU plan for customer demo product images.

## Scope

- Updates `Product2.DisplayUrl` by matching `Product2.StockKeepingUnit`.
- Intended to run after product records are loaded by `customer-template-pcm`.

## CSV contract

`Product2.csv` headers:

- `DisplayUrl` (image URL shown on product experiences)
- `Name` (optional for readability)
- `StockKeepingUnit` (required lookup key)

## DisplayUrl conventions

- Preferred: Salesforce static resource path
  - `DisplayUrl=/resource/<StaticResourceName>`
  - Example: `/resource/RLM_customer_acme_logo_sq`
- Allowed fallback: external `https://...` URL when static resource deployment is not used.

For customer demos, prefer static resources so image rendering is stable and independent of third-party hosting.

## Customer logo workflow

1. Generate static resource files from a public customer logo URL:
   - `python3 scripts/customer-demo/prepare_customer_logo_static_resource.py --company-name "Acme" --logo-url "https://example.com/logo.png"`
2. Deploy generated resources:
   - `cci task run deploy_customer_demo_staticresources --org <org-alias>`
3. Set `DisplayUrl` in `Product2.csv` to `/resource/<StaticResourceName>`.
4. Run `insert_customer_demo_product_images_data` (or `prepare_customer_demo_catalog` flow).

## Usage

1. Copy this template into your customer dataset path if needed.
2. Add image URLs for SKUs that require visual representation in the demo.
3. Keep values consistent with the deployed static resource names.
4. Run via customer demo flow/task after PCM records exist.
