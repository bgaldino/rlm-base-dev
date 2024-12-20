public with sharing class EffectiveQuantityUtil {
    private static final String EFFECTIVE_QUANTITY_TREATMENT_ATTRIBUTE_KEY = 'EffectiveQuantityTreatment';

    public static Integer hashQuoteProductKey(Id quoteId, Id productId, Id productSellingModelId) {
        return (31 * String.valueOf(quoteId).toUpperCase().hashCode()) ^
            String.valueOf(productId).toUpperCase().hashCode() ^
            String.valueOf(productSellingModelId).toUpperCase().hashCode();
    }

    public static Integer hashAccountProductKey(Id accountId, Id productId, Id productSellingModelId) {
        return (31 * String.valueOf(accountId).toUpperCase().hashCode()) ^
            String.valueOf(productId).toUpperCase().hashCode() ^
            String.valueOf(productSellingModelId).toUpperCase().hashCode();
    }

    public static boolean areDatesOverlapping(Quote quote, QuoteLineItem quoteLineItem, AssetActionSource assetActionSource) {
        if (areQLIDatesNull(quoteLineItem)) {
            return quote.ServiceStartDate__c <= assetActionSource.EndDate && quote.ServiceEndDate__c >= assetActionSource.StartDate;
        }
        return quoteLineItem.StartDate <= assetActionSource.EndDate && quoteLineItem.EndDate >= assetActionSource.StartDate;
    }

    public static Boolean quoteAndQLIDatesMatch(Quote quote, QuoteLineItem quoteLineItem) {
        //Assume QLI Start Dates match Quote if null.
        if (areQLIDatesNull(quoteLineItem)) {
            return true;
        }
        return quote.ServiceStartDate__c == quoteLineItem.StartDate && quote.ServiceEndDate__c == quoteLineItem.EndDate;
    }

    public static Boolean isAnnualized(Id product2Id, Map<Id, Map<String, Object>> productAttributes) {
        if (product2Id == null || productAttributes == null || productAttributes.size() == 0) {
            return false;
        }

        if (!productAttributes.containsKey(product2Id)) {
            return false;
        }

        Map<String, Object> attributes = productAttributes.get(product2Id);
        if (!attributes.containsKey(EFFECTIVE_QUANTITY_TREATMENT_ATTRIBUTE_KEY)) {
            return false;
        }

        return attributes.get(EFFECTIVE_QUANTITY_TREATMENT_ATTRIBUTE_KEY) == 'Annualized';
    }

    public static Integer calculateQuoteLineItemLengthInMonths(Quote quote, QuoteLineItem quoteLineItem) {
        if (areQLIDatesNull(quoteLineItem)) {
            return calculateDifferenceBetweenDatesInMonths(quote.ServiceStartDate__c, quote.ServiceEndDate__c);
        }
        return calculateDifferenceBetweenDatesInMonths(quoteLineItem.StartDate, quoteLineItem.EndDate);
    }

    public static Integer calculateAssetLengthInMonths(AssetActionSource assetActionSource) {
        return calculateDifferenceBetweenDatesInMonths(
            assetActionSource?.AssetAction?.Asset?.LifecycleStartDate,
            assetActionSource?.AssetAction?.Asset?.LifecycleEndDate
        );
    }

    public static Integer calculateDifferenceBetweenDatesInMonths(Datetime startDate, Datetime endDate) {
        if (startDate == null || endDate == null) {
            return 0;
        }

        Integer startDateMonths = startDate.year() * 12 + startDate.month();
        Integer endDateMonths = endDate.year() * 12 + endDate.month();
        return endDateMonths - startDateMonths;
    }

    public static Boolean areQLIDatesNull(QuoteLineItem quoteLineItem) {
        return quoteLineItem.StartDate == null && quoteLineItem.EndDate == null;
    }
}
