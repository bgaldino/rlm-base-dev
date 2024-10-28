public interface IEffectiveDiscountService {
    boolean shouldRun(Map<Id, QuoteLineItem> newQuoteLineItems, Map<Id, QuoteLineItem> oldQuoteLineItems);
    List<QuoteLineItem> calculateEffectiveDiscount(QuoteLineTriggerDataBag dataBag);
}