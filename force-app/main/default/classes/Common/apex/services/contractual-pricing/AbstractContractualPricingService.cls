public abstract class AbstractContractualPricingService implements IContractualPricingService {
    public virtual void createOrUpdateContractsWithPricing(List<QuoteLineItem> quoteLines){
        throw new NotImplementedException();
    }
    public virtual void filterQuoteLines(List < QuoteLineItem > quoteLines, Map<Id,QuoteLineItem> quotelineMap){
        throw new NotImplementedException();
    }
}