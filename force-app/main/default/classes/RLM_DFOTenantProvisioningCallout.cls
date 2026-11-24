/**
 * Deliberately system mode (WITH SYSTEM_MODE) and without sharing.
 * This class is outside rule 1 of apex-security-hardening (it is not an Aura, Invocable, Visualforce or
 * webservice entry); it is a DRO integration-provider step, so the system-mode justification rule (6) applies.
 * The record id is supplied by the fulfillment engine, not by a user. The user the step runs as is not
 * known from this repo, and the class has to read FulfillmentLineSourceRel and OrderItem (and is handed a
 * FulfillmentOrderLineItem id) to find the order id; under USER_MODE a missing read for that user would
 * fail a provisioning step that works today. It reads only the order id behind the step and sends it to the
 * QuantumBit tenant service.
 * 'without sharing' states what an undeclared entry-point class does today; 'with sharing' or
 * 'inherited sharing' could hide the order item from the fulfillment user.
 */
global without sharing class RLM_DFOTenantProvisioningCallout implements industriesintegrationfwk.ProcessIntegrationProvider{

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

        // Success is the HTTP status of the tenant service, not the mere fact that a callout was made.
        Integer statusCode = response.getStatusCode();
        if (statusCode < 200 || statusCode >= 300) {
            return failure(statusCode, 'The tenant service answered HTTP ' + statusCode + ': ' + bounded(response.getBody()));
        }
        industriesintegrationfwk.IntegrationCalloutResponse succeeded = new industriesintegrationfwk.IntegrationCalloutResponse(true);
        succeeded.setResponseCode(statusCode);
        return succeeded;
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
                                                              WHERE (SourceLineItem.Type = 'OrderItem' AND FulfilmentOrderLineId =: sourceId)
                                                              WITH SYSTEM_MODE LIMIT 1];
            if (lineSourceRels.isEmpty()) {
                throw new TenantProvisioningException('The fulfillment order line ' + sourceId + ' has no order item source');
            }
            orderItemId = lineSourceRels[0].SourceLineItemId;
        } else {
            throw new TenantProvisioningException('Unsupported source type ' + sourceObjectType + '; only order items and fulfillment order lines provision a tenant');
        }

        List<OrderItem> orderItems = [SELECT Id, OrderId
                                      FROM OrderItem
                                      WHERE Id =: orderItemId
                                      WITH SYSTEM_MODE LIMIT 1];
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

    /** The start of a response body, so a failed step says what the service answered without logging a whole page. */
    private static String bounded(String body) {
        return body == null ? '' : body.abbreviate(255);
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