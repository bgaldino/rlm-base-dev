public with sharing class DynamicAddressSchema {
    @AuraEnabled
    public List<DynamicAddressRowDefinition> rowDefinitions { get; set; }

    public DynamicAddressSchema() {
        this.rowDefinitions = new List<DynamicAddressRowDefinition>();
    }
}
