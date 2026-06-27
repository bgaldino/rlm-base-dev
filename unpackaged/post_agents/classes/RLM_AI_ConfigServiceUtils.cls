/**
 * Shared helpers for the RLM AI Product Configuration invocable services
 * (RLM_AI_ProductAttributeService, RLM_AI_ProductAttributeSaveService,
 * RLM_AI_ProductAttributeReadService, RLM_AI_QuoteLineItemLookupService).
 *
 * Declared `inherited sharing` so it runs in the sharing mode of its caller.
 * The four invocable services remain the `with sharing` entry points; this
 * utility never widens or narrows their record visibility.
 *
 * Scope: ID parse/prefix validation, null-safe JSON (de)serialization, and
 * SOQL LIKE escaping. The two picklist-query shapes used by the attribute
 * services are intentionally NOT centralized here — they build different maps
 * for different purposes and the SOQL skeleton is the only shared part.
 */
public inherited sharing class RLM_AI_ConfigServiceUtils {

    // Salesforce key prefixes for the records these services handle.
    public static final String QUOTE_PREFIX = '0Q0';
    public static final String QUOTE_LINE_ITEM_PREFIX = '0QL';

    /**
     * Shared confidence floor for fuzzy name resolution. A productNameScore below
     * this is treated as accidental overlap (a shared generic token like
     * "Product"/"Solution") and never auto-resolves. Used identically by the
     * DIRECT product search (matchProductsByName) and the INDIRECT quote-line
     * resolution (matchLinesByProductName) so both paths behave the same way for
     * a demo. Exact (100), name-subset/noise-word (90), and contains-all (85)
     * matches all sit well above it.
     */
    public static final Integer MIN_CONFIDENT_SCORE = 50;

    /**
     * Parses a String to an Id, returning null (instead of throwing) when the
     * value is blank or not a valid Salesforce Id. Callers map null to their
     * own input-error response so existing error messages are preserved.
     */
    public static Id toIdOrNull(String raw) {
        if (String.isBlank(raw)) {
            return null;
        }
        try {
            return Id.valueOf(raw.trim());
        } catch (Exception ignored) {
            return null;
        }
    }

    /**
     * True when `raw` is a valid Salesforce Id whose 3-character key prefix
     * matches `prefix`. Blank/invalid input returns false.
     */
    public static Boolean hasPrefix(String raw, String prefix) {
        if (String.isBlank(prefix)) {
            return false;
        }
        Id parsed = toIdOrNull(raw);
        return parsed != null && String.valueOf(parsed).startsWith(prefix);
    }

    /**
     * Validates `raw` as a Salesforce Id of the expected key prefix.
     * Returns the parsed Id, or throws IllegalArgumentException with a
     * caller-supplied label when the value is missing or the wrong type.
     */
    public static Id validateId(String raw, String prefix, String label) {
        Id parsed = toIdOrNull(raw);
        if (parsed == null) {
            throw new IllegalArgumentException('Invalid ' + label + ': ' + raw);
        }
        if (String.isNotBlank(prefix) && !String.valueOf(parsed).startsWith(prefix)) {
            throw new IllegalArgumentException('Invalid ' + label + ': ' + raw);
        }
        return parsed;
    }

    /** Null-safe JSON serialization. Returns null when the value is null. */
    public static String safeSerialize(Object value) {
        if (value == null) {
            return null;
        }
        return JSON.serialize(value);
    }

    /**
     * Null-safe deserialization into an untyped String→Object map. Returns an
     * empty map for blank input; propagates JSONException for malformed input
     * so callers can surface a parse error.
     */
    public static Map<String, Object> safeDeserializeMap(String jsonText) {
        if (String.isBlank(jsonText)) {
            return new Map<String, Object>();
        }
        return (Map<String, Object>) JSON.deserializeUntyped(jsonText);
    }

    /**
     * Escapes SOQL LIKE wildcards (`%`, `_`) and the escape character itself
     * so user-supplied search text is matched literally.
     */
    public static String escapeLikeTerm(String rawValue) {
        if (rawValue == null) {
            return '';
        }
        return rawValue
            .replace('\\', '\\\\')
            .replace('%', '\\%')
            .replace('_', '\\_');
    }

    /**
     * Matches a product name against a search term using tokenized fuzzy matching.
     * Returns true if all tokens in searchTerm appear as substrings in productName
     * (case-insensitive, order-independent).
     *
     * This is the pure in-memory matcher used for scoring and filtering lines
     * after SOQL retrieval. Testable without DML.
     */
    @TestVisible
    private static Boolean productNameMatchesTokens(String productName, String searchTerm) {
        if (String.isBlank(productName) || String.isBlank(searchTerm)) {
            return false;
        }
        String normalizedProduct = productName.toLowerCase().trim();
        String normalizedSearch = searchTerm.toLowerCase().trim();

        // Exact match scores highest but still returns true
        if (normalizedProduct == normalizedSearch) {
            return true;
        }

        // Tokenize search term (split on whitespace and punctuation)
        List<String> searchTokens = extractTokens(normalizedSearch);
        if (searchTokens.isEmpty()) {
            return false;
        }

        // All search tokens must appear as substrings in the product name
        for (String token : searchTokens) {
            if (!normalizedProduct.contains(token)) {
                return false;
            }
        }
        return true;
    }

    /**
     * Scores how well a product (or any) name matches a search term, tolerant of
     * extra noise words the user adds that are not in the catalog name (e.g.
     * "quantumbit complete solution BUNDLE" vs "QuantumBit Complete Solution").
     *
     * Returns 0-100:
     *  - 100  exact normalized match
     *  -  90  every NAME token is present in the search term (search is a
     *         superset — the noise-word case: "complete solution bundle" ⊇ name)
     *  -  85  every SEARCH token is present in the name (classic contains-all)
     *  - 1-80 proportional to the fraction of search tokens found in the name
     *         (partial overlap), scaled so more overlap ranks higher
     *  -   0  no token overlap
     * Order-independent, case-insensitive.
     *
     * Public so every name resolver — the direct product search
     * (matchProductsByName), the discount/field-update line resolution
     * (matchLinesByProductName), and the QuoteLineItem lookup behind
     * Get_QuoteLineItem_from_Quote (RLM_AI_QuoteLineItemLookupService) — scores
     * names through the SAME primitive and therefore behaves identically.
     */
    public static Integer productNameScore(String candidateName, String searchTerm) {
        if (String.isBlank(candidateName) || String.isBlank(searchTerm)) {
            return 0;
        }
        String normName = candidateName.toLowerCase().trim();
        String normSearch = searchTerm.toLowerCase().trim();
        if (normName == normSearch) {
            return 100;
        }

        List<String> searchTokens = extractTokens(normSearch);
        List<String> nameTokens = extractTokens(normName);
        if (searchTokens.isEmpty() || nameTokens.isEmpty()) {
            return 0;
        }

        Set<String> nameTokenSet = new Set<String>(nameTokens);
        Set<String> searchTokenSet = new Set<String>(searchTokens);

        // Every name token present in the search term (search is a superset of
        // the catalog name + noise words) — the strongest non-exact signal.
        Boolean allNameTokensInSearch = true;
        for (String nt : nameTokenSet) {
            if (!searchTokenSet.contains(nt)) {
                allNameTokensInSearch = false;
                break;
            }
        }
        if (allNameTokensInSearch) {
            return 90;
        }

        // Every search token present in the name (classic contains-all).
        Boolean allSearchTokensInName = true;
        Integer foundInName = 0;
        for (String st : searchTokenSet) {
            Boolean found = false;
            for (String nt : nameTokens) {
                if (nt.contains(st) || st.contains(nt)) {
                    found = true;
                    break;
                }
            }
            if (found) {
                foundInName++;
            } else {
                allSearchTokensInName = false;
            }
        }
        if (allSearchTokensInName) {
            return 85;
        }

        // Partial overlap — scale by fraction of search tokens found (1..80).
        if (foundInName == 0) {
            return 0;
        }
        Decimal fraction = (Decimal) foundInName / searchTokenSet.size();
        return (Integer) (fraction * 80).round();
    }

    /**
     * Extracts tokens from a string by splitting on whitespace and common
     * punctuation, filtering out empty strings.
     */
    @TestVisible
    private static List<String> extractTokens(String text) {
        List<String> tokens = new List<String>();
        if (String.isBlank(text)) {
            return tokens;
        }
        // Split on whitespace and common punctuation
        String normalized = text.replaceAll('[\\s\\-_,;:.!?()\\[\\]{}]+', ' ').trim();
        for (String token : normalized.split(' ')) {
            if (String.isNotBlank(token)) {
                tokens.add(token.toLowerCase());
            }
        }
        return tokens;
    }

    /**
     * The outcome of ranking confident candidates: NONE (nothing cleared the
     * floor), SINGLE (one clear winner — auto-resolve), or AMBIGUOUS (present
     * candidates and let the user pick). Shared by the direct product search and
     * the indirect quote-line resolution so both decide identically.
     */
    public enum MatchResolution { NONE, SINGLE, AMBIGUOUS }

    /**
     * Classifies confidence-filtered, score-descending candidates into a single
     * clear winner vs a set the user must disambiguate. A winner is: the only
     * confident candidate; OR a unique exact match (100); OR a top score >= 85
     * that leads the runner-up by >= 10. This is the ONE place that encodes
     * "confident enough to act without asking" — every name resolver calls it.
     *
     * @param sortedDescScores confident scores (>= MIN_CONFIDENT_SCORE), highest first.
     */
    public static MatchResolution classifyScores(List<Integer> sortedDescScores) {
        if (sortedDescScores == null || sortedDescScores.isEmpty()) {
            return MatchResolution.NONE;
        }
        if (sortedDescScores.size() == 1) {
            return MatchResolution.SINGLE;
        }
        Integer best = sortedDescScores[0];
        Integer second = sortedDescScores[1];
        if (best == 100 && second < 100) {
            return MatchResolution.SINGLE;
        }
        if (best >= 85 && (best - second) >= 10) {
            return MatchResolution.SINGLE;
        }
        return MatchResolution.AMBIGUOUS;
    }

    /** A scored quote-line match: the QuoteLineItem plus its 0-100 relevance score. */
    public class ScoredLine implements Comparable {
        public QuoteLineItem line;
        public Integer score;
        public ScoredLine(QuoteLineItem line, Integer score) {
            this.line = line;
            this.score = score;
        }
        // Sort descending by score, then ascending by LineNumber (a String like
        // "0001" — zero-padded, so lexical order matches natural order) for a
        // stable, natural tie-break.
        public Integer compareTo(Object other) {
            ScoredLine o = (ScoredLine) other;
            if (this.score != o.score) {
                return o.score - this.score;
            }
            String a = (this.line != null && this.line.LineNumber != null) ? this.line.LineNumber : '';
            String b = (o.line != null && o.line.LineNumber != null) ? o.line.LineNumber : '';
            return a.compareTo(b);
        }
    }

    /** A scored product match: the Product2 plus its 0-100 relevance score. */
    public class ScoredProduct implements Comparable {
        public Product2 product;
        public Integer score;
        public ScoredProduct(Product2 product, Integer score) {
            this.product = product;
            this.score = score;
        }
        // Sort descending by score, then by name for stable ordering.
        public Integer compareTo(Object other) {
            ScoredProduct o = (ScoredProduct) other;
            if (this.score != o.score) {
                return o.score - this.score;
            }
            String a = (this.product != null && this.product.Name != null) ? this.product.Name : '';
            String b = (o.product != null && o.product.Name != null) ? o.product.Name : '';
            return a.compareTo(b);
        }
    }

    /**
     * Finds active products matching a search term using tokenized, scored fuzzy
     * matching that tolerates extra noise words (e.g. trailing "bundle"). Builds
     * a broad token-OR SOQL filter (each search token may appear anywhere in the
     * name), then scores and ranks in memory via productNameScore. Returns only
     * candidates with score > 0, highest first, capped at `limitCount`.
     *
     * This is the product-search analogue of matchLinesByProductName, replacing
     * the brittle single contiguous LIKE that failed when the user's phrase was
     * not a substring of the catalog name.
     */
    public static List<ScoredProduct> matchProductsByName(String searchTerm, Integer limitCount) {
        List<ScoredProduct> ranked = new List<ScoredProduct>();
        if (String.isBlank(searchTerm)) {
            return ranked;
        }
        List<String> tokens = extractTokens(searchTerm.toLowerCase());
        if (tokens.isEmpty()) {
            return ranked;
        }

        // Build a token-OR LIKE filter: any token appearing anywhere in the name
        // makes the product a candidate; scoring then ranks by overlap. SOQL LIKE
        // takes a single value (not a list), so build the OR clause dynamically
        // with a bind list of patterns. Dedupe tokens to keep it small.
        Set<String> uniqueTokens = new Set<String>(tokens);
        Map<String, Object> binds = new Map<String, Object>();
        List<String> orClauses = new List<String>();
        Integer idx = 0;
        for (String t : uniqueTokens) {
            String bindName = 'tok' + idx;
            binds.put(bindName, '%' + escapeLikeTerm(t) + '%');
            orClauses.add('Name LIKE :' + bindName);
            idx++;
        }
        String soql =
            'SELECT Id, Name, ProductCode FROM Product2 ' +
            'WHERE IsActive = true AND (' + String.join(orClauses, ' OR ') + ') ' +
            'ORDER BY Name ASC LIMIT 500';
        List<Product2> candidates = Database.queryWithBinds(
            soql,
            binds,
            AccessLevel.USER_MODE
        );

        Integer cap = (limitCount != null && limitCount > 0) ? limitCount : 200;
        for (Product2 p : candidates) {
            Integer score = productNameScore(p.Name, searchTerm);
            if (score > 0) {
                ranked.add(new ScoredProduct(p, score));
            }
        }
        ranked.sort();
        if (ranked.size() > cap) {
            List<ScoredProduct> trimmed = new List<ScoredProduct>();
            for (Integer i = 0; i < cap; i++) {
                trimmed.add(ranked[i]);
            }
            return trimmed;
        }
        return ranked;
    }

    /**
     * Resolves QuoteLineItems by the product name on each line, using the SAME
     * scored, noise-word-tolerant engine as the direct product search
     * (matchProductsByName) so the indirect (QuoteLineItem -> Product2.Name) path
     * behaves identically to the direct one. Fetches all lines on the quote,
     * scores each line's product name via productNameScore, drops anything below
     * MIN_CONFIDENT_SCORE, and then:
     *   - returns the single clear winner when classifyScores says SINGLE
     *     (exact match, or a dominant top score) — so "discount the complete
     *     solution bundle line" resolves straight to the one matching line; or
     *   - returns the meaningfully-close set (within 25 points of the top, never
     *     below the floor) when AMBIGUOUS, so the caller can disambiguate.
     *
     * This is the public entry point that both the discount and field-update
     * services use. Result is ranked best-first; on a SINGLE winner it has one
     * element, letting callers keep their existing `size() > 1 -> disambiguate`
     * logic while gaining consistent fuzzy behavior.
     */
    public static List<QuoteLineItem> matchLinesByProductName(
        Id quoteId, String searchTerm
    ) {
        List<ScoredLine> ranked = matchLinesByProductNameScored(quoteId, searchTerm);
        if (ranked.isEmpty()) {
            return new List<QuoteLineItem>();
        }

        List<Integer> scores = new List<Integer>();
        for (ScoredLine sl : ranked) {
            scores.add(sl.score);
        }
        MatchResolution res = classifyScores(scores);
        if (res == MatchResolution.SINGLE) {
            return new List<QuoteLineItem>{ ranked[0].line };
        }

        // Ambiguous — return the meaningfully-relevant set for disambiguation,
        // dropping low partial-overlap noise (keep within 25 points of the top).
        Integer best = scores[0];
        Integer floor = Math.max(best - 25, MIN_CONFIDENT_SCORE);
        List<QuoteLineItem> matches = new List<QuoteLineItem>();
        for (ScoredLine sl : ranked) {
            if (sl.score >= floor) {
                matches.add(sl.line);
            }
        }
        return matches;
    }

    /**
     * Scores every line on the quote by its product name against the search term
     * (tokenized, noise-word tolerant), keeps only confident matches
     * (>= MIN_CONFIDENT_SCORE), and returns them ranked best-first. The shared
     * primitive behind matchLinesByProductName; exposed for callers that want the
     * raw ranked scores rather than the single-vs-many decision.
     */
    public static List<ScoredLine> matchLinesByProductNameScored(
        Id quoteId, String searchTerm
    ) {
        List<ScoredLine> ranked = new List<ScoredLine>();
        if (String.isBlank(searchTerm)) {
            return ranked;
        }

        // Fetch all lines on the quote (bounded by quote size; typical quotes
        // have <200 lines). This avoids brittle SOQL LIKE that fails on
        // non-contiguous matches.
        List<QuoteLineItem> allLines = [
            SELECT Id, Product2Id, Product2.Name, Quantity, UnitPrice, NetUnitPrice, ListPrice,
                   LineNumber, ProductSellingModel.SellingModelType
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId
            WITH USER_MODE
            ORDER BY LineNumber ASC
            LIMIT 200
        ];

        for (QuoteLineItem qli : allLines) {
            String productName = (qli.Product2 != null && String.isNotBlank(qli.Product2.Name))
                ? qli.Product2.Name
                : '';
            Integer score = productNameScore(productName, searchTerm);
            if (score >= MIN_CONFIDENT_SCORE) {
                ranked.add(new ScoredLine(qli, score));
            }
        }
        ranked.sort();
        return ranked;
    }
}
