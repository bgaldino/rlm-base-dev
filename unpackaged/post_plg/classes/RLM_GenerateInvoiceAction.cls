public with sharing class RLM_GenerateInvoiceAction {

    public class Request {
        @InvocableVariable(label='Sales Transaction ID' required=true)
        public String salesTransactionId;
        @InvocableVariable(label='Account ID' required=true)
        public String accountId;
    }

    public class Result {
        @InvocableVariable(label='Invoice ID')
        public String invoiceId;
        @InvocableVariable(label='Invoice Number')
        public String invoiceNumber;
        @InvocableVariable(label='Response JSON')
        public String responseJson;
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;
        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Generate Invoice (RLM)'
        description='POST /commerce/invoicing/invoices/collection/actions/generate — Generates an invoice'
        category='Revenue Cloud'
    )
    public static List<Result> execute(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            Result res = new Result();
            try {
                Map<String, Object> invoiceReq = new Map<String, Object>{
                    'salesTransactionId' => req.salesTransactionId,
                    'accountId' => req.accountId
                };
                Map<String, Object> response = RLM_RevenueCloudService.generateInvoice(invoiceReq);
                res.invoiceId = (String) response.get('id');
                res.invoiceNumber = (String) response.get('invoiceNumber');
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