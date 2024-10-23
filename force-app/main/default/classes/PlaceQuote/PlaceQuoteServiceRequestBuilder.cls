public with sharing class PlaceQuoteServiceRequestBuilder {

    private static final String QUOTE_FIELD_SERVICE_START_DATE = 'ServiceStartDate__c';
    private static final String QUOTE_FIELD_SERVICE_END_DATE = 'ServiceEndDate__c';
    private static final String QUOTE_FIELD_EXPIRATION_DATE = 'ExpirationDate';

    private static final String QUOTE_LINE_ITEM_FIELD_START_DATE = 'StartDate';
    private static final String QUOTE_LINE_ITEM_FIELD_END_DATE = 'EndDate';

    private static final List<String> QUOTE_DATE_FIELDS = new List<String> {
        QUOTE_FIELD_SERVICE_START_DATE,
        QUOTE_FIELD_SERVICE_END_DATE,
        QUOTE_FIELD_EXPIRATION_DATE
    };

    private static final List<String> QUOTE_LINE_ITEM_DATE_FIELDS = new List<String> {
        QUOTE_LINE_ITEM_FIELD_START_DATE,
        QUOTE_LINE_ITEM_FIELD_END_DATE
    };

    private QuoteRequest quoteRequest;
    private List<QuoteLineItemRequest> quoteLineItemRequests;
    private Map<Id, QuoteAction> quoteActions;
    private String method = 'POST';
    private String graphId;
    private PlaceQuote.PricingPreferenceEnum pricingPreference = PlaceQuote.PricingPreferenceEnum.SYSTEM;
    private PlaceQuote.ConfigurationInputEnum configEnum = PlaceQuote.ConfigurationInputEnum.RunAndAllowErrors;
    private PlaceQuote.ConfigurationOptionsInput config = new PlaceQuote.ConfigurationOptionsInput();

    public PlaceQuoteServiceRequestBuilder quote(QuoteRequest quoteRequest) {
        this.quoteRequest = quoteRequest;
        return this;
    }

    public PlaceQuoteServiceRequestBuilder method(String method) {
        this.method = method;
        return this;
    }

    public PlaceQuoteServiceRequestBuilder graphId(String graphId) {
        this.graphId = graphId;
        return this;
    }

    public PlaceQuoteServiceRequestBuilder quoteActions(Map<Id, QuoteAction> quoteActions) {
        this.quoteActions = quoteActions;
        return this;
    }
    
    public PlaceQuoteServiceRequestBuilder quoteLineItems(List<QuoteLineItemRequest> quoteLineItemRequests) {
        this.quoteLineItemRequests = quoteLineItemRequests;
        return this;
    }

    public PlaceQuoteServiceRequestBuilder pricingPreference(PlaceQuote.PricingPreferenceEnum pricingPreference) {
        this.pricingPreference = pricingPreference;
        return this;
    }

    public PlaceQuoteServiceRequestBuilder configEnum(PlaceQuote.ConfigurationInputEnum configEnum) {
        this.configEnum = configEnum;
        return this;
    }

    public PlaceQuoteServiceRequestBuilder config(PlaceQuote.ConfigurationOptionsInput config) {
        this.config = config;
        return this;
    }

    public PlaceQuoteServiceRequest build() {

         List<PlaceQuote.RecordWithReferenceRequest> listOfRecords = new List<PlaceQuote.RecordWithReferenceRequest>();
 
         // Get request
         Integer i = 0;
         Map<Id, PlaceQuote.RecordResource> quoteActionRecordMap = new Map<Id,PlaceQuote.RecordResource>();
         AmendQuoteHelper amendQuoteHelper = new AmendQuoteHelper();
         PlaceQuote.RecordResource quoteActionRecord;

         PlaceQuote.RecordResource quoteRecord = new PlaceQuote.RecordResource(Quote.getSobjectType(), quoteRequest.method);
         quoteRecord.fieldValues = new Map<String, Object>(quoteRequest.quote.getPopulatedFieldsAsMap());
             
         // Dates are coming as YYYY-MM-DD HH:MM:SS from screen flow component, so need to fix
         sanitizeDateFields(quoteRecord, QUOTE_DATE_FIELDS);
     
         String refQuoteId = 'refQuote';
         listOfRecords.add(new PlaceQuote.RecordWithReferenceRequest(refQuoteId, quoteRecord));
 
         if(quoteActions != null && quoteActions.size() > 0){
            quoteActionRecordMap = amendQuoteHelper.prepareQuoteActions(quoteActions.values(), refQuoteId, quoteRequest.method);            
         }

         if (quoteLineItemRequests != null) {
             for (QuoteLineItemRequest qliRequest : quoteLineItemRequests) {
                 PlaceQuote.RecordResource quoteLineItemRecord = new PlaceQuote.RecordResource(QuoteLineItem.getSobjectType(), qliRequest.method);
                 quoteLineItemRecord.fieldValues = new Map<String, Object>(qliRequest.quoteLineItem.getPopulatedFieldsAsMap());
 
                     // Dates are coming as YYYY-MM-DD HH:MM:SS from screen flow component, so need to fix
                 sanitizeDateFields(quoteLineitemRecord, QUOTE_LINE_ITEM_DATE_FIELDS);
 
                 quoteLineItemRecord.fieldValues.put('QuoteId', '@{' + refQuoteId + '.id}');

                 if(quoteActionRecordMap.size() > 0 && qliRequest.quoteLineItem.QuoteActionId != null){           
                    String refQuoteActionId = 'refQuoteAction' + i;
                    quoteActionRecord = quoteActionRecordMap.get(qliRequest.quoteLineItem.QuoteActionId);
                    listOfRecords.add(new PlaceQuote.RecordWithReferenceRequest(refQuoteActionId, quoteActionRecord));
                    quoteLineItemRecord.fieldValues.put('QuoteActionId', '@{' + refQuoteActionId + '.id}');
                 }

                 String refQuoteLineItemId = 'refQuoteLineItem' + i;
                 listOfRecords.add(new PlaceQuote.RecordWithReferenceRequest(refQuoteLineItemId, quoteLineItemRecord));
                 i++;
             }
         }
         // Place Quote Call
         PlaceQuoteServiceRequest serviceRequest = new PlaceQuoteServiceRequest();
         serviceRequest.pricingPreference = pricingPreference;
         serviceRequest.configEnum = configEnum;
         serviceRequest.config = config;
         serviceRequest.graphId = graphId;
         serviceRequest.records = listOfRecords;
         serviceRequest.method = method;

         return serviceRequest;
    }

    private void sanitizeDateFields(PlaceQuote.RecordResource record, List<String> fieldList) {
        for (String dateField : fieldList) {
            if (record.fieldValues.get(dateField) != null) {
                record.fieldValues.put(dateField, String.valueOf(record.fieldValues.get(dateField)).split(' ')[0]);
            }       
        }
    }

    public class QuoteRequest {
        public Quote quote;
        public String method;
    }

    public class QuoteLineItemRequest {
        public QuoteLineItem quoteLineItem;
        public String method;
    }
}