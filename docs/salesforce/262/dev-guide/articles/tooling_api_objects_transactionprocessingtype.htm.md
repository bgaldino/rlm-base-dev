---
page_id: tooling_api_objects_transactionprocessingtype.htm
title: TransactionProcessingType
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/tooling_api_objects_transactionprocessingtype.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# TransactionProcessingType

Represents the settings to configure the processing constraints for a
request.. This object is available in API version 63.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

Refer to the Usage section to learn more about creating Transaction Processing
Type records based on your requirements. See the [setup details](https://help.salesforce.com/s/articleView?id=ind.product_configurator_specify_which_rule_engine_to_use.htm&language=en_US "HTML (New Window)") to specify
the default rule engine on the Revenue Settings page.

## Supported SOAP API Calls

`create()`, `describeSObjects()`, `query()`, `retrieve()`

## Supported REST API Methods

`GET, HEAD, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The description of the transaction processing configuration to help Salesforce admins with configuration in their orgs. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. The unique name of the object in the API. This name can contain only underscores and alphanumeric characters, and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. In managed packages, this field prevents naming conflicts on package installations. With this field, a developer can change the object’s name in a managed package and the changes are reflected in a subscriber’s organization. Label is **Record Type Name**. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Nillable, Update  Description  The language of the TransactionProcessingType object.  Valid values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish   (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese   (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese   (Simplified) - `zh_TW`—Chinese   (Traditional) |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The label for the TransactionProcessingType object. |
| PricingPreference | Type  string  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies whether to execute the price calculation step for each sales transaction record. Valid values are:   - `Force`—Reprices   all lines. - `System`—Performs   a delta pricing request on the unprocessed lines when [Delta Pricing](https://help.salesforce.com/s/articleView?id=ind.qocal_use_delta_pricing_for_quotes_and_orders.htm&language=en_US "HTML (New Window)") is enabled in the org. - `Skip`—Skips the   pricing request on all lines.  Available in API version 65.0 and later. |
| RatingPreference | Type  string  Properties    Description  Specifies whether catalog rates are fetched and saved during quote creation. Valid value is `Fetch`. Use this value to retrieve and save catalog rates for usage resources associated with each sales transaction record. If this value isn't specified, catalog rates aren't saved by default when a quote line item is added to a quote. Available in API version 66.0 and later if Rate Management is enabled. |
| RuleEngine | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The rule engine to be used for processing rules.  Valid values are:  - `AdvancedConfigurator` - `StandardConfigurator` |
| SaveType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies how the transaction results are processed when saved for Salesforce administrators to adjust the user experience as desired. Valid values are:   - `Standard` - `Large`—Reserved   for future use. |
| TaxPreference | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies whether to execute or skip the tax calculation step for each sales transaction record.  Valid value is `Skip`. If this value isn't specified, then tax calculation request is performed by default. Available in API version 65.0 and later. |

## Usage

Create transaction type records by calling this resource
through a POST
method.

```
/services/data/v67.0/tooling/sobjects/TransactionProcessingType
```

Here's
a sample payload that specifies the rule engine to use and steps to skip for each sales
transaction record.

```
{
  "SaveType": "Standard",
  "Description": "Setup for Transaction Processing Type",
  "DeveloperName": "SkipPricingAndTaxStep",
  "MasterLabel": "SkipPricingAndTaxStep",
  "RuleEngine": "StandardConfigurator",
  "PricingPreference": "Skip",
  "TaxPreference": "Skip"
}
```

Here's a sample payload that specifies a value for rating preference and the
steps to skip for each sales transaction
record.

```
{
  "SaveType": "Standard",
  "Description": "Setup for Transaction Processing Type",
  "DeveloperName": "SkipPricingAndTaxStep",
  "MasterLabel": "SkipPricingAndTaxStep",
  "RuleEngine": "StandardConfigurator",
  "PricingPreference": "Skip",
  "TaxPreference": "Skip",
  "RatingPreference": "Fetch"
}
```
