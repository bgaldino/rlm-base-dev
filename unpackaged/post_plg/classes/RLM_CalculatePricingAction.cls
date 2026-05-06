public with sharing class RLM_CalculatePricingAction {

    public class Request {
        @InvocableVariable(label='Product Name' required=true)
        public String productName;
        @InvocableVariable(label='Quantity' required=true)
        public Integer quantity;
        @InvocableVariable(label='Billing Frequency (monthly/annual)')
        public String billingFrequency;
        @InvocableVariable(label='Pricebook ID')
        public String pricebookId;
    }

    public class Result {
        @InvocableVariable(label='Pricing JSON')
        public String pricingJson;
        @InvocableVariable(label='Total Amount')
        public Decimal totalAmount;
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;
        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Calculate Pricing (RLM)'
        description='POST /connect/core-pricing/pricing — Calculates real-time pricing via Revenue Cloud'
        category='Revenue Cloud'
    )
    public static List<Result> execute(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            Result res = new Result();
            try {
                Map<String, Object> pricingReq = new Map<String, Object>{
                    'pricingFlow' => 'GET_PRICE',
                    'lineItems' => new List<Map<String, Object>>{
                        new Map<String, Object>{
                            'productName' => req.productName,
                            'quantity' => req.quantity,
                            'billingFrequency' => String.isNotBlank(req.billingFrequency)
                                ? req.billingFrequency : 'monthly'
                        }
                    }
                };
                if (String.isNotBlank(req.pricebookId)) {
                    pricingReq.put('listPricebookId', req.pricebookId);
                }
                Map<String, Object> response = RLM_RevenueCloudService.calculatePricing(pricingReq);
                res.pricingJson = JSON.serialize(response);
                res.totalAmount = response.containsKey('totalAmount')
                    ? (Decimal) response.get('totalAmount') : 0;
                res.isSuccess = true;
            } catch (Exception e) {
                res.isSuccess = false;
                res.errorMessage = e.getMessage();
            }
            results.add(res);
        }
        return results;
    }
}