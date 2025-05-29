public with sharing class RLM_QuoteHeaderFlowController{
    @InvocableMethod(label='Quote Header - Patch Dates' description='Set Date and Term from Quote Header' category='Quote')
    public static void createQuote(List<QuoteRecordInput> inputs) {
        QuoteRecordInput input = inputs.get(0);

        List<PlaceQuote.RecordWithReferenceRequest> listOfRecords = new List<PlaceQuote.RecordWithReferenceRequest>();

        PlaceQuote.RecordResource quoteRecord = new PlaceQuote.RecordResource(Quote.getSObjectType(), 'PATCH', input.inputQuote.Id);
        Map<String, Object> quoteValues = new Map<String, Object>();
        quoteValues.put('RLM_TermMonths__c', input.quoteTermMonths);
        quoteValues.put('StartDate', String.valueOf(input.quoteStartDate));
        quoteValues.put('RLM_EndDate__c', String.valueOf(input.quoteEndDate));
        quoteValues.put('RLM_SoftwareTargetAmount__c', input.quoteSoftwareTarget);
        quoteValues.put('RLM_HardwareTargetAmount__c', input.quoteHardwareTarget);
        quoteValues.put('RLM_ServicesTargetAmount__c', input.quoteServicesTarget);
        quoteValues.put('RLM_SoftwareDiscountPercent__c', input.quoteSoftwareDiscountPercent);
        quoteValues.put('RLM_HardwareDiscountPercent__c', input.quoteHardwareDiscountPercent);
        quoteValues.put('RLM_ServicesDiscountPercent__c', input.quoteServicesDiscountPercent);
        quoteValues.put('RLM_TargetNetTotal__c', input.quoteTotalTarget);
        quoteRecord.fieldValues = quoteValues;
        PlaceQuote.RecordWithReferenceRequest quoteItemRecord = new PlaceQuote.RecordWithReferenceRequest('refQuote', quoteRecord);
        listOfRecords.add(quoteItemRecord);

        for(Integer i=0; i<input.inputQuoteLineItems.size(); i++){
            QuoteLineItem inputQuoteLine = input.inputQuoteLineItems[i];
            PlaceQuote.RecordResource quoteLineRecord = new PlaceQuote.RecordResource(QuoteLineItem.getSObjectType(), 'PATCH', inputQuoteLine.Id);
            Map<String, Object> quoteLineItemValues = new Map<String, Object>();
            quoteLineItemValues.put('StartDate', String.valueOf(inputQuoteLine.StartDate));
            quoteLineItemValues.put('EndDate', String.valueOf(inputQuoteLine.EndDate));
            quoteLineItemValues.put('Discount', inputQuoteLine.Discount);
            quoteLineItemValues.put('DiscountAmount', inputQuoteLine.DiscountAmount);
            quoteLineRecord.fieldValues = quoteLineItemValues;
            PlaceQuote.RecordWithReferenceRequest quoteLineItemRecord = new PlaceQuote.RecordWithReferenceRequest('refQuoteItem'+(i+1), quoteLineRecord);
            listOfRecords.add(quoteLineItemRecord);
        }

        PlaceQuote.GraphRequest graph = new PlaceQuote.GraphRequest('createQuote', listOfRecords);
        PlaceQuote.ConfigurationOptionsInput cInput = new PlaceQuote.ConfigurationOptionsInput();
        cInput.validateProductCatalog=false;
        cInput.validateAmendRenewCancel=false;
        cInput.executeConfigurationRules=false;
        cInput.addDefaultConfiguration=false;
        system.debug(graph);
        system.debug(cInput);

        PlaceQuote.PlaceQuoteResponse resp = PlaceQuote.PlaceQuoteRLMApexProcessor.execute(PlaceQuote.PricingPreferenceEnum.System, graph, PlaceQuote.ConfigurationInputEnum.Skip,cInput);
        System.debug(resp);
    }

    public class QuoteRecordInput{
        @InvocableVariable
        public Quote inputQuote;

        @InvocableVariable
        public List<QuoteLineItem> inputQuoteLineItems;

        @InvocableVariable
        public Date quoteStartDate;

        @InvocableVariable
        public Date quoteEndDate;

        @InvocableVariable
        public Integer quoteTermMonths;

        @InvocableVariable
        public Decimal quoteSoftwareTarget;
        
        @InvocableVariable
        public Decimal quoteHardwareTarget;
        
        @InvocableVariable
        public Decimal quoteServicesTarget;

        @InvocableVariable
        public Decimal quoteSoftwareDiscountPercent;
        
        @InvocableVariable
        public Decimal quoteHardwareDiscountPercent;
        
        @InvocableVariable
        public Decimal quoteServicesDiscountPercent;

        @InvocableVariable
        public Decimal quoteTotalTarget;
    }
}