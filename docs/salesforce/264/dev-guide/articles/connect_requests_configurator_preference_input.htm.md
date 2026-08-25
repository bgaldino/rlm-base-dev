---
page_id: connect_requests_configurator_preference_input.htm
title: Configurator Preference Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configurator_preference_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Configurator Preference Input

Input representation of the configuration preference for the place sales transaction
    request.

**JSON example**

: 

```
{
  "configurationPref": {
    "configurationMethod": "Skip",
    "configurationOptions": {
      "validateProductCatalog": true,
      "validateAmendRenewCancel": true,
      "executeConfigurationRules": true,
      "addDefaultConfiguration": true
    }
  }
}
```

**Properties**

: 

                    

                    

                    
- 
- 
- 

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configuration​Method` | String | Configuration method for the place sales transaction request. Valid values are: `Force`—Specifies to enforce the predefined configuration process during the sales transaction process. `Skip`—Specifies to skip the configuration process during the quote creation process. `System`—Specifies the system to determine whether the configuration process is required. The default value is `Skip`. | Optional | 63.0 |
| `configuration​Options` | [Configuration Options Input](./connect_requests_configuration_options_input.htm.md) | Configuration options during the ingestion process. | Optional | 63.0 |
