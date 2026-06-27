/**
 * Invocable service for looking up a QuoteLineItem on a Quote by partial
 * product name.
 *
 * Matching is delegated to the SHARED fuzzy engine in RLM_AI_ConfigServiceUtils
 * (productNameScore + MIN_CONFIDENT_SCORE + classifyScores) — the SAME engine
 * used by the direct product search (matchProductsByName) and the
 * discount/field-update line resolution (matchLinesByProductName), so all three
 * name resolvers score and decide identically.
 *
 * Why this matters: the old per-class scorer gave a "startsWith" bonus and ran a
 * brittle contiguous SOQL LIKE pre-filter. For "change the additional API type
 * to Prod" that picked "API Access Requests (AEH)" over "Additional API" (the
 * shorter name started with the noise token "API") and even auto-selected it.
 * The shared engine instead fetches EVERY line on the quote, scores each line's
 * product name token-wise (noise words like the attribute name no longer break
 * the match), drops anything below MIN_CONFIDENT_SCORE, and lets classifyScores
 * decide single-vs-ambiguous. autoSelectThresholdPercent remains as a SECONDARY
 * tightening gate: it can demote an otherwise-clear winner below the threshold to
 * disambiguation, but it can never force-pick one of several equally-scoring
 * lines (a genuine tie always disambiguates).
 */
