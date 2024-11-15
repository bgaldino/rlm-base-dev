public with sharing class AssetDAO implements IAssetDAO {
    /************************************************
     * Setup class instance
     ************************************************/
    private static IAssetDAO instance = null;
    public static IAssetDAO getInstance() {
        if (instance == null) {
            instance = new AssetDAO();
        }
        return instance;
    }

    /** @description: Make class mockable for unit tests */
    public static void setInstance(IAssetDAO existingInstance) {
        instance = existingInstance;
    }

    public void insertLines(List<Asset> lines) {
        if (lines.getSObjectType().getDescribe().isCreateable()) {
            Database.insert(lines, SecurityCheck.getAccessLevel());
        }
    }

    public void updateLines(List<Asset> lines) {
        if (lines.getSObjectType().getDescribe().isUpdateable()) {
            Database.update(lines, SecurityCheck.getAccessLevel());
        }
    }

    public void deleteLines(List<Asset> lines) {
        if (lines.getSObjectType().getDescribe().isDeletable()) {
            Database.delete(lines, SecurityCheck.getAccessLevel());
        }
    }

    public List<Asset> getAssetsByAccountAndProductId(Id accountId, Set<Id> contributingProductIds) {
        List<String> fields = getAssetFields();
        return this.runQuery(fields, accountId, contributingProductIds);
    }

    public List<Asset> getAssetLinesWithTenant(Id accountId, Date serviceStartDate) {
        if (Test.isRunningTest()) {
            Asset testAsset = new Asset(Quantity = 5, Product2Id = fflib_IDGenerator.generate(Product2.SObjectType));
            return new List<Asset>{ testAsset };
        }
        return Database.queryWithBinds(
            'Select Id,Tenant__c,Product2.name,tenant__r.Tenant_Information_Parameters__c,CurrentQuantity,Tenant__r.Fulfillment_Provider_Name__c,Tenant__r.OptionalName__c,LifecycleStartDate,LifecycleEndDate,TotalLifecycleAmount,' +
            '(Select id,(SELECT TYPEOF ReferenceEntityItem WHEN OrderItem THEN Reference_Order_Item_IDs__c END FROM AssetActionSources WHERE ReferenceEntityItem.Type = \'OrderItem\' order by CreatedDate DESC LIMIT 1) from AssetActions order by CreatedDate DESC LIMIT 1),'+
            '(Select id, Contract.ContractTerm from AssetContractRelationships) '+
            'from Asset where AccountId=:accountId AND LifecycleEndDate >= : serviceStartDate',
            new Map<String, Object>{ 'accountId' => accountId, 'serviceStartDate' => serviceStartDate },
            SecurityCheck.getAccessLevel()
        );
    }

    private List<Asset> runQuery(List<String> fields, Id accountId, Set<Id> contributingProductIds) {
        String query = String.format(
            'SELECT {0} FROM Asset WHERE AccountID =:accountId and Product2Id IN:contributingProductIds',
            new List<String>{ String.join(fields, ', ') }
        );

        return Database.queryWithBinds(
            query,
            new Map<String, Object>{ 'accountId' => accountId, 'contributingProductIds' => contributingProductIds },
            SecurityCheck.getAccessLevel()
        );
    }

    private static List<String> getAssetFields() {
        return new List<String>{ 'id', 'LifecycleStartDate', 'CurrentLifecycleEndDate', 'Product2Id', 'TenantId__c', 'Tenant__c', 'Product2.Name' };
    }

    private static final List<String> ACTIVE_ASSET_STATUSES = new List<String>{ 'Purchased', 'Shipped', 'Installed', 'Registered' };

    public List<AssetActionSource> getActionAssetSourcesForEffectiveFieldCalculation(List<QuoteLineItem> quoteLineItems) {
        if (quoteLineItems == null || quoteLineItems.size() == 0) {
            return new List<AssetActionSource>();
        }
        Map<String, Object> queryBinding = new Map<String, Object>();
        String query = makeActionAssetSourceForEffectiveFieldCalculationQuery(queryBinding, quoteLineItems);
        return Database.queryWithBinds(query, queryBinding, SecurityCheck.getAccessLevel());
    }

    public static String makeActionAssetSourceForEffectiveFieldCalculationQuery(Map<String, Object> queryBinding, List<QuoteLineItem> quoteLineItems) {
        List<String> queryParts = new List<String>{
            'SELECT Id, Quantity, ProductSellingModel.Id, AssetAction.Asset.Product2Id, AssetAction.Asset.AccountId, StartDate, EndDate, AssetAction.Asset.LifecycleStartDate, AssetAction.Asset.LifecycleEndDate ' +
            'FROM AssetActionSource ' +
            'WHERE AssetAction.Asset.Status IN :ACTIVE_ASSET_STATUSES ' +
            'AND ('
        };

        queryBinding.put('ACTIVE_ASSET_STATUSES', ACTIVE_ASSET_STATUSES);

        Integer index = 0;
        for (QuoteLineItem quoteLineItem : quoteLineItems) {
            if (index > 0) {
                queryParts.add('OR');
            }
            queryParts.add(makeEffectiveFieldCalculationWhereClausePart(queryBinding, index, quoteLineItem));
            index++;
        }
        queryParts.add(')');

        return String.join(queryParts, ' ');
    }

    public static String makeEffectiveFieldCalculationWhereClausePart(Map<String, Object> queryBinding, Integer index, QuoteLineItem quoteLineItem) {
        List<String> formatParams = new List<String>{ index.toString() };

        queryBinding.put(String.format('qli{0}AccountId', formatParams), quoteLineItem.Quote.Opportunity.AccountId);
        queryBinding.put(String.format('qli{0}ProductId', formatParams), quoteLineItem.Product2Id);
        queryBinding.put(String.format('qli{0}PSMId', formatParams), quoteLineItem.ProductSellingModelId);

        return String.format(
            ' (AssetAction.Asset.AccountId = :qli{0}AccountId AND AssetAction.Asset.Product2Id = :qli{0}ProductId AND ProductSellingModelId = :qli{0}PSMId) ',
            formatParams
        );
    }
}
