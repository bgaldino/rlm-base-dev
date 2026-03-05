public with sharing class RLM_AmendmentRenewalRepository {

    // ------------------------------------------------------------
    // Quote Header Summary
    // ------------------------------------------------------------
    public static Quote getQuote(Id quoteId) {
        return [
            SELECT Id,
                   AccountId,
                   Subtotal,
                   RLM_TotalDiscountAmount__c,
                   TotalPrice,
                   RLM_OriginalActionType__c
            FROM Quote
            WHERE Id = :quoteId
            LIMIT 1
        ];
    }

    // ------------------------------------------------------------
    // Quote Line Items with Product information
    // ------------------------------------------------------------
    public static List<QuoteLineItem> getQuoteLineItemsWithAssets(Id quoteId) {
        return [
            SELECT Id,
                   Product2Id,
                   Product2.Name,
                   Subtotal,
                   TotalAdjustmentAmount,
                   TotalPrice,
                   Quantity,
                   StartQuantity,
                   EndQuantity,
                   UnitPrice,
                   SubscriptionTerm,
                   SubscriptionTermUnit,
                   RLM_PreviousAmount__c
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId
            AND Product2Id != null
        ];
    }
    
    // ------------------------------------------------------------
    // Get Assets by Product2Id and AccountId (AccountId optional)
    // ------------------------------------------------------------
    public static Map<Id, List<Asset>> getAssetsByProduct(Set<Id> productIds, Id accountId) {
        if (productIds == null || productIds.isEmpty()) {
            return new Map<Id, List<Asset>>();
        }
        
        List<Asset> assets;
        if (accountId != null) {
            assets = [
                SELECT Id,
                       Name,
                       Product2Id,
                       AccountId,
                       CurrentAmount,
                       CurrentQuantity,
                       CurrentMrr
                FROM Asset
                WHERE Product2Id IN :productIds
                AND AccountId = :accountId
            ];
        } else {
            // If AccountId is null, find Assets by Product2Id only
            // Group by AccountId to find the most common Account
            assets = [
                SELECT Id,
                       Name,
                       Product2Id,
                       AccountId,
                       CurrentAmount,
                       CurrentQuantity,
                       CurrentMrr
                FROM Asset
                WHERE Product2Id IN :productIds
                ORDER BY AccountId, Product2Id
            ];
        }
        
        Map<Id, List<Asset>> assetsByProduct = new Map<Id, List<Asset>>();
        for (Asset a : assets) {
            if (!assetsByProduct.containsKey(a.Product2Id)) {
                assetsByProduct.put(a.Product2Id, new List<Asset>());
            }
            assetsByProduct.get(a.Product2Id).add(a);
        }
        
        return assetsByProduct;
    }
    
    // ------------------------------------------------------------
    // Get AccountId from Assets by Product2Id (used when Quote AccountId is null)
    // ------------------------------------------------------------
    public static Id getAccountIdFromAssets(Set<Id> productIds) {
        if (productIds == null || productIds.isEmpty()) {
            return null;
        }
        
        // Find Assets for these products and get the most common AccountId
        List<Asset> assets = [
            SELECT AccountId
            FROM Asset
            WHERE Product2Id IN :productIds
            AND AccountId != null
            ORDER BY AccountId
            LIMIT 100
        ];
        
        if (assets.isEmpty()) {
            return null;
        }
        
        // Count occurrences of each AccountId
        Map<Id, Integer> accountCounts = new Map<Id, Integer>();
        for (Asset a : assets) {
            if (a.AccountId != null) {
                accountCounts.put(a.AccountId, accountCounts.containsKey(a.AccountId) 
                    ? accountCounts.get(a.AccountId) + 1 
                    : 1);
            }
        }
        
        // Return the AccountId with the most occurrences
        Id mostCommonAccountId = null;
        Integer maxCount = 0;
        for (Id accId : accountCounts.keySet()) {
            if (accountCounts.get(accId) > maxCount) {
                maxCount = accountCounts.get(accId);
                mostCommonAccountId = accId;
            }
        }
        
        return mostCommonAccountId;
    }

    // ------------------------------------------------------------
    // Asset State Periods for comparison
    // ------------------------------------------------------------
    public static List<AssetStatePeriod> getAssetStatePeriods(Set<Id> assetIds) {
        if (assetIds == null || assetIds.isEmpty()) {
            return new List<AssetStatePeriod>();
        }

        return [
            SELECT Id,
                   AssetId,
                   Asset.Name,
                   Amount,
                   Quantity,
                   StartDate,
                   EndDate
            FROM AssetStatePeriod
            WHERE AssetId IN :assetIds
            ORDER BY AssetId, EndDate DESC NULLS FIRST
        ];
    }

    // ------------------------------------------------------------
    // Asset Actions related to Quote
    // ------------------------------------------------------------
    public static List<AssetAction> getAssetActions(Set<Id> assetIds, Id quoteId) {
        if (assetIds == null || assetIds.isEmpty()) {
            return new List<AssetAction>();
        }

        // Query AssetActions for the assets
        // Note: AssetAction may have a relationship to Order/Quote through AssetActionSource
        return [
            SELECT Id,
                   AssetId,
                   Asset.Name,
                   Type,
                   CreatedDate,
                   Amount
            FROM AssetAction
            WHERE AssetId IN :assetIds
            ORDER BY AssetId, CreatedDate DESC
        ];
    }

}