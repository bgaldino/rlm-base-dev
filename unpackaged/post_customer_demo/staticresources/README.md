# Customer Demo Static Resources

Deployed by `deploy_customer_demo_staticresources` (step 3 of `prepare_customer_demo_catalog`),
which must run **before** `insert_customer_demo_product_images_data` sets
`Product2.DisplayUrl` to `/resource/<ResourceName>`. A DisplayUrl pointing at a resource that
does not exist in the org renders as a broken image.

Current customer: **Salesforce** (prefix `sfdc`, brand `#00B4FF` on `#FFFFFF`).

| Resource | Purpose |
|---|---|
| `sfdc_logo_sq` | Square customer mark. Generic fallback image; not referenced by any SKU today. |
| `sfdc_tile_<slug>` | One brand-colored product tile per `image_required: true` SKU in the contract. |

All payloads are self-contained SVG — background, text, and a base64-embedded logo. Salesforce
renders static resource images in secure static mode, so SVG cannot reference another resource
or an external URL; everything must be inlined.

## Regenerating

These files are generated. Edit the generator, not the output:

```bash
.venv/bin/python \
  datasets/sfdmu/customer-template/en-US/customer-template-product-images/tools/generate_branded_tiles.py \
  --logo-path datasets/sfdmu/customer-template/en-US/customer-template-product-images/tools/assets/sfdc-logo.png
```

The generator reads `sku-contract.yaml` for the customer name, colors, static resource prefix,
and the set of SKUs with `image_required: true`, and it rewrites the product-images
`Product2.csv` in the same pass so resource names and `DisplayUrl` values cannot drift.

## Swapping in the real logo

The committed logo is a generated wordmark placeholder — salesforce.com and Wikimedia both
return 403 to server-side fetches, so no real logo was available at authoring time. To swap:

1. Overwrite `…/customer-template-product-images/tools/assets/sfdc-logo.png` with the real file.
2. Re-run the generator command above (refreshes all tiles).
3. Re-run `scripts/customer-demo/prepare_customer_branding.py` with the same `--logo-path`
   (refreshes the theme ContentAsset).

## File naming

Payload files use the `.resource` extension with a matching `<Name>.resource-meta.xml`
declaring `contentType`. The extensionless form written by
`scripts/customer-demo/prepare_customer_logo_static_resource.py` also deploys, but `.resource`
is unambiguous in both metadata and source format.
