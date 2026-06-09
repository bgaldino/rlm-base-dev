---
page_id: dynamic_revenue_orchestrator_apex_type_provider.htm
title: Apex Type Provider
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_apex_type_provider.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_callouts_overview.htm
fetched_at: 2026-06-09
---

# Apex Type Provider

Implement custom integration logic via Apex by using the Apex Type Provider. This
provider requires an Apex Integration Developer to implement a custom Apex adapter
interface.

Use a custom Apex adapter to:

- Include and use integration parameters in adapter implementations such as timeouts,
  credentials, and path.
- Generate and transform requests and responses via Omnistudio Integration Procedures or
  Extract, Transform, Load (ETL) libraries.
- Enable asynchronous interaction pattern.
- Enable request and response logging by implementing a specific Apex interface.
- Handle errors, and integrate with fallout rules.

To ‌configure the callout settings for Apex Type Provider, see [Configuration Steps](./dynamic_revenue_orchestrator_callout_configuration_steps.htm.md "Before you set up a callout provider, configure the callout settings. The settings include the creation of a named credential and an external credential, the creation of an integration definition, and the configuration of a fulfillment step definition.").

## Integration Adapter Implementation

Implement the `industriesintegrationfwk.ProcessIntegrationProvider` Apex interface. Use the
`industriesintegrationfwk.ApexProviderAttr`  class to
define and access the attribute values in the integration provider definition.

```
global with sharing class DROSampleOrderAdapter implements industriesintegrationfwk.ProcessIntegrationProvider {
    
    // Named credential attribute
    private static final String MOCK_CALLOUT_NAMED_CREDENTIAL = 'callout:DROOrderInterfaceNamedCred';
    private final static Integer TIMEOUT = 10000; // Request timeout in milliseconds, or can be defined on Integration Definition as an Attribute
    
    
    private static final industriesintegrationfwk.ApexProviderAttr NAMED_CRED_ATTR = new industriesintegrationfwk.ApexProviderAttr('Named Credential', 
    'Named_Credential', 'DROOrderInterfaceNamedCred', true, 'String');
    private static final industriesintegrationfwk.ApexProviderAttr ENDPOINT_ATTR = new industriesintegrationfwk.ApexProviderAttr('Endpoint URI', 
    'Endpoint_URI', '/v1/orderitems/', true, 'String');

    
    /**
     * @param requestGuid                 Request Globally Unique Identifier (GUID) provided by the client
     * @param inputRecordId               Input Record ID — value is taken from Fulfillment Step > Fulfillment Step Source > Source Line Item
     * @param payload                     Payload to be passed to the Provider Class (empty in DRO)
     * @param attributes                  Map of configuration attributes
     * @return IntegrationCalloutResponse Response sent to the client
    */
    global static industriesintegrationfwk.IntegrationCalloutResponse executeCallout(String requestGuid, String inputRecordId, String payload, Map<String, Object> attributes) {
        // create request
        String msgBody = '{\"message\":\"Hello\",' 
            + '\n\"requestGuid\":\"' + requestGuid + '\",\n'
            + '\n\"inputRecordId\":\"' + inputRecordId + '\",\n'
            + '\n\"payload\":\"' + payload + '\"}'            
            ;
        
        String endpointUri = (String) attributes.get('Endpoint_URI');

        // Make a call
        HttpResponse response = makeCallout(endpointUri, msgBody);
        // process response and pass details to the DRO Callout Step processor by using IntegrationCalloutResponse(isSuccess, ResponseCode, ErrorMessage)
 
         industriesintegrationfwk.IntegrationCalloutResponse integrationCalloutResponse = handleResponse(response); 

        return integrationCalloutResponse;
    }

    // define configurable attriobutes 
    global static List<industriesintegrationfwk.ApexProviderAttr> getProviderAttributes() {
        List<industriesintegrationfwk.ApexProviderAttr> defaults = new List<industriesintegrationfwk.ApexProviderAttr>();
        defaults.add(NAMED_CRED_ATTR);
        defaults.add(ENDPOINT_ATTR);
        // add any attributes such as endpoint, timeout, interface, and params
        // ...
        return defaults;
    }   

    // Call Mock Service API.
    private static HttpResponse makeCallout(String endpointUri, String msgBody) {
        
        // Construct the request object
        String endPoint = MOCK_CALLOUT_NAMED_CREDENTIAL + endpointUri;
        HttpRequest request = new HttpRequest();
        request.setMethod('POST');
        request.setHeader('Content-Type', 'application/json');
        request.setHeader('Accept', 'application/json');
        request.setEndpoint(endPoint);
        request.setTimeout(TIMEOUT);
        request.setBody(msgBody);
        
        // Send request
        HttpResponse response = new Http().send(request);
        return response;
    }
}
```

## Error Handling

