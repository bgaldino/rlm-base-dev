public with sharing class QuotePricingChartController {
    
    @AuraEnabled(cacheable=true)
    public static List<QuoteLineItemStats> getQuoteLineItemStats(Id accountId) {
        
        // 1) Run the SOQL query exactly as you specified
        List<AggregateResult> aggResults = [
            SELECT 
                Product2Id, 
                StartDate, 
                SUM(Quantity) totalQuantity, 
                AVG(UnitPrice) averageUnitPrice, 
                SUM(TotalLineAmount) totalLineAmount
            FROM QuoteLineItem
            WHERE Quote.AccountId = :accountId
            GROUP BY Product2Id, StartDate
            ORDER BY Product2Id, StartDate
        ];
        
        // 2) Transform each AggregateResult row into a custom wrapper
        List<QuoteLineItemStats> results = new List<QuoteLineItemStats>();
        
        for (AggregateResult ar : aggResults) {
            QuoteLineItemStats row = new QuoteLineItemStats();
            row.productId = (Id) ar.get('Product2Id');
            row.startDate = (Date) ar.get('StartDate');
            row.totalQuantity = (Decimal) ar.get('totalQuantity');
            row.averageUnitPrice = (Decimal) ar.get('averageUnitPrice');
            row.totalLineAmount = (Decimal) ar.get('totalLineAmount');
            
            results.add(row);
        }
        
        return results;
    }
    
    // 3) Wrapper class
    public class QuoteLineItemStats {
        @AuraEnabled public Id productId;
        @AuraEnabled public Date startDate;
        @AuraEnabled public Decimal totalQuantity;
        @AuraEnabled public Decimal averageUnitPrice;
        @AuraEnabled public Decimal totalLineAmount;
    }
}