public Interface IAmendQuoteDataSelector {
    List<OpportunityLineItem> selectOpportunityLineItems(Id opportunityId);
    Map<Id, Contract> selectContracts(Set<Id> contractIds);
    List<Quote> selectQuotes(Set<Id> quoteIds);
    Map<Id, QuoteAction> selectQuoteActions(Set<Id> quoteActionIds);
    Map<Id, QuoteAction> selectQuoteActionsByQuoteIds(Set<Id> quoteIds);
    List<AssetContractRelationship> selectAssetContractRelationships(Set<Id> contractIds);
    Map<Id, AssetAction> selectAssetActions(Set<Id> assetIds);
    List<AssetActionSource> selectAssetActionSources(Set<Id> assetActionIds);
    Map<Id, Account> selectAccountByQuoteAccountIds(Set<Id> quoteAccountIds);
}