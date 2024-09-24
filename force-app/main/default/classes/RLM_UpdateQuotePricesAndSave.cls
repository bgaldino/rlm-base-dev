public class RLM_UpdateQuotePricesAndSave {
    public Id quoteId;
    public RLM_UpdateQuotePricesAndSave(ApexPages.StandardController controller) {
        Quote quot = (Quote) controller.getRecord();
        quoteId = quot.Id;
    }
    public void updateQuotePrices() {
        Id qId = quoteId;// quote id from the VF page / APEX class
        // since we'll be calling with an empty quote header, need to tell the system to force pricing
        PlaceQuote.PricingPreferenceEnum pricingPreference = PlaceQuote.PricingPreferenceEnum.FORCE;
        PlaceQuote.ConfigurationInputEnum configEnum = PlaceQuote.ConfigurationInputEnum.RunAndAllowErrors;
        PlaceQuote.ConfigurationOptionsInput config = new PlaceQuote.ConfigurationOptionsInput();
        config.addDefaultConfiguration = true;
        config.executeConfigurationRules = true;
        config.validateAmendRenewCancel = true;
        config.validateProductCatalog = true;
        PlaceQuote.RecordResource quoteRecord = new PlaceQuote.RecordResource(Quote.getSobjectType(), 'PATCH', qId);
        PlaceQuote.RecordWithReferenceRequest quoteObject = new PlaceQuote.RecordWithReferenceRequest('refQuote', quoteRecord);
        // create the empty object graph w/only a reference to the quote
        List<PlaceQuote.RecordWithReferenceRequest> records = new List<PlaceQuote.RecordWithReferenceRequest>();
        records.add(quoteObject);

        // Invoke the Place Quote API
        PlaceQuote.GraphRequest graph = new PlaceQuote.GraphRequest('myGraphId', records);
        PlaceQuote.PlaceQuoteResponse resp = PlaceQuote.PlaceQuoteRLMApexProcessor.execute(pricingPreference, graph, configEnum, config);
        // check for errors
        System.debug('response ' + resp);
    }
}