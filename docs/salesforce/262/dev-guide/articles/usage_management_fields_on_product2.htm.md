---
page_id: usage_management_fields_on_product2.htm
title: Usage Management Fields on Product2
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/usage_management_fields_on_product2.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Usage Management Fields on Product2

Standard and custom fields extend the standard Product2 object for
use in Usage Management to represent information about products.

## Fields

| Field | Details |
| --- | --- |
| UsageModelType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The type of usage model for a product or service.  Valid values are:  - `Anchor`—The main   subscription product or service. Available in API version   62.0 and later. - `Pack`—The add-on   product or service that grants additional usage resources for   consumption. Available in API version 62.0 and later. - `Monetary   Commitment`—An agreement by a customer to   spend a minimum amount for a product or service in a defined   period. Available in API version 65.0 and later. - `Quantity   Commitment`—An agreement by a customer to use   a minimum quantity of a product or service in a defined   period. Available in API version 65.0 and later. - `Token   Commitement`—An agreement by a customer to use   a minimum quantity of tokens for a product or service in a   defined period. Available in API version 65.0 and later. |

#### See Also

- [Product2](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_product2.htm)
