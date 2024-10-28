public interface IChapiClient {
    Map<String, Object> callCountryRESTService(String countryIsoCode);
    Map<String, Object> callCountryRESTService(String countryIsoCode, String currencyCode);
    Map<String, Object> callValidateTaxId( TaxValidationReqItem requestItem);
}