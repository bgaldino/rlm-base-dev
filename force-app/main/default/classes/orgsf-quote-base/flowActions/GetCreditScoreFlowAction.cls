public with sharing class GetCreditScoreFlowAction {
    
    public class CreditScoreResult {
        @InvocableVariable
        public Integer creditScore;
        @InvocableVariable
        public String transactionID;

        public CreditScoreResult(Integer creditScore, String transactionID) {
            this.creditScore = creditScore;
            this.transactionID = transactionID;
        }
    }

    @InvocableMethod(label='Get Credit Score for the Account')
    public static List<CreditScoreResult> flowActionGetCreditScore(List<String> dunsNumberList) {
        List<CreditScoreResult> result = new List<CreditScoreResult>();
        for (String dunsNumber : dunsNumberList) {
            ICreditScoreService creditScoreService = (ICreditScoreService) ServiceRegistry.getInstance('ICreditScoreService');
            CreditScoreServiceRequestItem requestItem = new CreditScoreServiceRequestItem();
            requestItem.creditScoreId = dunsNumber;
            BaseRequest request = new BaseRequest();
            request.addRequestItem(requestItem); 
            IResponse resp = creditScoreService.getCreditScore(request);
            CreditScoreServiceResponseItem responseItem = (CreditScoreServiceResponseItem) resp.getResponseItems().get(0);            
            Integer creditScore = Integer.valueOf(responseItem.sfdcCreditScore);
            String transactionID = responseItem.creditScoreTransactionID;
            result.add(new CreditScoreResult(creditScore, transactionID));
        }
        return result;
    }
}