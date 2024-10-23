public with sharing class PlaceQuoteAddQLAction {

    public class PlaceQuoteAddQLActionRequest {
        @InvocableVariable
        public Quote quote;
        @InvocableVariable
        public List<QuoteLineItem> quoteLineItemList;
    }

    public class PlaceQuoteAddQLActionResponse {
        @InvocableVariable
        public Id quoteId;
    }
    
    private static final String QUOTE_LINE_ITEM_FIELD_START_DATE = 'StartDate';
    private static final String QUOTE_LINE_ITEM_FIELD_END_DATE = 'EndDate';

    /*
    private static final List<String> QUOTE_DATE_FIELDS = new List<String> {
        QUOTE_FIELD_SERVICE_START_DATE,
        QUOTE_FIELD_SERVICE_END_DATE,
        QUOTE_FIELD_EXPIRATION_DATE
    };
	*/

    private static final List<String> QUOTE_LINE_ITEM_DATE_FIELDS = new List<String> {
        QUOTE_LINE_ITEM_FIELD_START_DATE,
        QUOTE_LINE_ITEM_FIELD_END_DATE
    };

    @InvocableMethod(label='Place Quote' description='Calls the place quote Apex API to add QuoteLine to quote')
    public static List<PlaceQuoteAddQLActionResponse> placeQuote(List<PlaceQuoteAddQLActionRequest> requests) {
        // Setup Response 
        PlaceQuoteAddQLActionResponse actionResponse = new PlaceQuoteAddQLActionResponse();
        PlaceQuoteAddQLActionRequest request = requests[0];

        PlaceQuoteServiceRequestBuilder.QuoteRequest quoteRequest = new PlaceQuoteServiceRequestBuilder.QuoteRequest();
        quoteRequest.quote = request.quote;
        quoteRequest.method = 'POST';

        //quote record
        //quote - 0Q0O4000000oWSvKAM
        Id quoteid = request.quote.Id;
         PlaceQuote.RecordResource quoteRecord = new PlaceQuote.RecordResource(Quote.getSobjectType(),'PATCH', quoteid);
        Map<String,Object> quoteFieldValues = new Map<String,Object>();
    
        QuoteLineItem lineItemData = request.quoteLineItemList[0]; 
        
        //QuoteLinteItem record
        PlaceQuote.RecordResource quoteLineItemRecord1 = new PlaceQuote.RecordResource(QuoteLineItem.getSobjectType(),'POST');
        quoteLineItemRecord1.fieldValues = new Map<String, Object>(lineItemData.getPopulatedFieldsAsMap());
        sanitizeDateFields(quoteLineItemRecord1, QUOTE_LINE_ITEM_DATE_FIELDS);
        quoteLineItemRecord1.fieldValues.put('QuoteId', '@{' + 'refQuote' + '.id}');

        /*
        Map<String,Object> quoteLineItemFieldValues = new Map<String,Object>();
        quoteLineItemFieldValues.put('Product2Id','01tO3000002keqIIAQ');
        quoteLineItemFieldValues.put('PricebookEntryId','01uO3000000VkTlIAK');
        quoteLineItemFieldValues.put('Quantity','10.0');
        quoteLineItemFieldValues.put('UnitPrice','80.0');
        quoteLineItemFieldValues.put('PeriodBoundary','Anniversary');
        quoteLineItemFieldValues.put('BillingFrequency','Annual');
        quoteLineItemFieldValues.put('StartDate','2024-10-08');
        quoteLineItemFieldValues.put('EndDate','2025-10-07');
        quoteLineItemFieldValues.put('QuoteId','@{refQuote.id}');
        quoteLineItemRecord1.fieldValues = quoteLineItemFieldValues;
        */
        PlaceQuote.RecordWithReferenceRequest quoteRecords = new PlaceQuote.RecordWithReferenceRequest('refQuote',quoteRecord);
        PlaceQuote.RecordWithReferenceRequest quoteLineItemRecords1 = new PlaceQuote.RecordWithReferenceRequest('refQuoteItem1',quoteLineItemRecord1);

        //add records
        List<PlaceQuote.RecordWithReferenceRequest> listOfRecords = new List<PlaceQuote.RecordWithReferenceRequest>();
        listOfRecords.add(quoteRecords);
        listOfRecords.add(quoteLineItemRecords1);
    
        //make call
        PlaceQuote.PricingPreferenceEnum pricingPreference = PlaceQuote.PricingPreferenceEnum.Force;        
        PlaceQuote.GraphRequest graph = new PlaceQuote.GraphRequest('test',listOfRecords);
        PlaceQuote.ConfigurationInputEnum configurationPreference = PlaceQuote.ConfigurationInputEnum.RunAndAllowErrors;
        PlaceQuote.ConfigurationOptionsInput cInput = new PlaceQuote.ConfigurationOptionsInput();
        cInput.addDefaultConfiguration = true;
        cInput.executeConfigurationRules = true;
        cInput.validateAmendRenewCancel = true;
        cInput.validateProductCatalog = true;
        //System.debug(graph);
      
        //Place Quote Call
        PlaceQuote.PlaceQuoteResponse resp = PlaceQuote.PlaceQuoteRLMApexProcessor.execute(pricingPreference, graph, configurationPreference, cInput);
        System.debug(resp);


        actionResponse.quoteId = resp.quoteId;

        return new List<PlaceQuoteAddQLActionResponse> { actionResponse };
    }
    
    private static void sanitizeDateFields(PlaceQuote.RecordResource record, List<String> fieldList) {
        for (String dateField : fieldList) {
            if (record.fieldValues.get(dateField) != null) {
                record.fieldValues.put(dateField, String.valueOf(record.fieldValues.get(dateField)).split(' ')[0]);
            }       
        }
    }
}