public interface IRevenueOwnerMdtSelector {
    List<ROCountryAugmentation__mdt> getEligibleCountries();
    ROCountryAugmentation__mdt getSupplementalData(String countryIsoCode);
    List<ROCountryAugmentation__mdt> getSupplementalDataList(Set<String> countryIsoCodes);
    List<ROCountryAddressField__mdt> getDefaultAddressFieldData();
    List<ROCountryAddressField__mdt> getAddressFieldDataForCountry(String countryIsoCode);
}