This sample shows how to pass errors from response to orchestration via the `IntegrationResponse` interface in the Apex provider
implementation. See [ProcessIntegrationProvider Interface](https://help.salesforce.com/s/articleView?id=ind.consumption_framework_process_integration_provider_interface.htm&type=5&language=en_US "HTML (New Window)").

```
public static industriesintegrationfwk.IntegrationCalloutResponse handleResponse(HttpResponse response) { 
    
        industriesintegrationfwk.IntegrationCalloutResponse integrationCalloutResponse;
        
        Map<String, Object> responseGroup = getResponseGroupAfterCallout(response);
        
        if(response.getStatusCode() == 200)
        {
            // SUCCESS
            integrationCalloutResponse = new industriesintegrationfwk.IntegrationCalloutResponse(true);
                    integrationCalloutResponse.setResponseCode(response.getStatusCode());
              integrationCalloutResponse.setReturnValue(responseGroup);
        
        } else {
            //FAILURE - pass error to DRO Fallout Handling to apply Retry Policies
            integrationCalloutResponse = new industriesintegrationfwk.IntegrationCalloutResponse(false);
            integrationCalloutResponse.setResponseCode(response.getStatusCode());
            integrationCalloutResponse.setReturnValue(responseGroup);
            integrationCalloutResponse.setErrorMessage('Unable to process request.');
        }
        return integrationCalloutResponse;
        }
    
    // Process Response payLoad 
    private static Map<String, Object> getResponseGroupAfterCallout(HttpResponse response) {
        Map<String, Object> responseGroup = new Map<String, Object>();
        if (response.getStatusCode() == 200) {
            responseGroup.put('isSuccess', true);
        } else {
            responseGroup.put('isSuccess', false);
        }
        responseGroup.put('response', getResponseMap(response.getBody()));
        return responseGroup;
    }
    
    // Convert response string into Map 
    private static Map<String,Object> getResponseMap(String responseBody) {
        try {
            Map<String,Object> responseBodyMap = (Map<String,Object>) JSON.deserializeUntyped(responseBody);
            return responseBodyMap;
        } catch (Exception e) {
            Map<String, Object> responseMap = new Map<String,Object>();
            responseMap.put('response', responseBody);
            return responseMap;
        }
    }
```

The fulfillment step state changes to `Fatally Failed`,
and the error message is saved in the Execution Message field.

![A change of state in the Filfillment Step record page with Apex Service Type Provider.](/docs/resources/img/en-us/262.0?doc_id=dev_guides%2Frev_lifecycle_mgmt%2Fdynamic_revenue_orchestrator%2Fimages%2Fdynamic_revenue_orchestrator_callout_fulfillment_step.png&folder=revenue_lifecycle_management_dev_guide)

![A change of state in the Filfillment Plan record page with Apex Service Type Provider.](/docs/resources/img/en-us/262.0?doc_id=dev_guides%2Frev_lifecycle_mgmt%2Fdynamic_revenue_orchestrator%2Fimages%2Fdynamic_revenue_orchestrator_callout_fulfillment_plan.png&folder=revenue_lifecycle_management_dev_guide)

## Apex Advanced Interface Implementation

To use advanced features such as logging, the Apex provider must implement the Apex
Provider Advanced interface. You must use the HttpBaseProvider client for HTTP requests.

This example shows a sample of the `ProcessIntegrationProviderAdvanced` Apex interface implementation.

```
global with sharing class DFOApexVlocMockWithDelay
implements industriesintegrationfwk.ProcessIntegrationProviderAdvanced {
...
global static industriesintegrationfwk.IntegrationCalloutResponse executeCallout(String requestGuid, String inputRecordId, String payload, Map<String, Object> attributes,
industriesintegrationfwk.HttpBaseProvider httpProvider) {
...
String endPoint = MOCK_CALLOUT_NAMED_CREDENTIAL + '/delay/5';
HttpRequest request = new HttpRequest();
request.setMethod('POST');
request.setHeader('Content-Type', 'application/json');
request.setHeader('Accept', 'application/json');
request.setEndpoint(endPoint);
request.setTimeout(TIMEOUT);
request.setBody(msgBody);

// Send request
//HttpResponse response = httpProvider.httpCallout(request);
HttpResponse response = new Http().send(request);
```

## Integration Definition Configuration

Select the
**Save
the request and response as attachments to the record** checkbox for the
integration definition to save request and response payloads as attachments to the
Integration Provider Execution record. Content publish limits apply when saving request
and response payloads as attachments. Use [Shield
Platform Encryption](https://help.salesforce.com/s/articleView?id=xcloud.security_pe_overview.htm&type=5&language=en_US "HTML (New Window)") for secure storage of sensitive information.

See [Create an
Integration Definition](https://help.salesforce.com/s/articleView?id=ind.consumption_framework_integration_definitions.htm&type=5&language=en_US "HTML (New Window)").

## Log Records

Integration Provider execution records are created on every request and associated with the
fulfillment step. The referenced object identifier is set to order item or fulfillment order
line item ID. See[IntegrationProviderExecution](https://developer.salesforce.com/docs/atlas.en-us.262.0.sfFieldRef.meta/sfFieldRef/salesforce_field_reference_IntegrationProviderExecution.htm).

To view the Integration Provider execution records, configure the Fulfillment Step record
page to include the Integration Provider Executions related list by using Lightning App
Builder. See [Lightning App
Builder](https://help.salesforce.com/s/articleView?id=platform.lightning_app_builder_overview.htm&type=5&language=en_US "HTML (New Window)").

![The Lightning App Builder page to add the Integration Provider Executions related list to the Fulfillment Step record page.](/docs/resources/img/en-us/262.0?doc_id=dev_guides%2Frev_lifecycle_mgmt%2Fdynamic_revenue_orchestrator%2Fimages%2Fdynamic_revenue_orchestrator_fulfillment_step_record_page.png&folder=revenue_lifecycle_management_dev_guide)
