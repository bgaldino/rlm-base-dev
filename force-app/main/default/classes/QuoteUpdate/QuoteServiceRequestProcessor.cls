public with sharing class QuoteServiceRequestProcessor {
    private IQuoteDAO quoteDAO;
    
    public QuoteServiceRequestProcessor() {
        this((IQuoteDAO)ServiceRegistry.getInstance('IQuoteDAO'));
    }
    
    public QuoteServiceRequestProcessor(IQuoteDAO quoteDAO) {
        this.quoteDAO = quoteDAO;
    }
    
     public void quoteUpdate(QuoteServiceRequest request){
        List<Quote> quotes = new List<Quote>();
        for(QuoteRecord currentquote: request.quoteRecords){
            Quote newQuoteObj = updateQuoteFromCurrenQuote(currentquote);
            quotes.add(newQuoteObj);
        }
        
        SObjectAccessDecision securityDecision = Security.stripInaccessible(AccessType.UPDATABLE, quotes);
        if(!securityDecision.getRecords().isEmpty()){
            quoteDAO.quoteUpdate(securityDecision.getRecords());
        }
    }
    
    private Quote updateQuoteFromCurrenQuote(QuoteRecord currentquote){
        Quote newQuoteObj = new Quote();
        newQuoteObj.Id = currentquote.quoteId;
        if(currentquote.importStatus != null){
            newQuoteObj.ImportStatus__c = currentquote.importStatus;
        }
        if(currentquote.importCompletionDate != null){
            newQuoteObj.ImportCompletionDate__c = currentquote.importCompletionDate;
        }
        if(currentquote.rejectReason != null){
            newQuoteObj.RejectionReason__c = currentquote.rejectReason;
        }
        if(currentquote.status != null){
            newQuoteObj.Status = currentquote.status;
        }
        if(currentquote.substatus != null){
            newQuoteObj.SubStatus__c = currentquote.substatus;
        }
        if(currentquote.hasProductRuleErrors != null){
            newQuoteObj.HasProductRuleErrors__c = currentquote.hasProductRuleErrors;
        }
        if(currentquote.autoRollDate != null){
            newQuoteObj.AutoRollDate__c = currentquote.autoRollDate;
        }
        return newQuoteObj;
    }
}