public interface IPlaceQuoteService {

    PlaceQuoteServiceResponse placeQuote(PlaceQuoteServiceRequest request);

    void refreshPrices(List<Id> quoteIds);

    PlaceQuote.PlaceQuoteResponse executePlaceQuoteRLMApexProcessor(PlaceQuoteServiceRequest serviceRequest);

}