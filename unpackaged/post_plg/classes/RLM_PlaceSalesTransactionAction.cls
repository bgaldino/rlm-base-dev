public with sharing class RLM_PlaceSalesTransactionAction {

    public class Request {
        @InvocableVariable(label='Account ID' required=true)
        public String accountId;
        @InvocableVariable(label='Contact ID')
        public String contactId;
        @InvocableVariable(label='Opportunity ID')
        public String opportunityId;
        @InvocableVariable(label='Transaction Type (Trial/Quote/Subscription)' required=true)
        public String transactionType;
        @InvocableVariable(label='Product Name' required=true)
        public String productName;
        @InvocableVariable(label='Quantity')
        public Integer quantity;
        @InvocableVariable(label='Pricing Data JSON')
        public String pricingDataJson;
    }

    public class Result {
        @InvocableVariable(label='Transaction ID')
        public String transactionId;
        @InvocableVariable(label='Transaction Number')
        public String transactionNumber;
        @InvocableVariable(label='Response JSON')
        public String responseJson;
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;
        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Place Sales Transaction (RLM)'
        description='POST /connect/rev/sales-transaction/actions/place — Creates a quote or order via Revenue Cloud'
        category='Revenue Cloud'
    )
    public static List<Result> execute(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            Result res = new Result();
            try {
                Map<String, Object> lineItem = new Map<String, Object>{
                    'productName' => req.productName,
                    'quantity' => req.quantity != null ? req.quantity : 1
                };
                if (String.isNotBlank(req.pricingDataJson)) {
                    lineItem.put('pricingData',
                        JSON.deserializeUntyped(req.pricingDataJson));
                }

                Map<String, Object> txnReq = new Map<String, Object>{
                    'accountId' => req.accountId,
                    'status' => 'Draft',
                    'type' => req.transactionType,
                    'lineItems' => new List<Map<String, Object>>{ lineItem }
                };
                if (String.isNotBlank(req.contactId)) {
                    txnReq.put('contactId', req.contactId);
                }
                if (String.isNotBlank(req.opportunityId)) {
                    txnReq.put('opportunityId', req.opportunityId);
                }

                Map<String, Object> response = RLM_RevenueCloudService.placeSalesTransaction(txnReq);
                res.transactionId = (String) response.get('id');
                res.transactionNumber = (String) response.get('transactionNumber');
                res.responseJson = JSON.serialize(response);
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