public interface IRevenueOwnerService {
    Set<RevenueOwnerCountry> getQuotableCountries();
    Map<String, List<RevenueOwnerCountry>> getRevenueOwnerMappings();
    RevenueOwnerCountryDetail getRevenueOwnerDetailsByCountryIsoCode(String countryIsoCode);
    List<SupportedCurrency> getSupportedCurrencies(String countryIsoCode);
    List<String> getBusinessTypes(String countryIsoCode);
    List<String> getPaymentMethods(String countryIsoCode);
    String getRevenueOwner(String countryIsoCode);
    TaxInformation getTaxInformation(String countryIsoCode);
    ZipCodeMetadata getZipCodeMetadata(String countryIsoCode);
    List<StateProvinceMetadata> getStateProvinceMetadataList(String countryIsoCode);
    List<RevenueOwnerCountry> getSupportedCountriesPerCurrency(String currencyCode);
    //Deprecated
    MerchantInfo getMerchantInfo(String countryIsoCode);
    MerchantInfo getMerchantInfo(String countryIsoCode, String currencyCode);
}
