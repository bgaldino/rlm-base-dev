/**
 * Invocable service backing Get_Quote_Line_Attributes: reports the attributes
 * on a quote line with each one's CURRENT value (and, for picklists, the valid
 * options), so the agent can ground "Type is currently Flex; valid values are
 * Flex/Gov/Pre-Prod/Prod" before changing it.
 *
 * Resolution is delegated to RLM_AI_AttributeResolver — the SAME single path
 * that backs Get_Product_Attribute_Options — so the two actions can never
 * disagree about which attributes a line has. The only difference is framing:
 * this action's hasAttributes reports whether any attribute value is actually
 * SET on the line (current state), while Get_Product_Attribute_Options reports
 * whether any attribute is configurable (definable OR set). Both read the merged
 * resolver, so neither can return an attribute the other has never heard of.
 *
 * Read-only. Demo code: system mode (no WITH USER_MODE) — see
 * RLM_AI_AttributeResolver for why.
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
            description='JSON array of the attributes on the line. Each has: name, developerName, dataType, currentValue, isPriceImpacting, picklistValues (array, Picklist only). Used internally by the planner.')
        public String attributesJson;

        @InvocableVariable(label='Attribute Summary'
            description='Pre-formatted human-readable summary of the attributes on the line, each with its current value and (for picklists) the valid options. Display this directly to the user.')
        public String attributeSummary;

        @InvocableVariable(label='Has Attributes'
            description='True when the line has at least one attribute with a value set.')
        public Boolean hasAttributes;

        @InvocableVariable(label='Is Success'
            description='True if the action ran without a system-level error. False if an exception prevented it from completing. Distinct from hasAttributes, which is a domain result.')
        public Boolean isSuccess;

        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Get Quote Line Attributes'
        description='Reads the attributes on a quote line with each current value and valid picklist options. Use before changing an existing attribute. Read-only.'
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

            RLM_AI_AttributeResolver.Resolution res = RLM_AI_AttributeResolver.resolve(qliId);
            if (!res.lineFound) {
                out.errorMessage = 'QuoteLineItem not found: ' + qliId;
                out.hasAttributes = false;
                out.attributesJson = '[]';
                return out;
            }
            out.productName = res.productName;
            summarize(out, res.attributes);

        } catch (Exception e) {
            out.errorMessage = e.getMessage();
            out.hasAttributes = false;
            out.isSuccess = false;
        }
        return out;
    }

    /**
     * Builds the output from resolved attributes. hasAttributes is true when at
     * least one attribute carries a value set on the line (current state); the
     * summary lists every known attribute with its current value so the agent
     * can validate a requested change against the valid options.
     *
     * @TestVisible so the populated branch can be unit-tested with in-memory
     * resolved rows — QuoteLineItemAttribute is async-creatable and cannot be
     * inserted-and-queried-back in one test transaction.
     */
    @TestVisible
    private static void summarize(
        GetLineAttributesOutput out,
        List<RLM_AI_AttributeResolver.ResolvedAttribute> attrs
    ) {
        out.attributesJson = RLM_AI_AttributeResolver.toJson(attrs);

        Boolean anyValueSet = false;
        if (attrs != null) {
            for (RLM_AI_AttributeResolver.ResolvedAttribute a : attrs) {
                if (String.isNotBlank(a.currentValue)) {
                    anyValueSet = true;
                    break;
                }
            }
        }
        out.hasAttributes = anyValueSet;
        out.attributeSummary = buildSummary(out.productName, attrs, anyValueSet);
    }

    private static GetLineAttributesOutput fail(GetLineAttributesOutput out, String message) {
        out.errorMessage = message;
        out.hasAttributes = false;
        out.attributesJson = '[]';
        out.isSuccess = false;
        return out;
    }

    private static String buildSummary(
        String productName,
        List<RLM_AI_AttributeResolver.ResolvedAttribute> attrs,
        Boolean anyValueSet
    ) {
        String header = String.isNotBlank(productName) ? productName : 'This line';
        if (attrs == null || attrs.isEmpty()) {
            return header + ' has no attributes set.';
        }
        if (!anyValueSet) {
            // Attributes are configurable but none are set yet — say so plainly
            // instead of the misleading "no attributes".
            List<String> names = new List<String>();
            for (RLM_AI_AttributeResolver.ResolvedAttribute a : attrs) {
                names.add(a.name);
            }
            return header + ' has no attribute values set yet. Configurable attributes: '
                + String.join(names, ', ') + '.';
        }
        List<String> lines = new List<String>();
        lines.add('Attributes on ' + header + ':');
        lines.add('');
        Integer i = 1;
        for (RLM_AI_AttributeResolver.ResolvedAttribute a : attrs) {
            String current = String.isNotBlank(a.currentValue) ? a.currentValue : '(not set)';
            // Bold the currently-selected value so it stands out from the options.
            String row = i + '. ' + a.name + ' — currently **' + current + '**';
            if (a.dataType == 'Picklist') {
                List<String> valStrs = a.picklistValues != null
                    ? a.picklistValues : new List<String>();
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
