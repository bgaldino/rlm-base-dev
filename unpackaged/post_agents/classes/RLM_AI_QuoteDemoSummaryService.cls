/**
 * Invocable service that builds a satisfying, names-only recap of a Revenue
 * Cloud quote for the Quinn quoting assistant (Get_Quote_Demo_Summary action).
 *
 * Read-only. Complements the native Quote record card (Get_Quote_Record_Card):
 * the card is the clickable, navigable artifact; this service returns a rich-text
 * recap (quote name, account/opportunity names, line count, subtotal / discount /
 * grand total, and a names-only per-line list) for a "show me the quote" moment.
 *
 * Totals are BEST-EFFORT, never a gate: a missing or inaccessible total/discount
 * field must not fail the action. The recap degrades to line count + per-line
 * names / quantities / prices so it always returns something useful.
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
            description='Rich-text, names-only quote recap for user-facing display.')
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
        description='Builds a names-only rich-text recap of a quote (header, totals when available, and per-line product list). Read-only.'
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

    private static Quote queryQuote(Id quoteId) {
        return [
            SELECT Id, Name, Subtotal, GrandTotal, AppliedDiscountAmount,
                   Account.Name, Opportunity.Name
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

    private static String renderDisplay(Quote quote, List<QuoteLineItem> lines) {
        List<String> parts = new List<String>();

        String quoteName = quote != null && String.isNotBlank(quote.Name)
            ? quote.Name
            : 'Quote';
        parts.add('**' + quoteName + '**');

        if (quote != null) {
            String accountName = quote.Account != null ? quote.Account.Name : null;
            String oppName = quote.Opportunity != null ? quote.Opportunity.Name : null;
            if (String.isNotBlank(accountName)) {
                parts.add('Account: ' + accountName);
            }
            if (String.isNotBlank(oppName)) {
                parts.add('Opportunity: ' + oppName);
            }
        }

        parts.add('Line items: ' + String.valueOf(lines.size()));

        // Totals are best-effort. Show each only when populated.
        if (quote != null) {
            List<String> totalsBits = new List<String>();
            if (quote.Subtotal != null) {
                totalsBits.add('Subtotal ' + formatCurrency(quote.Subtotal));
            }
            if (quote.AppliedDiscountAmount != null && quote.AppliedDiscountAmount != 0) {
                totalsBits.add('Discount ' + formatCurrency(quote.AppliedDiscountAmount));
            }
            if (quote.GrandTotal != null) {
                totalsBits.add('Grand Total ' + formatCurrency(quote.GrandTotal));
            }
            if (!totalsBits.isEmpty()) {
                parts.add(String.join(totalsBits, ' | '));
            }
        }

        if (!lines.isEmpty()) {
            parts.add('');
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
