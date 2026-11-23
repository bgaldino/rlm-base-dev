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

        HttpResponse response;
        try {
            Id orderId = resolveOrderId(inputRecordId);
            system.debug('Order to callout on is ' + orderId);
            response = makeCallout(orderId);
        } catch (TenantProvisioningException e) {
            return failure(400, e.getMessage());
        } catch (CalloutException e) {
            return failure(503, 'The tenant callout failed: ' + e.getMessage());
        }

        // Group response by groupId
        Map<String, Object> responseGroup = getResponseGroupAfterCallout(response);

        // Success is the HTTP status of the tenant service, not the mere fact that a callout was made.
        Boolean isSuccess = (Boolean) responseGroup.get('isSuccess');
        if (!isSuccess) {
            return failure(response.getStatusCode(), 'The tenant service answered HTTP ' + response.getStatusCode());
        }
        return new industriesintegrationfwk.IntegrationCalloutResponse(true);
    }

    /**
     * The order a tenant is created for: the order item's own order, or, for a fulfillment order line,
     * the order of the order item it was sourced from. Anything else cannot provision a tenant.
     */
    private static Id resolveOrderId(String inputRecordId) {
        if (String.isBlank(inputRecordId)) {
            throw new TenantProvisioningException('The input record id is missing');
        }
        Id sourceId;
        try {
            sourceId = Id.valueOf(inputRecordId);
        } catch (StringException e) {
            throw new TenantProvisioningException('The input record id is not a valid id: ' + inputRecordId);
        }
        String sourceObjectType = String.valueOf(sourceId.getSObjectType());
        system.debug('Source Object Type is ' + sourceObjectType);

        Id orderItemId;
        if (sourceObjectType == 'OrderItem') {
            orderItemId = sourceId;
        } else if (sourceObjectType == 'FulfillmentOrderLineItem') {
            List<FulfillmentLineSourceRel> lineSourceRels = [SELECT Id, SourceLineItemId, FulfilmentOrderLineId
                                                              FROM FulfillmentLineSourceRel
                                                              WHERE (SourceLineItem.Type = 'OrderItem' AND FulfilmentOrderLineId =: sourceId) LIMIT 1];
            if (lineSourceRels.isEmpty()) {
                throw new TenantProvisioningException('The fulfillment order line ' + sourceId + ' has no order item source');
            }
            orderItemId = lineSourceRels[0].SourceLineItemId;
        } else {
            throw new TenantProvisioningException('Unsupported source type ' + sourceObjectType + '; only order items and fulfillment order lines provision a tenant');
        }

        List<OrderItem> orderItems = [SELECT Id, OrderId
                                      FROM OrderItem
                                      WHERE Id =: orderItemId LIMIT 1];
        if (orderItems.isEmpty()) {
            throw new TenantProvisioningException('Order item ' + orderItemId + ' was not found');
        }
        return orderItems[0].OrderId;
    }

    private static industriesintegrationfwk.IntegrationCalloutResponse failure(Integer statusCode, String message) {
        industriesintegrationfwk.IntegrationCalloutResponse failed = new industriesintegrationfwk.IntegrationCalloutResponse(false);
        failed.setResponseCode(statusCode);
        failed.setErrorMessage(message);
        return failed;
    }

    private static Map<String, Object> getResponseGroupAfterCallout(HttpResponse response) {
        Map<String, Object> responseGroup = new Map<String, Object>();
        Integer statusCode = response.getStatusCode();
        responseGroup.put('isSuccess', statusCode >= 200 && statusCode < 300);
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

    public class TenantProvisioningException extends Exception {}

    public class TenantCreationInfo{
        public String orderId;
    }
}