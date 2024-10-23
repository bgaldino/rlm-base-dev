public with sharing class QuoteLineServiceRequestProcessor {
    private IQuoteLineDAO quoteLineDAO;
    
    public QuoteLineServiceRequestProcessor() {
        this(new QuoteLineDAO());
    }
    
    public QuoteLineServiceRequestProcessor(IQuoteLineDAO quoteLineDAO) {
        this.quoteLineDAO = quoteLineDAO;
    }
    
    public void insertLines(QuoteLineServiceRequest request){
        List<QuoteLineItem> lines = new List<QuoteLineItem>();
        List<QuoteLineItem> existingQLIList = quoteLineDAO.getQuoteLinesByQuoteId(request.quoteId);
        if(existingQLIList == null){
            existingQLIList = new List<QuoteLineItem>();
        } 
        Integer lineNumber = existingQLIList.size()>0 ? existingQLIList.size():0;
        for(QuoteLine currentLine: request.quoteLines){
            lineNumber = lineNumber+1;
            currentLine.sortOrder = lineNumber;
            QuoteLineItem newLineObj = createQuoteLineItemFromCurrentLine(currentLine, request.quoteId);
            lines.add(newLineObj);
        }
        SObjectAccessDecision securityDecision = Security.stripInaccessible(AccessType.CREATABLE, lines);
        if(!securityDecision.getRecords().isEmpty()){
            quoteLineDAO.insertLines(securityDecision.getRecords());
        }
    }

    public void updateLines(QuoteLineServiceRequest request){
        List<QuoteLineItem> lines = new List<QuoteLineItem>();
        for(QuoteLine currentLine: request.quoteLines){
            QuoteLineItem newLineObj = updateQuoteLineItemFromCurrentLine(currentLine);
            lines.add(newLineObj);
        }
        SObjectAccessDecision securityDecision = Security.stripInaccessible(AccessType.UPDATABLE, lines);
        if(!securityDecision.getRecords().isEmpty()){
            quoteLineDAO.updateLines(securityDecision.getRecords());
        }
    }

    public void deleteLines(QuoteLineServiceRequest request){
        List<QuoteLineItem> lines = new List<QuoteLineItem>();
        for(QuoteLine currentLine: request.quoteLines){
            QuoteLineItem newLineObj = new QuoteLineItem();
            newLineObj.Id = currentLine.quoteLineId;
            lines.add(newLineObj);
        }
        quoteLineDAO.deleteLines(lines);
        updateQLIOrderAfterDelete(request.quoteId);
    }
    
    private void updateQLIOrderAfterDelete(Id quoteId){
        
        List<QuoteLineItem> qLIListAfterDelete = quoteLineDAO.getQuoteLinesByQuoteId(quoteId);
        List<QuoteLineItem> quoteLinesToUpdateList = new List<QuoteLineItem>();
        Integer lineNumber = 1;
        
        if(qLIListAfterDelete == null){
            qLIListAfterDelete = new List<QuoteLineItem>();
        }
        
        for(QuoteLineItem objQLI : qLIListAfterDelete){
            QuoteLineItem qLIObj = new QuoteLineItem();
            
            qLIObj.SortOrder = lineNumber;
            qLIObj.Id = objQLI.Id;
            lineNumber++;
            
            quoteLinesToUpdateList.add(qLIObj);
        }
        if(!quoteLinesToUpdateList.isEmpty()){
            SObjectAccessDecision securityDecision = Security.stripInaccessible(AccessType.UPDATABLE, quoteLinesToUpdateList);
            if(!securityDecision.getRecords().isEmpty()){
                quoteLineDAO.updateLines(securityDecision.getRecords());
            }
        } 
    }
    
    private QuoteLineItem createQuoteLineItemFromCurrentLine(QuoteLine currentLine, Id quoteId){
        QuoteLineItem newLineObj = new QuoteLineItem();
        newLineObj.QuoteId = quoteId;
        newLineObj.Product2Id = currentLine.product2Id;
        newLineObj.PricebookEntryId = currentLine.pricebookentryId;
        newLineObj.Quantity = currentLine.quantity;
        newLineObj.BillingFrequency = currentLine.billingFrequency;
        newLineObj.UnitPrice = currentLine.unitPrice;
        newLineObj.StartDate = currentLine.startDate;
        newLineObj.SubscriptionTerm = currentLine.subscriptionTerm;
        newLineObj.Discount = currentLine.discount;
        newLineObj.Tenant__c = currentLine.tenantId;
        newLineObj.SortOrder = currentLine.sortOrder;
        return newLineObj;
    }
    
    private QuoteLineItem updateQuoteLineItemFromCurrentLine(QuoteLine currentLine){
        QuoteLineItem newLineObj = new QuoteLineItem();
        newLineObj.Id = currentLine.quoteLineId;
        newLineObj.Quantity = currentLine.quantity;
        newLineObj.BillingFrequency = currentLine.billingFrequency;
        newLineObj.UnitPrice = currentLine.unitPrice;
        newLineObj.StartDate = currentLine.startDate;
        newLineObj.SubscriptionTerm = currentLine.subscriptionTerm;
        newLineObj.Discount = currentLine.discount;
        newLineObj.Tenant__c = currentLine.tenantId;
        return newLineObj;
    }
}