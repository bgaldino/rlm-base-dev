public with sharing class EffectiveQuantityService implements IEffectiveQuantityService {
    public static boolean quotesHadTermChange = false;
    private static boolean hasRunDueToTermChange = false;

    private IEffectiveQuantityCalculator effectiveQuantityCalculator;

    public EffectiveQuantityService() {
        this((IEffectiveQuantityCalculator) ServiceRegistry.getInstance('IEffectiveQuantityCalculator'));
    }

    public EffectiveQuantityService(IEffectiveQuantityCalculator effectiveQuantityCalculator) {
        this.effectiveQuantityCalculator = effectiveQuantityCalculator;
    }

    public boolean shouldRun(Map<Id, QuoteLineItem> newQuoteLineItems, Map<Id, QuoteLineItem> oldQuoteLineItems) {
        if (quotesHadTermChange && !hasRunDueToTermChange) {
            hasRunDueToTermChange = true;
            return true;
        }

        if (newQuoteLineItems == null || newQuoteLineItems.isEmpty()) {
            return false;
        }

        for (QuoteLineItem qli : newQuoteLineItems.values()) {
            if (qli.Quantity != null && qli.Quantity != oldQuoteLineItems?.get(qli.Id).Quantity) {
                return true;
            }
        }
        
        return false;
    }

    public List<QuoteLineItem> calculateEffectiveQuantity(QuoteLineTriggerDataBag dataBag) {
        EffectiveQuantityDataBag effectiveQuantityDataBag = new EffectiveQuantityDataBag();
        effectiveQuantityDataBag.quoteLineTriggerDataBag = dataBag;

        effectiveQuantityCalculator.calculateCumulativeQuantity(effectiveQuantityDataBag);
        effectiveQuantityCalculator.calculateAssetActionSourceSum(effectiveQuantityDataBag);
        List<QuoteLineItem> quoteLineItems = new List<QuoteLineItem>();

        for (Id quoteId : dataBag.quoteMap.keySet()) {
            Quote quote = dataBag.quoteMap.get(quoteId);
            if (quote == null) {
                continue;
            }

            if (dataBag.quoteLineItemsWithRelatedFieldsByQuote.get(quote.Id) == null) {
                continue;
            }

            for (QuoteLineItem quoteLineItem : dataBag.newQuoteLineItemsByQuote.get(quote.Id)) {
                quoteLineItem.EffectiveQuantity__c = 0;
                setFromCurrentQuoteQuantities(effectiveQuantityDataBag.cumulativeQuantityMap, quoteLineItem);
                setFromAssetActionSources(effectiveQuantityDataBag.assetActionSourceMap, quoteLineItem, quote);
                if (EffectiveQuantityUtil.isAnnualized(quoteLineItem.Product2Id, dataBag.productAttributes)) {
                    calculateAnnualizedQuantity(effectiveQuantityDataBag, quoteLineItem, quote);
                }
                quoteLineItems.add(quoteLineItem);
            }
        }
        return quoteLineItems;
    }

    public void calculateAnnualizedQuantity(EffectiveQuantityDataBag dataBag, QuoteLineItem quoteLineItem, Quote quote) {
        Integer quoteProductKey = EffectiveQuantityUtil.hashQuoteProductKey(
            quoteLineItem.QuoteId,
            quoteLineItem.Product2Id,
            quoteLineItem.ProductSellingModelId
        );

        Integer accountProductKey = EffectiveQuantityUtil.hashAccountProductKey(
            quote.AccountId,
            quoteLineItem.Product2Id,
            quoteLineItem.ProductSellingModelId
        );

        Integer qliTerm = dataBag.longestQLITermInMonths.get(quoteProductKey) ?? 0;
        Integer assetTerm = dataBag.longestAssetTermInMonths.get(accountProductKey) ?? 0;

        Integer longestTerm = Math.max(qliTerm, assetTerm);
        if (longestTerm <= 12) {
            return;
        }

        quoteLineItem.EffectiveQuantity__c = ((Double)quoteLineItem.EffectiveQuantity__c / longestTerm) * 12;
    }

    private static void setFromCurrentQuoteQuantities(Map<Integer, Double> currentQuoteQuantities, QuoteLineItem quoteLineItem) {
        Integer productKey = EffectiveQuantityUtil.hashQuoteProductKey(quoteLineItem.QuoteId, quoteLineItem.Product2Id, quoteLineItem.ProductSellingModelId);
        if (!currentQuoteQuantities.containsKey(productKey)) {
            return;
        }
        quoteLineItem.EffectiveQuantity__c = currentQuoteQuantities.get(productKey);
    }

    private static void setFromAssetActionSources(Map<Integer, List<AssetActionSource>> assetActionSourcesMap, QuoteLineItem quoteLineItem, Quote quote) {
        Integer productKey = EffectiveQuantityUtil.hashAccountProductKey(
            quote.AccountId,
            quoteLineItem.Product2Id,
            quoteLineItem.ProductSellingModelId
        );
        if (!assetActionSourcesMap.containsKey(productKey)) {
            return;
        }

        List<AssetActionSource> assetActionSourcesByProductKey = assetActionSourcesMap.get(productKey);
        if (assetActionSourcesByProductKey == null || assetActionSourcesByProductKey.size() == 0) {
            return;
        }

        for (AssetActionSource assetActionSource : assetActionSourcesByProductKey) {
            if (!EffectiveQuantityUtil.areDatesOverlapping(quote, quoteLineItem, assetActionSource)) {
                continue;
            }
            quoteLineItem.EffectiveQuantity__c += assetActionSource.Quantity;
        }
    }
}
