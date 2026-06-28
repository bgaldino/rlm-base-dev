/**
 * Invocable service that adds a product to a quote in ONE call for the Quinn
 * quoting assistant (Add_Product_To_Quote action). Collapses the fragile
 * identify-product -> get-selling-model -> add-line chain the old agent had to
 * drive turn by turn.
 *
 * Implementation boundary: this Apex is a RESOLVER / ORCHESTRATOR, not a
 * replacement for managed quote-line DML. It resolves the product, the default
 * ProductSellingModel, and any product-name disambiguation, then invokes the
 * managed add-line action (`quotingAI__addQuoteLineItemToQuote`) with the
 * resolved inputs. The managed DML contract stays the source of truth; we never
 * reimplement Revenue Cloud quote-line creation here.
 *
 * The managed invocation is isolated behind an injectable seam
 * (ManagedAddLineInvoker) so the resolver/validation logic is fully
 * unit-testable. The real managed call is exercised live in `sf agent preview`
 * (managed actions are not invocable/mockable in @isTest).
 *
 * Names-only by contract: the agent surfaces `lineSummaryDisplay` /
 * `productNameAdded`, never raw Ids. Id outputs are flagged
 * `is_used_by_planner: false` in the .agent so they wire variables without
 * entering planner context.
 *
 * `with sharing` entry point; null-safe Id handling via RLM_AI_ConfigServiceUtils.
 */
