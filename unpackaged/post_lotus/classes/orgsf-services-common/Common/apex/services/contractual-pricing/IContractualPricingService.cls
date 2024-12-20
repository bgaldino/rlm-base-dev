public interface IContractualPricingService {
    void createOrUpdateContractsWithPricing(List<QuoteLineItem> quoteLines);
    void filterQuoteLines(List < QuoteLineItem > quoteLines, Map<Id,QuoteLineItem> quotelineMap);
    
}