public with sharing class CreateAmendQuoteLinesAction {

    @InvocableMethod(label='Create Amend Quote Lines')
    public static void createAmendQuoteLines(List<QuoteLineCreateRequest> requests){
        AmendQuoteHelper.createAmendQuoteLinesAsync(requests[0].opptyId, requests[0].quoteId, requests[0].assetProductIds);
    }


    public class QuoteLineCreateRequest {
        @InvocableVariable(required=true)
        public Id quoteId;
        
        @InvocableVariable(required=true)
        public Id opptyId;
        
        @InvocableVariable(required=true)
        public List<Id> assetProductIds;
    }
    
}