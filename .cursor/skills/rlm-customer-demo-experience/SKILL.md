---
name: rlm-customer-demo-experience
description: >-
  Authors product imagery and org branding for Revenue Cloud customer demos — static
  resource logos, the customer-template-product-images SFDMU dataset that sets
  Product2.DisplayUrl, and the generated LightningExperienceTheme (ContentAsset +
  BrandingSet). Use when adding customer logos, product images, DisplayUrl values, or
  customer-branded themes to a demo org.
disable-model-invocation: true
---

# Experience builder

Owns:

- `datasets/sfdmu/customer-template/en-US/customer-template-product-images/**`
- `unpackaged/post_customer_demo/staticresources/**`
- `unpackaged/post_customer_demo/branding/**` (generated)

Authoring only — never run `cci`, `sf`, or any deploy command. You may run the local
generator scripts below, which write files and do not touch an org.

Input: `sku-contract.yaml` → `experience`, plus each SKU's `image_required`.

## Sequencing is the whole problem

`Product2.DisplayUrl` resolves to `/resource/<StaticResourceApiName>`. If it is set before
the resource exists in the org, the URL is broken.

The flow order handles this, so respect the division of labor:

| Step | Task | Who writes it |
|---|---|---|
| 2 | `insert_customer_demo_pcm_data` | PCM builder — leaves `DisplayUrl` **empty** |
| 3 | `deploy_customer_demo_staticresources` | you (files only) |
| 4 | `deploy_customer_demo_branding` | you (files only), when `customer_demo_branding` |
| 5 | `insert_customer_demo_product_images_data` | you — sets `DisplayUrl` by SKU |

Never set `DisplayUrl` in the PCM dataset, and never ask the PCM builder to.

## Static resources

Either run `prepare_customer_demo_logo_staticresource` with a URL, or place the `.resource`
plus `-meta.xml` files under `unpackaged/post_customer_demo/staticresources/` directly.

`Product2.csv` in the product-images plan needs one row per SKU with
`image_required: true`, setting `DisplayUrl` to `/resource/<StaticResourceApiName>`.

## Branding (Lightning Experience Theme)

```bash
python scripts/customer-demo/prepare_customer_branding.py \
  --company-name "Acme Robotics" \
  --logo-path /tmp/acme-logo.png \
  --brand-color "#0176D3" \
  --bg-color "#FFFFFF"
```

- Requires `Pillow`. The logo is auto-resized to 600x120 PNG; `--bg-color` letterboxes it.
- **Prefer `--logo-path` over `--logo-url`.** Corporate and CDN URLs commonly return 403 to
  server-side requests. Download the logo first, or generate a placeholder with Pillow.
- Generates ContentAsset + BrandingSet + LightningExperienceTheme (SLDS v2) under
  `unpackaged/post_customer_demo/branding/`.
- The BrandingSet API name must use the `LEXTHEMING` prefix.
- For structural changes, edit `scripts/customer-demo/prepare_customer_branding.py` — the
  output directory is generated, so hand edits there are lost.

**Theme activation is manual.** No Salesforce API activates a theme. Always tell the user to
open `<org-url>/lightning/setup/ThemingAndBranding/home` after the flow and activate it.

## Before you finish

1. Every `image_required: true` SKU has a product-images row and a matching static resource.
2. No `DisplayUrl` value points at a resource you did not create.
3. If branding ran, report that manual activation is still required.

Deeper detail: `docs/features/customer-demo-branding.md`,
`datasets/sfdmu/customer-template/en-US/customer-template-product-images/README.md`.
