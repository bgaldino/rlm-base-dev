public with sharing class EffectiveQuantityCalculator implements IEffectiveQuantityCalculator {
    private IAssetDAO assetDAO;

    public EffectiveQuantityCalculator() {
        this((IAssetDAO) ServiceRegistry.getInstance('IAssetDAO'));
    }

    public EffectiveQuantityCalculator(IAssetDAO assetDAO) {
        this.assetDAO = assetDAO;
    }

    public void calculateCumulativeQuantity(EffectiveQuantityDataBag effectiveQuantityDataBag) {
        Map<Id, Quote> quoteMap = effectiveQuantityDataBag.quoteLineTriggerDataBag.quoteMap;
        Map<Id, List<QuoteLineItem>> quoteLineItemsByQuote = effectiveQuantityDataBag.quoteLineTriggerDataBag.quoteLineItemsWithRelatedFieldsByQuote;

        if (quoteMap == null || quoteMap.size() == 0) {
            return;
        }

        if (quoteLineItemsByQuote == null || quoteLineItemsByQuote.size() == 0) {
            return;
        }

        for (Id quoteId : quoteMap.keySet()) {
            Quote quote = quoteMap.get(quoteId);
            if (quote == null) {
                continue;
            }
                
            processQuoteLines(effectiveQuantityDataBag, quote, quoteLineItemsByQuote.get(quote.Id));
        }
    }

    @TestVisible
    private static void processQuoteLines(EffectiveQuantityDataBag effectiveQuantityDataBag, Quote quote, List<QuoteLineItem> quoteLineItems) {
        if (quoteLineItems == null || quoteLineItems.size() == 0) {
            return;
        }

        for (QuoteLineItem currentQuoteLineItem : quoteLineItems) {
            QuoteLineItem quoteLineItem = pickQLIToUse(currentQuoteLineItem, effectiveQuantityDataBag);
            Integer productKey = EffectiveQuantityUtil.hashQuoteProductKey(quoteLineItem.QuoteId, quoteLineItem.Product2Id, quoteLineItem.ProductSellingModelId);
            determineLongestQLITerm(effectiveQuantityDataBag, productKey, quote, quoteLineItem);
            sumSimilarQuoteLineItemQuantities(effectiveQuantityDataBag, productKey, quote, quoteLineItem);
        }
    }

    @TestVisible
    private static void determineLongestQLITerm(EffectiveQuantityDataBag effectiveQuantityDataBag, Integer productKey, Quote quote, QuoteLineItem quoteLineItem) {
        if (!effectiveQuantityDataBag.longestQLITermInMonths.containsKey(productKey)) {
            effectiveQuantityDataBag.longestQLITermInMonths.put(productKey, 0);
        }
        Integer qliTerm = EffectiveQuantityUtil.calculateQuoteLineItemLengthInMonths(quote, quoteLineItem);

        if (qliTerm > effectiveQuantityDataBag.longestQLITermInMonths.get(productKey)) {
            effectiveQuantityDataBag.longestQLITermInMonths.put(productKey, qliTerm);
        }
    }
    
    @TestVisible
    private static void sumSimilarQuoteLineItemQuantities(EffectiveQuantityDataBag effectiveQuantityDataBag, Integer productKey, Quote quote, QuoteLineItem quoteLineItem) {
        if (!EffectiveQuantityUtil.quoteAndQLIDatesMatch(quote, quoteLineItem)) {
            return;
        }

        if (!effectiveQuantityDataBag.cumulativeQuantityMap.containsKey(productKey)) {
            effectiveQuantityDataBag.cumulativeQuantityMap.put(productKey, 0);
        }

        effectiveQuantityDataBag.cumulativeQuantityMap.put(productKey, effectiveQuantityDataBag.cumulativeQuantityMap.get(productKey) + quoteLineItem.Quantity);
    }

    public void calculateAssetActionSourceSum(EffectiveQuantityDataBag effectiveQuantityDataBag) {
        Map<Id, List<QuoteLineItem>> quoteLineItemsByQuote = effectiveQuantityDataBag.quoteLineTriggerDataBag.quoteLineItemsWithRelatedFieldsByQuote;
        if (quoteLineItemsByQuote == null || quoteLineItemsByQuote.size() == 0) {
            return;
        }

        List<QuoteLineItem> quoteLineItems = new List<QuoteLineItem>();
        for (Id quoteId : quoteLineItemsByQuote.keySet()) {
            quoteLineItems.addAll(quoteLineItemsByQuote.get(quoteId));
        }
        List<AssetActionSource> assetActionSources = assetDAO.getActionAssetSourcesForEffectiveFieldCalculation(quoteLineItems);
        mapAssetActionSourcesByAccount(effectiveQuantityDataBag, assetActionSources);
    }

    @TestVisible
    private static void mapAssetActionSourcesByAccount(EffectiveQuantityDataBag effectiveQuantityDataBag, List<AssetActionSource> assetActionSources) {
        if (assetActionSources == null || assetActionSources.size() == 0) {
            return;
        }

        for (AssetActionSource assetActionSource : assetActionSources) {
            Integer assetActionSourceKey = EffectiveQuantityUtil.hashAccountProductKey(
                assetActionSource.AssetAction.Asset.AccountId,
                assetActionSource.AssetAction.Asset.Product2Id,
                assetActionSource.ProductSellingModel.Id
            );

            if (!effectiveQuantityDataBag.assetActionSourceMap.containsKey(assetActionSourceKey)) {
                effectiveQuantityDataBag.assetActionSourceMap.put(assetActionSourceKey, new List<AssetActionSource>());
            }
            effectiveQuantityDataBag.assetActionSourceMap.get(assetActionSourceKey).add(assetActionSource);

            determineLongestAssetTerm(effectiveQuantityDataBag, assetActionSourceKey, assetActionSource);
        }
    }

    @TestVisible
    private static void determineLongestAssetTerm(EffectiveQuantityDataBag effectiveQuantityDataBag, Integer assetActionSourceKey, AssetActionSource assetActionSource) {
        if (!effectiveQuantityDataBag.longestAssetTermInMonths.containsKey(assetActionSourceKey)) {
            effectiveQuantityDataBag.longestAssetTermInMonths.put(assetActionSourceKey, 0);
        }
        Integer assetTerm = EffectiveQuantityUtil.calculateAssetLengthInMonths(assetActionSource);

        if (assetTerm > effectiveQuantityDataBag.longestAssetTermInMonths.get(assetActionSourceKey)) {
            effectiveQuantityDataBag.longestAssetTermInMonths.put(assetActionSourceKey, assetTerm);
        }
    }

    private static QuoteLineItem pickQLIToUse(QuoteLineItem currentQuoteLineItem, EffectiveQuantityDataBag effectiveQuantityDataBag) {
        QuoteLineItem updatedQuoteLineItem = effectiveQuantityDataBag?.quoteLineTriggerDataBag?.newQuoteLineItems?.get(currentQuoteLineItem.Id);
        return updatedQuoteLineItem ?? currentQuoteLineItem;
    }
}
