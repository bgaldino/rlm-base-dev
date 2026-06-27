/**
 * Invocable service that reads the attributes ALREADY materialized on a quote
 * line (QuoteLineItemAttribute), for the Quinn quoting assistant's
 * Get_Quote_Line_Attributes action.
 *
 * This is the ground-truth source for ALTERING an existing attribute on a line:
 * it returns each QuoteLineItemAttribute's current value plus, for picklist
 * attributes, the valid values from the AttributeDefinition's picklist — so the
 * agent can ground "Type is currently Prod; valid values are Flex/Gov/Pre-Prod/
 * Prod" instead of re-deriving configurability from the product classification.
 *
 * Complements RLM_AI_ProductAttributeService (which lists what COULD be
 * configured from ProductClassificationAttr); this lists what IS set on the line.
 *
 * Read-only. `with sharing`; null-safe Id handling via RLM_AI_ConfigServiceUtils.
 */
public with sharing class RLM_AI_QuoteLineAttributeService {

    public class GetLineAttributesInput {
        @InvocableVariable(required=true label='Quote Line Item Id'
            description='18-character Salesforce Id of the QuoteLineItem (starts with 0QL) whose existing attributes to read.')
        public String quoteLineItemId;
    }

    public class GetLineAttributesOutput {
        @InvocableVariable(label='Product Name')
        public String productName;

        @InvocableVariable(label='Attributes JSON'
            description='JSON array of the attributes set on the line. Each has: name, developerName, dataType, currentValue, isPriceImpacting, picklistValues (array, Picklist only). Used internally by the planner.')
        public String attributesJson;

        @InvocableVariable(label='Attribute Summary'
            description='Pre-formatted human-readable summary of the attributes set on the line, each with its current value and (for picklists) the valid options. Display this directly to the user.')
        public String attributeSummary;

        @InvocableVariable(label='Has Attributes'
            description='True when the line has at least one materialized QuoteLineItemAttribute.')
        public Boolean hasAttributes;

        @InvocableVariable(label='Is Success'
            description='True if the action ran without a system-level error. False if an exception prevented it from completing. Distinct from hasAttributes, which is a domain result.')
        public Boolean isSuccess;

        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Get Quote Line Attributes'
        description='Reads the attributes already set on a quote line (QuoteLineItemAttribute), with each current value and valid picklist options. Use before changing an existing attribute. Read-only.'
        category='Product Configuration'
    )
    public static List<GetLineAttributesOutput> getQuoteLineAttributes(
        List<GetLineAttributesInput> inputs
    ) {
        List<GetLineAttributesOutput> results = new List<GetLineAttributesOutput>();
        if (inputs == null || inputs.isEmpty()) {
            return results;
        }
        for (GetLineAttributesInput input : inputs) {
            results.add(fetchLineAttributes(input));
        }
        return results;
    }

    private static GetLineAttributesOutput fetchLineAttributes(GetLineAttributesInput input) {
        GetLineAttributesOutput out = new GetLineAttributesOutput();
        out.isSuccess = true;
        try {
            if (input == null) {
                return fail(out, 'Select a quote line item before reading its attributes.');
            }
            Id qliId = RLM_AI_ConfigServiceUtils.toIdOrNull(input.quoteLineItemId);
            if (qliId == null
                || !String.valueOf(qliId).startsWith(RLM_AI_ConfigServiceUtils.QUOTE_LINE_ITEM_PREFIX)) {
                return fail(out, 'Select a valid quote line item before reading its attributes.');
            }

            // Resolve the product name for a friendly summary (best-effort).
            List<QuoteLineItem> qlis = [
                SELECT Product2.Name
                FROM QuoteLineItem
                WHERE Id = :qliId
                WITH USER_MODE
                LIMIT 1
            ];
            if (qlis.isEmpty()) {
                out.errorMessage = 'QuoteLineItem not found: ' + qliId;
                out.hasAttributes = false;
                out.attributesJson = '[]';
                return out;
            }
            out.productName = qlis[0].Product2 != null ? qlis[0].Product2.Name : null;

            // Read the attributes materialized on this line.
            List<QuoteLineItemAttribute> lineAttrs = [
                SELECT AttributeName, AttributeValue, IsPriceImpacting,
                       AttributeDefinitionId,
                       AttributeDefinition.Name, AttributeDefinition.DeveloperName,
                       AttributeDefinition.DataType, AttributeDefinition.PicklistId
                FROM QuoteLineItemAttribute
                WHERE QuoteLineItemId = :qliId
                WITH USER_MODE
                ORDER BY AttributeName ASC
            ];

            summarizeAttributes(out, lineAttrs);

        } catch (Exception e) {
            out.errorMessage = e.getMessage();
            out.hasAttributes = false;
            out.isSuccess = false;
        }
        return out;
    }

    /**
     * Transforms the raw QuoteLineItemAttribute rows into the output's
     * hasAttributes / attributesJson / attributeSummary fields, enriching
     * picklist-typed attributes with their valid values.
     *
     * Split out from the query so it can be unit-tested with in-memory rows:
     * QuoteLineItemAttribute is an async-creatable entity that cannot be
     * created (insertImmediate) and queried back within the same test
     * transaction, so the "found" branch is otherwise uncoverable.
     */
    @TestVisible
    private static void summarizeAttributes(
        GetLineAttributesOutput out,
        List<QuoteLineItemAttribute> lineAttrs
    ) {
        if (lineAttrs == null || lineAttrs.isEmpty()) {
            out.hasAttributes = false;
            out.attributesJson = '[]';
            out.attributeSummary = (out.productName != null ? out.productName : 'This line')
                + ' has no attributes set.';
            return;
        }

        // Gather picklist values for any picklist-typed attributes.
        Set<Id> picklistIds = new Set<Id>();
        for (QuoteLineItemAttribute a : lineAttrs) {
            AttributeDefinition ad = a.AttributeDefinition;
            if (ad != null && ad.DataType == 'Picklist' && ad.PicklistId != null) {
                picklistIds.add(ad.PicklistId);
            }
        }
        Map<Id, List<String>> picklistValuesMap = new Map<Id, List<String>>();
        if (!picklistIds.isEmpty()) {
            for (AttributePicklistValue pv : [
                SELECT Name, Code, PicklistId
                FROM AttributePicklistValue
                WHERE PicklistId IN :picklistIds
                WITH USER_MODE
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

        // Build the attribute list.
        List<Map<String, Object>> attrList = new List<Map<String, Object>>();
        for (QuoteLineItemAttribute a : lineAttrs) {
            AttributeDefinition ad = a.AttributeDefinition;
            String dataType = ad != null ? ad.DataType : null;
            String name = ad != null && String.isNotBlank(ad.Name)
                ? ad.Name
                : a.AttributeName;

            Map<String, Object> entry = new Map<String, Object>{
                'name'             => name,
                'developerName'    => ad != null ? ad.DeveloperName : null,
                'dataType'         => dataType,
                'currentValue'     => a.AttributeValue,
                'isPriceImpacting' => a.IsPriceImpacting,
                'attributeId'      => a.AttributeDefinitionId
            };
            if (dataType == 'Picklist' && ad != null && ad.PicklistId != null) {
                List<String> vals = picklistValuesMap.get(ad.PicklistId);
                entry.put('picklistValues', vals != null ? vals : new List<String>());
            }
            attrList.add(entry);
        }

        out.attributesJson = RLM_AI_ConfigServiceUtils.safeSerialize(attrList);
        out.hasAttributes = !attrList.isEmpty();
        out.attributeSummary = buildSummary(out.productName, attrList);
    }

    private static GetLineAttributesOutput fail(GetLineAttributesOutput out, String message) {
        out.errorMessage = message;
        out.hasAttributes = false;
        out.attributesJson = '[]';
        out.isSuccess = false;
        return out;
    }

    private static String buildSummary(String productName, List<Map<String, Object>> attrList) {
        String header = (String.isNotBlank(productName) ? productName : 'This line');
        if (attrList.isEmpty()) {
            return header + ' has no attributes set.';
        }
        List<String> lines = new List<String>();
        lines.add('Attributes currently set on ' + header + ':');
        lines.add('');
        Integer i = 1;
        for (Map<String, Object> attr : attrList) {
            String label = (String) attr.get('name');
            String dataType = (String) attr.get('dataType');
            Object curObj = attr.get('currentValue');
            String current = curObj == null ? '(not set)' : String.valueOf(curObj);
            // Bold the currently-selected value so it stands out from the options.
            String row = i + '. ' + label + ' — currently **' + current + '**';
            if (dataType == 'Picklist') {
                List<Object> vals = (List<Object>) attr.get('picklistValues');
                List<String> valStrs = new List<String>();
                if (vals != null) { for (Object v : vals) valStrs.add((String) v); }
                if (!valStrs.isEmpty()) {
                    row += ' (options: ' + String.join(valStrs, ', ') + ')';
                }
            }
            lines.add(row);
            i++;
        }
        return String.join(lines, '\n');
    }
}
