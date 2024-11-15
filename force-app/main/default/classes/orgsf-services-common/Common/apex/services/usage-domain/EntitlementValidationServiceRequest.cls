public class EntitlementValidationServiceRequest {
    
    public EntitlementValidationServiceRequest(){}

    public EntitlementValidationServiceRequest(List<UsageDetailsWrapper> usageDetailsWrapper, UsageDetailsTransactionType transactionType) {
        this.UsageDetailsWrapper = UsageDetailsWrapper;
        this.transactionType = transactionType;
        this.isValid = true;
    }

    public List<UsageDetailsWrapper> usageDetailsWrapper;
    public UsageDetailsTransactionType transactionType;
    public Id contractId;
    public Boolean isValid;
    public String quoteType;
    public String originalActionType;
    public List<EntitlementValidationType> validationsToPerform;
    public Map<String, String> mapUsageTypeVsEVSValidationsToPerform;
}