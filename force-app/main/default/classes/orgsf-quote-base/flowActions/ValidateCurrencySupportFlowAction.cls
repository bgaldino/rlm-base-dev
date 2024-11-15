public with sharing class ValidateCurrencySupportFlowAction {
    @InvocableMethod(label='Validate if the currency is supported by the country')
    public static List<Boolean> flowActionValidateCurrencySupport(List<ValidateCurrencySupportFlowActionRequest> requestList) {
        List<Boolean> result = new List<Boolean>();
        for (ValidateCurrencySupportFlowActionRequest request : requestList) {
            IRevenueOwnerService revenueOwnerService = (IRevenueOwnerService)ServiceRegistry.getInstance('IRevenueOwnerService');
            List<SupportedCurrency> supportedCurrencies = revenueOwnerService.getSupportedCurrencies(request.country);
            for (SupportedCurrency supportedCurrency : supportedCurrencies) {
                if (supportedCurrency.currencyCode.equals(request.billingCurrency)) {
                    result.add(true);
                    return result;
                }
            }
            result.add(false);
        }
        return result;
    }

    public class ValidateCurrencySupportFlowActionRequest {
        @InvocableVariable(required=true)
        public String country;
        
        @InvocableVariable(required=true)
        public String billingCurrency;
    }
}