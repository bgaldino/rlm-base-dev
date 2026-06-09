---
page_id: sforce_api_objects_productconfigurationrule.htm
title: ProductConfigurationRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productconfigurationrule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: prod_config_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductConfigurationRule

Represents the validation, inclusion, and exclusion rules for products in the
context of the selling process. The selling process can be quoting, configuration, or
ordering. This object is available in API version 61.0 and later.

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
| ApiName | Type  string  Properties  Filter, Group, Nillable, Sort  Description |
| ConfigurationRuleDefinition | Type  textarea  Properties  Create, Nillable, Update  Description  The configuration rule criteria and actions. |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The description of the configuration rule. |
| EffectiveFromDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date and time from which the configuration rules comes into effect. |
| EffectiveToDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date and time to which the configuration rules ceases to be in effect. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the configuration rule record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the configuration rule record was last viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the configuration rule. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the configuraion rule owner.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| ProcessScope | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The scope of the configuration rule.  Possible values are:  - `Bundle` - `Product`  The default value is `Product`. |
| RuleSubType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The segregation of products into subsets such that the configuration rules only apply to the products that fall under the ambit of the selected rule subtype.  Possible values are:  - `BundleProduct` - `BundleProductClassification` - `Product` - `ProductClassification`  The default value is `Product`. |
| RuleType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Indicates the industry vertical or the feature of the industry vertical that’s using the configuration rule.  Possible values are:  - `Configurator` - `Promotions`  The default value is `Configurator`. |
| Sequence | Type  int  Properties  Filter, Group, Nillable, Sort  Description  Indicates the order for executing the configuration rule. Rules with lower numbers run first when multiple rules are triggered at once. |
| Status | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The lifecycle status of the configuration rule.  Possible values are:  - `Active` - `Draft` - `Inactive`  The default value is `Draft`. |
