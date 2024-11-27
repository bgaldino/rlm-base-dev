public interface IEntitlementValidationService {
    EntitlementValidationServiceRequest populateRequest(Id businessObjectId);
    EntitlementValidationServiceResponse processValidations(EntitlementValidationServiceRequest request);                                                            
}