public with sharing class AmendQuoteHelper {
    private IQuoteDAO quoteDAO;
    private IAmendQuoteDataSelector amendQuoteDataSelector;
    private IQuoteLineDAO quoteLineDAO;

    public AmendQuoteHelper() {
        this(
            (IQuoteDAO) ServiceRegistry.getInstance('IQuoteDAO'),
            (IAmendQuoteDataSelector) ServiceRegistry.getInstance('IAmendQuoteDataSelector'),
            (IQuoteLineDAO) ServiceRegistry.getInstance('IQuoteLineDAO')
        );
    }

    public AmendQuoteHelper(IQuoteDAO quoteDAO, IAmendQuoteDataSelector amendQuoteDataSelector, IQuoteLineDAO quoteLineDAO) {
        this.quoteDAO = quoteDAO;
        this.amendQuoteDataSelector = amendQuoteDataSelector;
        this.quoteLineDAO = quoteLineDAO;
    }

    public void defaultAmendFields(List<Quote> quotes, Boolean isTestingAmend){
        Set<ID> quoteIds = new Set<ID>();
        Set<ID> contractIds = new Set<ID>();
        Map<Id, Contract> contractMap = new Map<Id, Contract>();

        for(Quote quote : quotes){
/*             if(QuoteTriggerHelper.shouldProcessQuoteUpdate(quote) 
            && (quote.originalActionType == 'Amend' || isTestingAmend)){

                quoteIds.add(quote.Id);
                contractIds.add(quote.ContractId);
            } */
        }
        if(quoteIds.size() <= 0 || contractIds.size() <= 0 )
        return;

        contractMap = amendQuoteDataSelector.selectContracts(contractIds);

        Date contractEndDate;
        for(Quote quote : quotes){
                            
            Contract contract = contractMap.get(quote.ContractId);
            if(contract == null){
                quote.addError('Quote : ' + quote.Name + ' ( '+quote.Id+' ) is missing contract. Please associate a contract to this Amend Quote.');
                continue;
            }
            performAmendFieldsUpdate(quote, contract);
        }
    }

    public void performAmendFieldsUpdate(Quote quote, Contract contract){
        if(quote.ServiceStartDate__c == null){
            quote.ServiceStartDate__c = quote.StartDate;
        }
        if(quote.ServiceEndDate__c == null){
            quote.ServiceEndDate__c = contract.EndDate;
        }
        if(quote.ExpirationDate == null){
            quote.ExpirationDate = contract.EndDate;
        }
        if(quote.BillingCountry == null){
            quote.BillingCountry = 'US';
        }
        if(quote.ShippingCountry == null){
            quote.ShippingCountry = 'US';
        }
        if( quote.ServiceStartDate__c != null && quote.ServiceEndDate__c != null){
            Decimal term = calculateTerm(quote.ServiceStartDate__c, quote.ServiceEndDate__c);
            if(quote.Term__c != term){
                quote.Term__c = term;
            }            
        }
        if(quote.QuoteType__c == null){
            quote.QuoteType__c = 'Amend';
        }
    }

    public Decimal calculateTerm(Date startDate, Date endDate){
        Integer monthDiff = startDate.monthsBetween(endDate);
        Integer daysEnd = Date.daysInMonth(endDate.year(),endDate.month());
        Decimal day_s = startDate.day();
        Decimal day_e = endDate.day();
        Decimal factor = 0;
        if(day_s != day_e){
            factor = (day_e - (day_s-1))/daysEnd;
        }
        return monthDiff+factor;
    }

    

/*     public static void performTenantAssignment( Map<Id, Set<Id>> accountProductsMap, Map<Id, List<QuoteLineItem>> accountQuoteLinesMap, Set<Id> quoteActionIds){
        Set<Id> productIds;
        Map<Id, QuoteAction> quoteActions;
        AmendQuoteDataSelector amendQuoteDataSelector = new AmendQuoteDataSelector();
        if(quoteActionIds!=null && quoteActionIds.size()>0){
            quoteActions = amendQuoteDataSelector.selectQuoteActions(quoteActionIds);
        }

        for(Id accountId : accountProductsMap.keyset()){
            productIds = new Set<Id>();
            productIds.addAll(accountProductsMap.get(accountId));
            ITenantShellService tenantShellService = (ITenantShellService) ServiceRegistry.getInstance('ITenantShellService');
            Map<Id, Id> defaultTenantMap = tenantShellService.findOrCreateDefaultTenant(accountId, productIds);
            for(QuoteLineItem qliToUpdate : accountQuoteLinesMap.get(accountId)){
                if(qliToUpdate.Tenant__c != null) { continue; }
                if(quoteActionIds.contains(qliToUpdate.QuoteActionId) && quoteActions.get(qliToUpdate.QuoteActionId).SourceAsset.Tenant__c != null){
                    qliToUpdate.Tenant__c = quoteActions.get(qliToUpdate.QuoteActionId).SourceAsset.Tenant__c;
                }
                else{
                    qliToUpdate.Tenant__c = defaultTenantMap.get(qliToUpdate.Product2Id);
                }
            }
        }
    } */

    public static void populateTenantForQuoteLines(List<QuoteLineItem> quoteLines){
        
        Set<Id> quoteIds = new Set<Id>();
        Set<Id> quoteActionIds = new Set<Id>();
        List<Quote> quotes;
        Map<Id, Set<Id>> accountProductsMap = new Map<Id, Set<Id>>();
        Map<Id, List<QuoteLineItem>> accountQuoteLinesMap = new Map<Id, List<QuoteLineItem>>();
        Map<Id, Id> quoteIDAccountIDMap = new Map<Id, Id>();
        List<QuoteLineItem> qlisWIthQuoteAction = new List<QuoteLIneItem>();
        List<QuoteLineItem> qlisWIthoutQuoteAction = new List<QuoteLIneItem>();


        for (QuoteLineItem line : quoteLines) {
            quoteIds.add(line.quoteId);
            if(line.QuoteActionId != null){
                qlisWIthQuoteAction.add(line);
                quoteActionIds.add(line.QuoteActionId);
                line.PeriodBoundary = 'Anniversary';
                line.PeriodBoundaryDay = null;
            }
            else{
                qlisWIthoutQuoteAction.add(line);
            }
        }
        quotes = new AmendQuoteDataSelector().selectQuotes(quoteIds);
        for (Quote q: quotes) {
            quoteIDAccountIDMap.put(q.Id, q.AccountId);
        }

        for (QuoteLineItem line : quoteLines) {
            Id accountId = quoteIDAccountIDMap.get(line.quoteId);
            if(accountQuoteLinesMap.containsKey(accountId)){
            accountQuoteLinesMap.get(accountId).add(line);
            }else{
                accountQuoteLinesMap.put(accountId, new List<QuoteLineItem>{line});
            }
            
            if(accountProductsMap.containsKey(quoteIDAccountIDMap.get(line.quoteId))){
                accountProductsMap.get(quoteIDAccountIDMap.get(line.quoteId)).add(line.Product2Id);
            }
            else{
                accountProductsMap.put(quoteIDAccountIDMap.get(line.quoteId), new Set<Id>{line.Product2Id});
            }
        }

        // performTenantAssignment( accountProductsMap, accountQuoteLinesMap, quoteActionIds);
    }    
    
    public void updateBillingInformationForAmendQuotes(List<Quote> newQuotes, Boolean isTestingAmend){

        List<Quote> amendQuotes = new List<Quote>();
        Set<Id> contractIds = new Set<Id>();
        Set<Id> assetIds = new Set<Id>();
        Set<Id> quoteAccountIds = new Set<Id>();
        Map<Id, Contract> contractMap = new Map<Id, Contract>();
        Map<Id, AssetContractRelationship> contractAssetsMap = new Map<Id, AssetContractRelationship>();
        
        /* for (Quote q : newQuotes) {
            if (isTestingAmend || 
            (QuoteTriggerHelper.shouldProcessQuoteUpdate(q) && q.OriginalActionType == 'Amend' && q.ContractId != null)) {
                amendQuotes.add(q);
                contractIds.add(q.ContractId);
            }
        } */
        contractMap = amendQuoteDataSelector.selectContracts(contractIds);
        
        for(Contract c: contractMap.values()){
            quoteAccountIds.add(c.AccountId);
        }
        
        if (amendQuotes.isEmpty()) {
            return;
        }
        
        List<AssetContractRelationship> assetContractRelationships = amendQuoteDataSelector.selectAssetContractRelationships(contractIds);
        for(AssetContractRelationship acr : assetContractRelationships){
            AssetContractRelationship acrTemp = contractAssetsMap.get(acr.contractId);
            if(acrTemp == null || (acrTemp != null && acr.Asset.LastModifiedDate > acrTemp.Asset.LastModifiedDate)){
                contractAssetsMap.put(acr.contractId, acr);
            }
        }

        for(AssetContractRelationship acr : contractAssetsMap.values()){
            assetIds.add(acr.AssetId);
        }

        Map<Id, AssetAction> assetActions = amendQuoteDataSelector.selectAssetActions(assetIds);
        
        Map<Id, Account> accountMap = amendQuoteDataSelector.selectAccountByQuoteAccountIds(quoteAccountIds);
        
        List<AssetActionSource> assetActionSources = amendQuoteDataSelector.selectAssetActionSources(assetActions.keySet());  
        
        performBillingInformationUpdate(amendQuotes, assetActionSources, contractAssetsMap, contractMap, accountMap);
    }
    
    public void performBillingInformationUpdate(List<Quote> amendQuotes, List<AssetActionSource> assetActionSources, Map<Id, AssetContractRelationship> contractAssetsMap, Map<Id, Contract> contractMap, Map<Id, Account> accountMap){
        for(Quote quote : amendQuotes){
            Id cId = quote.contractId;
            if(cId == null) continue;
            Account acct = accountMap.get(contractMap.get(cId).AccountId);
            if(acct==null) continue;
            AssetContractRelationship acr = contractAssetsMap.get(cId);
            if(acr == null) continue;
            for(AssetActionSource aas : assetActionSources){
                if(aas.AssetAction.AssetId == acr.AssetId){
                    assignBillingInformationFields(quote, aas, acct);
                    break;
                }
            }
        }
    }
    
    public void assignBillingInformationFields(Quote quote, AssetActionSource aas, Account acct){
        quote.CurrencyIsoCode = aas.CurrencyIsoCode;
        quote.AutoRenewal__c  = aas.AutoRenewCode__c;
        quote.RenewalTerm__c = aas.RenewalTerm__c;
    }

    //Non Trigger methods

    public void createAmendQuoteLines(Id opptyId, Id quoteId, List<Id> assetProductIds) {
        List<OpportunityLineItem> opptyLines = amendQuoteDataSelector.selectOpportunityLineItems(opptyId);

        List<Quote> quotes = quoteDAO.getQuotesForSync(new Set<Id>{ quoteId });
        Quote quote = quotes[0];
        List<QuoteLineItem> quoteLines = new List<QuoteLineItem>();
        QuoteLineItem quoteLine;

        if (opptyLines == null || opptyLines.size() < 1) {
            return;
        }

        for (OpportunityLineItem opptyLine : opptyLines) {
            if (assetProductIds.contains(opptyLine.Product2Id)) {
                continue;
            }
            quoteLine = new QuoteLineItem(
            quoteId = quoteId,
            Description = opptyLine.Description,
            OpportunityLineItemId = opptyLine.Id,
            PricebookEntryId = opptyLine.PricebookEntryId,
            Product2Id = opptyLine.Product2Id,
            Quantity = opptyLine.Quantity,
            StartDate = quote.ServiceStartDate__c,
            SubscriptionTerm = math.round(quote.Term__c),
            EndDate = quote.ServiceEndDate__c,
            UnitPrice = opptyLine.UnitPrice,
            PeriodBoundary = 'Anniversary');
            quoteLines.add(quoteLine);
        }

        quoteLineDAO.insertLines(quoteLines);

        List<RefreshPriceAction.RefreshPriceActionRequest> requests = new List<RefreshPriceAction.RefreshPriceActionRequest>();
        RefreshPriceAction.RefreshPriceActionRequest req = new RefreshPriceAction.RefreshPriceActionRequest();
        req.quoteId = quoteId;
        requests.add(req);
        RefreshPriceAction.refreshPrices(requests);    

    }

    @future
    public static void createAmendQuoteLinesAsync(Id opptyId, Id quoteId, List<Id> assetProductIds) {
        new AmendQuoteHelper().createAmendQuoteLines(opptyId, quoteId, assetProductIds);
    }

    public void updateQuoteIdToOppty(Id opptyId, Id quoteId) {

        Opportunity oppty = new Opportunity(Id = opptyId, SyncedQuoteId = quoteId);
        update oppty;
    
    }
    
    @future
    public static void updateQuoteToOpptyAsync(Id opptyId, Id quoteId) {
        new AmendQuoteHelper().updateQuoteIdToOppty(opptyId, quoteId);
    }

    public Map<Id,PlaceQuote.RecordResource> prepareQuoteActions( List<QuoteAction> quoteActions, String refQuoteId, String method){
        PlaceQuote.RecordResource quoteActionRecord;
        Map<Id, PlaceQuote.RecordResource> cloneQuoteActionRecordMap = new Map<Id, PlaceQuote.RecordResource>();

        for(QuoteAction qa : quoteActions){
            quoteActionRecord = new PlaceQuote.RecordResource(QuoteAction.getSobjectType(), method);
            quoteActionRecord.fieldValues = new Map<String, Object>();
            quoteActionRecord.fieldValues.put('QuoteId', '@{' + refQuoteId + '.id}');
            quoteActionRecord.fieldValues.put('SourceAssetId', qa.SourceAssetId);
            quoteActionRecord.fieldValues.put('Type', 'Amend');
            cloneQuoteActionRecordMap.put(qa.Id, quoteActionRecord);  //Using Original Quote Action Id as key so that it can be used to refer back in the QLI Record creation.
        }

        return cloneQuoteActionRecordMap;
    }
}