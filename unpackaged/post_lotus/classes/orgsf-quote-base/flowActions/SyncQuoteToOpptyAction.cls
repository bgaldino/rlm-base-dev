public with sharing class SyncQuoteToOpptyAction{
    
    @InvocableMethod(label='Sync Quote To Oppty Action')
    public static void syncQuoteToOppty(List<SyncQuoteToOpptyRequest> requests){
        AmendQuoteHelper.updateQuoteToOpptyAsync(requests[0].opptyId, requests[0].quoteId);
    }
    
    public class SyncQuoteToOpptyRequest {
        @InvocableVariable(required=true)
        public Id quoteId;
        
        @InvocableVariable(required=true)
        public Id opptyId;
        
    }
    
}