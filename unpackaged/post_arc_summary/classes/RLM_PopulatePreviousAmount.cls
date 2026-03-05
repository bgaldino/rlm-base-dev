/**
 * Invocable Apex class to populate RLM_PreviousAmount__c on QuoteLineItems
 * This captures the previous amount from AssetStatePeriod before the quote is saved
 */
public with sharing class RLM_PopulatePreviousAmount {
    
    @InvocableMethod(label='Populate Previous Amount on Quote Line Items' 
                     description='Captures previous amount from AssetStatePeriod and stores it on QuoteLineItem.RLM_PreviousAmount__c')
    public static List<Response> populatePreviousAmount(List<Request> requests) {
        List<Response> responses = new List<Response>();
        
        for (Request req : requests) {
            Response res = new Response();
            try {
                populatePreviousAmountForQuote(req.quoteId);
                res.success = true;
                res.message = 'Previous amounts populated successfully';
            } catch (Exception e) {
                res.success = false;
                res.message = 'Error: ' + e.getMessage();
            }
            responses.add(res);
        }
        
        return responses;
    }
    
    private static void populatePreviousAmountForQuote(Id quoteId) {
        // Get the quote to check if it's an amendment or renewal
        Quote q = [
            SELECT Id, AccountId, RLM_OriginalActionType__c
            FROM Quote
            WHERE Id = :quoteId
            LIMIT 1
        ];
        
        // Only process amendment/renewal quotes
        if (!isAmendmentOrRenewal(q.RLM_OriginalActionType__c)) {
            return;
        }
        
        // Get QuoteLineItems (single query — includes subscription term fields)
        List<QuoteLineItem> qlis = [
            SELECT Id, Product2Id, RLM_PreviousAmount__c,
                   SubscriptionTerm, SubscriptionTermUnit
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId
            AND Product2Id != null
        ];
        
        if (qlis.isEmpty()) {
            return;
        }
        
        // Get Product IDs
        Set<Id> productIds = new Set<Id>();
        for (QuoteLineItem qli : qlis) {
            productIds.add(qli.Product2Id);
        }
        
        // Get AccountId (may be null)
        Id accountId = q.AccountId;
        if (accountId == null) {
            accountId = RLM_AmendmentRenewalRepository.getAccountIdFromAssets(productIds);
        }
        
        // Get Assets by Product
        Map<Id, List<Asset>> assetsByProduct = RLM_AmendmentRenewalRepository.getAssetsByProduct(productIds, accountId);
        
        // Get Asset IDs
        Set<Id> assetIds = new Set<Id>();
        Map<Id, Id> assetToProductMap = new Map<Id, Id>();
        for (Id productId : productIds) {
            if (assetsByProduct.containsKey(productId)) {
                for (Asset a : assetsByProduct.get(productId)) {
                    assetIds.add(a.Id);
                    assetToProductMap.put(a.Id, productId);
                }
            }
        }
        
        if (assetIds.isEmpty()) {
            return;
        }
        
        // Get Assets with their amounts for fallback
        Map<Id, Asset> assetsMap = new Map<Id, Asset>();
        for (Id productId : productIds) {
            if (assetsByProduct.containsKey(productId)) {
                for (Asset a : assetsByProduct.get(productId)) {
                    assetsMap.put(a.Id, a);
                }
            }
        }
        
        // Get AssetStatePeriods
        List<AssetStatePeriod> statePeriods = RLM_AmendmentRenewalRepository.getAssetStatePeriods(assetIds);
        
        // Map latest period by Asset
        Map<Id, AssetStatePeriod> latestPeriodsByAsset = new Map<Id, AssetStatePeriod>();
        for (AssetStatePeriod asp : statePeriods) {
            if (!latestPeriodsByAsset.containsKey(asp.AssetId)) {
                latestPeriodsByAsset.put(asp.AssetId, asp);
            } else {
                AssetStatePeriod existing = latestPeriodsByAsset.get(asp.AssetId);
                // Prioritize active periods (EndDate = null)
                if (asp.EndDate == null && existing.EndDate != null) {
                    latestPeriodsByAsset.put(asp.AssetId, asp);
                } else if (asp.EndDate != null && existing.EndDate != null && 
                          asp.EndDate > existing.EndDate) {
                    latestPeriodsByAsset.put(asp.AssetId, asp);
                }
            }
        }
        
        // Build subscription term map per product for CurrentMrr conversion
        Map<Id, Integer> productSubscriptionTermMonths = new Map<Id, Integer>();
        for (QuoteLineItem qli : qlis) {
            if (!productSubscriptionTermMonths.containsKey(qli.Product2Id) && 
                qli.SubscriptionTerm != null && qli.SubscriptionTermUnit != null) {
                Integer term = Integer.valueOf(qli.SubscriptionTerm);
                String termUnit = qli.SubscriptionTermUnit;
                Integer termMonths = 12; // Default
                if (termUnit == 'Month' || termUnit == 'Months') {
                    termMonths = term;
                } else if (termUnit == 'Year' || termUnit == 'Years') {
                    termMonths = term * 12;
                } else if (termUnit == 'Day' || termUnit == 'Days') {
                    termMonths = Integer.valueOf(Math.ceil(term / 30.0));
                }
                productSubscriptionTermMonths.put(qli.Product2Id, termMonths);
            }
        }
        
        // Calculate previous amounts per product
        Map<Id, Decimal> productPreviousAmounts = new Map<Id, Decimal>();
        Map<Id, Integer> productAssetCounts = new Map<Id, Integer>();
        
        for (Id assetId : assetIds) {
            Id productId = assetToProductMap.get(assetId);
            if (productId == null) continue;
            
            Decimal previousAmount = 0;
            Boolean hasAmount = false;
            
            // Priority 1: Use AssetStatePeriod.Amount if available
            if (latestPeriodsByAsset.containsKey(assetId)) {
                AssetStatePeriod asp = latestPeriodsByAsset.get(assetId);
                if (asp.Amount != null && asp.Amount != 0) {
                    previousAmount = asp.Amount;
                    hasAmount = true;
                }
            }
            
            // Priority 2: Fallback to Asset.CurrentAmount or CurrentMrr
            if (!hasAmount && assetsMap.containsKey(assetId)) {
                Asset a = assetsMap.get(assetId);
                if (a.CurrentAmount != null && a.CurrentAmount != 0) {
                    previousAmount = a.CurrentAmount;
                    hasAmount = true;
                } else if (a.CurrentMrr != null && a.CurrentMrr != 0) {
                    // Convert CurrentMrr to term amount
                    Integer termMonths = productSubscriptionTermMonths.containsKey(productId) 
                        ? productSubscriptionTermMonths.get(productId) 
                        : 12; // Default to 12 months
                    previousAmount = a.CurrentMrr * termMonths;
                    hasAmount = true;
                }
            }
            
            if (hasAmount && previousAmount > 0) {
                Decimal amount = productPreviousAmounts.containsKey(productId) 
                    ? productPreviousAmounts.get(productId) + previousAmount
                    : previousAmount;
                productPreviousAmounts.put(productId, amount);
                
                Integer count = productAssetCounts.containsKey(productId) 
                    ? productAssetCounts.get(productId) + 1
                    : 1;
                productAssetCounts.put(productId, count);
            }
        }
        
        // Update QuoteLineItems with previous amounts
        // Distribute product previous amount across QuoteLineItems for that product
        Map<Id, List<QuoteLineItem>> qlisByProduct = new Map<Id, List<QuoteLineItem>>();
        for (QuoteLineItem qli : qlis) {
            if (!qlisByProduct.containsKey(qli.Product2Id)) {
                qlisByProduct.put(qli.Product2Id, new List<QuoteLineItem>());
            }
            qlisByProduct.get(qli.Product2Id).add(qli);
        }
        
        List<QuoteLineItem> qlisToUpdate = new List<QuoteLineItem>();
        for (QuoteLineItem qli : qlis) {
            // Only update if RLM_PreviousAmount__c is not already populated
            if (qli.RLM_PreviousAmount__c == null || qli.RLM_PreviousAmount__c == 0) {
                if (productPreviousAmounts.containsKey(qli.Product2Id)) {
                    Decimal productAmount = productPreviousAmounts.get(qli.Product2Id);
                    Integer qliCount = qlisByProduct.get(qli.Product2Id).size();
                    // Distribute equally across QuoteLineItems for the same product
                    qli.RLM_PreviousAmount__c = productAmount / qliCount;
                    qlisToUpdate.add(qli);
                }
            }
        }
        
        if (!qlisToUpdate.isEmpty()) {
            update qlisToUpdate;
        }
    }
    
    private static Boolean isAmendmentOrRenewal(String actionType) {
        if (actionType == null) {
            return false;
        }
        String lowerActionType = actionType.toLowerCase();
        return lowerActionType == 'amendment' || lowerActionType == 'amend' ||
               lowerActionType == 'renewal' || lowerActionType == 'renew';
    }
    
    public class Request {
        @InvocableVariable(label='Quote ID' required=true)
        public Id quoteId;
    }
    
    public class Response {
        @InvocableVariable
        public Boolean success;
        
        @InvocableVariable
        public String message;
    }
}
