public with sharing class DynamicAddressRowDefinition {
    @AuraEnabled
    public List<DynamicAddressRowField> rowFields { get; set; }

    public DynamicAddressRowDefinition() {
        this.rowFields = new List<DynamicAddressRowField>();
    }
}
