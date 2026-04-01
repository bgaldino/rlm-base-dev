# Agent Operating Rules

## Customer Demo Product Onboarding UX

When a user asks to set up products for a customer demonstration:

1. Treat this as onboarding intent.
2. Ask for **either**:
   - a company description, or
   - a company website URL.
3. Ask for additional context when available (services, pricing model, recurring vs one-time offers, add-ons, known SKUs, billing expectations, and product image preferences/URLs). If product images are requested, ask for a preferred customer logo URL and confirm it can be used.
4. Research the customer inputs and propose a product vision:
   - categories/families,
   - 10-15 SKU set,
   - selling model assumptions,
   - bundle assumptions (parent bundles, component groups, required vs optional components),
   - attribute/configuration assumptions (definitions, picklists, product attribute behavior),
   - relationship assumptions (relationship types, related components, qualification/disqualification rules when needed),
   - pricing assumptions,
   - billing assumptions (for example payment term and billing policy intent),
   - image coverage assumptions (which SKUs require product images).
5. Ask the user to confirm the vision before creating or deploying records.
6. After confirmation, use repo assets:
   - dataset templates:
     - `datasets/sfdmu/customer-template/en-US/customer-template-pcm`
     - `datasets/sfdmu/customer-template/en-US/customer-template-product-images`
     - `datasets/sfdmu/customer-template/en-US/customer-template-billing`
   - model customer-specific PCM using `datasets/sfdmu/qb/en-US/qb-pcm` as the reference shape for advanced objects (attributes, classifications, bundles, related components, ramp/proration, qualifications)
   - before running import/deploy, validate that all `ProductSellingModel.Name` + `SellingModelType` values used in customer CSVs exist in the target org; adjust to org-native names if needed
   - flow: `prepare_customer_demo_catalog`
   - logo preparation task: `prepare_customer_demo_logo_staticresource`
   - logo deployment task: `deploy_customer_demo_staticresources`
   - verification task: `customer_demo_verify_catalog`
7. Do not run deployment/import steps without explicit user approval.
