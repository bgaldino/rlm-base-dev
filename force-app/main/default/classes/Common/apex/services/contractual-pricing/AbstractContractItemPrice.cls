public with sharing abstract class AbstractContractItemPrice implements IContractItemPriceDAO {
    public virtual  List<SObject> getContractItemForSync(Set<Id> contractItemIds,Set<Id> accountIdSet, Set<Id> productIdList, String status) {
        throw new NotImplementedException();
    }
    public virtual  List<SObject> getContractQuoteDraft(String status, Set<Id> productIdList ,String recordId) {
        throw new NotImplementedException();
    }
    public virtual  List<SObject> getContractQuoteFinalized(String status, Set<Id> accountIdSet ,Set<Id> productIdList, Boolean checkCurrency, String quoteCurrencyCode) {
        throw new NotImplementedException();
    }
    public virtual  List<SObject> getContractAccount(String status, String recordId, String type) {
        throw new NotImplementedException();
    }
    public virtual List<SObject> queryContractItemPrices(Set<Id> contractIds) {
        throw new NotImplementedException();
    }
    public virtual List<SObject> getContractService(String status, Set<Id> accountIdSet ,Set<Id> productIdList) {
        throw new NotImplementedException();
    }
    public virtual List<SObject> getContractItemPrices(Set<Id> accountIdSet ,Set<Id> productIdList) {
        throw new NotImplementedException();
    }
    public virtual List<Database.UpsertResult> contractItemPriceUpsert(List<SObject> contractItemPrices) {
        throw new NotImplementedException();
    }
    public virtual List<Database.DeleteResult> contractItemPriceDelete(List<SObject> contractItemPrices) {
        throw new NotImplementedException();
    }
    public virtual List<Database.SaveResult> contractItemPriceUpdate(List<SObject> contractItemPrices) {
        throw new NotImplementedException();
    }   
    
}