public with sharing class RLM_AI_QuoteLineItemLookupService {
    // Heap/SOQL safety bound on candidate lines fetched from a quote. Set to 200
    // (a full quote) so "show all lines" / "discount all lines" never silently
    // truncate — NOT a UX cap.
    private static final Integer MAX_CANDIDATES = 200;
    private static final Integer AUTO_SELECT_CONFIDENCE_THRESHOLD = 80;

    public class LookupInput {
        @InvocableVariable(required=true label='Quote Id'
            description='18-character Salesforce Id of the Quote (starts with 0Q0).')
        public String quoteId;

        @InvocableVariable(label='Product Name'
            description='Partial or full product name to search for. Leave blank to return every quote line on the quote as disambiguation candidates (used to let the user pick lines to discount, including "all").')
        public String productName;

        @InvocableVariable(label='Auto Select Threshold Percent'
            description='Optional confidence threshold (0-100) required to auto-select a match. Defaults to 80. Raising it forces a confirmation step; it never forces a pick between equally-scoring lines.')
        public Integer autoSelectThresholdPercent;
    }

    public class LookupOutput {
        @InvocableVariable(label='Quote Line Item Id')
        public String quoteLineItemId;

        @InvocableVariable(label='Product Name Found')
        public String productNameFound;

        @InvocableVariable(label='Is Success'
            description='True if the lookup ran correctly (including no-match and disambiguation outcomes). False only when a system or input error prevented it from running. Distinct from isFound, which reports whether a single high-confidence match was selected.')
        public Boolean isSuccess;

        @InvocableVariable(label='Is Found')
        public Boolean isFound;

        @InvocableVariable(label='Match Confidence Percent')
        public Integer matchConfidencePercent;

        @InvocableVariable(label='Needs Disambiguation')
        public Boolean needsDisambiguation;

        @InvocableVariable(label='Candidate Product Names JSON')
        public String candidateProductNamesJson;

        @InvocableVariable(label='Candidate Products')
        public List<Product2> candidateProducts;

        @InvocableVariable(label='Candidate Quote Line Items')
        public List<QuoteLineItem> candidateQuoteLineItems;

        @InvocableVariable(label='Candidate Quote Line Summaries JSON')
        public String candidateQuoteLineSummariesJson;

        @InvocableVariable(label='Candidate Quote Line Summaries Display'
            description='Formatted numbered summary of quote line candidates for user-facing disambiguation.')
        public String candidateQuoteLineSummariesDisplay;

        @InvocableVariable(label='Error Message')
        public String errorMessage;

        public LookupOutput() {
            this.isSuccess = false;
            this.isFound = false;
            this.needsDisambiguation = false;
            this.matchConfidencePercent = 0;
            this.candidateProductNamesJson = '[]';
            this.candidateProducts = new List<Product2>();
            this.candidateQuoteLineItems = new List<QuoteLineItem>();
            this.candidateQuoteLineSummariesJson = '[]';
            this.candidateQuoteLineSummariesDisplay = '';
        }
    }

    private class MatchCandidate {
        public QuoteLineItem qli;
        public Integer score;
        public Integer confidence;

        public MatchCandidate(QuoteLineItem qli, Integer score, Integer confidence) {
            this.qli = qli;
            this.score = score;
            this.confidence = confidence;
        }
    }

    @InvocableMethod(
        label='Get QuoteLineItem from Quote'
        description='Looks up a QuoteLineItem on a Quote by scored product-name matching (shared fuzzy engine). Returns the QuoteLineItem Id for use in product configuration actions, or disambiguation candidates when the name is ambiguous.'
    )
    public static List<LookupOutput> lookup(List<LookupInput> inputs) {
        List<LookupOutput> results = new List<LookupOutput>();
        if (inputs == null || inputs.isEmpty()) {
            return results;
        }
        for (LookupInput input : inputs) {
            results.add(fetchQuoteLineItem(input));
        }
        return results;
    }

    private static LookupOutput fetchQuoteLineItem(LookupInput input) {
        LookupOutput out = new LookupOutput();
        try {
            if (input == null) {
                out.errorMessage = 'Input is required.';
                return out;
            }
            if (String.isBlank(input.quoteId)) {
                out.errorMessage = 'Quote Id is required.';
                return out;
            }

            Id quoteId = RLM_AI_ConfigServiceUtils.toIdOrNull(input.quoteId);
            if (quoteId == null) {
                out.errorMessage = 'Invalid quote Id: ' + input.quoteId;
                return out;
            }

            // A blank product name means "list every line on the quote" so the
            // agent can present them for selection (e.g. discount one, several,
            // or all). A populated product name runs scored matching over all
            // lines via the shared fuzzy engine (no brittle contiguous LIKE).
            Boolean listAllMode = String.isBlank(input.productName);
            String queryText = listAllMode ? '' : input.productName.trim();

            // Fetch every line on the quote in either mode. In list-all mode we
            // keep all of them; in search mode we score them and keep only the
            // confident matches. Scoring in memory (not via SOQL LIKE) is what
            // lets a noise word the user adds — e.g. the attribute name in
            // "change the additional API type to Prod" — stop breaking the match.
            List<QuoteLineItem> qlis = queryAllQuoteLines(quoteId);

            // The lookup ran correctly past validation — match, disambiguation,
            // list-all, and no-match are all successful outcomes (isSuccess = true).
            // Only input/system errors leave isSuccess = false.
            out.isSuccess = true;

            if (qlis.isEmpty()) {
                out.errorMessage = listAllMode
                    ? 'No quote lines were found on this quote. Verify the quote ID and that it has line items.'
                    : 'No quote lines were found on this quote. Verify the quote ID and that it has line items.';
                return out;
            }

            if (listAllMode) {
                // Return all lines as candidates in their natural quote order; the
                // agent always asks the user which line(s) to act on. No scoring,
                // no auto-selection.
                List<MatchCandidate> allCandidates = new List<MatchCandidate>();
                for (QuoteLineItem qli : qlis) {
                    allCandidates.add(new MatchCandidate(qli, 0, 0));
                }
                populateDisambiguationOutputs(out, allCandidates, allCandidates.size());
                out.errorMessage =
                    'Listing all ' + allCandidates.size()
                    + ' quote line(s) for selection. Present candidateQuoteLineSummariesJson as a numbered list and ask the user which line(s) to act on (they may choose all, several, or one).';
                return out;
            }

            // Search mode: score every line through the SHARED engine and keep
            // only confident matches (>= MIN_CONFIDENT_SCORE), highest first.
            List<MatchCandidate> rankedCandidates = rankConfidentCandidates(qlis, queryText);

            if (rankedCandidates.isEmpty()) {
                out.errorMessage =
                    'No QuoteLineItem found on this quote matching product name "'
                    + input.productName
                    + '". Verify the quote ID and product name and try again.';
                return out;
            }

            Integer thresholdPercent = resolveThresholdPercent(input.autoSelectThresholdPercent);
            MatchCandidate bestMatch = rankedCandidates[0];
            out.matchConfidencePercent = bestMatch.confidence;

            // Two or more lines carry the SAME product name (e.g. the product was
            // added twice). The user must pick which line, regardless of score.
            if (hasDuplicateTopProductLines(rankedCandidates)) {
                populateDisambiguationOutputs(out, rankedCandidates);
                out.errorMessage =
                    'Multiple quote lines were found for product "'
                    + bestMatch.qli.Product2.Name
                    + '". Ask the user to choose from candidateQuoteLineItems and proceed with the selected line.';
                return out;
            }

            // Single-vs-ambiguous is the shared decision; the threshold is a
            // secondary floor that can only demote a clear winner, never promote
            // a tie.
            List<Integer> scores = new List<Integer>();
            for (MatchCandidate c : rankedCandidates) {
                scores.add(c.confidence);
            }
            RLM_AI_ConfigServiceUtils.MatchResolution resolution =
                RLM_AI_ConfigServiceUtils.classifyScores(scores);

            if (resolution == RLM_AI_ConfigServiceUtils.MatchResolution.SINGLE
                && bestMatch.confidence >= thresholdPercent) {
                out.quoteLineItemId = bestMatch.qli.Id;
                out.productNameFound = bestMatch.qli.Product2.Name;
                out.isFound = true;
            } else {
                populateDisambiguationOutputs(out, rankedCandidates);
                out.errorMessage =
                    'No single quote line clearly matched "' + input.productName
                    + '" at the ' + thresholdPercent
                    + '% confidence threshold (the top matches scored too closely, or the best match fell below the threshold). Ask the user to choose from candidateQuoteLineItems and proceed with the selected line.';
            }
        } catch (Exception e) {
            out.errorMessage = e.getMessage();
        }
        return out;
    }

    private static List<QuoteLineItem> queryAllQuoteLines(Id quoteId) {
        return [
            SELECT Id, Product2Id, Product2.Name, Quantity, UnitPrice, NetUnitPrice, TotalPrice, NetTotalPrice
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId
            ORDER BY LineNumber ASC, Product2.Name ASC
            LIMIT :MAX_CANDIDATES
        ];
    }

    /**
     * Scores each line's product name against the search term via the SHARED
     * productNameScore engine, keeps only confident matches
     * (>= RLM_AI_ConfigServiceUtils.MIN_CONFIDENT_SCORE), and returns them ranked
     * best-first. score and confidence are the same 0-100 value so the rest of
     * the contract (matchConfidencePercent, comparator) is unchanged.
     */
    private static List<MatchCandidate> rankConfidentCandidates(
        List<QuoteLineItem> qlis, String searchTerm
    ) {
        List<MatchCandidate> candidates = new List<MatchCandidate>();
        for (QuoteLineItem qli : qlis) {
            String candidateName = qli?.Product2?.Name;
            Integer score = RLM_AI_ConfigServiceUtils.productNameScore(candidateName, searchTerm);
            if (score >= RLM_AI_ConfigServiceUtils.MIN_CONFIDENT_SCORE) {
                candidates.add(new MatchCandidate(qli, score, score));
            }
        }
        candidates.sort(new MatchCandidateComparator());
        return candidates;
    }

    private class MatchCandidateComparator implements Comparator<MatchCandidate> {
        public Integer compare(MatchCandidate a, MatchCandidate b) {
            if (a.confidence != b.confidence) {
                return b.confidence - a.confidence;
            }
            if (a.score != b.score) {
                return b.score - a.score;
            }
            String nameA = a?.qli?.Product2?.Name == null ? '' : a.qli.Product2.Name;
            String nameB = b?.qli?.Product2?.Name == null ? '' : b.qli.Product2.Name;
            if (nameA == nameB) {
                return 0;
            }
            return nameA < nameB ? -1 : 1;
        }
    }

    private static String buildCandidateNamesJson(List<MatchCandidate> rankedCandidates, Integer maxToReturn) {
        List<String> candidateNames = new List<String>();
        for (MatchCandidate candidate : rankedCandidates) {
            if (candidateNames.size() >= maxToReturn) {
                break;
            }
            String productName = candidate?.qli?.Product2?.Name;
            if (String.isNotBlank(productName) && !candidateNames.contains(productName)) {
                candidateNames.add(productName);
            }
        }
        return JSON.serialize(candidateNames);
    }

    private static List<Product2> buildCandidateProducts(List<MatchCandidate> rankedCandidates, Integer maxToReturn) {
        List<Product2> products = new List<Product2>();
        Set<Id> seenProductIds = new Set<Id>();
        for (MatchCandidate candidate : rankedCandidates) {
            if (products.size() >= maxToReturn) {
                break;
            }
            Id productId = candidate?.qli?.Product2Id;
            String productName = candidate?.qli?.Product2?.Name;
            if (productId != null && !seenProductIds.contains(productId)) {
                products.add(new Product2(Id = productId, Name = productName));
                seenProductIds.add(productId);
            }
        }
        return products;
    }

    private static List<QuoteLineItem> buildCandidateQuoteLineItems(List<MatchCandidate> rankedCandidates, Integer maxToReturn) {
        List<QuoteLineItem> quoteLines = new List<QuoteLineItem>();
        Set<Id> seenQuoteLineIds = new Set<Id>();
        for (MatchCandidate candidate : rankedCandidates) {
            if (quoteLines.size() >= maxToReturn) {
                break;
            }
            QuoteLineItem qli = candidate?.qli;
            if (qli != null && qli.Id != null && !seenQuoteLineIds.contains(qli.Id)) {
                QuoteLineItem displayQuoteLine = new QuoteLineItem(
                    Id = qli.Id,
                    Product2Id = qli.Product2Id,
                    Quantity = qli.Quantity,
                    UnitPrice = resolveDisplayUnitPrice(qli)
                );
                if (qli.Product2Id != null) {
                    displayQuoteLine.Product2 = new Product2(
                        Id = qli.Product2Id,
                        Name = qli?.Product2?.Name
                    );
                }
                quoteLines.add(displayQuoteLine);
                seenQuoteLineIds.add(qli.Id);
            }
        }
        return quoteLines;
    }

    private static Decimal resolveDisplayUnitPrice(QuoteLineItem qli) {
        if (qli == null) {
            return null;
        }
        if (qli.NetUnitPrice != null) {
            return qli.NetUnitPrice;
        }
        return qli.UnitPrice;
    }

    private static void populateDisambiguationOutputs(
        LookupOutput out,
        List<MatchCandidate> rankedCandidates
    ) {
        // Show EVERY ranked candidate — never hide valid choices behind a cap.
        // The user must be able to pick any matching line, not just the top few.
        Integer all = (rankedCandidates == null) ? 0 : rankedCandidates.size();
        populateDisambiguationOutputs(out, rankedCandidates, all);
    }

    private static void populateDisambiguationOutputs(
        LookupOutput out,
        List<MatchCandidate> rankedCandidates,
        Integer maxToReturn
    ) {
        Integer cap = Math.max(maxToReturn, 1);
        out.needsDisambiguation = true;
        out.candidateProductNamesJson = buildCandidateNamesJson(rankedCandidates, cap);
        out.candidateProducts = buildCandidateProducts(rankedCandidates, cap);
        out.candidateQuoteLineItems = buildCandidateQuoteLineItems(rankedCandidates, cap);
        out.candidateQuoteLineSummariesJson = buildCandidateQuoteLineSummariesJson(rankedCandidates, cap);
        out.candidateQuoteLineSummariesDisplay = buildCandidateQuoteLineSummariesDisplay(rankedCandidates, cap);
    }

    private static Boolean hasDuplicateTopProductLines(List<MatchCandidate> rankedCandidates) {
        if (rankedCandidates == null || rankedCandidates.isEmpty()) {
            return false;
        }

        String topProductName = normalizeText(rankedCandidates[0]?.qli?.Product2?.Name);
        if (String.isBlank(topProductName)) {
            return false;
        }

        Integer duplicateCount = 0;
        for (MatchCandidate candidate : rankedCandidates) {
            if (normalizeText(candidate?.qli?.Product2?.Name) == topProductName) {
                duplicateCount++;
                if (duplicateCount > 1) {
                    return true;
                }
            }
        }
        return false;
    }

    private static String buildCandidateQuoteLineSummariesJson(List<MatchCandidate> rankedCandidates, Integer maxToReturn) {
        List<Object> summaries = new List<Object>();
        Set<Id> seenQuoteLineIds = new Set<Id>();
        for (MatchCandidate candidate : rankedCandidates) {
            if (summaries.size() >= maxToReturn) {
                break;
            }

            QuoteLineItem qli = candidate?.qli;
            if (qli == null || qli.Id == null || seenQuoteLineIds.contains(qli.Id)) {
                continue;
            }

            Decimal netUnitPrice = resolveDisplayUnitPrice(qli);
            Decimal netTotalPrice = qli.NetTotalPrice != null ? qli.NetTotalPrice : qli.TotalPrice;
            summaries.add(new Map<String, Object>{
                'quoteLineItemId' => qli.Id,
                'productName' => qli?.Product2?.Name,
                'quantity' => qli.Quantity,
                'netUnitPrice' => netUnitPrice,
                'netTotalPrice' => netTotalPrice
            });
            seenQuoteLineIds.add(qli.Id);
        }
        return JSON.serialize(summaries);
    }

    private static String buildCandidateQuoteLineSummariesDisplay(List<MatchCandidate> rankedCandidates, Integer maxToReturn) {
        List<String> lines = new List<String>();
        lines.add('Select the quote line(s) to update:');
        Set<Id> seenQuoteLineIds = new Set<Id>();
        Integer lineNumber = 1;
        for (MatchCandidate candidate : rankedCandidates) {
            if (lineNumber > maxToReturn) {
                break;
            }
            QuoteLineItem qli = candidate?.qli;
            if (qli == null || qli.Id == null || seenQuoteLineIds.contains(qli.Id)) {
                continue;
            }

            String productName = String.isNotBlank(qli?.Product2?.Name)
                ? qli.Product2.Name
                : 'Unnamed Product';
            Decimal netUnitPrice = resolveDisplayUnitPrice(qli);
            Decimal netTotalPrice = qli.NetTotalPrice != null ? qli.NetTotalPrice : qli.TotalPrice;
            lines.add(
                lineNumber + '. **' + productName
                + '** - Quantity: ' + String.valueOf(qli.Quantity)
                + ', Net Unit Price: ' + formatCurrency(netUnitPrice)
                + ', Net Total Price: ' + formatCurrency(netTotalPrice)
            );
            seenQuoteLineIds.add(qli.Id);
            lineNumber++;
        }
        return String.join(lines, '\n');
    }

    private static String formatCurrency(Decimal value) {
        if (value == null) {
            return 'N/A';
        }
        return '$' + String.valueOf(value.setScale(2));
    }

    private static Integer resolveThresholdPercent(Integer requestedThresholdPercent) {
        if (requestedThresholdPercent == null) {
            return AUTO_SELECT_CONFIDENCE_THRESHOLD;
        }
        return Math.max(0, Math.min(100, requestedThresholdPercent));
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
}
