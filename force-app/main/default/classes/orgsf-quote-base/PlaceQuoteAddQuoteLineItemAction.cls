public with sharing class PlaceQuoteAddQuoteLineItemAction {
    /**
     * @name PlaceQuoteAddQLActionRequest
     * @description This class is used as a request object for the PlaceQuoteAddQuoteLineItemAction.
     * It defines input parameters for the action, including a Quote and a list of Quote Line Items.
     */
    public class PlaceQuoteAddQLActionRequest {
        @InvocableVariable(label='Quote' description='The Quote to which the Quote Line Items will be added.' required=true)
        public Quote quote;
        @InvocableVariable(label='Quote Line Items' description='The list of Quote Line Items to be added to the Quote.' required=true)
        public List<QuoteLineItem> quoteLineItemList;
    }

    /**
     * @name PlaceQuoteAddQLActionResponse
     * @description This class is used as a response object for the PlaceQuoteAddQuoteLineItemAction.
     * It defines output parameters for the action, including the Id of the Quote, a success flag, an error message, and a list of error messages.
     */
    public class PlaceQuoteAddQLActionResponse {
        @InvocableVariable(label='Quote Id' description='The Id of the Quote.')
        public Id quoteId;
        @InvocableVariable(label='Success' description='Indicates whether the operation was successful.')
        public Boolean success;
        @InvocableVariable(label='Error Messages' description='A list of error messages if the operation was not successful.')
        public List<ErrorMessage> errorMessages = new List<ErrorMessage>();
    }

    /**
     * @name ErrorMessage
     * @description This class is used to define error messages with both an error message and an error code.
     */
    public class ErrorMessage {
        @InvocableVariable(label='Error Message' description='The error message.')
        public String errorMessage;
        @InvocableVariable(label='Error Code' description='The error code.')
        public String errorCode;

        /**
         * @name Constructor
         * @description This constructor is used to initialize an instance of the ErrorMessage class with an error message and an error code.
         * @param errorMessage The error message.
         * @param errorCode The error code.
         */
        public ErrorMessage(String errorMessage, String errorCode) {
            this.errorMessage = errorMessage;
            this.errorCode = errorCode;
        }
    }

    /**
     * @name placeQuote
     * @description This method is the main entry point of the action. It adds a Quote Line Item to a Quote.
     * @param requests A list of PlaceQuoteAddQLActionRequest objects containing the Quote and Quote Line Items to be added.
     * @return A list of PlaceQuoteAddQLActionResponse objects containing the results of the operation.
     */
    @InvocableMethod(label='Place Quote to add line items' description='Adds a Quote Line Item to a Quote.')
    public static List<PlaceQuoteAddQLActionResponse> placeQuote(List<PlaceQuoteAddQLActionRequest> requests) {

        PlaceQuoteAddQLActionResponse actionResponse = new PlaceQuoteAddQLActionResponse();
        List<PlaceQuoteAddQLActionResponse> actionResponseCollection = new List<PlaceQuoteAddQLActionResponse>();
        List<PlaceQuote.PlaceQuoteResponse> placeQuoteResponseCollection = new List<PlaceQuote.PlaceQuoteResponse>();

        for (PlaceQuoteAddQLActionRequest request : requests) {
            PlaceQuoteServiceRequestBuilder.QuoteRequest quoteRequest = new PlaceQuoteServiceRequestBuilder.QuoteRequest();
            quoteRequest.quote = request.quote;
            quoteRequest.method = 'PATCH';

            List<PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest> quoteLineItemRequests = new List<PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest>();
            if (request.quoteLineItemList != null) {
                for (QuoteLineItem quoteLineItem : request.quoteLineItemList) {
                    PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest quoteLineItemRequest = new PlaceQuoteServiceRequestBuilder.QuoteLineItemRequest(); 
                    quoteLineItemRequest.quoteLineItem = quoteLineItem;
                    quoteLineItemRequest.method = 'POST';
                    quoteLineItemRequests.add(quoteLineItemRequest);
                }
            }

            PlaceQuote.ConfigurationOptionsInput cInput = new PlaceQuote.ConfigurationOptionsInput();
            cInput.addDefaultConfiguration = true;
            cInput.executeConfigurationRules = true;
            cInput.validateAmendRenewCancel = true;
            cInput.validateProductCatalog = true;
            
            PlaceQuoteServiceRequest serviceRequest = new PlaceQuoteServiceRequestBuilder()
                .quote(quoteRequest)
                .quoteLineItems(quoteLineItemRequests)
                .graphId('CreateLineItem')
                .method('')
                .pricingPreference(PlaceQuote.PricingPreferenceEnum.SYSTEM)
                .configEnum(PlaceQuote.ConfigurationInputEnum.RUNANDALLOWERRORS)
                .config(cInput)
                .build();
            
            IPlaceQuoteService placeQuoteService = (IPlaceQuoteService) ServiceRegistry.getInstance('IPlaceQuoteService');
            placeQuoteResponseCollection.add(placeQuoteService.executePlaceQuoteRLMApexProcessor(serviceRequest));
        }

        for(PlaceQuote.PlaceQuoteResponse result : placeQuoteResponseCollection){
            actionResponse = new PlaceQuoteAddQLActionResponse();
            actionResponse.success = result.success;
            actionResponse.quoteId = result.quoteId;
            if(!result.success) {
           		for(ConnectApi.PlaceQuoteErrorResponse responseError : result.responseError){
                	actionResponse.errorMessages.add(new ErrorMessage(responseError.message, responseError.errorCode));
            	}   
            }
            actionResponseCollection.add(actionResponse);
        }
        return actionResponseCollection;
    }
}
