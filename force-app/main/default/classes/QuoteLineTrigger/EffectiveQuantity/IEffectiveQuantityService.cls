public interface IEffectiveQuantityService {
    boolean shouldRun(Map<Id, QuoteLineItem> newQuoteLineItems, Map<Id, QuoteLineItem> oldQuoteLineItems);
    List<QuoteLineItem> calculateEffectiveQuantity(QuoteLineTriggerDataBag dataBag);
}