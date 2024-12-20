public class EntitlementValidationServiceResponse {

    public EntitlementValidationServiceResponse(){}
    
    public EntitlementValidationServiceResponse(boolean isSuccess, List<UsageTypeValidationError> errors) {
        this.isSuccess = isSuccess;
        this.errors = errors;
    }

    public boolean isSuccess;
    public Set<String> errorMessages;
    public List<UsageTypeValidationError> errors;
}