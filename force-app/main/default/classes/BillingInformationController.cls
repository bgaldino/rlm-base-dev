public class BillingInformationController {
    @AuraEnabled
    public static DynamicAddressSchema getAddressSchemaForCountry(String countryIsoCode) {
        IDynamicAddressService dynamicAddressService = (IDynamicAddressService)ServiceRegistry.getInstance('IDynamicAddressService');
        return dynamicAddressService.getAddressSchemaForCountry(countryIsoCode);
    }

    @AuraEnabled
    public static BaseResponse updateAddress(QuoteAddressRequestItem quoteAddressRequestItem) {
        IQuoteService quoteService = (IQuoteService)ServiceRegistry.getInstance('IQuoteService');

        BaseRequest updateAddressRequest = new BaseRequest();
        updateAddressRequest.addRequestItem(quoteAddressRequestItem);
        
        return quoteService.updateAddress(updateAddressRequest);
    }

    @AuraEnabled(cacheable=true)
    public static RevenueOwnerCountryDetail getRevenueOwnerDetails(String countryIsoCode) {
        RevenueOwnerService revenueOwnerService = (RevenueOwnerService) ServiceRegistry.getInstance('IRevenueOwnerService');
        RevenueOwnerCountryDetail roDetail = revenueOwnerService.getRevenueOwnerDetailsByCountryIsoCode(countryIsoCode);
        return roDetail;
    }
    
    @AuraEnabled
    public static List<StateProvinceMetadata> getStateInfo(String strCountry) {
        List<StateProvinceMetadata> listStateProvince = new List<StateProvinceMetadata>();

        try {
            IRevenueOwnerService revenueOwnerService = (IRevenueOwnerService) ServiceRegistry.getInstance('IRevenueOwnerService');
            listStateProvince = revenueOwnerService.getStateProvinceMetadataList(strCountry);
            listStateProvince.sort();
        } catch (Exception e) {
            System.debug('An error occurred while fetching state/province information: ' + e.getMessage());
        }
        return listStateProvince;
    }

    @AuraEnabled(cacheable=true)
    public static List<RevenueOwnerCountry> getQuotableCountries(){
        RevenueOwnerService revenueOwnerService = (RevenueOwnerService)ServiceRegistry.getInstance('IRevenueOwnerService');
        Set<RevenueOwnerCountry> countrySet = revenueOwnerService.getQuotableCountries();
        return new List<RevenueOwnerCountry>(countrySet);
    }

    @AuraEnabled
    public static List<String> getAllEligibleCountryIsoCodes(String countryIsoCode){
        RevenueOwnerService revenueOwnerService = (RevenueOwnerService) ServiceRegistry.getInstance('IRevenueOwnerService');
        String revOwner = revenueOwnerService.getRevenueOwner(countryIsoCode);
        Map<String, List<RevenueOwnerCountry>> revOwnerMappings = revenueOwnerService.getRevenueOwnerMappings();
        List<RevenueOwnerCountry> revOwnerCountries = revOwnerMappings.get(revOwner);
        List<String> isoCodes = new List<String>();
        for(RevenueOwnerCountry roc : revOwnerCountries){
            isoCodes.add(roc.isoCode);
        }
        return isoCodes;
    }
    
    @AuraEnabled
    public static Boolean isTrueUpSchedulePopulated(Id contractId){
        IConsumptionRateService consumptionRateService = (IConsumptionRateService) ServiceRegistry.getInstance('IConsumptionRateService');
        if(consumptionRateService.isTrueUpScheduleForAmendContract(contractId)){
            return true;
        }
        return false;
    }

    @AuraEnabled(cacheable=true)
    public static Boolean validateCurrencySupport(String billingCountry, String billingCurrency) {
        IRevenueOwnerService revenueOwnerService = (IRevenueOwnerService)ServiceRegistry.getInstance('IRevenueOwnerService');
        List<SupportedCurrency> supportedCurrencies = revenueOwnerService.getSupportedCurrencies(billingCountry);
        for (SupportedCurrency supportedCurrency : supportedCurrencies) {
            if (supportedCurrency.currencyCode.equals(billingCurrency)) {
                return true;
            }
        }
        return false;
    }

    @AuraEnabled
    public static BillingInfoServiceResponseItem createBillingInfoRecord(BillingInformation billingInfo) {
        BaseRequest request = new BaseRequest();
        request.addRequestItem(new BillingInfoServiceRequestItem(billingInfo));
        BillingInfoService billingInfoService = (BillingInfoService)ServiceRegistry.getInstance('IBillingInfoService');
        IResponse response = billingInfoService.createBillingInformation(request);
        List<IResponseItem> responseItems = response.getResponseItems();
        if (responseItems.size() == 0) {
            return null;
        }
        return (BillingInfoServiceResponseItem)responseItems.get(0);
   }

    @AuraEnabled
    public static Map<String,String> getProfileNames(List<String> profileLabels){
        try {
            IQuoteBaseQuery query = QuoteBaseQuery.getInstance();
            Map<String, String > profilesMap = new Map<String,String >();
            List<Application_Configuration__mdt> profiles = query.getApplicationConfigurationsByCategoriesAndFunctionalAreas(QuoteBaseConstants.APP_CONFIG_MDT_CATEGORIES, 
                                                                                                                            QuoteBaseConstants.APP_CONFIG_MDT_FUNCTIONAL_AREAS);
            if (profiles == null){
                throw new AuraHandledException('No Profile Names retrieved');
            }
            for (Application_Configuration__mdt profile : profiles){
                if (profileLabels.contains(profile.Label)){
                    profilesMap.put(profile.Label, profile.Value__c);
                }
            }
            return profilesMap;
        } catch (Exception e) {
            throw new AuraHandledException('Error retrieving Profile Name');
        }
    }
}
