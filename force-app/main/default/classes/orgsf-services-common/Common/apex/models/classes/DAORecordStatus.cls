public with sharing class DAORecordStatus {
    public List<String> errorMessages {get; set;}
    public Boolean isSuccess {get; set;}
    public AbstractRecord record {get; set;}
}