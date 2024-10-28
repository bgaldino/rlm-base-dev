public with sharing class QuoteTriggerHandler extends tf_TriggerHandler {
    public static Boolean isQLIModified = false;
    public override void handleBeforeInsert() {
        AmendQuoteHelper amendQuoteHelper = new AmendQuoteHelper();
        amendQuoteHelper.defaultAmendFields(Trigger.new, false);
        AmendQuoteHelper.updateBillingInformationForAmendQuotes(Trigger.new, false);
        QuoteTriggerHelper.processTaxInformation(Trigger.new);
        QuoteTriggerHelper.populatePricingContract(Trigger.new);
    }

    public override void handleBeforeUpdate() {
        AmendQuoteHelper amendQuoteHelper = new AmendQuoteHelper();
        amendQuoteHelper.defaultAmendFields(Trigger.new, false);
        QuoteTriggerHelper.processTaxInformation(Trigger.new);
        QuoteTriggerHelper.maintainPaymentDetails((Map<Id, Quote>) Trigger.oldMap, (List<Quote>) Trigger.new);
        QuoteTriggerHelper.validateQuoteForConversion((Map<Id, Quote>) Trigger.oldMap, (List<Quote>) Trigger.new);
        QuoteTriggerHelper.clearRejectionFieldsOnStatusChange((Map<Id, Quote>) Trigger.oldMap, (List<Quote>) Trigger.new);
        QuoteTriggerHelper.processQuoteHeaderUpdate((Map<Id, Quote>) Trigger.oldMap,  (List<Quote>) Trigger.new);
        QuoteTriggerHelper.populatePricingContract(Trigger.new);
    }
    

    public override void handleAfterInsert() {
        //calling method to set Auto Default QSTs
        Map<Id, QuoteLineItem> quoteLinesToUpdate = new Map<Id, QuoteLineItem>();
        
  /*       QuoteTermsGateway quoteTermsGateway = new QuoteTermsGateway();
        quoteTermsGateway.evaluateAndCreateQuoteTerms((Map<Id, Quote>)Trigger.newMap, null); */
        QuoteSyncRunner.syncQuotes((List<Quote>) Trigger.new, (Map<Id, Quote>) Trigger.oldMap, quoteLinesToUpdate);
    }

    public override void handleAfterUpdate() {
        List<Quote> quotes = (List<Quote>) Trigger.new;
        Map<Id, QuoteLineItem> quoteLinesToUpdate = new Map<Id, QuoteLineItem>();

        if(!isQLIModified){
            isQLIModified = quotes[0].CalculationStatus == 'Saving';
        }
        if(isQLIModified) {
/*             UsageDetailsRunner usageDetailRunner = new UsageDetailsRunner();
            usageDetailRunner.runUsageDetailsService(quotes); */
        } 

        QuoteTriggerApprovalLevelRunner quoteTriggerApprovalLevelRunner = new QuoteTriggerApprovalLevelRunner();
        quoteTriggerApprovalLevelRunner.processQuotes(quotes, (Map<Id, Quote>) Trigger.oldMap, quoteLinesToUpdate);
        
        //calling method to set Auto Default QSTs
/*         QuoteTermsGateway quoteTermsGateway = new QuoteTermsGateway();
        quoteTermsGateway.evaluateAndCreateQuoteTerms((Map<Id, Quote>)Trigger.newMap, (Map<Id, Quote>) Trigger.oldMap); */

        QuoteSyncRunner.syncQuotes((List<Quote>) Trigger.new, (Map<Id, Quote>) Trigger.oldMap, quoteLinesToUpdate);

        //set previous term text
/*         QuoteStatusASTUpdate qASTUpdate = new QuoteStatusASTUpdate();
        qASTUpdate.updatePreviousTermText((List<Quote>) Trigger.new, (Map<Id, Quote>) Trigger.oldMap); */

        QuoteTriggerHelper.processQuoteHeaderUpdateActions((Map<Id, Quote>) Trigger.oldMap, (List<Quote>) Trigger.new);
    }
}