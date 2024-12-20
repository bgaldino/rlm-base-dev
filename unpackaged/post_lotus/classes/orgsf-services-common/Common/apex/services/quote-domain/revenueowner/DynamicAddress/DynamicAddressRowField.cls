public with sharing class DynamicAddressRowField {
    @AuraEnabled
    public String fieldLabel { get; set; }
    @AuraEnabled
    public String fieldId { get; set; }
    @AuraEnabled
    public String type {
        get;
        set {
            type = value;
            if (value == 'text') {
                this.renderTextBox = true;
            } else if (value == 'combobox') {
                this.renderComboBox = true;
            }
        }
    }
    @AuraEnabled
    public Boolean renderTextBox { get; set; }
    @AuraEnabled
    public Boolean renderComboBox { get; set; }
    @AuraEnabled
    public Integer width { get; set; }
    @AuraEnabled
    public Boolean isRequired { get; set; }
    @AuraEnabled
    public Boolean isOptional { get; set; }
    @AuraEnabled
    public String mapToField { get; set; }
    @AuraEnabled
    public String mapToProperty { get; set; }
    @AuraEnabled
    public String validationRegex { get; set; }
    @AuraEnabled
    public String helpText { get; set; }
    @AuraEnabled
    public String validationErrorText { get; set; }
    @AuraEnabled
    public String placeholderText { get; set; }
}
