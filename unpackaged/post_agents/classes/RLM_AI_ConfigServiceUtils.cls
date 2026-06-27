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
     * Resolves QuoteLineItems by productName using tokenized fuzzy matching.
     * Returns all lines whose Product2.Name matches the search term (all tokens
     * present, case-insensitive, order-independent). Sorted by LineNumber asc.
     *
     * This is the public entry point that both discount and field-update services
     * use. It fetches all lines on the quote and filters in-memory for maximum
     * match flexibility (no brittle contiguous LIKE).
     */
    public static List<QuoteLineItem> matchLinesByProductName(
        Id quoteId, String searchTerm
    ) {
        if (String.isBlank(searchTerm)) {
            return new List<QuoteLineItem>();
        }

        // Fetch all lines on the quote (bounded by quote size; typical quotes
        // have <200 lines). This avoids brittle SOQL LIKE that fails on
        // non-contiguous matches.
        List<QuoteLineItem> allLines = [
            SELECT Id, Product2.Name, Quantity, UnitPrice, NetUnitPrice, ListPrice, LineNumber
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId
            WITH USER_MODE
            ORDER BY LineNumber ASC
            LIMIT 200
        ];

        List<QuoteLineItem> matches = new List<QuoteLineItem>();
        for (QuoteLineItem qli : allLines) {
            String productName = (qli.Product2 != null && String.isNotBlank(qli.Product2.Name))
                ? qli.Product2.Name
                : '';
            if (productNameMatchesTokens(productName, searchTerm)) {
                matches.add(qli);
            }
        }
        return matches;
    }
}
