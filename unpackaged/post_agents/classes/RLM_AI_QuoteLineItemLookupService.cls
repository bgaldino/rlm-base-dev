/**
 * Invocable service for looking up a QuoteLineItem on a Quote by partial
 * product name.
 *
 * Matching strategy uses a scored SOQL candidate query so the service can
 * prefer exact and higher-confidence partial matches while preserving the
 * current flow/agent output contract.
 */
public with sharing class RLM_AI_QuoteLineItemLookupService {
    private static final Integer MAX_CANDIDATES = 20;
    private static final Integer AUTO_SELECT_CONFIDENCE_THRESHOLD = 80;
    private static final Integer MIN_CANDIDATES_TO_RETURN = 3;

    public class LookupInput {
        @InvocableVariable(required=true label='Quote Id'
            description='18-character Salesforce Id of the Quote (starts with 0Q0).')
        public String quoteId;

        @InvocableVariable(label='Product Name'
            description='Partial or full product name to search for (LIKE match). Leave blank to return every quote line on the quote as disambiguation candidates (used to let the user pick lines to discount, including "all").')
        public String productName;

        @InvocableVariable(label='Auto Select Threshold Percent'
            description='Optional confidence threshold (0-100) required to auto-select a match. Defaults to 80.')
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
        description='Looks up a QuoteLineItem on a Quote using a partial product name LIKE match. Returns the QuoteLineItem Id for use in product configuration actions.'
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
            // or all). A populated product name runs scored LIKE matching.
            Boolean listAllMode = String.isBlank(input.productName);

            String queryText = listAllMode ? '' : input.productName.trim();
            String normalizedQuery = normalizeText(queryText);
            List<QuoteLineItem> qlis = listAllMode
                ? queryAllQuoteLines(quoteId)
                : queryMatchingQuoteLines(quoteId, queryText);
            // The lookup ran correctly past validation — match, disambiguation,
            // list-all, and no-match are all successful outcomes (isSuccess = true).
            // Only input/system errors leave isSuccess = false.
            out.isSuccess = true;
            if (!qlis.isEmpty()) {
                List<MatchCandidate> rankedCandidates = rankCandidates(qlis, normalizedQuery);

                if (listAllMode) {
                    // Return all lines as candidates; the agent always asks the
                    // user which line(s) to act on. No auto-selection.
                    populateDisambiguationOutputs(out, rankedCandidates, rankedCandidates.size());
                    out.errorMessage =
                        'Listing all ' + rankedCandidates.size()
                        + ' quote line(s) for selection. Present candidateQuoteLineSummariesJson as a numbered list and ask the user which line(s) to act on (they may choose all, several, or one).';
                    return out;
                }

                Integer thresholdPercent = resolveThresholdPercent(input.autoSelectThresholdPercent);
                MatchCandidate bestMatch = rankedCandidates[0];
                out.matchConfidencePercent = bestMatch.confidence;

                if (hasDuplicateTopProductLines(rankedCandidates)) {
                    populateDisambiguationOutputs(out, rankedCandidates);
                    out.errorMessage =
                        'Multiple quote lines were found for product "'
                        + bestMatch.qli.Product2.Name
                        + '". Ask the user to choose from candidateQuoteLineItems and proceed with the selected line.';
                } else if (bestMatch.confidence >= thresholdPercent) {
                    out.quoteLineItemId = bestMatch.qli.Id;
                    out.productNameFound = bestMatch.qli.Product2.Name;
                    out.isFound = true;
                } else {
                    populateDisambiguationOutputs(out, rankedCandidates);
                    out.errorMessage =
                        'Multiple partial matches were found and no result met the auto-selection confidence threshold of '
                        + thresholdPercent
                        + '%. Ask the user to choose from candidateProductNamesJson and retry with a more specific product name.';
                }
            } else {
                out.errorMessage = listAllMode
                    ? 'No quote lines were found on this quote. Verify the quote ID and that it has line items.'
                    : 'No QuoteLineItem found on this quote matching product name "' + input.productName + '". Verify the quote ID and product name and try again.';
            }
        } catch (Exception e) {
            out.errorMessage = e.getMessage();
        }
        return out;
    }

    private static List<QuoteLineItem> queryMatchingQuoteLines(Id quoteId, String queryText) {
        String likePattern = '%' + RLM_AI_ConfigServiceUtils.escapeLikeTerm(queryText) + '%';
        return [
            SELECT Id, Product2Id, Product2.Name, Quantity, UnitPrice, NetUnitPrice, TotalPrice, NetTotalPrice
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId
              AND Product2.Name LIKE :likePattern
            ORDER BY Product2.Name ASC
            LIMIT :MAX_CANDIDATES
        ];
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

    private static List<MatchCandidate> rankCandidates(List<QuoteLineItem> qlis, String normalizedQuery) {
        List<MatchCandidate> candidates = new List<MatchCandidate>();
        for (QuoteLineItem qli : qlis) {
            String candidateName = qli?.Product2?.Name;
            Integer score = computeMatchScore(normalizedQuery, candidateName);
            Integer confidence = computeConfidencePercent(normalizedQuery, candidateName);
            candidates.add(new MatchCandidate(qli, score, confidence));
        }
        // With no query (list-all mode), there is nothing to rank — keep the
        // SOQL LineNumber order so the numbered list matches the quote.
        if (String.isNotBlank(normalizedQuery)) {
            candidates.sort(new MatchCandidateComparator());
        }
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

    private static Integer computeMatchScore(String normalizedQuery, String candidateName) {
        String normalizedCandidate = normalizeText(candidateName);
        Integer score = 0;

        if (normalizedCandidate == normalizedQuery) {
            score += 1000;
        } else if (normalizedCandidate.startsWith(normalizedQuery)) {
            score += 700;
        } else if (normalizedCandidate.contains(normalizedQuery)) {
            score += 500;
        }

        Set<String> queryTokens = toTokenSet(normalizedQuery);
        if (!queryTokens.isEmpty()) {
            Set<String> candidateTokens = toTokenSet(normalizedCandidate);
            Integer matchedTokens = 0;
            for (String token : queryTokens) {
                if (candidateTokens.contains(token)) {
                    matchedTokens++;
                }
            }
            score += matchedTokens * 80;
        }

        Integer lengthDelta = Math.abs(normalizedCandidate.length() - normalizedQuery.length());
        score -= Math.min(lengthDelta, 50);
        return score;
    }

    private static Integer computeConfidencePercent(String normalizedQuery, String candidateName) {
        String normalizedCandidate = normalizeText(candidateName);
        if (String.isBlank(normalizedQuery) || String.isBlank(normalizedCandidate)) {
            return 0;
        }

        if (normalizedCandidate == normalizedQuery) {
            return 100;
        }

        Set<String> queryTokens = toTokenSet(normalizedQuery);
        Set<String> candidateTokens = toTokenSet(normalizedCandidate);
        Integer matchedTokens = 0;
        for (String token : queryTokens) {
            if (candidateTokens.contains(token)) {
                matchedTokens++;
            }
        }
        Decimal tokenCoverage = queryTokens.isEmpty()
            ? 0
            : (Decimal.valueOf(matchedTokens) / Decimal.valueOf(queryTokens.size()));

        Integer confidence;
        if (normalizedCandidate.startsWith(normalizedQuery)) {
            confidence = 78 + Integer.valueOf((tokenCoverage * 20).setScale(0, RoundingMode.HALF_UP));
        } else if (normalizedCandidate.contains(normalizedQuery)) {
            confidence = 72 + Integer.valueOf((tokenCoverage * 20).setScale(0, RoundingMode.HALF_UP));
        } else if (tokenCoverage > 0) {
            confidence = 40 + Integer.valueOf((tokenCoverage * 30).setScale(0, RoundingMode.HALF_UP));
        } else {
            confidence = 0;
        }

        Integer lengthDelta = Math.abs(normalizedCandidate.length() - normalizedQuery.length());
        Integer lengthPenalty = Math.min(15, lengthDelta);
        confidence = confidence - lengthPenalty;

        if (confidence < 0) {
            confidence = 0;
        } else if (confidence > 100) {
            confidence = 100;
        }
        return confidence;
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
        populateDisambiguationOutputs(out, rankedCandidates, MIN_CANDIDATES_TO_RETURN);
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

    private static Set<String> toTokenSet(String value) {
        Set<String> tokens = new Set<String>();
        if (String.isBlank(value)) {
            return tokens;
        }
        for (String token : value.split('\\s+')) {
            if (String.isNotBlank(token)) {
                tokens.add(token);
            }
        }
        return tokens;
    }
}
