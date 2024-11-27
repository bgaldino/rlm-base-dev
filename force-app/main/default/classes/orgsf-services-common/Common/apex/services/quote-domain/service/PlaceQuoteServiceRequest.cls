public class PlaceQuoteServiceRequest {
    public PlaceQuote.PricingPreferenceEnum pricingPreference;
    public PlaceQuote.ConfigurationInputEnum configEnum;
    public PlaceQuote.ConfigurationOptionsInput config;
    public List<PlaceQuote.RecordWithReferenceRequest> records;
    public String method;
    public String graphId;
}