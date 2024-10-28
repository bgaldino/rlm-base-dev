public with sharing class ProductRuleRunner {
    private IProductRulesService productRuleService;
    private IQuoteDAO quoteDAO;
    private IQuoteLineDAO quoteLineDAO;
    private IAssetDAO assetDAO;
    private ITenantSelector tenantSelector;

    private Map<Id, Quote> quoteResultMap = new Map<Id, Quote>();
    private Map<Id, QuoteLineItem> quoteLineMap = new Map<Id, QuoteLineItem>();
    private Map<Id, QuoteFieldsWrapper> quoteFieldsWrapper = new Map<Id, QuoteFieldsWrapper>();

    private List<QuoteLineItem> quoteLinesToUpdate = new List<QuoteLineItem>();
    private Map<Id, List<QuoteLineItem>> quoteToLinesMap = new Map<Id, List<QuoteLineItem>>();
    private static AccessLevel accessLevelMode = UserInfo.getUserType() == 'automatedprocess'? AccessLevel.SYSTEM_MODE: AccessLevel.USER_MODE;
    private List<String> VALID_STATUS_LIST = new List<String>{'Draft', 'Rejected'};


    private static Set<String> processedTriggerOperations = new Set<String>();
    
    
    public ProductRuleRunner() {
        this(
            (IProductRulesService) ServiceRegistry.getInstance('IProductRulesService'),
            (IQuoteDAO) ServiceRegistry.getInstance('IQuoteDAO'),
            (IQuoteLineDAO) ServiceRegistry.getInstance('IQuoteLineDAO'),
            (IAssetDAO) ServiceRegistry.getInstance('IAssetDAO'),
            (ITenantSelector)ServiceRegistry.getInstance('ITenantSelector')
        );
    }

    public ProductRuleRunner(IProductRulesService productRuleService, IQuoteDAO quoteDAO, IQuoteLineDAO quoteLineDAO, IAssetDAO assetDAO, ITenantSelector tenantSelector) {
        this.productRuleService = productRuleService;
        this.quoteDAO = quoteDAO;
        this.quoteLineDAO = quoteLineDAO;
        this.assetDAO = assetDAO;
        this.tenantSelector = tenantSelector;     
    }

    public void runForQuoteLines(List<QuoteLineItem> newQuoteLineItems, List<QuoteLineItem> oldQuoteLineItems, IQuoteLineItemWorker qliWorker, String triggerOperation) {
        Set<Id> quoteIds = new Set<Id>();
        Map<Id, QuoteLineItem> mappedNewQuoteLineItems = new Map<Id, QuoteLineItem>();

        if ((newQuoteLineItems == null || newQuoteLineItems?.size() == 0) && (oldQuoteLineItems == null || oldQuoteLineItems.size() == 0)) {
            return;
        }

        if (newQuoteLineItems != null && newQuoteLineItems.size() > 0) {
            for (QuoteLineItem quoteLineItem : newQuoteLineItems) {
                quoteIds.add(quoteLineItem.QuoteId);
                mappedNewQuoteLineItems.put(quoteLineItem.Id, quoteLineItem);
            }
        }

        if (oldQuoteLineItems != null && oldQuoteLineItems.size() > 0) {
            for (QuoteLineItem quoteLineItem : oldQuoteLineItems) {
                quoteIds.add(quoteLineItem.QuoteId);
            }
        }

        this.runForQuotes(quoteIds, mappedNewQuoteLineItems , qliWorker, triggerOperation);
    }

    public void runForQuotes(Set<Id> quoteIds, Map<Id, QuoteLineItem> mappedNewQuoteLineItems, IQuoteLineItemWorker qliWorker, String triggerOperation) {
        if (processedTriggerOperations.contains(triggerOperation)) {
            return;
        }
        processedTriggerOperations.add(triggerOperation);
        List<QuoteLineItem> quoteLineItems = quoteLineDAO.getQuoteLinesByQuoteIdsConvertCurrencies(quoteIds);
        mapQuoteLineItemsByQuoteId(quoteIds, quoteLineItems, mappedNewQuoteLineItems);

        for (Id quoteId : this.quoteToLinesMap.keySet()) {
            List<QuoteLineItem> linesForQuote = this.quoteToLinesMap.get(quoteId);
            if (!linesForQuote.isEmpty()) {
                this.processQuoteLinesForQuote(quoteId, linesForQuote);
            }
        }

        this.updateQuotes();
        this.updateQuoteLines(qliWorker);
        this.publishPlatformEvents();
    }

    private void processQuoteLinesForQuote(Id quoteId, List<QuoteLineItem> quoteLineItems) {
        List<ProductRulesRequestWrapper> requestWrappers = new List<ProductRulesRequestWrapper>();
        List<ProductRulesRequestWrapper> assetWrappers = new List<ProductRulesRequestWrapper>();
        ProductRuleServiceRequest.Options options = new ProductRuleServiceRequest.Options();
        options.buyingProgram = 'Quoting';
        options.byPassRule = false;

        for (QuoteLineItem quoteLineItem : quoteLineItems) {
            populateRequestOptions(options, quoteLineItem);
            requestWrappers.add(makeRequestWrapper(quoteLineItem));
        }

        QuoteFieldsWrapper quoteFieldsWrpr = this.quoteFieldsWrapper.get(quoteId);

        List<Asset> assetLines = assetDAO.getAssetLinesWithTenant(quoteFieldsWrpr.accountId, quoteFieldsWrpr.serviceStartDate);
        if (assetLines != null && !assetLines.isEmpty()) {
            for(Asset assetLine : assetLines){
                assetWrappers.add(makeRequestWrapperForAsset(assetLine));
            }
        }

        ProductRuleServiceRequest productRuleServiceRequest = new ProductRuleServiceRequest();
        productRuleServiceRequest.buyingProductLines = requestWrappers;
        productRuleServiceRequest.assetLines = assetWrappers;
        productRuleServiceRequest.options = options;
        List<String> tenantQuotingStatus = validateTenantQuotingStatus(quoteLineItems);
      
        ProductRulesResponse productRuleResponse = this.productRuleService.runRules(productRuleServiceRequest);
        if(tenantQuotingStatus.size()>0) {
            updateResponseForIncompleteTenant(tenantQuotingStatus);
        }
        this.processResponse(quoteId, quoteLineItems, productRuleResponse);
    }

    private void processResponse(Id quoteId, List<QuoteLineItem> quoteLineItems, ProductRulesResponse productRuleResponse) {
        if (productRuleResponse.status == 'FAILURE') {
            processResponseFailure(quoteId, quoteLineItems, productRuleResponse);
            return;
        }
        processResponseSuccess(quoteId, quoteLineItems, productRuleResponse);
    }

    

    private void processResponseFailure(Id quoteId, List<QuoteLineItem> quoteLineItems, ProductRulesResponse productRuleResponse) {
        Map<Id, QuoteLineItemErrorsWrapper> errorWrapperMap = new Map<Id, QuoteLineItemErrorsWrapper>();
        for (QuoteLineItem quoteLineItem : quoteLineItems) {
            if(!errorWrapperMap.containskey(quoteLineItem.id)){
                errorWrapperMap.put(quoteLineItem.id, new QuoteLineItemErrorsWrapper());
            }
            errorWrapperMap.get(quoteLineItem.id).productRuleResults.addAll(makeServiceFailureResults(productRuleResponse.getMessage()));
        }
        processQuoteLinesForUpdates(quoteId, quoteLineItems, errorWrapperMap);
    }

    private void processResponseSuccess(Id quoteId, List<QuoteLineItem> quoteLineItems, ProductRulesResponse productRuleResponse) {
         Map<String, List<ProductRulesResponse.ProductRuleResult>> resultsByQuoteLineId = mapByReferenceId(productRuleResponse.getResults());
         Map<Id, QuoteLineItemErrorsWrapper> errorWrapperMap = new Map<Id, QuoteLineItemErrorsWrapper>();
         for (QuoteLineItem quoteLineItem : quoteLineItems) {
            if (resultsByQuoteLineId.containsKey(quoteLineItem.Id)) {
                if(!errorWrapperMap.containskey(quoteLineItem.id)) {
                    errorWrapperMap.put(quoteLineItem.id, new QuoteLineItemErrorsWrapper());
                }
                errorWrapperMap.get(quoteLineItem.id).productRuleResults.addAll(resultsByQuoteLineId.get(quoteLineItem.Id));
            }
         }
         processQuoteLinesForUpdates(quoteId, quoteLineItems, errorWrapperMap);
    }

    private void processQuoteLinesForDPPErrors(List<QuoteLineItem> quoteLineItems, Map<Id, QuoteLineItemErrorsWrapper> errorWrapperMap) {
        Map<Id, List<String>> dppValidations = QuoteLineItemDPPValidationService.quoteLineItemValidationMsg;
        if(dppValidations!=null && !dppValidations.isEmpty()) {
            for(QuoteLineItem quoteLineItem: quoteLineItems) {
                if(dppValidations.containsKey(quoteLineItem.Id)) {
                    if(!errorWrapperMap.containskey(quoteLineItem.Id)){
                        errorWrapperMap.put(quoteLineItem.Id, new QuoteLineItemErrorsWrapper());
                    }
                    errorWrapperMap.get(quoteLineItem.Id).dppResults.addAll(processDPPResults(dppValidations.get(quoteLineItem.Id)));
                }
            }
        }
    }

    private void processQuoteLinesForUpdates(Id quoteId, List<QuoteLineItem> quoteLineItems, Map<Id, QuoteLineItemErrorsWrapper> errorWrapperMap) {
        processQuoteLinesForDPPErrors(quoteLineItems, errorWrapperMap);
        Boolean hasProductRuleErrors = false;
        for(QuoteLineItem quoteLineItem: quoteLineItems) {
            QuoteLineItemErrorsWrapper errorWrapper = new QuoteLineItemErrorsWrapper();

            if(errorWrapperMap.containskey(quoteLineItem.id)) {
                QuoteLineItemErrorsWrapper existingWrapper = errorWrapperMap.get(quoteLineItem.id);
                if(!existingWrapper.dppResults.isEmpty()) {
                    errorWrapper.dppResults.addAll(existingWrapper.dppResults);
                }
                if(!existingWrapper.productRuleResults.isEmpty()) {
                    errorWrapper.productRuleResults.addAll(existingWrapper.productRuleResults);
                }
            }

            //check if either list has any entries
            Boolean hasResults = !errorWrapper.dppResults.isEmpty() || !errorWrapper.productRuleResults.isEmpty();
            if (!hasProductRuleErrors) {
                hasProductRuleErrors = hasProductRuleErrors(errorWrapper);
            }
            //serialize and update the field
            String errorJSONString = hasResults ? JSON.serialize(errorWrapper) : '';
            quoteLinesToUpdate.add(new QuoteLineItem(Id = quoteLineItem.id, ProductRuleResultJSON__c = errorJSONString));
        }
        
        this.quoteResultMap.get(quoteId).HasProductRuleErrors__c = hasProductRuleErrors;
    }

    private Boolean hasProductRuleErrors(QuoteLineItemErrorsWrapper errorWrapper) {
        // if results has product rule errors, then return true
        // else if dppResults has results, then also return true
        for (ProductRulesResponse.ProductRuleResult result : errorWrapper.productRuleResults) {
            if (result.messageType == 'Error') {
                return true;
            }
        }
        return !errorWrapper.dppResults.isEmpty();
    }

    private void updateQuotes() {
        this.quoteDAO.quoteUpdate(this.quoteResultMap.values(), true);
    }

    private void updateQuoteLines(IQuoteLineItemWorker qliWorker) {
        qliWorker.registerDirty(this.quoteLinesToUpdate, new List<SObjectField> { QuoteLineItem.ProductRuleResultJSON__c });
    }

    private void publishPlatformEvents() {
        List<QuoteChangeEvent__e> quoteChangeEvents = new List<QuoteChangeEvent__e>();

        for (Id quoteId : this.quoteToLinesMap.keySet()) {
            quoteChangeEvents.add(new QuoteChangeEvent__e(QuoteId__c = quoteId, Status__c = 'ProductRulesInvocationComplete'));
        }
        EventBus.publish(quoteChangeEvents);
    }

    private void populateRequestOptions(ProductRuleServiceRequest.Options options, QuoteLineItem quoteLineItem) {
        if (String.isBlank(options.quoteType)) {
            options.quoteType = quoteLineItem.Quote.QuoteType__c;
        }

        if (!options.bypassRule) {
            options.bypassRule = shouldBypassRules(quoteLineItem.Quote.QuoteBypass__c);
        }
    }

    private Map<String, List<ProductRulesResponse.ProductRuleResult>> mapByReferenceId(List<ProductRulesResponse.ProductRuleResult> productRuleResults) {
        Map<String, List<ProductRulesResponse.ProductRuleResult>> resultsByReferenceId = new Map<String, List<ProductRulesResponse.ProductRuleResult>>();
        for (ProductRulesResponse.ProductRuleResult result : productRuleResults) {
            if (!resultsByReferenceId.containsKey(result.referenceId)) {
                resultsByReferenceId.put(result.referenceId, new List<ProductRulesResponse.ProductRuleResult>());
            }
            handleTenantLogic(result);
            resultsByReferenceId.get(result.referenceId).add(result);
        }
        return resultsByReferenceId;
    }

    private void handleTenantLogic(ProductRulesResponse.ProductRuleResult result) {
        if (result.message == 'This line is not processed as Tenant is not linked.') {
            result.message = Label.Tenant_Required_Validation_Message;
            result.messageType = 'Error';
            return;
        } 
        
        if (result.message == Label.Tenant_Validation_Message_Before_Publishing_Quote) {
            QuoteLineItem quoteLineItem = quoteLineMap.get(result.referenceId);
            if (quoteLineItem == null) {
                return;
            }

            if (quoteLineItem.Quote.Status == 'Approved') {
                result.messageType = 'Error';
            }
        }
    }
    private List<String> validateTenantQuotingStatus(List<QuoteLineItem> quoteLineItems){
        Set<String> tenantIds = new Set<String>();
        List<String> tenantQuotingStatus = new List<String>();
        Map<String, List<String>> tenantReferenceIds = new Map<String,List<String>>();
        for(QuoteLineItem qli: quoteLineItems){
            tenantIds.add(qli.Tenant__c);
            if (!tenantReferenceIds.containsKey(qli.Tenant__c )) {
                tenantReferenceIds.put(qli.Tenant__c, new List<String>{qli.Id});
                continue;
            }
            List<string> referenceId = (list<string>)tenantReferenceIds.get(qli.Tenant__c );
            referenceId.add(qli.Id);
            tenantReferenceIds.put(qli.Tenant__c , referenceId);
        }
        Map<Id,Tenant__c> tenantMap = tenantSelector.selectTenantForId(tenantIds);
        for( String item : tenantIds){
            if(tenantMap.containsKey(item) && (tenantMap.get(item).Quoting_Status__c == 'Incomplete')){
                tenantQuotingStatus.addAll(tenantReferenceIds.get(item));            
            }
        }
        return tenantQuotingStatus;
    }
    private static void updateResponseForIncompleteTenant(List<String> incompleteTenantWrappersMap){
        for (String field : incompleteTenantWrappersMap) {
            ProductRulesResponse.ProductRuleResult res = new ProductRulesResponse.ProductRuleResult();
            res.pending = true;
            res.message = system.label.Tenant_Validation_Message_Before_Publishing_Quote;
            res.messageType = 'Warning';
            res.referenceId = field;
            ProductRuleResultsSingletonManager.getInstance().addResult(res);       
        }
    }

    private static boolean shouldBypassRules(String quoteBypassValue) {
        if (String.isBlank(quoteBypassValue)) {
            return false;
        }
        return quoteBypassValue.split(';').contains('Rules');
    }

    private static List<ProductRulesResponse.ProductRuleResult> makeServiceFailureResults(String message) {
        List<ProductRulesResponse.ProductRuleResult> serviceFailureResults = new List<ProductRulesResponse.ProductRuleResult>();
        ProductRulesResponse.ProductRuleResult ruleResult = new ProductRulesResponse.ProductRuleResult();
        ruleResult.message = Label.ValidationRulesErrorMessage + ' Service Error Message: ' + message;
        ruleResult.messageType = 'Error';
        serviceFailureResults.add(ruleResult);
        return serviceFailureResults;
    }

    private ProductRulesRequestWrapper makeRequestWrapper(QuoteLineItem qli) {
        // Use queried quoteLineItem record since it has all required fields
        QuoteLineItem quoteLineItem = this.quoteLineMap.get(qli.Id);
        Map<String, Object> requestMap = new Map<String, Object>{
            'id' => quoteLineItem.Id,
            'quantity' => quoteLineItem.Quantity,
            'productid' => quoteLineItem.Product2Id,
            'referenceid' => quoteLineItem.Id,
            'locationid' => quoteLineItem.Tenant__c,
            'locationname' => quoteLineItem?.Tenant__r?.OptionalName__c,
            'netunitprice' => quoteLineItem.NetUnitPrice,
            'billingcountry' => quoteLineItem.Quote?.BillingCountry,
            'floorpriceruleoverride' => quoteLineItem.Quote?.FloorPriceRuleOverride__c,
            'startdate' => (DateTime)quoteLineItem.StartDate,
            'enddate' => (DateTime)quoteLineItem.EndDate
        };

        ProductRulesRequestWrapper requestWrapper = new ProductRulesRequestWrapper();
        requestWrapper.setWrapperAttributes(requestMap);

        return requestWrapper;
    }

    private static ProductRulesRequestWrapper makeRequestWrapperForAsset(Asset assetLineItem) {
        Map<String, Object> requestMap = new Map<String, Object>{
            'id' => assetLineItem.Id,
            'quantity' => assetLineItem.CurrentQuantity,
            'productid' => assetLineItem.Product2Id,
            'referenceid' => assetLineItem.Id,
            'locationid' => assetLineItem.Tenant__c,
            'locationname' => assetLineItem?.Tenant__r?.OptionalName__c,
            'startdate' => (DateTime)assetLineItem.LifecycleStartDate,
            'enddate' => (DateTime)assetLineItem.LifecycleEndDate
        };

        ProductRulesRequestWrapper requestWrapper = new ProductRulesRequestWrapper();
        requestWrapper.setWrapperAttributes(requestMap);

        return requestWrapper;
    }

    private static List<Map<String, string>> processDPPResults(List<String> dppValidationMsg) {
        List<Map<String, String>> messageList = new List<Map<String, String>>();
        for(String message: dppValidationMsg) {
                Map<String, String> messageMap = new Map<String, String>{
                'message' => message,
                'messageType' => 'Error'
            };
            messageList.add(messageMap);
         }
        return messageList;
    }

    private Map<Id, List<QuoteLineItem>> initializeQuoteToLinesMap(Set<Id> quoteIds) {
        Map<Id, List<QuoteLineItem>> quoteToLinesMap = new Map<Id, List<QuoteLineItem>>();
        for (Id quoteId : quoteIds) {
            quoteToLinesMap.put(quoteId, new List<QuoteLineItem>());
        }

        return quoteToLinesMap;
    }

    private Map<Id, Quote> initializeQuoteResultMap(Set<Id> quoteIds) {
        Map<Id, Quote> quoteResultMap = new Map<Id, Quote>();
        for (Id quoteId : quoteIds) {
            quoteResultMap.put(quoteId, new Quote(Id = quoteId, HasProductRuleErrors__c = false));
        }

        return quoteResultMap;
    }

    private void mapQuoteLineItemsByQuoteId(Set<Id> quoteIds, List<QuoteLineItem> quotelineItems, Map<Id, QuoteLineItem> mappedNewQuoteLineItems) {
        
        this.quoteToLinesMap = initializeQuoteToLinesMap(quoteIds);
        this.quoteResultMap = initializeQuoteResultMap(quoteIds);
        for (QuoteLineItem quoteLineItem : quoteLineItems) {
            if (!VALID_STATUS_LIST.contains(quoteLineItem.Quote.Status)) {
                continue;
            }

            quoteLineMap.put(quoteLineItem.Id, quoteLineItem);
            if (mappedNewQuoteLineItems.containsKey(quoteLineItem.Id)) {
                this.quoteToLinesMap.get(quoteLineItem.QuoteId).add(mappedNewQuoteLineItems.get(quoteLineItem.Id));
            } else {
                this.quoteToLinesMap.get(quoteLineItem.QuoteId).add(quoteLineItem);
            }
        
            this.quoteFieldsWrapper.put(quoteLineItem.QuoteId, new QuoteFieldsWrapper(quoteLineItem.Quote.AccountId, quoteLineItem.Quote.ServiceStartDate__c));
        
        }
        
    }

    class QuoteFieldsWrapper {
        public Id accountId;
        public Date serviceStartDate;

        public QuoteFieldsWrapper(Id accountId, Date serviceStartDate) {
            this.accountId = accountId;
            this.serviceStartDate = serviceStartDate;
        }
    }

    public class QuoteLineItemErrorsWrapper {
        public List<Map<string, string>> dppResults {get;set;}
        public List<ProductRulesResponse.ProductRuleResult> productRuleResults {get;set;}
        public QuoteLineItemErrorsWrapper() {
            this.dppResults = new List<Map<string, string>>();
            this.productRuleResults = new List<ProductRulesResponse.ProductRuleResult>();
        }
    }
}