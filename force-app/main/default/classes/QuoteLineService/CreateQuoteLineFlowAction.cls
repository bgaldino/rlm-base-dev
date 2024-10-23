public with sharing class CreateQuoteLineFlowAction {
    @InvocableMethod(label='Create Quote Lines From Oppotunity Lines')
    public static void flowActionCreateQuoteLines(List<CreateQuoteLineFlowActionRequest> requestList) {
        for (CreateQuoteLineFlowActionRequest request : requestList) {
            ITenantShellService tenantShellService = (ITenantShellService) ServiceRegistry.getInstance('ITenantShellService');
            Set<Id> productIds = getProductsFromQuoteLines(request.quoteLines);
            Map<Id, Id> defaultTenantMap = tenantShellService.findOrCreateDefaultTenant(request.accountId, productIds);
            List<QuoteLine> quoteLinesToCreate = toQuoteLinePOJO(request.quoteLines, defaultTenantMap);
            
            IQuoteLineService quoteLineService = (IQuoteLineService) ServiceRegistry.getInstance('IQuoteLineService');
            QuoteLineServiceRequest serviceRequest = new QuoteLineServiceRequest().createRequest(quoteLinesToCreate, request.quoteId);
            quoteLineService.createQuoteLines(serviceRequest);
        }
    }
    
    private static Set<Id> getProductsFromQuoteLines(List<QuoteLineItem> quoteLines) {
        Set<Id> productIds = new Set<Id>();
        for (QuoteLineItem qli : quoteLines) {
            productIds.add(qli.Product2Id);
        }
        return productIds;
    }
    
    private static List<QuoteLine> toQuoteLinePOJO(List<QuoteLineItem> quoteLines, Map<Id, Id> defaultTenantMap) {
        List<QuoteLine> quoteLinesToCreate = new List<QuoteLine>();
        Integer index = 0;
        for (QuoteLineItem qli : quoteLines) {
            QuoteLine quoteLinetoCreate = new QuoteLine(qli);
            quoteLinetoCreate.quoteLineId = String.valueOf(index++);
            quoteLinetoCreate.tenantId = defaultTenantMap.get(qli.Product2Id);
            quoteLinesToCreate.add(quoteLinetoCreate);
        }
        return quoteLinesToCreate;
    }
    
    public class CreateQuoteLineFlowActionRequest {
        @InvocableVariable(required=true)
        public List<QuoteLineItem> quoteLines;
        
        @InvocableVariable(required=true)
        public Id quoteId;
        
        @InvocableVariable(required=true)
        public Id accountId;
    }
}