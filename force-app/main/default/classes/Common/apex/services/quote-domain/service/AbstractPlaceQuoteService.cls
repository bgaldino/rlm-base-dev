public with sharing abstract class AbstractPlaceQuoteService implements IPlaceQuoteService {

    public virtual PlaceQuoteServiceResponse placeQuote(PlaceQuoteServiceRequest request) {
        throw new NotImplementedException();   
    }

    public virtual void refreshPrices(List<Id> quoteIds) {
        throw new NotImplementedException();
    }
}