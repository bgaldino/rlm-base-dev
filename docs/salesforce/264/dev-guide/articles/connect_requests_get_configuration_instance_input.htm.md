---
page_id: connect_requests_get_configuration_instance_input.htm
title: Configuration Get Instance Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_get_configuration_instance_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Configuration Get Instance Input

Input representation of the request to get a product configuration instance.

**JSON example**

: 

```

{
"contextId": "008d27d7-e004-4906-a949-ee7d7c323c77"
}
```

**Properties**

: 

                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | Transaction context ID of the product configuration instance that’s to be fetched. | Required | 60.0 |
