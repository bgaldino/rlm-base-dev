---
page_id: sforce_api_objects_productsellingmodeloption.htm
title: ProductSellingModelOption
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productsellingmodeloption.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductSellingModelOption

A junction object between Product Selling Model and Product2. This
object is available in API version 60.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  The description of the product selling model option. |
| DisplayName | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the product selling model option to display to customers. |
| Increment | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The number of pricing term units that can be used to increase a subscription term. |
| IsDefault | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indcates the default product selling model for a product. Setting a default is optional. A product can only have one default product selling model.  The default value is `false`. This field requires Industries EPC. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record, a record related to this record, or a list view. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, the user might have only accessed this record or list view but not viewed it. |
| Maximum | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The maximum number of pricing term units for a subscription term. |
| Minimum | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The minimum number of pricing term units for a subscription term. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the product selling model option. |
| Product2Id | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the Product2 record associated with this ProductSellingModelOption record.  This field is a relationship field.  Relationship Name  Product2  Relationship Type  Lookup  Refers To  Product2 |
| ProductSellingModelId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the ProductSellingModel record associated with this ProductSellingModelOption record.  This field is a relationship field.  Relationship Name  ProductSellingModel  Relationship Type  Lookup  Refers To  ProductSellingModel |
| ProrationPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The ID of the ProrationPolicy record associated with this ProductSellingModelOption record.  This field is a relationship field.  Relationship Name  ProrationPolicy  Relationship Type  Lookup  Refers To  ProrationPolicy |
