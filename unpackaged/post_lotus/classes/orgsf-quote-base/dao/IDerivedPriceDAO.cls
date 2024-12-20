public interface IDerivedPriceDAO {
    void insertLines(List<PriceBookEntryDerivedPrice> lines);
    void updateLines(List<PriceBookEntryDerivedPrice> lines);
    void deleteLines(List<PriceBookEntryDerivedPrice> lines);
    List<PriceBookEntryDerivedPrice> getDerivedPricesByPriceBookEntryIds(Set<Id> pricebookEntryIds, Set<Id> contributingProductIds);
}