public with sharing class GetSupportedCountriesFlowAction {
    @InvocableMethod(label='Get Supported Countries Per Currency')
    public static List<String> flowActionGetSupportedCountriesPerCurrency(List<String> currencyList) {
        List<String> result = new List<String>();
        for (String curr : currencyList) {
            IRevenueOwnerService revenueOwnerService = (IRevenueOwnerService) ServiceRegistry.getInstance('IRevenueOwnerService');
            List<RevenueOwnerCountry> supportedCountries = revenueOwnerService.getSupportedCountriesPerCurrency(curr);
            String countryString = '';
            for (RevenueOwnerCountry country : supportedCountries) {
                countryString += country.isocode + ',';
            }
            result.add(countryString);
        }
        return result;
    }
}