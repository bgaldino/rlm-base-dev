/**
 * Invocable service that applies a discount to one, several, or all lines of a
 * quote in ONE call for the Quinn quoting assistant
 * (Apply_Discount_To_Quote_Lines action). Fixes the old agent's N+1 "discount
 * each line" loop and model-side Id/JSON handling: Apex resolves WHICH lines to
 * touch from high-level targeting, validates each belongs to the quote, then
 * loops the managed discount action server-side.
 *
 * Implementation boundary: this Apex is a RESOLVER / VALIDATOR, not a
 * replacement for managed discount DML. It resolves and validates the target
 * lines and computes a discount PERCENTAGE per line (the managed action accepts
 * only `discountPercentage`; "sell at $900" / "90% of list" are converted from
 * each line's ListPrice in Apex). The managed action
 * (`quotingAI__applyDiscountToQuoteLine`) performs the actual mutation.
 *
 * The managed invocation is isolated behind an injectable seam
 * (ManagedDiscountInvoker) so resolution/validation/percentage-math are fully
 * unit-testable. The real managed call is exercised live in `sf agent preview`.
 *
 * Targeting precedence (first non-empty wins): explicit quoteLineItemIds >
 * pendingSelectionJson ordinal map + selectedDisplayNumbersJson > applyToAll >
 * productName. Display ordinals are mapped ONLY through pendingSelectionJson
 * when present (Finding 1: ordinals are meaningless without the exact list they
 * indexed); otherwise they index into this helper's own freshly-built candidate
 * list (LineNumber asc), which is returned so the ordinals stay anchored.
 *
 * `with sharing` entry point; null-safe Id handling via RLM_AI_ConfigServiceUtils.
 */
