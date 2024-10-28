public with sharing class CreditScoreServiceResponseItem extends BaseResponseItem{
    
    public String nativeCreditScore { get; set; }
    public String sfdcCreditScore { get; set; }
    public String creditScoreTransactionID { get; set; }

    public CreditScoreServiceResponseItem(String requestId) {
        super(requestId);
    }   
}