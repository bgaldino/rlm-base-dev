public with sharing class ProductRuleServiceRequest {
    public List<ProductRulesRequestWrapper> buyingProductLines { get; set; }
    public List<ProductRulesRequestWrapper> assetLines { get; set; }
    public Options options { get; set; }
    
    public class Options {
        public String quoteType;
        public String buyingProgram;
        public String transactionObjectId;
        public String transactionObjectType;
        public Boolean byPassRule;
        public Boolean runProductRules;
        public Boolean runEditionExclusivityRules;
        public List<String> incompleteTenantWrappersMap;

        public Options() {
            this.byPassRule = false;
            this.runProductRules = true;
            this.runEditionExclusivityRules = true;
        }
    }

}