public with sharing class RLM_AI_AddProductToQuoteService {

    // Upper bound on product-name search matches returned for disambiguation.
    // Set high (200) so a broad search term never silently hides valid products;
    // it is a heap/SOQL safety bound, not a UX cap. Quantity is per line and
    // unbounded. Single-currency by default (demo scope).
    private static final Integer MAX_PRODUCT_CANDIDATES = 200;

    public class AddInput {
        @InvocableVariable(required=true label='Quote Id'
            description='18-character Salesforce Id of the Quote (starts with 0Q0) to add the product to.')
        public String quoteId;

        @InvocableVariable(label='Product Id'
            description='Salesforce Id of the product to add, when already known. Takes precedence over Product Name.')
        public String productId;

        @InvocableVariable(label='Product Name'
            description='Name of the product to add. Used when Product Id is not supplied; resolved by name match.')
        public String productName;

        @InvocableVariable(label='Quantity'
            description='Number of units to add. Defaults to 1.')
        public Decimal quantity;

        @InvocableVariable(label='Selling Model Name'
            description='Optional. Only set this when the USER explicitly names a selling model (e.g. "add it as Term Monthly"). Matched case-insensitively against the selling-model option names of the product. When blank, the DEFAULT selling model of the product is used automatically — do NOT ask the user to choose.')
        public String sellingModelName;

        @InvocableVariable(label='Start Date'
            description='Optional start date for the line.')
        public Date startDate;

        @InvocableVariable(label='End Date'
            description='Optional end date for the line.')
        public Date endDate;
    }

    public class AddOutput {
        @InvocableVariable(label='Is Success'
            description='True only when the line was added. False on input error, disambiguation, or a managed add-line failure.')
        public Boolean isSuccess;

        @InvocableVariable(label='Quote Line Item Id')
        public String quoteLineItemId;

        @InvocableVariable(label='Product Name Added')
        public String productNameAdded;

        @InvocableVariable(label='Quantity Added')
        public Decimal quantityAdded;

        @InvocableVariable(label='Selling Model Name')
        public String sellingModelName;

        @InvocableVariable(label='Line Summary Display'
            description='Rich-text, names-only confirmation of what was added, for user-facing display.')
        public String lineSummaryDisplay;

        @InvocableVariable(label='Needs Disambiguation'
            description='True when the product name matched more than one product and the user must pick.')
        public Boolean needsDisambiguation;

        @InvocableVariable(label='Candidate Products')
        public List<Product2> candidateProducts;

        @InvocableVariable(label='Candidate Summaries Display'
            description='Formatted numbered list of matching products for user-facing disambiguation.')
        public String candidateSummariesDisplay;

        @InvocableVariable(label='Error Message')
        public String errorMessage;

        public AddOutput() {
            this.isSuccess = false;
            this.needsDisambiguation = false;
            this.candidateProducts = new List<Product2>();
            this.candidateSummariesDisplay = '';
            this.lineSummaryDisplay = '';
        }
    }

    @InvocableMethod(
        label='Add Product To Quote'
        description='Adds a product to a quote in one call: resolves the product and its default selling model, then invokes the managed add-line action. Returns a names-only confirmation, or product candidates when the name is ambiguous.'
    )
    public static List<AddOutput> addProduct(List<AddInput> inputs) {
        List<AddOutput> results = new List<AddOutput>();
        if (inputs == null || inputs.isEmpty()) {
            return results;
        }
        for (AddInput input : inputs) {
            results.add(processAdd(input));
        }
        return results;
    }

    private static AddOutput processAdd(AddInput input) {
        AddOutput out = new AddOutput();
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

            // 1. Resolve the product (by Id, or by name with disambiguation).
            Product2 product = resolveProduct(input, out);
            if (product == null) {
                // out already carries the error or disambiguation payload.
                return out;
            }

            // 2. Resolve the selling model (hard prerequisite for add-line):
            // the user-named one when supplied, otherwise the product default.
            SellingModelResolution psm = resolveSellingModel(product.Id, input.sellingModelName);
            if (psm.errorMessage != null) {
                out.errorMessage = psm.errorMessage;
                return out;
            }

            // 3. Invoke the managed add-line action with the resolved inputs.
            Decimal quantity = (input.quantity == null || input.quantity <= 0)
                ? 1
                : input.quantity;
            ManagedResult mr = invoker.addLine(
                quoteId, product.Id, psm.sellingModelId, quantity,
                input.startDate, input.endDate
            );
            if (mr == null || mr.isSuccess != true) {
                out.errorMessage = (mr != null && String.isNotBlank(mr.errorMessage))
                    ? mr.errorMessage
                    : 'The product could not be added to the quote.';
                return out;
            }

            // 4. Success — locate the newly added line for downstream wiring.
            out.isSuccess = true;
            out.productNameAdded = product.Name;
            out.quantityAdded = quantity;
            out.sellingModelName = psm.sellingModelName;
            out.quoteLineItemId = findNewQuoteLineId(quoteId, product.Id);
            out.lineSummaryDisplay = buildLineSummary(product.Name, quantity, psm.sellingModelName);
        } catch (Exception e) {
            out.isSuccess = false;
            out.errorMessage = e.getMessage();
        }
        return out;
    }

    /**
     * Resolves the target product. Populates `out` with an error or
     * disambiguation payload and returns null when no single product is found.
     */
    private static Product2 resolveProduct(AddInput input, AddOutput out) {
        Id productId = RLM_AI_ConfigServiceUtils.toIdOrNull(input.productId);
        if (productId != null) {
            List<Product2> byId = [
                SELECT Id, Name FROM Product2 WHERE Id = :productId LIMIT 1
            ];
            if (byId.isEmpty()) {
                out.errorMessage = 'No product found for the supplied product Id.';
                return null;
            }
            return byId[0];
        }

        if (String.isBlank(input.productName)) {
            out.errorMessage = 'A product Id or product name is required.';
            return null;
        }

        String term = input.productName.trim();

        // Tokenized, scored matching (tolerant of noise words like a trailing
        // "bundle" the user adds that is not in the catalog name). Replaces the
        // brittle single contiguous LIKE that failed when the typed phrase was
        // not a substring of the product name.
        List<RLM_AI_ConfigServiceUtils.ScoredProduct> scored =
            RLM_AI_ConfigServiceUtils.matchProductsByName(term, MAX_PRODUCT_CANDIDATES);

        // Confidence floor + single-vs-ambiguous decision come from the SHARED
        // engine (RLM_AI_ConfigServiceUtils) so this direct product search and the
        // indirect quote-line resolution behave identically. Drop weak partial
        // matches that share only a generic token (e.g. a stray
        // "Product"/"Solution") — without the floor, a single accidental hit would
        // auto-resolve and add the wrong product. The noise-word case
        // ("quantumbit complete solution bundle" -> 90) and exact/contains-all
        // matches (100/85) stay well above the floor.
        List<RLM_AI_ConfigServiceUtils.ScoredProduct> confident =
            new List<RLM_AI_ConfigServiceUtils.ScoredProduct>();
        List<Integer> confidentScores = new List<Integer>();
        for (RLM_AI_ConfigServiceUtils.ScoredProduct sp : scored) {
            if (sp.score >= RLM_AI_ConfigServiceUtils.MIN_CONFIDENT_SCORE) {
                confident.add(sp);
                confidentScores.add(sp.score);
            }
        }

        if (confident.isEmpty()) {
            out.errorMessage = 'No active product found matching "' + term
                + '". Check the product name and try again.';
            return null;
        }

        // A single clear winner (exact match, or a dominant top score) resolves
        // without a prompt — keeps "add the complete solution" fluid even when
        // other products share a token.
        RLM_AI_ConfigServiceUtils.MatchResolution res =
            RLM_AI_ConfigServiceUtils.classifyScores(confidentScores);
        if (res == RLM_AI_ConfigServiceUtils.MatchResolution.SINGLE) {
            return confident[0].product;
        }

        // Genuinely ambiguous — surface candidates (highest score first), do not
        // guess. Only the meaningfully-relevant ones (drop low partial-overlap
        // noise: keep within 25 points of the top match, never below the floor).
        Integer best = confident[0].score;
        List<Product2> candidateList = new List<Product2>();
        Integer floor = Math.max(best - 25, RLM_AI_ConfigServiceUtils.MIN_CONFIDENT_SCORE);
        for (RLM_AI_ConfigServiceUtils.ScoredProduct sp : confident) {
            if (sp.score >= floor) {
                candidateList.add(sp.product);
            }
        }
        out.needsDisambiguation = true;
        out.candidateProducts = candidateList;
        out.candidateSummariesDisplay = buildProductCandidateDisplay(candidateList);
        out.errorMessage = 'Multiple products match "' + term
            + '". Ask the user which one to add.';
        return null;
    }

    private class SellingModelResolution {
        Id sellingModelId;
        String sellingModelName;
        String errorMessage;
    }

    /**
     * Resolves the default ProductSellingModel for a product. The managed
     * add-line action requires a ProductSellingModel Id and does not self-resolve
     * it. Prefers IsDefault; falls back to the sole option when only one exists;
     * returns a clean name-based message (no dead end) when ambiguous or missing.
     */
    private static SellingModelResolution resolveSellingModel(Id productId, String requestedName) {
        SellingModelResolution res = new SellingModelResolution();
        List<ProductSellingModelOption> options = [
            SELECT Id, ProductSellingModelId, ProductSellingModel.Name, IsDefault
            FROM ProductSellingModelOption
            WHERE Product2Id = :productId
            ORDER BY IsDefault DESC
        ];

        if (options.isEmpty()) {
            res.errorMessage = 'This product has no selling model configured, '
                + 'so it cannot be added to a quote yet. Configure a selling model for it first.';
            return res;
        }

        // User explicitly named a selling model — honor it (case-insensitive).
        if (String.isNotBlank(requestedName)) {
            String wanted = requestedName.trim().toLowerCase();
            List<String> available = new List<String>();
            for (ProductSellingModelOption o : options) {
                String n = o.ProductSellingModel != null ? o.ProductSellingModel.Name : null;
                if (String.isNotBlank(n)) {
                    available.add(n);
                    if (n.trim().toLowerCase() == wanted) {
                        res.sellingModelId = o.ProductSellingModelId;
                        res.sellingModelName = n;
                        return res;
                    }
                }
            }
            res.errorMessage = 'This product has no "' + requestedName
                + '" selling model. Available: ' + String.join(available, ', ')
                + '. Ask the user which one to use.';
            return res;
        }

        List<ProductSellingModelOption> defaults = new List<ProductSellingModelOption>();
        for (ProductSellingModelOption o : options) {
            if (o.IsDefault == true) {
                defaults.add(o);
            }
        }

        ProductSellingModelOption chosen;
        if (defaults.size() == 1) {
            chosen = defaults[0];
        } else if (defaults.isEmpty() && options.size() == 1) {
            chosen = options[0];
        } else {
            // No single default and more than one option — ask, don't guess.
            List<String> names = new List<String>();
            for (ProductSellingModelOption o : options) {
                String n = o.ProductSellingModel != null ? o.ProductSellingModel.Name : null;
                if (String.isNotBlank(n)) {
                    names.add(n);
                }
            }
            res.errorMessage = 'This product has multiple selling models ('
                + String.join(names, ', ')
                + ') and no default. Ask the user which selling model to use.';
            return res;
        }

        res.sellingModelId = chosen.ProductSellingModelId;
        res.sellingModelName = chosen.ProductSellingModel != null
            ? chosen.ProductSellingModel.Name
            : null;
        return res;
    }

    /** Best-effort lookup of the just-added line for variable wiring. */
    private static String findNewQuoteLineId(Id quoteId, Id productId) {
        List<QuoteLineItem> lines = [
            SELECT Id
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId AND Product2Id = :productId
            ORDER BY CreatedDate DESC, LineNumber DESC
            LIMIT 1
        ];
        return lines.isEmpty() ? null : String.valueOf(lines[0].Id);
    }

    private static String buildLineSummary(String productName, Decimal quantity, String sellingModelName) {
        String qty = formatQuantity(quantity);
        String summary = 'Added **' + qty + ' × ' + productName + '** to the quote';
        if (String.isNotBlank(sellingModelName)) {
            summary += ' (' + sellingModelName + ')';
        }
        return summary + '.';
    }

    private static String buildProductCandidateDisplay(List<Product2> products) {
        List<String> lines = new List<String>();
        lines.add('Multiple products match. Which one would you like to add?');
        Integer ordinal = 1;
        for (Product2 p : products) {
            String line = ordinal + '. **' + p.Name + '**';
            if (String.isNotBlank(p.ProductCode)) {
                line += ' (' + p.ProductCode + ')';
            }
            lines.add(line);
            ordinal++;
        }
        return String.join(lines, '\n');
    }

    private static String formatQuantity(Decimal value) {
        if (value == null) {
            return '1';
        }
        if (value == value.setScale(0)) {
            return String.valueOf(value.setScale(0));
        }
        return String.valueOf(value);
    }

    private static String normalizeText(String value) {
        if (String.isBlank(value)) {
            return '';
        }
        return value
            .toLowerCase()
            .replaceAll('[^a-z0-9]+', ' ')
            .replaceAll('\\s+', ' ')
            .trim();
    }

    // ---- Managed add-line invocation seam (injectable for tests) ----

    public class ManagedResult {
        public Boolean isSuccess;
        public String errorMessage;
        public ManagedResult(Boolean isSuccess, String errorMessage) {
            this.isSuccess = isSuccess;
            this.errorMessage = errorMessage;
        }
    }

    public interface ManagedAddLineInvoker {
        ManagedResult addLine(
            Id quoteId, Id productId, Id sellingModelId,
            Decimal quantity, Date startDate, Date endDate
        );
    }

    /**
     * Default invoker: calls the managed `quotingAI__addQuoteLineItemToQuote`
     * action via Invocable.Action (scalar params, confirmed live in the spike).
     * The outer invoke() success only means "the action ran"; the real outcome
     * is the action's own `isSuccess` / `errorMessage` output parameters.
     */
    public class DefaultManagedAddLineInvoker implements ManagedAddLineInvoker {
        public ManagedResult addLine(
            Id quoteId, Id productId, Id sellingModelId,
            Decimal quantity, Date startDate, Date endDate
        ) {
            Invocable.Action action =
                Invocable.Action.createCustomAction('flow', 'quotingAI__addQuoteLineItemToQuote');
            action.setInvocationParameter('quoteId', String.valueOf(quoteId));
            action.setInvocationParameter('productId', String.valueOf(productId));
            action.setInvocationParameter('productSellingModelID', String.valueOf(sellingModelId));
            action.setInvocationParameter('quantity', quantity);
            if (startDate != null) {
                action.setInvocationParameter('startDate', startDate);
            }
            if (endDate != null) {
                action.setInvocationParameter('endDate', endDate);
            }
            List<Invocable.Action.Result> actionResults = action.invoke();
            if (actionResults.isEmpty() || !actionResults[0].isSuccess()) {
                String err = actionResults.isEmpty()
                    ? 'The add-line action returned no result.'
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
                return 'The add-line action failed.';
            }
            List<String> msgs = new List<String>();
            for (Invocable.Action.Error e : errors) {
                msgs.add(e.getMessage());
            }
            return String.join(msgs, '; ');
        }
    }

    @TestVisible
    private static ManagedAddLineInvoker invoker = new DefaultManagedAddLineInvoker();
}
