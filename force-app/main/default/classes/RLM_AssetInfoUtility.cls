public without sharing class RLM_AssetInfoUtility{
    @InvocableMethod(label = 'Calculate Asset Info'description = 'Returns Asset Renewal Info')
    public static void calculateAssetRenewInfo(List<CreateAssetOrderEvent> assetOrderCreationEvents){
        if (assetOrderCreationEvents.isEmpty()){
            return;
        }

        CreateAssetOrderEvent assetOrderCreationEvent = assetOrderCreationEvents.get(0);
        Map<Id, OrderItem> orderItemsMap = fetchOrderItems(assetOrderCreationEvent.AssetDetails);
        Map<Id, AssetContractRelationship> acrMap = fetchAssetContractRelationships(assetOrderCreationEvent.AssetDetails);

        List<Asset> assetsToUpdate = new List<Asset>();

        for (CreateAssetOrderDtlEvent assetDetailEvent : assetOrderCreationEvent.AssetDetails){
            assetsToUpdate.add(processAssetDetailEvent(assetDetailEvent, orderItemsMap, acrMap));
        }

        if (!assetsToUpdate.isEmpty()){
            // Check CRUD permissions before upsert operation
            if (Schema.sObjectType.Asset.isCreateable() && Schema.sObjectType.Asset.isUpdateable()){
                upsert assetsToUpdate;
            }
        }
    }

    private static Map<Id, OrderItem> fetchOrderItems(List<CreateAssetOrderDtlEvent> assetDetailEvents){
        Set<Id> orderItemIds = new Set<Id>();
        for (CreateAssetOrderDtlEvent event : assetDetailEvents){
            orderItemIds.add(event.OrderItemId);
        }

        return new Map<Id, OrderItem>([SELECT Id, ServiceDate, EndDate, OrderAction.Type, ProductSellingModel.SellingModelType, ProductSellingModel.PricingTermUnit, Product2.Name
                                       FROM OrderItem
                                       WHERE Id IN:orderItemIds]);
    }

    private static Map<Id, AssetContractRelationship> fetchAssetContractRelationships(List<CreateAssetOrderDtlEvent> assetDetailEvents){
        Set<Id> assetIds = new Set<Id>();
        for (CreateAssetOrderDtlEvent event : assetDetailEvents){
            assetIds.add(event.AssetId);
        }

        return new Map<Id, AssetContractRelationship>([SELECT Id, AssetId, Contract.ContractTerm
                                                       FROM AssetContractRelationship
                                                       WHERE AssetId IN:assetIds]);
    }

    private static Asset processAssetDetailEvent(CreateAssetOrderDtlEvent assetDetailEvent, Map<Id, OrderItem> orderItemsMap, Map<Id, AssetContractRelationship> acrMap){
        OrderItem oi = orderItemsMap.get(assetDetailEvent.OrderItemId);
        Asset assetToUpdate = new Asset();
        assetToUpdate.Id = assetDetailEvent.AssetId;

        if (oi.OrderAction.Type == 'Add'){
            setRenewalInfoForNewAsset(oi, assetToUpdate);
        } else{
            updateRenewalInfoForExistingAsset(acrMap.get(assetDetailEvent.AssetId), assetToUpdate);
        }

        return assetToUpdate;
    }

    private static void setRenewalInfoForNewAsset(OrderItem oi, Asset assetToUpdate){
        if (oi.ProductSellingModel.SellingModelType == 'TermDefined' && oi.ProductSellingModel.PricingTermUnit == 'Months'){
            Integer monthsBetween = oi.ServiceDate.monthsBetween(oi.EndDate) + ((oi.EndDate.day() > oi.ServiceDate.day()) ? 1 : 0);
            assetToUpdate.RenewalTerm = (oi.ProductSellingModel.PricingTermUnit == 'Months') ? monthsBetween : monthsBetween / 12;
            assetToUpdate.RenewalTermUnit = oi.ProductSellingModel.PricingTermUnit;
        } else if (oi.ProductSellingModel.SellingModelType == 'Evergreen'){
            assetToUpdate.RenewalTerm = (oi.ProductSellingModel.PricingTermUnit == 'Months') ? 12 : 1;
            assetToUpdate.RenewalTermUnit = oi.ProductSellingModel.PricingTermUnit;
        } else{
            assetToUpdate.RenewalTerm = 1;
            assetToUpdate.RenewalTermUnit = 'Annual';
        }
        assetToUpdate.PricingSource = 'LastTransaction';
    }

    private static void updateRenewalInfoForExistingAsset(AssetContractRelationship acr, Asset assetToUpdate){
        if (acr != null){
            assetToUpdate.RenewalTermUnit = 'Months';
            assetToUpdate.RenewalTerm = acr.Contract.ContractTerm;
            assetToUpdate.PricingSource = 'PriceBookListPrice';
        }
    }

}