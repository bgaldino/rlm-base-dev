public with sharing class QuoteServiceRequestValidator {
    
    private List<String> validStatusList = new List<String>{'Rejected', 'Booked'};
    private static final String REJECTED = 'Rejected';
    private static final String REJECTED_BOOKINGS = 'Rejected - Bookings';
    private List<Id> acceptedQuoteIds = new List<Id>();
    public class QuoteServiceException extends Exception {}
    
    public void validateRequest(QuoteServiceRequest request, ErrorCollector errorCollector) {
        if(request == null){
            throw new QuoteServiceException(QuoteServiceErrorCodes.NULL_REQUEST.name());
        }
        if(request.quoteRecords == null || request.quoteRecords.isEmpty()){
            throw new QuoteServiceException(QuoteServiceErrorCodes.INVALID_QUOTE.name());
        }
        for(QuoteRecord quoteRecord: request.quoteRecords){
            validateQuoteData(quoteRecord, errorCollector);
        }
    }
    
    private void validateQuoteData(QuoteRecord quoteRecord, ErrorCollector errorCollector){
        if(quoteRecord.quoteId == null){
            errorCollector.addError(QuoteServiceErrorCodes.INVALID_QUOTE.name());
        }
        if(quoteRecord.status != null && !validStatusList.contains(quoteRecord.status)){
            errorCollector.addLineError(quoteRecord.quoteId, QuoteServiceErrorCodes.QUOTE_INVALID_STATUS.name());
        }
        if(quoteRecord.status != null && quoteRecord.status.equals(REJECTED)){
            validateRejectedStatus(quoteRecord,errorCollector);
        }
    }
    
   private void validateRejectedStatus(QuoteRecord quoteRecord, ErrorCollector errorCollector){
        if(quoteRecord.rejectReason == null){
            errorCollector.addLineError(quoteRecord.quoteId, QuoteServiceErrorCodes.QUOTE_REJECT_REASON_MANDATORY.name());
        }
        if(quoteRecord.substatus == null){
            errorCollector.addLineError(quoteRecord.quoteId, QuoteServiceErrorCodes.QUOTE_SUBSTATUS_MANDATORY.name());
        }
        if(quoteRecord.substatus != null && !quoteRecord.substatus.equals(REJECTED_BOOKINGS)){
            errorCollector.addLineError(quoteRecord.quoteId, QuoteServiceErrorCodes.QUOTE_INVALID_SUBSTATUS.name());
        }
   }
}