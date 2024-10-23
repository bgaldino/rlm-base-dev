public with sharing class RefreshPriceAction {

    public class RefreshPriceActionRequest {
        @InvocableVariable
        public Id quoteId;
    }
    
    @InvocableMethod(label='Refresh Price' description='Calls the place quote Apex API to refresh prices on quotes')
    public static void refreshPrices(List<RefreshPriceActionRequest> requests) {
        List<Id> quoteIds = new List<Id>();
        for (RefreshPriceActionRequest request : requests) {
            quoteIds.add(request.quoteId);
        }

        IPlaceQuoteService placeQuoteService = (IPlaceQuoteService) ServiceRegistry.getInstance('IPlaceQuoteService');
        placeQuoteService.refreshPrices(quoteIds);
    }
}