/**
 * Invocable service for looking up a QuoteLineItem on a Quote by partial
 * product name. Uses SOQL LIKE so the Flow does not need cross-object field
 * filters (which are unsupported in Flow record lookups).
 */
public with sharing class RLM_AI_QuoteLineItemLookupService {

    public class LookupInput {
        @InvocableVariable(required=true label='Quote Id'
            description='18-character Salesforce Id of the Quote (starts with 0Q0).')
        public String quoteId;

        @InvocableVariable(required=true label='Product Name'
            description='Partial or full product name to search for (LIKE match).')
        public String productName;
    }

    public class LookupOutput {
        @InvocableVariable(label='Quote Line Item Id')
        public String quoteLineItemId;

        @InvocableVariable(label='Product Name Found')
        public String productNameFound;

        @InvocableVariable(label='Is Found')
        public Boolean isFound;

        @InvocableVariable(label='Error Message')
        public String errorMessage;

        public LookupOutput() {
            this.isFound = false;
        }
    }

    @InvocableMethod(
        label='Get QuoteLineItem from Quote'
        description='Looks up a QuoteLineItem on a Quote using a partial product name LIKE match. Returns the QuoteLineItem Id for use in product configuration actions.'
    )
    public static List<LookupOutput> lookup(List<LookupInput> inputs) {
        List<LookupOutput> results = new List<LookupOutput>();
        for (LookupInput input : inputs) {
            results.add(fetchQuoteLineItem(input));
        }
        return results;
    }

    private static LookupOutput fetchQuoteLineItem(LookupInput input) {
        LookupOutput out = new LookupOutput();
        try {
            String likePattern = '%' + input.productName + '%';
            List<QuoteLineItem> qlis = [
                SELECT Id, Product2.Name
                FROM QuoteLineItem
                WHERE QuoteId = :input.quoteId
                  AND Product2.Name LIKE :likePattern
                ORDER BY Product2.Name ASC
                LIMIT 1
            ];
            if (!qlis.isEmpty()) {
                out.quoteLineItemId = qlis[0].Id;
                out.productNameFound = qlis[0].Product2.Name;
                out.isFound = true;
            } else {
                out.errorMessage = 'No QuoteLineItem found on this quote matching product name "' + input.productName + '". Verify the quote ID and product name and try again.';
            }
        } catch (Exception e) {
            out.errorMessage = e.getMessage();
        }
        return out;
    }
}
