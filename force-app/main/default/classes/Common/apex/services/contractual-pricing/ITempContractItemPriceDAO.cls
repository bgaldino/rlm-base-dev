public interface ITempContractItemPriceDAO {
    List<SObject> getTempContractItemPricesByCIPId(String status,Set<Id> contractIdSet);
    List<SObject> queryTempContractItemPrices(String status, Set<Id> contractIds);
    List<SObject> getTempContractItemPricesByContractId(String status,Set<Id> contractIdSet);
    List<SObject> getTempContractItemPricesByQuoteId(String status,Set<Id> quoteIdSet);
    List<Database.UpsertResult> tempContractItemPriceUpsert(List<SObject> tempContractItemPrices);
    List<Database.DeleteResult> tempContractItemPriceDelete(List<SObject> tempContractItemPrices);
    List<Database.SaveResult> tempContractItemPriceUpdate(List<SObject> contractItemPrices);
}
