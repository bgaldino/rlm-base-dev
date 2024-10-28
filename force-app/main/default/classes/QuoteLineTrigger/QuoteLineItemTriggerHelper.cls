public class QuoteLineItemTriggerHelper {
    private static IQuoteDAO quoteDAO = (IQuoteDAO) ServiceRegistry.getInstance('IQuoteDAO');
    static List<String> QUOTE_STATUS = new List<String> {'Draft', 'Rejected'};
    static List<String> ACCOUNT_LDP_STATUS = new List<String> {'Denied', 'OEHU: Restricted-No Banner', 'OEHU: Restricted-Banner'};
    
    public static void validateQuoteLineItemDeletion(List<QuoteLineItem> oldQuoteLineItem) {
        if (oldQuoteLineItem == null || oldQuoteLineItem.size() == 0) { return; }
        if(hasCustomPermission('Override_Quote_Maintenance_Mode')) {return;}
        validateQuoteLocked(oldQuoteLineItem);
                 
    }
    
    public static void validateQuoteLocked (List<QuoteLineItem> oldQuoteLineItem){
        Set < Id > quoteIds = new Set < Id > ();
        for (QuoteLineItem quoteLine: oldQuoteLineItem) {
            quoteIds.add(quoteLine.QuoteId);
        }
        
        Map<Id,Quote> quoteMap = new Map<Id,Quote>(); 
        for(Quote quoteRecord : quoteDAO.getQuotesForSync(quoteIds)){
            quoteMap.put(quoteRecord.Id, quoteRecord);
        }
        for (QuoteLineItem qli :oldQuoteLineItem ){
                isMaintenanceModeEnabled(qli,quoteMap.get(qli.quoteId));
        }   
    }
    
    private static void isMaintenanceModeEnabled(QuoteLineItem qli, quote currentQuote){
        if(currentquote.MaintenanceModeEnabled__c){
            qli.addError(Label.MaintenanceModeErrorMessage );
            return;
        }
        if(hasCustomPermission('Quote_Edit_Access')) {return;}
        isQuoteLocked(qli,currentQuote);
    }
    
    @TestVisible
    private static void isQuoteLocked( QuoteLineItem qli, quote currentQuote){
        
        if(ACCOUNT_LDP_STATUS.contains(currentQuote.Opportunity.Account.LDP_Status__c) || !QUOTE_STATUS.contains(currentQuote.Status)){
            qli.addError(Label.QuoteLockingDeleteMessage);
        }
    }
    
    private static boolean hasCustomPermission(string permissionName){
        return FeatureManagement.checkPermission(permissionName);
    }
   
}