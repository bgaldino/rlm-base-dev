global class RLM_DFOTenantProvisioningCallout implements industriesintegrationfwk.ProcessIntegrationProvider{

    private static final industriesintegrationfwk.ApexProviderAttr inputOrderIdTest = new industriesintegrationfwk.ApexProviderAttr('inputOrderId', 
    'inputOrderId', '', false, 'String');

    private static HttpResponse makeCallout(String inputOrderId){
        
        // Construct the request object
        String endPoint = 'callout:RLM/services/apexrest/QuantumBitTenantEnvironment/createNewTenant';
        HttpRequest request = new HttpRequest();
        request.setMethod('POST');
        request.setHeader('Content-Type', 'application/json');
        request.setHeader('Accept', 'application/json');
        request.setEndpoint(endPoint);

        TenantCreationInfo tci = new TenantCreationInfo();
        tci.orderId = inputOrderId;

        system.debug(JSON.serialize(tci));

        request.setBody(JSON.serialize(tci));
        
        // Send request
        HttpResponse response = new Http().send(request);
        return response;
    } 

    global static industriesintegrationfwk.IntegrationCalloutResponse executeCallout(String requestGuid, String inputRecordId, String payload, Map<String, Object> attributes) {
        system.debug('input record id is ' + inputRecordId);
        //Get Order

        //determine SObject source type
        Id sourceId = inputRecordId;
        String sourceObjectType = String.valueOf(sourceId.getSObjectType());

        system.debug('Source Object Type is ' + sourceObjectType);

        HttpResponse response = new HttpResponse();

        if(sourceObjectType == 'OrderItem'){
            OrderItem oi = [SELECT Id, OrderId
                                FROM OrderItem
                                WHERE Id =: inputRecordId LIMIT 1];
                                
            system.debug('Order to callout on is ' + oi.OrderId);

            response = makeCallout(oi.OrderId);
        }else if(sourceObjectType == 'FulfillmentOrderLineItem'){
            FulfillmentLineSourceRel lineSourceRel = [SELECT Id, SourceLineItemId, FulfilmentOrderLineId 
                                                        FROM FulfillmentLineSourceRel 
                                                        WHERE (SourceLineItem.Type = 'OrderItem' AND FulfilmentOrderLineId =: inputRecordId) LIMIT 1];
            
            OrderItem oi = [SELECT Id, OrderId
                            FROM OrderItem
                            WHERE Id =: lineSourceRel.SourceLineItemId LIMIT 1];
                                                        
            system.debug('Order to callout on is ' + oi.OrderId);
                        
            response = makeCallout(oi.OrderId);
        }
        
        // Group response by groupId 
        Map<String, Object> responseGroup = getResponseGroupAfterCallout(response);

        // Create IntegrationCalloutResponse Response
        industriesintegrationfwk.IntegrationCalloutResponse integrationCalloutResponse = new industriesintegrationfwk.IntegrationCalloutResponse(true);
//        integrationCalloutResponse.setReturnValue(responseGroup);
        return integrationCalloutResponse;
        
    }

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

    public List<industriesintegrationfwk.ApexProviderAttr> getProviderAttributes(){
        List<industriesintegrationfwk.ApexProviderAttr> defaults = new List<industriesintegrationfwk.ApexProviderAttr>();
//        defaults.add(inputOrderIdTest);
        return defaults;
    }

    public class TenantCreationInfo{
        public String orderId;
    }
}