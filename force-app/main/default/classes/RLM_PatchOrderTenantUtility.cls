public with sharing class RLM_PatchOrderTenantUtility {
    @InvocableMethod(label = 'Set Order Item Tenant Info' description='Set Tenant Environment Lookup on Order Item through Place Order API' category='RLM SE TAT')
    public static void callOrderPatchTenantInfo(List<OrderRecordInput> inputs){
        Http http = new Http();
        HttpRequest httpRequest = new HttpRequest();
        httpRequest.setMethod('POST');
//        httpRequest.setHeader('Authorization', 'OAuth ' + UserInfo.getSessionId());
//        httpRequest.setHeader('Authorization', 'Bearer ' + UserInfo.getSessionId());
        httpRequest.setHeader('Content-Type', 'application/json');

        system.debug('OAuth + Bearer Token is ' + UserInfo.getSessionId());

        RLM_PlaceOrderModel requestBody = buildRequestBodyObject(inputs.get(0).inputOrder, inputs.get(0).inputOrderItems, inputs.get(0).tenantEnvironmentId);

        httpRequest.setBody(JSON.serialize(requestBody));

        System.debug(JSON.serializePretty(requestBody));

        httpRequest.setEndpoint('callout:RLM/commerce/sales-orders/actions/place');

        HttpResponse response = http.send(httpRequest);

        system.debug('API response is: ' + response.getStatusCode());

    }

    public static RLM_PlaceOrderModel buildRequestBodyObject(Order inputOrder, List<OrderItem> inputOrderItems, String tenantEnvironmentId){
        RLM_PlaceOrderModel requestBody = new RLM_PlaceOrderModel();

        requestBody.pricingPref = 'System';
        requestBody.configurationInput = 'RunAndAllowErrors';

        Map<String, Boolean> optionConfigs = new Map<String, Boolean>();

        optionConfigs.put('validateProductCatalog', true);
        optionConfigs.put('validateAmendRenewCancel', true);
        optionConfigs.put('executeConfigurationRules', true);
        optionConfigs.put('addDefaultConfiguration', true);

        requestBody.configurationOptions = optionConfigs;

        requestBody.graph = new RLM_PlaceOrderModel.OrderGraphModel();

        requestBody.graph.graphId = 'updateOrder';

        requestBody.graph.records = new List<RLM_PlaceOrderModel.ObjectRecordModel>();

        RLM_PlaceOrderModel.ObjectRecordModel orderModel = new RLM_PlaceOrderModel.ObjectRecordModel();

        orderModel.referenceId = inputOrder.Id;

        Map<String, String> orderAttrMap = new Map<String, String>();

        orderAttrMap.put('type', 'Order');
        orderAttrMap.put('method', 'PATCH');
        orderAttrMap.put('id', inputOrder.Id);

        orderModel.record = new Map<String, Object>();

        orderModel.record.put('attributes', orderAttrMap);

        requestBody.graph.records.add(orderModel);

        if(inputOrderItems.size() > 0){
            for(OrderItem inputOrderLine: inputOrderItems){
                RLM_PlaceOrderModel.ObjectRecordModel orderLineModel = new RLM_PlaceOrderModel.ObjectRecordModel();
                orderLineModel.referenceId = inputOrderLine.Id;
                Map<String, String> oiAttrMap = new Map<String, String>();

                oiAttrMap.put('type', 'OrderItem');
                oiAttrMap.put('method', 'PATCH');
                oiAttrMap.put('id', inputOrderLine.Id);

                orderLineModel.record = new Map<String, Object>();

                orderLineModel.record.put('attributes', oiAttrMap);

                requestBody.graph.records.add(orderLineModel);
            }
        }

        return requestBody;

    }

    public class OrderRecordInput{
        @InvocableVariable
        public Order inputOrder;

        @InvocableVariable
        public List<OrderItem> inputOrderItems;

        @InvocableVariable
        public String tenantEnvironmentId;
    }
}