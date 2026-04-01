# Customer Demo Scripts

This directory contains reusable templates for customer-specific product onboarding.

- `customer-seed-products.apex`: optional Apex hook for product/catalog support records.
- `customer-purge-and-reimport.apex`: hard reset script template.
- `customer-pricebook-entries.csv`: input for API-based PricebookEntry recreation task.

Use these templates to create customer-specific files (for example `acme-seed-products.apex`) and wire them into your flow if you need per-customer variants.
