public with sharing abstract class AbstractTempContractItemPrice implements ITempContractItemPriceDAO{
    public virtual List<SObject> getTempContractItemPricesByCIPId(String status,Set<Id> contractIdSet) {
        throw new NotImplementedException();
    }
    public virtual List<SObject> queryTempContractItemPrices(String status,Set<Id> contractIdSet) {
        throw new NotImplementedException();
    }
    public virtual List<SObject> getTempContractItemPricesByContractId(String status,Set<Id> contractIdSet) {
        throw new NotImplementedException();
    }
    public virtual List<Database.UpsertResult> tempContractItemPriceUpsert(List<SObject> tempContractItemPrices) {
        throw new NotImplementedException();
    }
    public virtual  List<Database.DeleteResult> tempContractItemPriceDelete(List<SObject> tempContractItemPrices) {
        throw new NotImplementedException();
    }
    public virtual List<Database.SaveResult> tempContractItemPriceUpdate(List<SObject> contractItemPrices) {
        throw new NotImplementedException();
    }
    public virtual List<SObject> getTempContractItemPricesByQuoteId(String status,Set<Id> quoteIdSet) {
        throw new NotImplementedException();
    }
}