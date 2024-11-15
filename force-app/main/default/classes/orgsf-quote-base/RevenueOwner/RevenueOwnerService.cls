public with sharing class RevenueOwnerService extends AbstractRevenueOwnerService implements ICacheManager {
    private static final String CACHE_PARTITION_NAME = 'local.RevenueOwnerCache';
    private static final String REVENUE_OWNER_MAPPING_KEY = 'RevenueOwnerMappings';
    private static final Integer CACHE_TTL_SEC = 86400;
    private static final String SETTING_CACHED_VALUE_FOR = 'Setting Cached Value for ';

    IChapiClient chapiClient;
    IRevenueOwnerMdtSelector revenueOwnerMdtSelector;
    public RevenueOwnerService() {
        this((IChapiClient) ServiceRegistry.getInstance('IChapiClient'), (IRevenueOwnerMdtSelector) ServiceRegistry.getInstance('IRevenueOwnerMdtSelector'));
    }

    public RevenueOwnerService(IChapiClient chapiClient, IRevenueOwnerMdtSelector revenueOwnerMdtSelector) {
        this.chapiClient = chapiClient;
        this.revenueOwnerMdtSelector = revenueOwnerMdtSelector;
    }

    //Use as Singleton
    private Cache.OrgPartition orgPartition;
    private Cache.OrgPartition getPartition() {
        if (orgPartition == null) {
            orgPartition = Cache.Org.getPartition(CACHE_PARTITION_NAME);
        }
        return orgPartition;
    }

    public override Set<RevenueOwnerCountry> getQuotableCountries() {
        Set<RevenueOwnerCountry> revenueOwnerCountrySet = new Set<RevenueOwnerCountry>();
        List<ROCountryAugmentation__mdt> augmentationData = revenueOwnerMdtSelector.getEligibleCountries();
        for (ROCountryAugmentation__mdt augmentation : augmentationData) {
            RevenueOwnerCountry revenueOwnerCountry = new RevenueOwnerCountry();
            revenueOwnerCountry.isoCode = augmentation.CountryISOCode__c;
            revenueOwnerCountry.name = augmentation.CountryName__c;
            revenueOwnerCountrySet.add(revenueOwnerCountry);
        }
        return revenueOwnerCountrySet;
    }

    public override Map<String, List<RevenueOwnerCountry>> getRevenueOwnerMappings() {
        Object revenueOwnerMappingsObj = getValueForKey(REVENUE_OWNER_MAPPING_KEY);
        if (revenueOwnerMappingsObj != null) {
            return (Map<String, List<RevenueOwnerCountry>>) revenueOwnerMappingsObj;
        }

        Map<String, List<RevenueOwnerCountry>> revenueOwnerMappings = new Map<String, List<RevenueOwnerCountry>>();

        Set<RevenueOwnerCountry> eligibleCountries = this.getQuotableCountries();
        for (RevenueOwnerCountry country : eligibleCountries) {
            String revenueOwner = this.getRevenueOwner(country.isoCode);

            if (!revenueOwnerMappings.containsKey(revenueOwner)) {
                revenueOwnerMappings.put(revenueOwner, new List<RevenueOwnerCountry>());
            }
            revenueOwnerMappings.get(revenueOwner).add(country);
        }

        System.debug(SETTING_CACHED_VALUE_FOR + REVENUE_OWNER_MAPPING_KEY);
        getPartition().put(REVENUE_OWNER_MAPPING_KEY, revenueOwnerMappings, CACHE_TTL_SEC);

        return revenueOwnerMappings;
    }

    public override RevenueOwnerCountryDetail getRevenueOwnerDetailsByCountryIsoCode(String countryIsoCode) {
        return augmentChapiCountry(this.getChapiCountry(countryIsoCode));
    }

    public override List<RevenueOwnerCountry> getSupportedCountriesPerCurrency(String currencyCode) {
        Set<RevenueOwnerCountry> revenueOwnerCountries = this.getQuotableCountries();
        List<RevenueOwnerCountry> countriesPerCurrency = new List<RevenueOwnerCountry>();
        for (RevenueOwnerCountry revCountry : revenueOwnerCountries) {
            List<SupportedCurrency> supportedCurrencies = this.getSupportedCurrencies(revCountry.isoCode);
            for (SupportedCurrency suppCurrency : supportedCurrencies) {
                if (suppCurrency.currencyCode.equals(currencyCode) && !countriesPerCurrency.contains(revCountry)) {
                    countriesPerCurrency.add(revCountry);
                }
            }
        }
        return countriesPerCurrency;
    }

    public override List<SupportedCurrency> getSupportedCurrencies(String countryIsoCode) {
        RevenueOwnerCountryDetail revenueOwnerCountryDetail = getRevenueOwnerDetailsByCountryIsoCode(countryIsoCode);
        return revenueOwnerCountryDetail.supportedCurrencies;
    }

    public override List<String> getBusinessTypes(String countryIsoCode) {
        RevenueOwnerCountryDetail revenueOwnerCountryDetail = getRevenueOwnerDetailsByCountryIsoCode(countryIsoCode);
        return revenueOwnerCountryDetail.businessTypes;
    }

    public override List<String> getPaymentMethods(String countryIsoCode) {
        RevenueOwnerCountryDetail revenueOwnerCountryDetail = getRevenueOwnerDetailsByCountryIsoCode(countryIsoCode);
        return revenueOwnerCountryDetail.paymentMethods;
    }

    public override String getRevenueOwner(String countryIsoCode) {
        RevenueOwnerCountryDetail revenueOwnerCountryDetail = getRevenueOwnerDetailsByCountryIsoCode(countryIsoCode);
        return revenueOwnerCountryDetail.revenueOwner;
    }

    public override TaxInformation getTaxInformation(String countryIsoCode) {
        RevenueOwnerCountryDetail revenueOwnerCountryDetail = getRevenueOwnerDetailsByCountryIsoCode(countryIsoCode);
        return revenueOwnerCountryDetail.taxInformation;
    }

    public override ZipCodeMetadata getZipCodeMetadata(String countryIsoCode) {
        RevenueOwnerCountryDetail revenueOwnerCountryDetail = getRevenueOwnerDetailsByCountryIsoCode(countryIsoCode);
        return revenueOwnerCountryDetail.zipCodeMetadata;
    }

    public override List<StateProvinceMetadata> getStateProvinceMetadataList(String countryIsoCode) {
        RevenueOwnerCountryDetail revenueOwnerCountryDetail = getRevenueOwnerDetailsByCountryIsoCode(countryIsoCode);
        return revenueOwnerCountryDetail.stateProvinceMetadataList;
    }

    public override MerchantInfo getMerchantInfo(String countryIsoCode, String currencyCode) {
        String cacheKey = countryIsoCode + currencyCode;

        Map<String, Object> chapiCountry = (Map<String, Object>)getValueForKey(cacheKey);
        if (chapiCountry != null) {
            return RevenueOwnerServiceHelper.unwrapMerchantInfo(chapiCountry);
        }

        chapiCountry = this.chapiClient.callCountryRESTService(countryIsoCode, currencyCode);

        if (chapiCountry != null) {
            System.debug(SETTING_CACHED_VALUE_FOR + cacheKey);
            getPartition().put(cacheKey, chapiCountry, CACHE_TTL_SEC);
        }
        return RevenueOwnerServiceHelper.unwrapMerchantInfo(chapiCountry);
    }

    private Map<String, Object> getChapiCountry(String countryIsoCode) {
        Map<String, Object> chapiCountry = (Map<String, Object>) getValueForKey(countryIsoCode);
        if (chapiCountry != null) {
            return chapiCountry;
        }

        chapiCountry = this.chapiClient.callCountryRESTService(countryIsoCode);

        if (chapiCountry != null) {
            System.debug(SETTING_CACHED_VALUE_FOR + countryIsoCode);
            getPartition().put(countryIsoCode, chapiCountry, CACHE_TTL_SEC);
        }
        return chapiCountry;
    }

    public override Map<String, Object> validateTaxId(TaxValidationReqItem requestItem) {
        Map<String, Object> chapiTaxValidate = (Map<String, Object>) getValueForKey(requestItem.taxId);
        if (chapiTaxValidate != null) {
            return chapiTaxValidate;
        }
        chapiTaxValidate = this.chapiClient.callValidateTaxId(requestItem);

        if (chapiTaxValidate != null) {
            getPartition().put(requestItem.taxId, chapiTaxValidate, CACHE_TTL_SEC);
        }

        return chapiTaxValidate;
    }

    private RevenueOwnerCountryDetail augmentChapiCountry(Map<String, Object> chapiCountry) {
        ROCountryAugmentation__mdt augmentationData = revenueOwnerMdtSelector.getSupplementalData(RevenueOwnerServiceHelper.unwrapISOCode(chapiCountry));
        return RevenueOwnerServiceHelper.makeRevenueOwnerCountryDetail(chapiCountry, augmentationData);
    }

    //Implement the ICacheManager Interface
    public String getPartitionName() {
        return CACHE_PARTITION_NAME;
    }

    public Set<String> getKeys() {
        return getPartition().getKeys();
    }

    public Object getValueForKey(String key) {
        System.debug(key);
        if (getPartition().contains(key)) {
            System.debug('Using Cached Value for ' + key);
            return getPartition().get(key);
        }
        return null;
    }

    public Boolean deleteFromCache(String key) {
        return getPartition().remove(key);
    }
}
