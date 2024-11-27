public abstract with sharing class AbstractQLIDPPValidationService implements IQuoteLineItemDPPValidationService {
    public virtual void validateQuoteLineItems(List<QuoteLineItem> quoteLineItems) {
        throw new NotImplementedException();
    }

    public virtual void validateQuoteIds(Set<Id> quoteIds) {
        throw new NotImplementedException();
    }

    public virtual void validateQuoteLineByQuoteId(Map<Id, List<QuoteLineItem>> qliByQuoteIdMap) {
        throw new NotImplementedException();
    }
}
