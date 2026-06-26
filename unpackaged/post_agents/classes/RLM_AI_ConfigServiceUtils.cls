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
}
