public abstract class AbstractEntitlementValidationService implements IEntitlementValidationService{
    public abstract EntitlementValidationServiceRequest populateRequest(Id businessObjectId);
    public abstract EntitlementValidationServiceResponse processValidations(EntitlementValidationServiceRequest request);
}