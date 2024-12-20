public with sharing class CreditScoreServiceRequestItem extends BaseRequestItem {
    
    public String countryCode { get; set; }
    public String currencyCode { get; set; }
    public String creditScoreId { get; set; }
    public Id userId { get; set; }
    public Id accountId { get; set; }
        
}