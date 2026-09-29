---
page_id: cml_best_practice_pricing_fields.htm
title: Pricing Fields Not Supported in CML
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_best_practice_pricing_fields.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_best_practices.htm
fetched_at: 2026-09-29
---

# Pricing Fields Not Supported in CML

Pricing fields, such as ListPrice and NetUnitPrice, aren't supported in CML and
    shouldn't be used in constraint models.

    

Pricing fields, such as ListPrice, NetUnitPrice, and others, are not supported in CML and
      should not be used in constraint models. CML is designed to enforce configuration logic for
      products, not to perform pricing calculations. Attempting to reference or manipulate pricing
      fields in CML code leads to errors and unexpected behaviors in the constraint engine. Use
      dedicated pricing or calculation mechanisms outside of the CML constraint model for such
      functionality.
