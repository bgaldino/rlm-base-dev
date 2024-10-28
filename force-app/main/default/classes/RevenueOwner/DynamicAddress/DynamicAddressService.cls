public with sharing class DynamicAddressService extends AbstractDynamicAddressService {
    IRevenueOwnerMdtSelector revenueOwnerMdtSelector;
    public DynamicAddressService() {
        this((IRevenueOwnerMdtSelector) ServiceRegistry.getInstance('IRevenueOwnerMdtSelector'));
    }

    public DynamicAddressService(IRevenueOwnerMdtSelector revenueOwnerMdtSelector) {
        this.revenueOwnerMdtSelector = revenueOwnerMdtSelector;
    }

    public override DynamicAddressSchema getAddressSchemaForCountry(String isoCode) {
        ROCountryAugmentation__mdt augmentationData = revenueOwnerMdtSelector.getSupplementalData(isoCode);

        DynamicAddressSchema dynamicAddressSchema = (DynamicAddressSchema) JSON.deserialize(augmentationData.AddressRenderTemplate__c, DynamicAddressSchema.class);
        addFieldData(isoCode, dynamicAddressSchema);        

        return dynamicAddressSchema;
    }

    private void addFieldData(String isoCode, DynamicAddressSchema dynamicAddressSchema) {
        Map<String, ROCountryAddressField__mdt> addressFieldDataMap = new Map<String, ROCountryAddressField__mdt>();

        //Add the Defaults
        List<ROCountryAddressField__mdt> defaultAddressFieldDataList = revenueOwnerMdtSelector.getDefaultAddressFieldData();
        mapAddressFieldData(addressFieldDataMap, defaultAddressFieldDataList);

        //Override with Country Specific
        List<ROCountryAddressField__mdt> countryAddressFieldDataList = revenueOwnerMdtSelector.getAddressFieldDataForCountry(isoCode);
        mapAddressFieldData(addressFieldDataMap, countryAddressFieldDataList);

        mapFieldDataToAddressSchema(addressFieldDataMap, dynamicAddressSchema);
    }

    public static void mapAddressFieldData(Map<String, ROCountryAddressField__mdt> addressFieldDataMap, List<ROCountryAddressField__mdt> addressFieldDataList) {
        for (ROCountryAddressField__mdt addressFieldData : addressFieldDataList) {
            addressFieldDataMap.put(addressFieldData.FieldId__c, addressFieldData);
        }
    }

    public static void mapFieldDataToAddressSchema(Map<String, ROCountryAddressField__mdt> addressFieldDataMap, DynamicAddressSchema dynamicAddressSchema) {
        for (DynamicAddressRowDefinition rowDefinition : dynamicAddressSchema.rowDefinitions) {
            for (DynamicAddressRowField rowField : rowDefinition.rowFields) {
                ROCountryAddressField__mdt fieldMetadata = addressFieldDataMap.get(rowField.fieldId);
                if(fieldMetadata == null) {
                    continue;
                }
                rowField.fieldLabel = fieldMetadata.FieldLabel__c;
                rowField.isRequired = fieldMetadata.IsRequired__c;
                rowField.isOptional = fieldMetadata.IsOptional__c;
                rowField.mapToField = fieldMetadata.MapToField__c;
                rowField.mapToProperty = fieldMetadata.MapToProperty__c;
                rowField.validationRegex = fieldMetadata.ValidationRegex__c;
                rowField.helpText = fieldMetadata.HelpText__c;
                rowField.validationErrorText = fieldMetadata.ValidationErrorText__c;
                rowfield.placeholderText = fieldMetadata.PlaceholderText__c;
            }
        }
    }
}