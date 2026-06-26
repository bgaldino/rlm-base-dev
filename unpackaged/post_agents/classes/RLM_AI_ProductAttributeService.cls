/**
 * Invocable service for retrieving product attribute definitions via SOQL.
 * Uses ProductClassificationAttr → ProductClassification (Product2.BasedOnId)
 * to resolve attributes without a PCM REST API callout, which avoids the
 * UserInfo.getSessionId() null-session issue in Agentforce execution contexts.
 *
 * Product-agnostic: all attribute structure is resolved dynamically at runtime.
 * Each method is in its own class due to the one-@InvocableMethod-per-class rule.
 */
public with sharing class RLM_AI_ProductAttributeService {

    public class GetAttributeOptionsInput {
        @InvocableVariable(required=true label='Quote Line Item Id'
            description='18-character Salesforce Id of the QuoteLineItem record. The service resolves the Product2Id from this record.')
        public String quoteLineItemId;
    }

    public class GetAttributeOptionsOutput {
        @InvocableVariable(label='Product Name')
        public String productName;

        @InvocableVariable(label='Attributes JSON'
            description='JSON array of attribute objects. Each has: name, developerName, dataType, isRequired, isPriceImpacting, picklistValues (array, Picklist only). Used internally by the planner when calling Configure_Product_Attributes.')
        public String attributesJson;

        @InvocableVariable(label='Attribute Summary'
            description='Pre-formatted human-readable summary of all configurable attributes and their valid values. Display this directly to the user.')
        public String attributeSummary;

        @InvocableVariable(label='Has Configurable Attributes')
        public Boolean hasConfigurableAttributes;

        @InvocableVariable(label='Is Success'
            description='True if the action ran without a system-level error. False if an exception prevented it from completing. Distinct from hasConfigurableAttributes, which is a domain result.')
        public Boolean isSuccess;

        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Get Product Attribute Options'
        description='Retrieves configurable attribute definitions for any product via SOQL (ProductClassificationAttr). Product-agnostic: attribute structure resolved at runtime.'
        category='Product Configuration'
    )
    public static List<GetAttributeOptionsOutput> getProductAttributeOptions(
        List<GetAttributeOptionsInput> inputs
    ) {
        List<GetAttributeOptionsOutput> results = new List<GetAttributeOptionsOutput>();
        for (GetAttributeOptionsInput input : inputs) {
            results.add(fetchAttributeOptions(input.quoteLineItemId));
        }
        return results;
    }

    private static GetAttributeOptionsOutput fetchAttributeOptions(String qliId) {
        GetAttributeOptionsOutput out = new GetAttributeOptionsOutput();
        out.isSuccess = true;
        try {
            // Step 1: Resolve Product2Id and ProductClassificationId (BasedOnId)
            List<QuoteLineItem> qlis = [
                SELECT Product2Id, Product2.Name, Product2.BasedOnId
                FROM QuoteLineItem
                WHERE Id = :qliId
                LIMIT 1
            ];
            if (qlis.isEmpty()) {
                out.errorMessage = 'QuoteLineItem not found: ' + qliId;
                out.hasConfigurableAttributes = false;
                return out;
            }

            out.productName = qlis[0].Product2.Name;
            Id classificationId = qlis[0].Product2.BasedOnId;

            if (classificationId == null) {
                out.hasConfigurableAttributes = false;
                out.attributesJson = '[]';
                return out;
            }

            // Step 2: Get attribute associations from ProductClassificationAttr
            List<ProductClassificationAttr> pcAttrs = [
                SELECT AttributeDefinitionId, IsRequired, IsPriceImpacting
                FROM ProductClassificationAttr
                WHERE ProductClassificationId = :classificationId
                  AND Status = 'Active'
                  AND IsReadOnly = false
                  AND IsHidden = false
            ];

            if (pcAttrs.isEmpty()) {
                out.hasConfigurableAttributes = false;
                out.attributesJson = '[]';
                return out;
            }

            // Step 3: Fetch AttributeDefinition records
            Set<Id> attrDefIds = new Set<Id>();
            Map<Id, ProductClassificationAttr> pcaByAttrDefId = new Map<Id, ProductClassificationAttr>();
            for (ProductClassificationAttr pca : pcAttrs) {
                attrDefIds.add(pca.AttributeDefinitionId);
                pcaByAttrDefId.put(pca.AttributeDefinitionId, pca);
            }

            Map<Id, AttributeDefinition> attrDefs = new Map<Id, AttributeDefinition>([
                SELECT Id, Name, DeveloperName, DataType, PicklistId
                FROM AttributeDefinition
                WHERE Id IN :attrDefIds
            ]);

            // Step 4: Fetch picklist values for all Picklist-type attributes
            Set<Id> picklistIds = new Set<Id>();
            for (AttributeDefinition ad : attrDefs.values()) {
                if (ad.DataType == 'Picklist' && ad.PicklistId != null) {
                    picklistIds.add(ad.PicklistId);
                }
            }

            Map<Id, List<String>> picklistValuesMap = new Map<Id, List<String>>();
            if (!picklistIds.isEmpty()) {
                for (AttributePicklistValue pv : [
                    SELECT Id, Name, Code, PicklistId
                    FROM AttributePicklistValue
                    WHERE PicklistId IN :picklistIds
                    ORDER BY Name ASC
                ]) {
                    if (!picklistValuesMap.containsKey(pv.PicklistId)) {
                        picklistValuesMap.put(pv.PicklistId, new List<String>());
                    }
                    picklistValuesMap.get(pv.PicklistId).add(
                        String.isNotBlank(pv.Name) ? pv.Name : pv.Code
                    );
                }
            }

            // Step 5: Build attribute list JSON
            List<Map<String, Object>> attrList = new List<Map<String, Object>>();
            for (Id attrDefId : attrDefIds) {
                AttributeDefinition ad = attrDefs.get(attrDefId);
                if (ad == null) continue;

                ProductClassificationAttr pca = pcaByAttrDefId.get(attrDefId);

                Map<String, Object> entry = new Map<String, Object>{
                    'name'             => ad.Name,
                    'developerName'    => ad.DeveloperName,
                    'dataType'         => ad.DataType,
                    'isRequired'       => pca.IsRequired,
                    'isPriceImpacting' => pca.IsPriceImpacting,
                    'attributeId'      => ad.Id
                };

                if (ad.DataType == 'Picklist' && ad.PicklistId != null) {
                    List<String> vals = picklistValuesMap.get(ad.PicklistId);
                    entry.put('picklistValues', vals != null ? vals : new List<String>());
                }

                attrList.add(entry);
            }

            out.attributesJson = RLM_AI_ConfigServiceUtils.safeSerialize(attrList);
            out.hasConfigurableAttributes = !attrList.isEmpty();
            out.attributeSummary = buildSummary(out.productName, attrList);

        } catch (Exception e) {
            out.errorMessage = e.getMessage();
            out.hasConfigurableAttributes = false;
            out.isSuccess = false;
        }
        return out;
    }

    private static String buildSummary(String productName, List<Map<String, Object>> attrList) {
        if (attrList.isEmpty()) return productName + ' has no configurable attributes.';
        List<String> lines = new List<String>();
        lines.add('Here are the configurable attributes for ' + productName + ':');
        lines.add('');
        Integer i = 1;
        for (Map<String, Object> attr : attrList) {
            String label = (String) attr.get('name');
            String dataType = (String) attr.get('dataType');
            Boolean required = attr.get('isRequired') == true;
            String req = required ? ' (required)' : '';
            if (dataType == 'Picklist') {
                List<Object> vals = (List<Object>) attr.get('picklistValues');
                List<String> valStrs = new List<String>();
                if (vals != null) { for (Object v : vals) valStrs.add((String) v); }
                lines.add(i + '. ' + label + req);
                lines.add('   Options: ' + String.join(valStrs, ', '));
            } else if (dataType == 'Number') {
                lines.add(i + '. ' + label + req + ' — enter a number');
            } else if (dataType == 'Checkbox') {
                lines.add(i + '. ' + label + req + ' — yes or no');
            } else {
                lines.add(i + '. ' + label + req + ' — enter a value');
            }
            i++;
        }
        lines.add('');
        lines.add('Please provide a value for each attribute you want to configure.');
        return String.join(lines, '\n');
    }
}
