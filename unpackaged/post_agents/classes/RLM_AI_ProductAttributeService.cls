/**
 * Invocable service backing the Get_Product_Attribute_Options action: returns
 * the configurable attributes for the product on a quote line.
 *
 * Resolution is delegated ENTIRELY to RLM_AI_AttributeResolver, the single
 * shared path that merges the definable set (ProductClassificationAttr) with
 * the line's materialized values (QuoteLineItemAttribute). This service is now
 * just the invocable shell + presentation: it no longer carries its own SOQL,
 * so it can never diverge from Get_Quote_Line_Attributes (which reads through
 * the same resolver). hasConfigurableAttributes is true whenever the line has
 * ANY known attribute — definable or already set — which is what fixes the
 * "no configurable attributes" false negative for lines that already carry a
 * persisted attribute.
 *
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
        if (inputs == null || inputs.isEmpty()) {
            return results;
        }
        for (GetAttributeOptionsInput input : inputs) {
            results.add(fetchAttributeOptions(input));
        }
        return results;
    }

    private static GetAttributeOptionsOutput fetchAttributeOptions(GetAttributeOptionsInput input) {
        GetAttributeOptionsOutput out = new GetAttributeOptionsOutput();
        out.isSuccess = true;
        try {
            if (input == null) {
                return fail(out, 'Select a quote line item before looking up configurable attributes.');
            }
            Id qliId = RLM_AI_ConfigServiceUtils.toIdOrNull(input.quoteLineItemId);
            if (qliId == null || !String.valueOf(qliId).startsWith(RLM_AI_ConfigServiceUtils.QUOTE_LINE_ITEM_PREFIX)) {
                return fail(out, 'Select a valid quote line item before looking up configurable attributes.');
            }

            // Single shared resolution: merged definable + materialized set.
            RLM_AI_AttributeResolver.Resolution res = RLM_AI_AttributeResolver.resolve(qliId);
            if (!res.lineFound) {
                out.errorMessage = 'QuoteLineItem not found: ' + qliId;
                out.hasConfigurableAttributes = false;
                out.attributesJson = '[]';
                return out;
            }

            out.productName = res.productName;
            out.attributesJson = RLM_AI_AttributeResolver.toJson(res.attributes);
            out.hasConfigurableAttributes = res.hasAttributes();
            out.attributeSummary = buildSummary(out.productName, res.attributes);

        } catch (Exception e) {
            out.errorMessage = e.getMessage();
            out.hasConfigurableAttributes = false;
            out.isSuccess = false;
        }
        return out;
    }

    private static GetAttributeOptionsOutput fail(GetAttributeOptionsOutput out, String message) {
        out.errorMessage = message;
        out.hasConfigurableAttributes = false;
        out.attributesJson = '[]';
        out.isSuccess = false;
        return out;
    }

    private static String buildSummary(
        String productName, List<RLM_AI_AttributeResolver.ResolvedAttribute> attrList
    ) {
        String header = String.isNotBlank(productName) ? productName : 'This line';
        if (attrList == null || attrList.isEmpty()) {
            return header + ' has no configurable attributes.';
        }
        List<String> lines = new List<String>();
        lines.add('Here are the configurable attributes for ' + header + ':');
        lines.add('');
        Integer i = 1;
        for (RLM_AI_AttributeResolver.ResolvedAttribute attr : attrList) {
            String label = attr.name;
            String req = attr.isRequired == true ? ' (required)' : '';
            // Show the current value when one is set, so discovery and the
            // current-state read present the same fact.
            String cur = String.isNotBlank(attr.currentValue)
                ? ' — currently **' + attr.currentValue + '**'
                : '';
            if (attr.dataType == 'Picklist') {
                List<String> valStrs = attr.picklistValues != null
                    ? attr.picklistValues : new List<String>();
                lines.add(i + '. ' + label + req + cur);
                lines.add('   Options: ' + String.join(valStrs, ', '));
            } else if (attr.dataType == 'Number') {
                lines.add(i + '. ' + label + req + cur + ' — enter a number');
            } else if (attr.dataType == 'Checkbox') {
                lines.add(i + '. ' + label + req + cur + ' — yes or no');
            } else {
                lines.add(i + '. ' + label + req + cur + ' — enter a value');
            }
            i++;
        }
        lines.add('');
        lines.add('Please provide a value for each attribute you want to configure.');
        return String.join(lines, '\n');
    }
}