public with sharing class RLM_AI_ApplyQuoteLineDiscountsService {

    public class DiscountInput {
        @InvocableVariable(required=true label='Quote Id'
            description='18-character Salesforce Id of the Quote (starts with 0Q0).')
        public String quoteId;

        @InvocableVariable(label='Discount Mode'
            description='One of: percent, targetPrice, percentOfList. Determines which value field is used.')
        public String discountMode;

        @InvocableVariable(label='Discount Percentage'
            description='Percent off (0-100). Used when discountMode is percent.')
        public Decimal discountPercentage;

        @InvocableVariable(label='Target Price'
            description='Per-unit sell price. Used when discountMode is targetPrice (e.g. "sell at $900").')
        public Decimal targetPrice;

        @InvocableVariable(label='Target Percent Of List'
            description='Per-unit price as a percent of list price (0-100). Used when discountMode is percentOfList (e.g. "90% of list").')
        public Decimal targetPercentOfList;

        @InvocableVariable(label='Apply To All'
            description='When true, discount every line on the quote.')
        public Boolean applyToAll;

        @InvocableVariable(label='Product Name'
            description='Discount every line whose product name matches this term.')
        public String productName;

        @InvocableVariable(label='Selected Display Numbers JSON'
            description='JSON array of the displayed selection numbers the user picked (e.g. [1,3]). Mapped through Pending Selection JSON.')
        public String selectedDisplayNumbersJson;

        @InvocableVariable(label='Pending Selection JSON'
            description='Internal plumbing: hidden ordinal-to-quoteLineItemId map produced when a candidate list was shown. Never displayed.')
        public String pendingSelectionJson;

        @InvocableVariable(label='Quote Line Item Ids'
            description='Explicit QuoteLineItem Ids to discount, when already known.')
        public List<String> quoteLineItemIds;
    }

    public class DiscountOutput {
        @InvocableVariable(label='Is Success'
            description='True when at least the resolved lines were discounted. False on input error, ambiguous targeting, or managed-action failure.')
        public Boolean isSuccess;

        @InvocableVariable(label='Applied Count')
        public Decimal appliedCount;

        @InvocableVariable(label='Results Display'
            description='Rich-text, per-line by product name summary of what was discounted, for user-facing display.')
        public String resultsDisplay;

        @InvocableVariable(label='Needs Disambiguation'
            description='True when targeting did not resolve to a definite line set and the user must pick.')
        public Boolean needsDisambiguation;

        @InvocableVariable(label='Candidate Summaries Display'
            description='Formatted numbered list of quote lines for user-facing disambiguation.')
        public String candidateSummariesDisplay;

        @InvocableVariable(label='Pending Selection JSON'
            description='Internal plumbing: ordinal-to-quoteLineItemId map for the candidate list above. Never displayed; pass back unchanged.')
        public String pendingSelectionJson;

        @InvocableVariable(label='Error Message')
        public String errorMessage;

        public DiscountOutput() {
            this.isSuccess = false;
            this.appliedCount = 0;
            this.needsDisambiguation = false;
            this.resultsDisplay = '';
            this.candidateSummariesDisplay = '';
        }
    }

    @InvocableMethod(
        label='Apply Discount To Quote Lines'
        description='Applies a discount to one, several, or all lines of a quote in one call. Resolves target lines from high-level targeting, validates ownership, and loops the managed discount action. Supports percent, target-price, and percent-of-list modes.'
    )
    public static List<DiscountOutput> applyDiscounts(List<DiscountInput> inputs) {
        List<DiscountOutput> results = new List<DiscountOutput>();
        if (inputs == null || inputs.isEmpty()) {
            return results;
        }
        for (DiscountInput input : inputs) {
            results.add(processDiscount(input));
        }
        return results;
    }

    private static DiscountOutput processDiscount(DiscountInput input) {
        DiscountOutput out = new DiscountOutput();
        try {
            if (input == null || String.isBlank(input.quoteId)) {
                out.errorMessage = 'Quote Id is required.';
                return out;
            }
            Id quoteId = RLM_AI_ConfigServiceUtils.toIdOrNull(input.quoteId);
            if (quoteId == null) {
                out.errorMessage = 'Invalid quote Id: ' + input.quoteId;
                return out;
            }

            // 1. Validate the discount mode and its value.
            DiscountSpec spec = resolveDiscountSpec(input);
            if (spec.errorMessage != null) {
                out.errorMessage = spec.errorMessage;
                return out;
            }

            // 2. Resolve target lines from high-level targeting.
            List<QuoteLineItem> targets = resolveTargets(quoteId, input, out);
            if (targets == null) {
                // out carries the error or disambiguation payload.
                return out;
            }
            if (targets.isEmpty()) {
                out.errorMessage = 'No matching quote lines were found to discount.';
                return out;
            }
            // No per-request line cap: this is a demo assistant and bulk discounts
            // across an entire quote (applyToAll) are a first-class path. The
            // resolver query already bounds the set at LIMIT 200 (a full quote).

            // 3. Loop the managed discount action per resolved line.
            List<String> resultLines = new List<String>();
            List<String> failedLines = new List<String>();
            Integer applied = 0;
            for (QuoteLineItem qli : targets) {
                Decimal percent = computePercentForLine(spec, qli);
                if (percent == null) {
                    failedLines.add(lineLabel(qli)
                        + ' — could not compute a discount (missing list price).');
                    continue;
                }
                percent = percent.setScale(2, RoundingMode.HALF_UP);
                ManagedResult mr = invoker.applyDiscount(quoteId, qli.Id, percent);
                if (mr != null && mr.isSuccess == true) {
                    applied++;
                    resultLines.add(lineLabel(qli) + ' — '
                        + percent.stripTrailingZeros().toPlainString() + '% off');
                } else {
                    String err = (mr != null && String.isNotBlank(mr.errorMessage))
                        ? mr.errorMessage : 'discount failed';
                    failedLines.add(lineLabel(qli) + ' — ' + err);
                }
            }

            out.appliedCount = applied;
            out.isSuccess = applied > 0 && failedLines.isEmpty();
            out.resultsDisplay = buildResultsDisplay(resultLines, failedLines);
            if (applied == 0) {
                out.errorMessage = 'No lines were discounted.';
            } else if (!failedLines.isEmpty()) {
                out.errorMessage = 'Some lines could not be discounted.';
            }
        } catch (Exception e) {
            out.isSuccess = false;
            out.errorMessage = e.getMessage();
        }
        return out;
    }

    // ---- Discount mode resolution ----

    private class DiscountSpec {
        String mode;
        Decimal percent;             // for mode == percent
        Decimal targetPrice;         // for mode == targetPrice
        Decimal targetPercentOfList; // for mode == percentOfList
        String errorMessage;
    }

    private static DiscountSpec resolveDiscountSpec(DiscountInput input) {
        DiscountSpec spec = new DiscountSpec();
        String mode = String.isBlank(input.discountMode)
            ? inferMode(input)
            : input.discountMode.trim().toLowerCase();

        if (mode == 'percent') {
            if (input.discountPercentage == null) {
                spec.errorMessage = 'A discount percentage is required for percent mode.';
                return spec;
            }
            if (input.discountPercentage < 0 || input.discountPercentage > 100) {
                spec.errorMessage = 'Discount percentage must be between 0 and 100.';
                return spec;
            }
            spec.mode = 'percent';
            spec.percent = input.discountPercentage;
            return spec;
        }
        if (mode == 'targetprice') {
            if (input.targetPrice == null || input.targetPrice < 0) {
                spec.errorMessage = 'A non-negative target price is required for targetPrice mode.';
                return spec;
            }
            spec.mode = 'targetPrice';
            spec.targetPrice = input.targetPrice;
            return spec;
        }
        if (mode == 'percentoflist') {
            if (input.targetPercentOfList == null
                    || input.targetPercentOfList < 0 || input.targetPercentOfList > 100) {
                spec.errorMessage = 'Target percent of list must be between 0 and 100.';
                return spec;
            }
            spec.mode = 'percentOfList';
            spec.targetPercentOfList = input.targetPercentOfList;
            return spec;
        }

        spec.errorMessage = 'Specify exactly one discount: a percentage, a target price, '
            + 'or a percent of list.';
        return spec;
    }

    /** Infers the mode from which single value is populated (lenient entry). */
    private static String inferMode(DiscountInput input) {
        Integer supplied = 0;
        String mode = '';
        if (input.discountPercentage != null) { supplied++; mode = 'percent'; }
        if (input.targetPrice != null) { supplied++; mode = 'targetprice'; }
        if (input.targetPercentOfList != null) { supplied++; mode = 'percentoflist'; }
        return supplied == 1 ? mode : '';
    }

    /**
     * Converts the discount spec to a flat percentage for a specific line.
     * targetPrice / percentOfList need the line's ListPrice; returns null when
     * that cannot be determined so the caller can report it cleanly.
     */
    private static Decimal computePercentForLine(DiscountSpec spec, QuoteLineItem qli) {
        if (spec.mode == 'percent') {
            return spec.percent;
        }
        if (spec.mode == 'percentOfList') {
            return 100 - spec.targetPercentOfList;
        }
        if (spec.mode == 'targetPrice') {
            Decimal listPrice = resolveListPrice(qli);
            if (listPrice == null || listPrice <= 0) {
                return null;
            }
            if (spec.targetPrice >= listPrice) {
                return 0;
            }
            return (1 - (spec.targetPrice / listPrice)) * 100;
        }
        return null;
    }

    private static Decimal resolveListPrice(QuoteLineItem qli) {
        if (qli.ListPrice != null && qli.ListPrice > 0) {
            return qli.ListPrice;
        }
        // Fall back to UnitPrice as the reference list price when ListPrice is
        // not populated (best-effort; demo lines often carry UnitPrice only).
        return qli.UnitPrice;
    }

    // ---- Target resolution ----

    /**
     * Returns the resolved lines, or null when `out` has been populated with an
     * error or disambiguation payload. An empty list means "no match" (handled
     * by the caller as a clean message).
     */
    private static List<QuoteLineItem> resolveTargets(
        Id quoteId, DiscountInput input, DiscountOutput out
    ) {
        // (a) Explicit Ids — validate each belongs to the quote.
        if (input.quoteLineItemIds != null && !input.quoteLineItemIds.isEmpty()) {
            return resolveByIds(quoteId, input.quoteLineItemIds, out);
        }

        // (b) Display ordinals mapped through the pending selection map.
        List<Integer> ordinals = parseIntArray(input.selectedDisplayNumbersJson);
        if (!ordinals.isEmpty()) {
            return resolveByOrdinals(quoteId, ordinals, input.pendingSelectionJson, out);
        }

        // (c) Apply to all lines.
        if (input.applyToAll == true) {
            return queryAllLines(quoteId);
        }

        // (d) By product name.
        if (String.isNotBlank(input.productName)) {
            return RLM_AI_ConfigServiceUtils.matchLinesByProductName(quoteId, input.productName);
        }

        // No targeting at all — present the lines so the user can pick.
        List<QuoteLineItem> all = queryAllLines(quoteId);
        if (all.isEmpty()) {
            out.errorMessage = 'This quote has no lines to discount.';
            return null;
        }
        populateDisambiguation(out, all);
        return null;
    }

    private static List<QuoteLineItem> resolveByIds(
        Id quoteId, List<String> rawIds, DiscountOutput out
    ) {
        Set<Id> requested = new Set<Id>();
        for (String raw : rawIds) {
            Id parsed = RLM_AI_ConfigServiceUtils.toIdOrNull(raw);
            if (parsed != null) {
                requested.add(parsed);
            }
        }
        if (requested.isEmpty()) {
            out.errorMessage = 'No valid quote line Ids were supplied.';
            return null;
        }
        List<QuoteLineItem> lines = [
            SELECT Id, Product2.Name, Quantity, UnitPrice, NetUnitPrice, ListPrice, LineNumber
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId AND Id IN :requested
            ORDER BY LineNumber ASC
        ];
        // Every requested Id must belong to this quote.
        if (lines.size() != requested.size()) {
            out.errorMessage = 'One or more of the selected lines do not belong to this quote.';
            return null;
        }
        return lines;
    }

    private static List<QuoteLineItem> resolveByOrdinals(
        Id quoteId, List<Integer> ordinals, String pendingSelectionJson, DiscountOutput out
    ) {
        Map<String, Object> ordinalMap = parsePendingSelection(pendingSelectionJson);
        List<String> idsToResolve = new List<String>();

        if (!ordinalMap.isEmpty()) {
            // Preferred path — map ordinals ONLY through the carried map.
            for (Integer ord : ordinals) {
                Object idVal = ordinalMap.get(String.valueOf(ord));
                if (idVal == null) {
                    out.errorMessage = 'Selection ' + ord
                        + ' was not in the list shown. Ask the user to pick from the displayed lines.';
                    return null;
                }
                idsToResolve.add(String.valueOf(idVal));
            }
            return resolveByIds(quoteId, idsToResolve, out);
        }

        // Fallback — ordinals index into a fresh LineNumber-asc candidate list.
        List<QuoteLineItem> all = queryAllLines(quoteId);
        if (all.isEmpty()) {
            out.errorMessage = 'This quote has no lines to discount.';
            return null;
        }
        List<QuoteLineItem> chosen = new List<QuoteLineItem>();
        for (Integer ord : ordinals) {
            if (ord < 1 || ord > all.size()) {
                out.errorMessage = 'Selection ' + ord + ' is out of range (there are '
                    + all.size() + ' lines).';
                return null;
            }
            chosen.add(all[ord - 1]);
        }
        return chosen;
    }

    private static List<QuoteLineItem> queryAllLines(Id quoteId) {
        return [
            SELECT Id, Product2.Name, Quantity, UnitPrice, NetUnitPrice, ListPrice, LineNumber
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId
            ORDER BY LineNumber ASC, Product2.Name ASC
            LIMIT 200
        ];
    }

    private static void populateDisambiguation(DiscountOutput out, List<QuoteLineItem> lines) {
        out.needsDisambiguation = true;
        List<String> display = new List<String>();
        display.add('Which line(s) would you like to discount? You can pick numbers, name a product, or say "all".');
        Map<String, String> ordinalToId = new Map<String, String>();
        Integer ordinal = 1;
        for (QuoteLineItem qli : lines) {
            display.add(ordinal + '. ' + lineLabel(qli));
            ordinalToId.put(String.valueOf(ordinal), String.valueOf(qli.Id));
            ordinal++;
        }
        out.candidateSummariesDisplay = String.join(display, '\n');
        out.pendingSelectionJson = JSON.serialize(ordinalToId);
    }

    // ---- Parsing helpers ----

    private static List<Integer> parseIntArray(String jsonText) {
        List<Integer> result = new List<Integer>();
        if (String.isBlank(jsonText)) {
            return result;
        }
        try {
            for (Object o : (List<Object>) JSON.deserializeUntyped(jsonText)) {
                if (o instanceof Integer) {
                    result.add((Integer) o);
                } else if (o instanceof Decimal) {
                    result.add(((Decimal) o).intValue());
                } else if (o instanceof String && String.isNotBlank((String) o)) {
                    result.add(Integer.valueOf(((String) o).trim()));
                }
            }
        } catch (Exception ignored) {
            // Malformed selection — treat as no ordinals supplied.
        }
        return result;
    }

    private static Map<String, Object> parsePendingSelection(String jsonText) {
        if (String.isBlank(jsonText)) {
            return new Map<String, Object>();
        }
        try {
            return (Map<String, Object>) JSON.deserializeUntyped(jsonText);
        } catch (Exception ignored) {
            return new Map<String, Object>();
        }
    }

    // ---- Display helpers ----

    private static String lineLabel(QuoteLineItem qli) {
        String name = qli.Product2 != null && String.isNotBlank(qli.Product2.Name)
            ? qli.Product2.Name
            : 'Unnamed Product';
        return '**' + name + '** (Qty ' + formatQuantity(qli.Quantity) + ')';
    }

    private static String buildResultsDisplay(List<String> applied, List<String> failed) {
        List<String> parts = new List<String>();
        if (!applied.isEmpty()) {
            parts.add('Discount applied:');
            Integer ordinal = 1;
            for (String line : applied) {
                parts.add(ordinal + '. ' + line);
                ordinal++;
            }
        }
        if (!failed.isEmpty()) {
            parts.add('');
            parts.add('Could not discount:');
            for (String line : failed) {
                parts.add('- ' + line);
            }
        }
        return String.join(parts, '\n');
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

    // ---- Managed discount invocation seam (injectable for tests) ----

    public class ManagedResult {
        public Boolean isSuccess;
        public String errorMessage;
        public ManagedResult(Boolean isSuccess, String errorMessage) {
            this.isSuccess = isSuccess;
            this.errorMessage = errorMessage;
        }
    }

    public interface ManagedDiscountInvoker {
        ManagedResult applyDiscount(Id quoteId, Id quoteLineItemId, Decimal discountPercentage);
    }

    /**
     * Default invoker: calls the managed `quotingAI__applyDiscountToQuoteLine`
     * action via Invocable.Action (scalar params, confirmed live in the spike).
     * The outer invoke() success only means "the action ran"; the real outcome
     * is the action's own `isSuccess` / `errorMessage` output parameters.
     */
    public class DefaultManagedDiscountInvoker implements ManagedDiscountInvoker {
        public ManagedResult applyDiscount(Id quoteId, Id quoteLineItemId, Decimal discountPercentage) {
            Invocable.Action action =
                Invocable.Action.createCustomAction('flow', 'quotingAI__applyDiscountToQuoteLine');
            action.setInvocationParameter('quoteId', String.valueOf(quoteId));
            action.setInvocationParameter('quoteLineItemId', String.valueOf(quoteLineItemId));
            action.setInvocationParameter('discountPercentage', discountPercentage);
            List<Invocable.Action.Result> actionResults = action.invoke();
            if (actionResults.isEmpty() || !actionResults[0].isSuccess()) {
                String err = actionResults.isEmpty()
                    ? 'The discount action returned no result.'
                    : summarizeErrors(actionResults[0].getErrors());
                return new ManagedResult(false, err);
            }
            Map<String, Object> outputs = actionResults[0].getOutputParameters();
            Boolean innerSuccess = outputs.get('isSuccess') == true;
            String innerError = (String) outputs.get('errorMessage');
            return new ManagedResult(innerSuccess, innerError);
        }

        private String summarizeErrors(List<Invocable.Action.Error> errors) {
            if (errors == null || errors.isEmpty()) {
                return 'The discount action failed.';
            }
            List<String> msgs = new List<String>();
            for (Invocable.Action.Error e : errors) {
                msgs.add(e.getMessage());
            }
            return String.join(msgs, '; ');
        }
    }

    @TestVisible
    private static ManagedDiscountInvoker invoker = new DefaultManagedDiscountInvoker();
}
