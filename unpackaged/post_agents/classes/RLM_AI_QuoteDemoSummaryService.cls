/**
 * Invocable service that builds a satisfying, names-only recap of a Revenue
 * Cloud quote for the Quinn quoting assistant (Get_Quote_Demo_Summary action).
 *
 * Read-only. Complements the native Quote record card (Get_Quote_Record_Card):
 * the card is the clickable, navigable artifact that owns the quote HEADER and
 * money fields (name, status, Subtotal, Discount, Grand Total) and is shown
 * FIRST; this service returns ONLY the names-only per-LINE list, so the same
 * information is never duplicated in both the card and the text. "Show me the
 * quote" = card (header/totals) + this recap (the lines).
 *
 * `with sharing` entry point; null-safe Id handling via RLM_AI_ConfigServiceUtils.
 */
public with sharing class RLM_AI_QuoteDemoSummaryService {

    public class SummaryInput {
        @InvocableVariable(required=true label='Quote Id'
            description='18-character Salesforce Id of the Quote (starts with 0Q0) to summarize.')
        public String quoteId;
    }

    public class SummaryOutput {
        @InvocableVariable(label='Is Success'
            description='True if the recap was built (including a quote with no lines). False only on input/system error.')
        public Boolean isSuccess;

        @InvocableVariable(label='Summary Display'
            description='Rich-text, names-only per-line list for user-facing display (no header/totals — those are on the record card).')
        public String summaryDisplay;

        @InvocableVariable(label='Error Message')
        public String errorMessage;

        public SummaryOutput() {
            this.isSuccess = false;
            this.summaryDisplay = '';
        }
    }

    @InvocableMethod(
        label='Get Quote Demo Summary'
        description='Builds a names-only rich-text list of a quote\'s line items (product, quantity, unit and total price). Read-only. The quote header and totals are shown on the native Quote record card, not here, so nothing is duplicated.'
    )
    public static List<SummaryOutput> getSummary(List<SummaryInput> inputs) {
        List<SummaryOutput> results = new List<SummaryOutput>();
        if (inputs == null || inputs.isEmpty()) {
            return results;
        }
        for (SummaryInput input : inputs) {
            results.add(buildSummary(input));
        }
        return results;
    }

    private static SummaryOutput buildSummary(SummaryInput input) {
        SummaryOutput out = new SummaryOutput();
        if (input == null || String.isBlank(input.quoteId)) {
            out.errorMessage = 'Quote Id is required.';
            return out;
        }

        Id quoteId = RLM_AI_ConfigServiceUtils.toIdOrNull(input.quoteId);
        if (quoteId == null) {
            out.errorMessage = 'Invalid quote Id: ' + input.quoteId;
            return out;
        }

        Quote quote;
        try {
            quote = queryQuote(quoteId);
        } catch (Exception e) {
            // Header query failed (e.g. a field not accessible). Fall back to a
            // minimal recap built from the line items alone — never hard-fail.
            quote = null;
        }

        List<QuoteLineItem> lines;
        try {
            lines = queryLines(quoteId);
        } catch (Exception e) {
            lines = new List<QuoteLineItem>();
        }

        if (quote == null && lines.isEmpty()) {
            out.errorMessage =
                'Could not find a quote with that Id, or it has no readable details. '
                + 'Verify the quote and try again.';
            return out;
        }

        out.isSuccess = true;
        out.summaryDisplay = renderDisplay(quote, lines);
        return out;
    }

    // Header and money fields (name, status, Subtotal, Discount, Grand Total)
    // are presented on the native Quote record card, not here, so the recap does
    // not query them. We still confirm the quote exists / is readable so the
    // no-lines case can return a clean message rather than a hard error.
    private static Quote queryQuote(Id quoteId) {
        return [
            SELECT Id, Name
            FROM Quote
            WHERE Id = :quoteId
            WITH USER_MODE
            LIMIT 1
        ];
    }

    private static List<QuoteLineItem> queryLines(Id quoteId) {
        return [
            SELECT Id, Product2.Name, Quantity, NetUnitPrice, UnitPrice,
                   NetTotalPrice, TotalPrice, LineNumber
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId
            WITH USER_MODE
            ORDER BY LineNumber ASC, Product2.Name ASC
            LIMIT 200
        ];
    }

    /**
     * Renders the per-LINE list only. The quote header and money fields (name,
     * status, Subtotal, Discount, Grand Total) live on the native Quote record
     * card (Get_Quote_Record_Card), which is shown FIRST — so this recap must NOT
     * repeat them. "Display the information once, consistent across actions": the
     * card owns the header/totals, this owns the lines. The `quote` parameter is
     * retained for the no-lines fallback message only.
     */
    private static String renderDisplay(Quote quote, List<QuoteLineItem> lines) {
        List<String> parts = new List<String>();

        parts.add('**Line items: ' + String.valueOf(lines.size()) + '**');

        if (lines.isEmpty()) {
            parts.add('This quote has no line items yet.');
            return String.join(parts, '\n');
        }

        Integer ordinal = 1;
        for (QuoteLineItem qli : lines) {
            String productName = qli.Product2 != null && String.isNotBlank(qli.Product2.Name)
                ? qli.Product2.Name
                : 'Unnamed Product';
            Decimal unitPrice = qli.NetUnitPrice != null ? qli.NetUnitPrice : qli.UnitPrice;
            Decimal totalPrice = qli.NetTotalPrice != null ? qli.NetTotalPrice : qli.TotalPrice;
            String line = ordinal + '. **' + productName + '**'
                + ' — Qty ' + formatQuantity(qli.Quantity);
            if (unitPrice != null) {
                line += ', Unit ' + formatCurrency(unitPrice);
            }
            if (totalPrice != null) {
                line += ', Total ' + formatCurrency(totalPrice);
            }
            parts.add(line);
            ordinal++;
        }

        return String.join(parts, '\n');
    }

    private static String formatCurrency(Decimal value) {
        if (value == null) {
            return 'N/A';
        }
        return '$' + String.valueOf(value.setScale(2, RoundingMode.HALF_UP));
    }

    private static String formatQuantity(Decimal value) {
        if (value == null) {
            return '0';
        }
        if (value == value.setScale(0)) {
            return String.valueOf(value.setScale(0));
        }
        return String.valueOf(value);
    }
}
