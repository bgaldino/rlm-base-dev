public class ProductRulesResponse {
    @AuraEnabled
    public String status { get; set;}
    @AuraEnabled
    public ProductRuleResult[] results  { get; set;}    
    @AuraEnabled
    public String message  { get; set;}
    
    public Enum Status { SUCCESS,FAILURE }

    public ProductRulesResponse setStatus(Status status) {
        this.status = status.name();
        return this;
    }

    public String getStatus() {
        return status;
    }

    public ProductRulesResponse setResults(ProductRuleResult[] results) {
        this.results = results;
        return this;
    }

    public ProductRuleResult[] getResults(){
        return results;
    }

    public void setMessage(String message){
        this.message = message;
    }

    public String getMessage(){
        return message;
    }


    public class ProductRuleResult {
        @AuraEnabled
        public String message { get; set; }
        @AuraEnabled
        public String messageType { get; set; }
        @AuraEnabled
        public Boolean pending { get; set;}
        @AuraEnabled
        public Id productRuleId { get; set;}
        @AuraEnabled
        public List<Id> triggeringProductIds { get; set;}
        @AuraEnabled
        public List<Id> triggeringLocationIds { get; set;}
        @AuraEnabled
        public List<String> triggeringLocationIdByProdId { get; set; }
        @AuraEnabled
        public String referenceId { get; set; }
        
        public ProductRuleResult() {
            this.triggeringProductIds = new List<Id>();
            this.triggeringLocationIdByProdId = new List<String>();
            this.triggeringLocationIds = new List<Id>();
        }
    }
}