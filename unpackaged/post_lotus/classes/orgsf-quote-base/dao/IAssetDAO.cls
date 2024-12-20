public interface IAssetDAO {
    void insertLines(List<Asset> lines);
    void updateLines(List<Asset> lines);
    void deleteLines(List<Asset> lines);
    List<Asset> getAssetsByAccountAndProductId(Id accountID, Set<Id> contributingProductIds);
    List<Asset> getAssetLinesWithTenant(Id accountId, Date serviceStartDate);
    List<AssetActionSource> getActionAssetSourcesForEffectiveFieldCalculation(List<QuoteLineItem> quoteLineItems);
}