public with sharing class QuoteLineServiceRequestValidator {

    public class QuoteLineServiceException extends Exception {}

    public void validateRequest(QuoteLineServiceRequest request, DMLOperation op, ErrorCollector errorCollector) {
        if(request == null){
            throw new QuoteLineServiceException(QuoteLineServiceErrorCodes.NULL_REQUEST.name());
        }
        if(request.quoteLines == null || request.quoteLines.isEmpty()){
            throw new QuoteLineServiceException(QuoteLineServiceErrorCodes.INVALID_QUOTE_LINES.name());
        }
        for(QuoteLine line: request.quoteLines){
            if (!isValidQuoteLineId(line, errorCollector)){
                continue;
            }
            if(op.equals(DMLOperation.OP_UPDATE) || op.equals(DMLOperation.OP_INSERT)){
                validatePricingInfo(line, errorCollector);
            }
            if(op.equals(DMLOperation.OP_INSERT)){
                validateLineConfigInfo(line, errorCollector);
            }
        }
        if(op.equals(DMLOperation.OP_INSERT)){
            validateQuoteId(request.quoteId, errorCollector);
        }
    }
    
    private Boolean isValidQuoteLineId(QuoteLine line, ErrorCollector errorCollector){
        if(String.isBlank(line.quoteLineId)){
            errorCollector.addError(QuoteLineServiceErrorCodes.QUOTE_LINE_ID_MANDATORY.name());
            return false;
        }
        return true;
    }
    
    private void validatePricingInfo(QuoteLine line, ErrorCollector errorCollector){
        if(line.quantity == null){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_QUANTITY_MANDATORY.name());
        }
        if(line.quantity < 1){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_QUANTITY_GREATER_THAN_ZERO.name());
        }
        if(String.isBlank(line.billingFrequency)){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_BILLING_FREQUENCY_MANDATORY.name());
        }
        if(line.unitPrice == null){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_UNIT_PRICE_MANDATORY.name());
        }
        if(line.unitPrice < 0){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_UNIT_PRICE_GREATER_THAN_ZERO.name());
        }
        if(line.startDate == null){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_START_DATE_MANDATORY.name());
        }
        if(line.subscriptionTerm == null){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_TERM_MANDATORY.name());
        }
        if(line.subscriptionTerm <= 0){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_TERM_GREATER_THAN_ZERO.name());
        }
        if(line.discount != null && line.discount < 0){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_DISCOUNT_GREATER_THAN_ZERO.name());
        }
    }
    
    private void validateLineConfigInfo(QuoteLine line, ErrorCollector errorCollector){
        if(line.product2Id == null){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_PRODUCT2_ID_MANDATORY.name());
        }
        if(line.pricebookEntryId == null){
            errorCollector.addLineError(line.quoteLineId, QuoteLineServiceErrorCodes.QUOTE_LINE_PRICEBOOKENTRY_ID_MANDATORY.name());
        }
    }
    
    private void validateQuoteId(Id quoteId, ErrorCollector errorCollector){
        if(quoteId == null){
            errorCollector.addError(QuoteLineServiceErrorCodes.QUOTE_ID_MANDATORY.name());
        }
    }
}