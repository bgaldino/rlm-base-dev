public with sharing class DAORequest {
    
    public List<AbstractRecord> recordsToSave {get; set;}
    public Boolean isAllOrNone = false;
    public DMLOperation operation = DMLOperation.OP_UPSERT;
    public ITransformSObject mapper {get; set;}
    public AccessLevel accessLevel {get; set;}

}