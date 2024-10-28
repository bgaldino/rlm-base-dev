public without sharing class QuoteLineItemTriggerHandler extends tf_TriggerHandler {
    @TestVisible
    private List<QuoteLineItem> oldRecordList = Trigger.old;

    @TestVisible
    private List<QuoteLineItem> newRecordList = Trigger.new;

    @TestVisible
    private Map<Id, QuoteLineItem> oldRecordMap = (Map<Id, QuoteLineItem>) Trigger.oldMap;

    @TestVisible
    private Map<Id, QuoteLineItem> newRecordMap = (Map<Id, QuoteLineItem>) Trigger.newMap;

    private IProductAttributeService productAttributeService;
    private IQuoteLineDAO quoteLineDAO;
    private IAssetDAO assetDAO;

    public QuoteLineItemTriggerHandler() {
        this(
            (IProductAttributeService) ServiceRegistry.getInstance('IProductAttributeService'),
            (IQuoteLineDAO) ServiceRegistry.getInstance('IQuoteLineDAO'),
            (IAssetDAO) ServiceRegistry.getInstance('IAssetDAO')
        );
    }

    public QuoteLineItemTriggerHandler(IProductAttributeService productAttributeService, IQuoteLineDAO quoteLineDAO, IAssetDAO assetDAO) {
        this.productAttributeService = productAttributeService;
        this.quoteLineDAO = quoteLineDAO;
        this.assetDAO = assetDAO;
    }

    private static void populateQuoteIds(QuoteLineTriggerDataBag dataBag, List<QuoteLineItem> quoteLineItems) {
        if (quoteLineItems != null && quoteLineItems.size() > 0) {
            for (QuoteLineItem quoteLineItem : quoteLineItems) {
                dataBag.quoteIds.add(quoteLineItem.QuoteId);
                dataBag.productIds.add(quoteLineItem.Product2Id);
            }
        }
    }

    private static void processQuoteLines(QuoteLineTriggerDataBag dataBag, List<QuoteLineItem> quoteLinesWithRelatedFields, List<QuoteLineItem> newQuoteLineItems) {
        for (Id quoteId : dataBag.quoteIds) {
            dataBag.newQuoteLineItemsByQuote.put(quoteId, new List<QuoteLineItem>());
            dataBag.quoteLineItemsWithRelatedFieldsByQuote.put(quoteId, new List<QuoteLineItem>());
            
        }

        for (QuoteLineItem quoteLineItem : quoteLinesWithRelatedFields) {
            dataBag.productIds.add(quoteLineItem.Product2Id);
            dataBag.quoteMap.put(quoteLineItem.QuoteId, quoteLineItem.Quote);
            dataBag.quoteLineItemsWithRelatedFieldsByQuote.get(quoteLineItem.QuoteId).add(quoteLineItem);
        }

        for (QuoteLineItem quoteLineItem : newQuoteLineItems) {
            dataBag.newQuoteLineItemsByQuote.get(quoteLineItem.QuoteId).add(quoteLineItem);
        }
    }

    private QuoteLineTriggerDataBag fillDataBag() {
        QuoteLineTriggerDataBag dataBag = new QuoteLineTriggerDataBag();
        dataBag.newQuoteLineItems = newRecordMap;
        dataBag.oldQuoteLineItems = oldRecordMap;

        populateQuoteIds(dataBag, oldRecordList);
        populateQuoteIds(dataBag, newRecordList);

        List<QuoteLineItem> quoteLineItems = quoteLineDAO.getQuoteLinesByQuoteIds(dataBag.quoteIds);
        if(!quoteLineItems.isEmpty()){
            dataBag.activeAssets = assetDAO.getAssetLinesWithTenant(quoteLineItems[0].Quote?.AccountID , quoteLineItems[0].Quote?.ServiceStartDate__c);
        }
        dataBag.quoteLineItemsByQuoteId = quoteLineItems;
        processQuoteLines(dataBag, quoteLineItems, newRecordList ?? new List<QuoteLineItem>());

        dataBag.productAttributes = this.productAttributeService.getProductAttributesForProducts(dataBag.productIds);

        return dataBag;
    }

    public override void handleBeforeInsert() {
        AmendQuoteHelper.populateTenantForQuoteLines(newRecordList);
        QLISyncRunner.syncNewLines(newRecordList);
        //NegotiatedPricingHandler handler = new NegotiatedPricingHandler();
        //handler.updateNegotiatedPrice(newRecordList);
    }

    public override void handleBeforeUpdate() {
/*         ApprovalLevelRunner approvalLevelRunner = new ApprovalLevelRunner();
        if (approvalLevelRunner.shouldRun(newRecordMap, oldRecordMap)) {
            QuoteLineTriggerDataBag dataBag = fillDataBag();
            IQuoteLineItemWorker qliWorker = new QuoteLineItemWorker();
            approvalLevelRunner.run(dataBag, qliWorker, getOperationType());
        } */
    }

    public override void handleAfterInsert() {
        IQuoteLineItemWorker qliWorker = new QuoteLineItemWorker();
        QuoteLineTriggerDataBag dataBag = fillDataBag();

/*         ProductTermsGateway termGateway = new ProductTermsGateway();
        termGateway.evaluateAndCreateProductTerms(newRecordList);

        //calling method to set Auto Default QSTs
        QuoteTermsGateway quoteTermsGateway = new QuoteTermsGateway();
        quoteTermsGateway.processingQuoteLineItems(newRecordList, null);

        ProductRuleRunner productRuleRunner = new ProductRuleRunner();
        productRuleRunner.runForQuoteLines(newRecordList, oldRecordList, qliWorker, getOperationType());

        ContractualPricingServImpl contractService = new ContractualPricingServImpl();
        contractService.filterQuoteLines(newRecordlist, new Map<Id, QuoteLineItem>());

        DPPBreakupLineGenerationService dppBreakUpService = new DPPBreakupLineGenerationService();
        if (dppBreakUpService.shouldRun(getOperationType())) {
            dppBreakUpService.handlePriceBreakUps(dataBag, getOperationType());
        } */
        
        qliWorker.commitWork();
    }

    public override void handleAfterDelete() {
        IQuoteLineItemWorker qliWorker = new QuoteLineItemWorker();

/*         DPPBreakupLineGenerationService dppBreakUpService = new DPPBreakupLineGenerationService();
        if (dppBreakUpService.shouldRun(getOperationType())) {
            QuoteLineTriggerDataBag dataBag = fillDataBag();
            dppBreakUpService.handlePriceBreakUps(dataBag, getOperationType()); 
        }

        ProductTermsGateway termGateway = new ProductTermsGateway();
        termGateway.evaluateAndUpdateDeleteProductTerms(oldRecordList);

        //calling method to set Auto Default QSTs
        QuoteTermsGateway quoteTermsGateway = new QuoteTermsGateway();
        quoteTermsGateway.processingQuoteLineItems(oldRecordList, null);

        ProductRuleRunner productRuleRunner = new ProductRuleRunner();
        productRuleRunner.runForQuoteLines(newRecordList, oldRecordList, qliWorker, getOperationType());

        ContractualPricingServImpl contractService = new ContractualPricingServImpl();
        contractService.handleDeleteQuoteLines(oldRecordList); */


        qliWorker.commitWork();
    }

    public override void handleAfterUpdate() {
/*         UsageDetailsRunner usageDetailRunner = new UsageDetailsRunner(); 
        usageDetailRunner.handleAfterUpdateAction(oldRecordMap, newRecordMap); */
        
        IQuoteLineItemWorker qliWorker = new QuoteLineItemWorker();

        //calling method to set Auto Default QSTs
/*         QuoteTermsGateway quoteTermsGateway = new QuoteTermsGateway();
        quoteTermsGateway.processingQuoteLineItems(newRecordList, oldRecordMap);

        ProductRuleRunner productRuleRunner = new ProductRuleRunner();
        productRuleRunner.runForQuoteLines(newRecordList, oldRecordList, qliWorker, getOperationType());

        ContractualPricingServImpl contractService = new ContractualPricingServImpl();
        contractService.filterQuoteLines(newRecordList, oldRecordMap);

        DPPBreakupLineGenerationService dppBreakUpService = new DPPBreakupLineGenerationService(); */
        QuoteLineTriggerDataBag dataBag = fillDataBag();
        //dppBreakUpService.handlePriceBreakUps(dataBag, getOperationType());

        qliWorker.commitWork();
    }
  
    public override void handleBeforeDelete(){
        //QuoteLineItemTriggerHelper.validateQuoteLineItemDeletion((List<QuoteLineItem>) Trigger.Old);
    }

    private String getOperationType(){
        return Test.isRunningTest() ? 'Test' : Trigger.OperationType.name();
    }
}
