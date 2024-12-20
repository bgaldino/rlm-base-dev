public with sharing class ContractDAO extends AbstractContractDAO{
    
    private static IContractDAO instance = null;
    
    public static IContractDAO getInstance() {
        if (instance == null) {
            instance = new ContractDAO();
        }
        return instance;
    }
    
    public static void setInstance(IContractDAO existingInstance) {
        instance = existingInstance;
    }
    
    public override List<SObject> getContractByAccountId(String type, Set<Id> accountIdSet) {
        List<String> fields = getContractFields();
        return this.runQuery(fields, type, accountIdSet);
    }
    
    private static List<String> getContractFields() {
        return new List<String>{
            	'Id',
                'AccountId',
                'CurrencyIsoCode',
                'Status',
                'Type__c',
                'ContractTerm',
                'startDate'
                };
    }
    
    private List<Contract> runQuery(List<String> fields,String type,Set<Id> accountIdSet) {
        String query = String.format(
            'SELECT {0} FROM Contract WHERE Type__c =:type AND AccountId IN:accountIdSet', 
            new List<String>{ String.join(fields, ', ') }
        );
        
        return Database.queryWithBinds(query, new Map<String, Object>{ 'type' => type, 'accountIdSet' =>accountIdSet}, SecurityCheck.getAccessLevel());
    }
    
    public override List<Database.SaveResult> contractInsert(List<Sobject> contracts) {
        List<Database.SaveResult> saveResultList;
        if (contracts.getSObjectType().getDescribe().isCreateable()) {
            saveResultList = Database.insert(contracts, SecurityCheck.getAccessLevel());
        }
        return saveResultList;
    }

    public override List<Database.SaveResult> contractUpdate(List<SObject> contracts){
        List<Database.SaveResult> saveResultList;
        if(contracts.getSObjectType().getDescribe().isUpdateable()){
            saveResultList = Database.update(contracts, SecurityCheck.getAccessLevel());
        }
        return saveResultList;
    }
}