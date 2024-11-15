public with sharing class AmendQuoteDataSelector implements IAmendQuoteDataSelector {
    public static Map<Id, Contract> contractsMap;
    public static Set<Id> priorContractIds;

    public List<OpportunityLineItem> selectOpportunityLineItems(Id opportunityId) {
        String query = 'SELECT id, Description, PricebookEntryId, Product2Id, Quantity, Discount, UnitPrice'+
            ' FROM OpportunityLineItem'+
            ' WHERE OpportunityId = :opportunityId';

        return Database.queryWithBinds(query, new Map<String, Object>{ 'opportunityId' => opportunityId }, SecurityCheck.getAccessLevel());
    }

    public Map<Id, Contract> selectContracts(Set<Id> contractIds) {
        if(priorContractIds != null && priorContractIds.equals(contractIds) && contractsMap != null && contractsMap.size() > 0){
            return contractsMap;
        }
        else{
            String query = 'SELECT id, StartDate, EndDate, AccountId FROM contract WHERE id IN :contractIds';
            contractsMap = new Map<Id, Contract>((List<Contract>)Database.queryWithBinds(query, new Map<String, Object>{ 'contractIds' => contractIds }, SecurityCheck.getAccessLevel()));
            priorContractIds = contractIds;
        }
        return contractsMap;
    }

    public List<Quote> selectQuotes(Set<Id> quoteIds) {
        String query = 'SELECT id, accountId from Quote where id in :quoteIds';

        return Database.queryWithBinds(query, new Map<String, Object>{ 'quoteIds' => quoteIds }, SecurityCheck.getAccessLevel());
    }

    public Map<Id, QuoteAction> selectQuoteActions(Set<Id> quoteActionIds) {
        String query = 'SELECT id, SourceAsset.Tenant__c from QuoteAction where Id in :quoteActionIds';

        return  new Map<Id, QuoteAction>((List<QuoteAction>)Database.queryWithBinds(query, new Map<String, Object>{ 'quoteActionIds' => quoteActionIds }, SecurityCheck.getAccessLevel()));
    }

   public  Map<Id, QuoteAction> selectQuoteActionsByQuoteIds(Set<Id> quoteIds) {
        String query = 'SELECT id, SourceAssetId, Type from QuoteAction where quoteId in :quoteIds';

        return  new Map<Id, QuoteAction>((List<QuoteAction>)Database.queryWithBinds(query, new Map<String, Object>{ 'quoteIds' => quoteIds }, SecurityCheck.getAccessLevel()));
    }

    public List<AssetContractRelationship> selectAssetContractRelationships(Set<Id> contractIds){
        String query = 'SELECT ContractId, AssetId, Asset.LastModifiedDate from AssetContractRelationship where ContractId in :contractIds';

        return Database.queryWithBinds(query, new Map<String, Object>{ 'contractIds' => contractIds }, SecurityCheck.getAccessLevel());
    }

    public Map<Id, AssetAction> selectAssetActions(Set<Id> assetIds) {
        String query = 'SELECT Id, AssetId FROM AssetAction WHERE AssetId IN :assetIds';

        return  new Map<Id, AssetAction>((List<AssetAction>)Database.queryWithBinds(query, new Map<String, Object>{ 'assetIds' => assetIds }, SecurityCheck.getAccessLevel()));
    }

    public List<AssetActionSource> selectAssetActionSources(Set<Id> assetActionIds) {
        String query = 'SELECT id, AssetAction.AssetId, AutoRenewCode__c, CurrencyIsoCode, '
        +' BillingFrequency__c, RenewalTerm__c, '
        +' from AssetActionSource where AssetActionId in :assetActionIds';

        return Database.queryWithBinds(query, new Map<String, Object>{ 'assetActionIds' => assetActionIds }, SecurityCheck.getAccessLevel());
    }
    
    public  Map<Id, Account> selectAccountByQuoteAccountIds(Set<Id> quoteAccountIds) {
        String query = 'SELECT id, Name from Account where Id in :quoteAccountIds';

        return  new Map<Id, Account>((List<Account>)Database.queryWithBinds(query, new Map<String, Object>{ 'quoteAccountIds' => quoteAccountIds }, SecurityCheck.getAccessLevel()));
    }

}
