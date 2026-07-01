/**
 * Invocable service for reading saved QuoteLineItemAttribute records and
 * producing a human-readable configuration summary.
 */
public with sharing class RLM_AI_ProductAttributeReadService {

    public class ReadInput {
        @InvocableVariable(required=true label='Quote Line Item Id')
        public String quoteLineItemId;
    }

    public class ReadOutput {
        @InvocableVariable(label='Configuration Summary'
            description='Human-readable list of attribute name: value pairs')
        public String configurationSummary;

        @InvocableVariable(label='Saved Attributes JSON')
        public String savedAttributesJson;

        @InvocableVariable(label='Is Success'
            description='True if the read ran without a system-level error. False if an exception prevented it from completing.')
        public Boolean isSuccess;

        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Get Saved Attribute Values'
        description='Reads all QuoteLineItemAttribute records for a QuoteLineItem and returns a summary and JSON map. Product-agnostic.'
        category='Product Configuration'
    )
    public static List<ReadOutput> getSavedAttributeValues(List<ReadInput> inputs) {
        List<ReadOutput> results = new List<ReadOutput>();
        if (inputs == null || inputs.isEmpty()) {
            return results;
        }
        for (ReadInput input : inputs) {
            results.add(read(input));
        }
        return results;
    }

    private static ReadOutput read(ReadInput input) {
        ReadOutput out = new ReadOutput();
        out.isSuccess = true;
        out.savedAttributesJson = '{}';
        out.configurationSummary = '';
        try {
            if (input == null) {
                return fail(out, 'Select a quote line item before reading saved attribute values.');
            }
            Id qliId = RLM_AI_ConfigServiceUtils.toIdOrNull(input.quoteLineItemId);
            if (qliId == null || !String.valueOf(qliId).startsWith(RLM_AI_ConfigServiceUtils.QUOTE_LINE_ITEM_PREFIX)) {
                return fail(out, 'Select a valid quote line item before reading saved attribute values.');
            }

            List<QuoteLineItemAttribute> attrs = [
                SELECT AttributeName, AttributeValue
                FROM QuoteLineItemAttribute
                WHERE QuoteLineItemId = :qliId
                ORDER BY AttributeName
            ];

            Map<String, String> saved = new Map<String, String>();
            List<String> lines = new List<String>();
            for (QuoteLineItemAttribute qa : attrs) {
                saved.put(qa.AttributeName, qa.AttributeValue);
                lines.add(qa.AttributeName + ': ' + qa.AttributeValue);
            }

            out.savedAttributesJson = JSON.serialize(saved);
            out.configurationSummary = String.join(lines, '\n');

        } catch (Exception e) {
            out.errorMessage = e.getMessage();
            out.isSuccess = false;
        }
        return out;
    }

    private static ReadOutput fail(ReadOutput out, String message) {
        out.errorMessage = message;
        out.isSuccess = false;
        return out;
    }
}
