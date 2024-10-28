public interface IPlaceQuoteService {

    PlaceQuoteServiceResponse placeQuote(PlaceQuoteServiceRequest request);

    void refreshPrices(List<Id> quoteIds);

}