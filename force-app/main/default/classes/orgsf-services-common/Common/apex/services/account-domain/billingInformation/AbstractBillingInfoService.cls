public with sharing abstract class AbstractBillingInfoService implements IBillingInfoService {
    public virtual IResponse createBillingInformation(IRequest request) {
        throw new NotImplementedException();
    }
    public virtual IResponse updateBillingInformation(IRequest request) {
        throw new NotImplementedException();
    }
    public virtual List<BillingInformation> getBillingInformation(Id accountId, String country, String billingCurrency) {
        throw new NotImplementedException();
    }
}