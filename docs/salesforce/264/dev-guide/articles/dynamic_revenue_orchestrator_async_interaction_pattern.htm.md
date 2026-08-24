---
page_id: dynamic_revenue_orchestrator_async_interaction_pattern.htm
title: Asynchronous Interaction Pattern
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_async_interaction_pattern.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_callouts_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Asynchronous Interaction Pattern

To specify an asynchronous request, you must add the callback URI to the integration
    definition for Standard Fulfillment Provider or Apex Type Provider as an optional
    attribute.

    

## Standard Fulfillment Provider

      
      
        
- Provide the callback URI in the integration definition to accept the callback.

        
- Use these steps to set up the async callout.
            
  - 
              
                
    - Use the `ResponseUri` key to retrieve the
                  Callback URI value from the payload.

                
    - Use the `StepId` key to retrieve the
                  Fulfillment Step value from the payload. If order item ID is returned instead of
                  Fulfillment Step ID, use `CorrelationId` key to
                  extract the value of the step ID. For example, `callout:13Wxx0000004CAf:`.

                
    - Pass the StepId value to the callback URI endpoint. Return 202 response code to
                  ensure the Fulfillment Step is in `Running`
                  state. Otherwise, the 200 response code completes the step.

Here's a sample
                    payload.

```
{
    "ResponseUri": "/services/apexrest/async/callout",
    "StepId": "802xx000001nb1MAAQ",
    "CorrelationId": "callout:13Wxx0000004CAf:",
    ...//Other values
}
```

              

            

          

        
- Extract the step ID from the request. Find the Fulfillment Step ID in the org by using
          the extracted step ID and update the Fulfillment Step state to `Completed`.

      

    

    

## Apex Type Provider

      
      
        
- Provide the callback URI in the integration definition to accept the callback.

        
- Set up the async callout by using Apex Type Provider.
            
  - 
              
                
    - Create an Apex class that implements the `ProcessIntegrationProvider` interface.

Here's a sample that shows the
                    addition of a callback URI to the provider attribute for Apex Type
                  Provider.

global with sharing class DFOAsyncApexSample implements industriesintegrationfwk.ProcessIntegrationProvider {

    private static final industriesintegrationfwk.ApexProviderAttr NAMED_CRED_ATTR = 
        new industriesintegrationfwk.ApexProviderAttr('Named Credential', 
        'Named_Credential', 'DFOCalloutMockCreds', true, 'String');
 
    private static final industriesintegrationfwk.ApexProviderAttr CALLBACK_URL_ATTR = 
        new industriesintegrationfwk.ApexProviderAttr('Callback URL', 
        'Callback_URL', 'DFOCallbackUrl', true, 'String');

    global static List<industriesintegrationfwk.ApexProviderAttr> getProviderAttributes() {
        List<industriesintegrationfwk.ApexProviderAttr> defaults = new List<industriesintegrationfwk.ApexProviderAttr>();
        defaults.add(NAMED_CRED_ATTR);
        defaults.add(CALLBACK_URL_ATTR);
     
        return defaults;
    }
```

                
    - Specify the Fulfillment Step ID as the value of the `requestGuid` parameter of the `executeCallout` method. You can also extract the Step ID from the
                    `CorrelationId` key value. For example,
                    `"callout:13Wxx0000004CAf:"`.

Here's a
                    sample payload that assigns the provider attribute
                  values.

public interface ProcessIntegrationProvider {
    IntegrationCalloutResponse executeCallout(String requestGuid, 
    String inputRecordId, String payload, Map<String, Object> attributes);

    List<ProviderAttr> getProviderAttributes();
}
```

              

            

            
  - Set response code to 202 to indicate that the callout is asynchronously executed and
              in `Processing` state.

Here's a sample payload
                that sets the response
              code.

global with sharing class DFOAsyncApexSample implements industriesintegrationfwk.ProcessIntegrationProvider {
...
IntegrationCalloutResponse executeCallout(String requestGuid, 
    String inputRecordId, String payload, Map<String, Object> attributes){
    // execute http request
    ...
    // set accepted if no failures
    IntegrationCalloutResponse acceptedResponse = 
        new IntegrationCalloutResponse(true);
    acceptedResponse.setResponseCode(202);
    
    return new IntegrationCalloutResponse();
    }
}

```

            
  - The callback URI is visible in the integration definition.
                
              

          

        
- Extract the step ID from the request. Find the Fulfillment Step ID in the org by using
          the extracted step ID and update the Fulfillment Step state to `Completed`.

```
FulfillmentStep step = new FulfillmentStep(id = 'stepId', State = 'Completed'); 
upsert step;
```
