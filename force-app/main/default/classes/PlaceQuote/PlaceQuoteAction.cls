public with sharing class PlaceQuoteAction {
    
    public class PlaceQuoteActionRequest {
        @InvocableVariable
        public Quote quote;
        @InvocableVariable
        public List<QuoteLineItem> quoteLineItemList;
    }

    public class PlaceQuoteActionResponse {
        @InvocableVariable
        public Id quoteId;
        @InvocableVariable
        public String errorMessage;
    }

    @InvocableMethod(label='Place Quote' description='Calls the place quote Apex API to create and update quotes')
    public static List<PlaceQuoteActionResponse> placeQuote(List<PlaceQuoteActionRequest> requests) {
        // Setup Response 
        PlaceQuoteActionResponse actionResponse = new PlaceQuoteActionResponse();

        PlaceQuoteActionRequest request = requests[0];

        PlaceQuoteServiceRequestBuilder.QuoteRequest quoteRequest = new PlaceQuoteServiceRequestBuilder.QuoteRequest();
        quoteRequest.quote = request.quote;
        quoteRequest.method = 'POST';

        List<PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest> quoteLineItemRequests = new List<PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest>();
        if (request.quoteLineItemList != null) {
            for (QuoteLineItem quoteLineItem : request.quoteLineItemList) {
                PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest quoteLineItemRequest = new PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest(); 
                quoteLineItemRequest.quoteLineItem = quoteLineItem;
                quoteLineItemRequest.method = 'POST';
                quoteLineItemRequests.add(quoteLineItemRequest);
            }
        }

        PlaceQuoteServiceRequest serviceRequest = new PlaceQuoteServiceRequestBuilder()
            .quote(quoteRequest)
            .quoteLineItems(quoteLineItemRequests)
            .graphId('createQuote')
            .method('POST')
            .pricingPreference(PlaceQuote.PricingPreferenceEnum.SYSTEM)
            .configEnum(PlaceQuote.ConfigurationInputEnum.RUNANDALLOWERRORS)
            .config(new PlaceQuote.ConfigurationOptionsInput())
            .build();

        IPlaceQuoteService placeQuoteService = (IPlaceQuoteService) ServiceRegistry.getInstance('IPlaceQuoteService');
        PlaceQuoteServiceResponse placeQuoteResponse = placeQuoteService.placeQuote(serviceRequest);
        if(placeQuoteResponse.success == false){
            if(placeQuoteResponse.responseError != null && !placeQuoteResponse.responseError.isEmpty()){
                PlaceQuoteServiceResponse.ResponseError resError = placeQuoteResponse.responseError[0];
                if(resError != null){
                    actionResponse.errorMessage = resError.message;
                }                
            }
        }
        else{
            actionResponse.quoteId = placeQuoteResponse.quoteId;
        }

        return new List<PlaceQuoteActionResponse> { actionResponse };
    }
}
