public with sharing abstract class AbstractContractDAO implements IContractDAO{
    public virtual List<SObject> getContractByAccountId(String type, Set<Id> accountIdSet) {
        throw new NotImplementedException();
    }
    public virtual List<Database.SaveResult> contractInsert(List<SObject> contracts){
        throw new NotImplementedException();
    }
    public virtual List<Database.SaveResult> contractUpdate(List<SObject> contracts){
        throw new NotImplementedException();
    }
}