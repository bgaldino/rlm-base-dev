# Customer Demo Static Resources

This directory is the source for customer-specific demo static resources.

Use `scripts/customer-demo/prepare_customer_logo_static_resource.py` to generate:

- `<ResourceName>` (SVG payload file)
- `<ResourceName>.resource-meta.xml`

Naming convention:

- `RLM_customer_<company_slug>_logo_sq`

After files are generated, deploy this folder with the `deploy_customer_demo_staticresources` CCI task.
