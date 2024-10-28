public with sharing abstract class AbstractRevenueOwnerService implements IRevenueOwnerService {
    public virtual Set<RevenueOwnerCountry> getQuotableCountries() {
        throw new NotImplementedException();
    }

    public virtual Map<String, List<RevenueOwnerCountry>> getRevenueOwnerMappings() {
        throw new NotImplementedException();
    }

    public virtual RevenueOwnerCountryDetail getRevenueOwnerDetailsByCountryIsoCode(String countryIsoCode) {
        throw new NotImplementedException();
    }

    public virtual List<SupportedCurrency> getSupportedCurrencies(String countryIsoCode) {
        throw new NotImplementedException();
    }

    public virtual List<String> getBusinessTypes(String countryIsoCode) {
        throw new NotImplementedException();
    }

    public virtual List<String> getPaymentMethods(String countryIsoCode) {
        throw new NotImplementedException();
    }

    public virtual String getRevenueOwner(String countryIsoCode) {
        throw new NotImplementedException();
    }

    public virtual TaxInformation getTaxInformation(String countryIsoCode) {
        throw new NotImplementedException();
    }

    public virtual Map<String, Object> validateTaxId(TaxValidationReqItem requestItem) {
        throw new NotImplementedException();
    }

    public virtual ZipCodeMetadata getZipCodeMetadata(String countryIsoCode) {
        throw new NotImplementedException();
    }

    public virtual List<StateProvinceMetadata> getStateProvinceMetadataList(String countryIsoCode) {
        throw new NotImplementedException();
    }

    public virtual List<RevenueOwnerCountry> getSupportedCountriesPerCurrency(String currencyCode) {
        throw new NotImplementedException();
    }

    //Deprecated
    public virtual MerchantInfo getMerchantInfo(String countryIsoCode) {
        throw new NotImplementedException();
    }

    public virtual MerchantInfo getMerchantInfo(String countryIsoCode, String currencyCode) {
        throw new NotImplementedException();
    }
}
