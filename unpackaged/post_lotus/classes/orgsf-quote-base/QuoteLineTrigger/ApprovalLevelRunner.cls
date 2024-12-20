public with sharing class ApprovalLevelRunner {

    private IApprovalLevelService approvalLevelService;
    private IEffectiveQuantityService effectiveQuantityService;
    private IEffectiveDiscountService effectiveDiscountService;

    public ApprovalLevelRunner() {
        this.approvalLevelService = (IApprovalLevelService) ServiceRegistry.getInstance('IApprovalLevelService');
        this.effectiveQuantityService = (IEffectiveQuantityService) ServiceRegistry.getInstance('IEffectiveQuantityService');
        this.effectiveDiscountService = (IEffectiveDiscountService) ServiceRegistry.getInstance('IEffectiveDiscountService');
    }

    public boolean shouldRun(Map<Id, QuoteLineItem> newQuoteLineItems, Map<Id, QuoteLineItem> oldQuoteLineItems) {

        if (this.effectiveQuantityService.shouldRun(newQuoteLineItems, oldQuoteLineItems)) {
            return true;
        }
        if (this.effectiveDiscountService.shouldRun(newQuoteLineItems, oldQuoteLineItems)) {
            return true;
        }
        
        return false;
    }

    public void run(QuoteLineTriggerDataBag dataBag, IQuoteLineItemWorker qliWorker, String triggerOperation) {

        qliWorker.registerDirty(
            this.effectiveQuantityService.calculateEffectiveQuantity(dataBag),
            new List<SObjectField>{ QuoteLineItem.EffectiveQuantity__c }
        );

        qliWorker.registerDirty(
            this.effectiveDiscountService.calculateEffectiveDiscount(dataBag),
            new List<SObjectField>{ QuoteLineItem.EffectiveDiscount__c }
        );

        List<QuoteLineItem> quoteLinesToUpdate = this.approvalLevelService.updateApprovalLevels(dataBag);
        qliWorker.registerDirty(quoteLinesToUpdate, new List<SObjectField>{ QuoteLineItem.ApprovalLevel__c });
    }
}
