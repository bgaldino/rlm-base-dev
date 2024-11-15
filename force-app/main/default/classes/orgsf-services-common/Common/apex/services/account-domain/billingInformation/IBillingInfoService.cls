public interface IBillingInfoService { 
    IResponse createBillingInformation(IRequest request);
    IResponse updateBillingInformation(IRequest request);
    List<BillingInformation> getBillingInformation(Id accountId, String country, String billingCurrency);
}