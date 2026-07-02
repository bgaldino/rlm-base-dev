---
page_id: product_catalog_management_fields_on_product2.htm
title: Product Catalog Management Fields on Product2
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product2.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Product Catalog Management Fields on Product2

Standard and custom fields extend the standard Product2 object for
use in Product Catalog Management to represent information about products.

## Fields

| Field | Details |
| --- | --- |
| Based On | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the product classification from which this product inherits.  This field is a relationship field.  Relationship Name  BasedOn  Relationship Type  Lookup  Refers To  ProductClassification |
| Help Text | Type  textarea  Properties  Create, Nillable, Update  Description  The help text that appears at runtime for the product. The maximum size is 32,000 alphanumeric characters. The help text can include these special characters: @ ! - < > \* ? + = % # ( ) / \ & ‘ £ € $ ”. |
| Availability Date | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date when the product is available. |
| CanRamp | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the product’s terms, volumes, and other commitments can be ramped (true) at run time or not (false)  The default value is `false`. |
| Discontinued Date | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date when the product is discontinued. |
| End Of Life Date | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time after which a product isn’t supported, ordered, or maintained. |
| Specification Type | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The type of product specification that’s being created. |
| DecompositionScope | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The number of fulfillment order line items that must be generated. Available in API version 61.0 and later.  Valid values are:  - `Account` - `Bundle` - `Order` - `OrderLineItem` |
| FulfillmentQtyCalcMethod | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Determines whether the quantity of fulfillment order line items must always be one or must be aggregated from the source line items. Available in API version 61.0 and later.  Valid values are:  - `Aggregate` - `AlwaysOne` |
| UsageModelType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The type of usage model for a product or service. Anchor is the main subscription product or service. Pack is the add-on product or service that grants additional usage resources for consumption. Available in API version 62.0 and later.  Valid values are:  - `Anchor` - `Pack` |

#### See Also

- [Product2](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_product2.htm "Product2 - HTML (New Window)")
