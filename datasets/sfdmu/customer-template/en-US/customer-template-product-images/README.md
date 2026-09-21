# customer-template-product-images Data Plan

Sets `Product2.DisplayUrl` on customer demo products, matched by `StockKeepingUnit`.

Current customer: **Salesforce** (prefix `sfdc`, brand `#00B4FF` on `#FFFFFF`).

## Sequencing

`DisplayUrl` resolves to `/resource/<StaticResourceName>`, so the resource has to be in the org
first. `prepare_customer_demo_catalog` enforces the order:

| Step | Task | Effect |
|---|---|---|
| 2 | `insert_customer_demo_pcm_data` | Creates Product2 with `DisplayUrl` **empty** |
| 3 | `deploy_customer_demo_staticresources` | Deploys the tiles from `unpackaged/post_customer_demo/staticresources/` |
| 4 | `deploy_customer_demo_branding` | Theme ContentAsset/BrandingSet (independent of DisplayUrl) |
| 5 | `insert_customer_demo_product_images_data` | This plan — sets `DisplayUrl` by SKU |

Never set `DisplayUrl` in the PCM plan.

## CSV contract

`Product2.csv` headers: `DisplayUrl`, `Name`, `StockKeepingUnit`. One row per SKU with
`image_required: true` in `sku-contract.yaml` (8 rows for this catalog). `export.json` uses
`operation: Update` with `externalId: StockKeepingUnit`, so the products must already exist —
this plan never creates a Product2.

`Product2.csv` is generated. Do not hand-edit it; re-run the generator instead.

## Tile generator

`tools/generate_branded_tiles.py` reads the contract and writes both sides of the wiring in one
pass — the static resources and this plan's CSV — so resource names and `DisplayUrl` values
cannot drift apart.

```bash
# Tiles + Product2.csv
.venv/bin/python tools/generate_branded_tiles.py --logo-path tools/assets/sfdc-logo.png

# Regenerate the wordmark placeholder (only when the customer name or brand color changes)
.venv/bin/python tools/generate_branded_tiles.py --emit-logo-placeholder
```

Requires PyYAML, plus Pillow for `--emit-logo-placeholder`. The repo venv has both:
`.venv/bin/python -m pip install pyyaml Pillow`.

Each tile is a 512×512 SVG: solid brand-color field, a white logo band, the product name, and
the SKU. Everything is inlined — Salesforce renders static resource images in secure static
mode, which blocks references to other resources and external URLs.

## Logo

`tools/assets/sfdc-logo.png` is the single source of truth for customer imagery. It is
currently a generated wordmark placeholder, because salesforce.com and Wikimedia both return
403 to server-side fetches. Dropping in the real logo is a one-file change: overwrite that
file, re-run the generator, and re-run `scripts/customer-demo/prepare_customer_branding.py`
with the same `--logo-path`.

## Reusing for the next customer

Update `experience` and `image_required` in `sku-contract.yaml`, delete the previous customer's
resources from `unpackaged/post_customer_demo/staticresources/`, emit a new placeholder, and
re-run the generator. Prefixing resources with the customer's `static_resource_prefix` keeps
several demo catalogs coexisting in one org without name collisions.
