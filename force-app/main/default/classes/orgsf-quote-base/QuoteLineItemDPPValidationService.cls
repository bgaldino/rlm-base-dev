public with sharing class QuoteLineItemDPPValidationService implements IQuoteLineItemDPPValidationService {
    private IDerivedPriceDAO derivedPriceDAO;
    private IAssetDAO assetDAO;
    private static final String ASSET_EXCEPTION_MSG = System.Label.QuoteLineDPPValidationBasedOnContributingAsset;
    private static Map<Id, Set<Id>> dppToCPMap = new Map<Id, Set<Id>>();
    private static Map<Id, QuoteLineItem> quoteLineItemsByQuoteIdMap = new  Map<Id, QuoteLineItem>();
    @TestVisible
    public static Map<Id, List<string>> quoteLineItemValidationMsg = new Map<Id, List<string>>();

    public QuoteLineItemDPPValidationService() {
        this.derivedPriceDAO = (IDerivedPriceDAO) ServiceRegistry.getInstance('IDerivedPriceDAO');
        this.assetDAO = (IAssetDAO) ServiceRegistry.getInstance('IAssetDAO');
    }

    public void validateQuoteLineItems(List<QuoteLineItem> quoteLineItems) {
        if(quoteLineItems.isEmpty()){
            return;
        }
        Set<Id> pricebookEntryIds = new Set<Id>();

        //This Map will store all related DPP QLI's with respect to Quote ID 
        Map<Id, List<QuoteLineItem>> dppQLIMap = new Map<Id, List<QuoteLineItem>>();

            if(!quoteLineItems.isEmpty()){
                for(QuoteLineItem quoteLineItem : quoteLineItems) {
                    quoteLineItemsByQuoteIdMap.put(quoteLineItem.id, quoteLineItem);
                    processQuoteLineItems(quoteLineItem, pricebookEntryIds, dppQLIMap);
                }
                fetchDerivedPricesBasedOnDPPInGrid(dppQLIMap, pricebookEntryIds);
                processValidations(dppQLIMap);
            }
    }

    private void processQuoteLineItems(QuoteLineItem quoteLineItem, Set<Id> pricebookEntryIds, Map<Id, List<QuoteLineItem>> dppQLIMap) {

        if(quoteLineItem.PricebookEntry.IsDerived && !string.isBlank(quoteLineItem.Tenant__c)) {
            pricebookEntryIds.add(quoteLineItem.PricebookEntryId);
            addQuoteLineItemsToMap(dppQLIMap, quoteLineItem);
        }
    }

    //Utility method to form Map for the QLI
    private void addQuoteLineItemsToMap(Map<Id, List<QuoteLineItem>> quoteLineItemMap, QuoteLineItem quoteLineItem) {
        if(quoteLineItemMap.containsKey(quoteLineItem.QuoteId)) {
            quoteLineItemMap.get(quoteLineItem.QuoteId).add(quoteLineItem);
        }
        else {
            quoteLineItemMap.put(quoteLineItem.QuoteId, new List<QuoteLineItem>{quoteLineItem});
        }
    }

    //Process Validations based on DPP QLI's in the Grid
    private void processValidations(Map<Id, List<QuoteLineItem>> dppQLIMap) {
        for(Id quoteId:dppQLIMap.keyset()) {
            if(!dppToCPMap.isEmpty()){
                processModifiedDPPInGrid(dppQLIMap.get(quoteId));
            }
        }
    }

    //Process Validations for DPP In Grid 
    private void processModifiedDPPInGrid(List<QuoteLineItem> dppQLI) {
        List<Asset> contributingAssets = queryContributingAssetData(dppQLI, dppToCPMap);
        if(!contributingAssets.isEmpty()) {
            for(QuoteLineItem dppQLIRecord: dppQLI) {
                validateDPPStateInAsset(dppQLIRecord, contributingAssets);
            }
        }
    }

    //Fetch Contributing Asset Data based on AccountID and related contributing products for DPP modified in Grid
    public List<Asset> queryContributingAssetData(List<QuoteLineItem> dppQLI, Map<Id, Set<Id>> dppToCPMap) {
        Set<Id> contributingProducts = new Set<Id>();
        List<Asset> contributingAssets = new List<Asset>();
        Id accountId = dppQLI[0].Quote.AccountId;
        for(QuoteLineItem dppQLIRecord: dppQLI) {
            if(dppToCPMap.containsKey(dppQLIRecord.PricebookEntryId)) {
                contributingProducts.addAll(dppToCPMap.get(dppQLIRecord.PricebookEntryId));
            }
        }
        if(!contributingProducts.isEmpty()) {
            contributingAssets = assetDAO.getAssetsByAccountAndProductId(accountId, contributingProducts);
        }
        return contributingAssets;
    }

    //Validate Modified DPP QLI's in Grid over the Contributing Assets in the account if no CP QLI exists in Grid
    private void validateDPPStateInAsset(QuoteLineItem dppQLIRecord, List<Asset> contributingAssets) {
        for(Asset contAsset: contributingAssets) {
            //Check if dates of dpp line item overlap with contributing assets
            if(dppToCPMap.containsKey(dppQLIRecord.PricebookEntryId) && dppToCPMap.get(dppQLIRecord.PricebookEntryId).contains(contAsset.Product2id) && 
                dppQLIRecord.Tenant__c.equals(contAsset.Tenant__c) && (dppQLIRecord.EndDate > contAsset.CurrentLifecycleEndDate.date() ||
                dppQLIRecord.StartDate < contAsset.LifecycleStartDate.date())) {
                String quoteLineProduct = quoteLineItemsByQuoteIdMap.get(dppQLIRecord.id).Product2.Name;
                String validationMsgFromAsset = String.format(ASSET_EXCEPTION_MSG, new List<String>{ quoteLineProduct});
                if(quoteLineItemValidationMsg.containsKey(dppQLIRecord.id)) {
                    quoteLineItemValidationMsg.get(dppQLIRecord.id).add(validationMsgFromAsset);
                }
                else {
                    quoteLineItemValidationMsg.put(dppQLIRecord.id, new List<String>{validationMsgFromAsset});
                }
            } 
        }
    }

    //Query Derived Prices based on DPP - PriceBookEntryId 
    public void fetchDerivedPricesBasedOnDPPInGrid(Map<Id,List<QuoteLineItem>> dppQLIMap, Set<Id> pricebookEntryIds) {
        List<PriceBookEntryDerivedPrice> derivedPrices = new List<PriceBookEntryDerivedPrice>();
        //Atleast for R4.1, we need
        Set<Id> contributingProductIds = new Set<Id>();
        //Query Derived Prices based on the DPP Products in the Grid
        if(!dppQLIMap.isEmpty() && !pricebookEntryIds.isEmpty()) {
            derivedPrices = derivedPriceDAO.getDerivedPricesByPriceBookEntryIds(pricebookEntryIds, contributingProductIds);
        }
        if(!derivedPrices.isEmpty()) {
            for(PriceBookEntryDerivedPrice derivedPrice : derivedPrices) {
                if(dppToCPMap.containsKey(derivedPrice.PricebookEntryId)) {
                    dppToCPMap.get(derivedPrice.PricebookEntryId).add(derivedPrice.ContributingProductId);
                }
                else {
                    dppToCPMap.put(derivedPrice.PricebookEntryId, new Set<Id>{derivedPrice.ContributingProductId});
                }
            }
        }
    }

    public void validateQuoteIds(Set<Id> quoteIds) {}
    public void validateQuoteLineByQuoteId(Map<Id, List<QuoteLineItem>> quotelineItemByQuoteIdMap) {}
}