public interface IContractDAO {
    List<SObject> getContractByAccountId(String type,Set<Id> accountIdSet);
    List<Database.SaveResult> contractInsert(List<SObject> contracts);
    List<Database.SaveResult> contractUpdate(List<SObject> contracts);
}