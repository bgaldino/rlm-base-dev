public interface IContractItemPriceDAO {
    List<SObject> getContractItemForSync(Set<Id> contractItemIds,Set<Id> accountIdSet, Set<Id> productIdList, String status);
	List<SObject> getContractQuoteDraft(String status, Set<Id> productIdList ,String recordId);
    List<SObject> getContractQuoteFinalized(String status, Set<Id> accountIdSet ,Set<Id> productIdList, Boolean checkCurrency, String quoteCurrencyCode);
    List<SObject> getContractAccount(String status, String recordId, String type);
    List<SObject> queryContractItemPrices(Set<Id> contractIds);
    List<SObject> getContractService(String status, Set<Id> accountIdSet ,Set<Id> productIdList);
    List<SObject> getContractItemPrices(Set<Id> accountIdSet ,Set<Id> productIdList);
    List<Database.UpsertResult> contractItemPriceUpsert(List<SObject> contractItemPrices);
    List<Database.DeleteResult> contractItemPriceDelete(List<SObject> contractItemPrices);
    List<Database.SaveResult> contractItemPriceUpdate(List<SObject> contractItemPrices);
}