/**
 * Invocable service that updates fields on Revenue Cloud records
 * (QuoteLineItem and Quote primarily) via direct USER_MODE Apex DML for the
 * Quinn quoting assistant (Update_Record_Fields action).
 *
 * BROAD edit by default: accepts ANY field that is genuinely updateable
 * (validated dynamically via describe at call time; no hand-maintained field
 * allowlist). USER_MODE DML is the real gate, not a static list. Bypasses the
 * PST pricing engine so field values stick (the managed update actions reprice
 * and silently discard proration-owned values like EndDate).
 *
 * Carve-outs (CORRECTNESS rails): QuoteLineItemAttribute raw DML is disallowed
 * (routes to config actions); productName matching >1 line returns
 * disambiguation (does NOT fan out) — editing the wrong duplicate line is a
 * real error.
 *
 * Targeting precedence (QuoteLineItem): explicit quoteLineItemIds >
 * selectedDisplayNumbersJson + pendingSelectionJsonIn > applyToAll >
 * productName. Quote edits target the quote itself.
 *
 * `with sharing` entry point; null-safe Id handling via RLM_AI_ConfigServiceUtils.
 */
public with sharing class RLM_AI_UpdateRecordFieldsService {

    // Test-only flag: when true, uses System.AccessLevel.SYSTEM_MODE for DML
    // to bypass FLS checks in test context (test users don't have field grants).
    @TestVisible
    private static Boolean testBypassUserMode = false;

    // Test-only seam: QuoteLineItem Ids to treat as one-time selling model.
    // QuoteLineItem.SellingModelType/ProductSellingModelId are not createable
    // (the model flows from the product/pricebook), so a one-time line cannot be
    // built in an Apex test. This lets a test exercise the selling-model skip
    // path. Null/empty in production.
    @TestVisible
    private static Set<Id> testForceOneTimeLineIds;

    public class UpdateFieldsInput {
        @InvocableVariable(required=true label='Quote Id'
            description='18-character Salesforce Id of the Quote (starts with 0Q0). Required even for Quote edits.')
        public String quoteId;

        @InvocableVariable(label='sObject Type'
            description='QuoteLineItem (default) or Quote.')
        public String sObjectType;

        @InvocableVariable(required=true label='Field Updates JSON'
            description='JSON array: [{"fieldApiName":"EndDate","value":"2029-06-25"}]. Values as strings; dates yyyy-MM-dd. Omitted field=preserve, explicit null=clear (if nillable).')
        public String fieldUpdatesJson;

        @InvocableVariable(label='Quote Line Item Ids'
            description='Explicit QuoteLineItem Ids to update, when already known.')
        public List<String> quoteLineItemIds;

        @InvocableVariable(label='Product Name'
            description='Update lines whose product name matches this term. Multi-match=disambiguation (never fans out).')
        public String productName;

        @InvocableVariable(label='Apply To All'
            description='When true, update every line on the quote.')
        public Boolean applyToAll;

        @InvocableVariable(label='Selected Display Numbers JSON'
            description='JSON array of the displayed selection numbers the user picked (e.g. [1,3]). Mapped through Pending Selection JSON.')
        public String selectedDisplayNumbersJson;

        @InvocableVariable(label='Pending Selection JSON In'
            description='Internal plumbing: hidden ordinal-to-quoteLineItemId map produced when a candidate list was shown. Never displayed.')
        public String pendingSelectionJsonIn;

        @InvocableVariable(label='Reprice'
            description='Reserved for future use. Ignored in v1.')
        public Boolean reprice;
    }

    public class UpdateFieldsOutput {
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;

        @InvocableVariable(label='Updated Count')
        public Decimal updatedCount;

        @InvocableVariable(label='Results Display'
            description='Rich-text summary of what was updated, for user-facing display. Bold record/product names.')
        public String resultsDisplay;

        @InvocableVariable(label='Needs Disambiguation'
            description='True when targeting did not resolve to a definite line set and the user must pick.')
        public Boolean needsDisambiguation;

        @InvocableVariable(label='Candidate Quote Line Summaries Display'
            description='Formatted numbered list of quote lines for user-facing disambiguation.')
        public String candidateQuoteLineSummariesDisplay;

        @InvocableVariable(label='Pending Selection JSON'
            description='Internal plumbing: ordinal-to-quoteLineItemId map for the candidate list above. Never displayed; pass back unchanged.')
        public String pendingSelectionJson;

        @InvocableVariable(label='Error Message')
        public String errorMessage;

        public UpdateFieldsOutput() {
            this.isSuccess = false;
            this.updatedCount = 0;
            this.needsDisambiguation = false;
            this.resultsDisplay = '';
            this.candidateQuoteLineSummariesDisplay = '';
        }
    }

    @InvocableMethod(
        label='Update Record Fields'
        description='Updates any editable field on a quote/lines via direct DML so values stick. Never for discounts (Apply_Discount_To_Quote_Lines) or attributes (config actions). Output always renderable; always use show_command.'
        category='Quote Management'
    )
    public static List<UpdateFieldsOutput> updateRecordFields(List<UpdateFieldsInput> inputs) {
        List<UpdateFieldsOutput> results = new List<UpdateFieldsOutput>();
        if (inputs == null || inputs.isEmpty()) {
            return results;
        }
        for (UpdateFieldsInput input : inputs) {
            results.add(processUpdate(input));
        }
        return results;
    }

    private static UpdateFieldsOutput processUpdate(UpdateFieldsInput input) {
        UpdateFieldsOutput out = new UpdateFieldsOutput();
        try {
            if (input == null || String.isBlank(input.quoteId)) {
                out.errorMessage = 'Quote Id is required.';
                return out;
            }
            Id quoteId = RLM_AI_ConfigServiceUtils.toIdOrNull(input.quoteId);
            if (quoteId == null || !String.valueOf(quoteId).startsWith(RLM_AI_ConfigServiceUtils.QUOTE_PREFIX)) {
                out.errorMessage = 'Invalid quote Id: ' + input.quoteId;
                return out;
            }

            // 1. Resolve sObjectType
            String typeName = String.isBlank(input.sObjectType)
                ? 'QuoteLineItem'
                : input.sObjectType.trim();
            if (typeName == 'QuoteLineItemAttribute') {
                out.errorMessage = 'QuoteLineItemAttribute edits must use the configuration actions, not direct field updates.';
                return out;
            }
            if (typeName != 'QuoteLineItem' && typeName != 'Quote') {
                // Allow other objects (Opportunity, Account, etc.) — broad by design.
                // USER_MODE is the real gate.
            }

            // 2. Parse field updates
            List<FieldUpdate> fieldUpdates = parseFieldUpdates(input.fieldUpdatesJson);
            if (fieldUpdates.isEmpty()) {
                out.errorMessage = 'Specify at least one field to update.';
                return out;
            }

            // 3. Validate and coerce fields via describe
            Map<String, CoercedField> coercedFields = validateAndCoerce(typeName, fieldUpdates);
            if (coercedFields == null) {
                // Error message set by validateAndCoerce
                return out;
            }

            // 4. Resolve targets
            List<SObject> targets = resolveTargets(quoteId, typeName, input, out);
            if (targets == null) {
                // out carries error or disambiguation
                return out;
            }
            if (targets.isEmpty()) {
                out.errorMessage = 'No matching records were found to update.';
                return out;
            }

            // 5. Apply fields and DML.
            // The resolved `targets` rows were queried with read-only / calculated
            // fields (NetUnitPrice, ListPrice, UnitPrice, …) populated for display.
            // Updating those loaded rows in USER_MODE fails with "fields being
            // inaccessible" because USER_MODE validates FLS on EVERY populated
            // field, including the non-updateable ones. So DML a fresh BARE record
            // carrying only the Id + the fields being changed, and keep the loaded
            // row only for labels / change summaries.
            //
            // SELLING-MODEL GATE: the platform rejects date fields (EndDate, etc.)
            // on one-time order lines ("You can't specify EndDate for one-time
            // order products"). A batch that mixes one-time and termed/evergreen
            // lines (e.g. an EndDate edit with applyToAll) would otherwise fail on
            // every one-time line. So per record, drop date fields for OneTime
            // lines; if that leaves nothing to update, skip the line with a note
            // rather than failing the batch. This runs BEFORE the per-request cap
            // so an "apply to all" date edit is capped on the lines it will
            // actually touch (the termed/evergreen ones), not the raw target count
            // that includes lines it will skip anyway.
            List<SObject> dmlRecords = new List<SObject>();
            List<SObject> dmlTargets = new List<SObject>();
            List<String> skippedLines = new List<String>();
            for (SObject rec : targets) {
                Map<String, CoercedField> applicable = fieldsForRecord(typeName, rec, coercedFields);
                if (applicable.isEmpty()) {
                    // Every requested field was term-gated out for this one-time line.
                    skippedLines.add(recordLabel(typeName, rec)
                        + ' — skipped (one-time product; dates do not apply)');
                    continue;
                }
                // Mutate the loaded row too, so recordLabel/summarizeChanges read
                // the new values; it is never sent to the database.
                applyFields(rec, applicable);
                SObject bare = rec.getSObjectType().newSObject(rec.Id);
                applyFields(bare, applicable);
                dmlRecords.add(bare);
                dmlTargets.add(rec);
            }
            // No per-request line cap: this is a demo assistant and bulk edits
            // (applyToAll dates/fields across an entire quote) are a first-class
            // path. Apex bulk DML handles the whole set in one call; the resolver
            // queries already bound the set at LIMIT 200 (a full quote).

            List<String> successLines = new List<String>();
            List<String> failedLines = new List<String>();
            Integer successCount = 0;

            if (!dmlRecords.isEmpty()) {
                AccessLevel accessLevel = testBypassUserMode ? AccessLevel.SYSTEM_MODE : AccessLevel.USER_MODE;
                Database.SaveResult[] saveResults = Database.update(dmlRecords, accessLevel);

                for (Integer i = 0; i < saveResults.size(); i++) {
                    Database.SaveResult sr = saveResults[i];
                    SObject rec = dmlTargets[i];
                    String recLabel = recordLabel(typeName, rec);
                    if (sr.isSuccess()) {
                        successCount++;
                        Map<String, CoercedField> applied = fieldsForRecord(typeName, rec, coercedFields);
                        successLines.add(recLabel + ' — ' + summarizeChanges(rec, applied));
                    } else {
                        String err = summarizeErrors(sr.getErrors());
                        failedLines.add(recLabel + ' — ' + err);
                    }
                }
            }

            out.updatedCount = successCount;
            // Skipped one-time lines are an expected, non-error outcome: a success
            // as long as nothing actually failed and at least one line updated
            // (or every targeted line was legitimately skipped).
            out.isSuccess = failedLines.isEmpty() && (successCount > 0 || !skippedLines.isEmpty());
            out.resultsDisplay = buildResultsDisplay(successLines, failedLines, skippedLines);
            if (successCount == 0 && skippedLines.isEmpty()) {
                out.errorMessage = 'No records were updated.';
            } else if (!failedLines.isEmpty()) {
                out.errorMessage = 'Some records could not be updated.';
            }

        } catch (Exception e) {
            out.isSuccess = false;
            out.errorMessage = e.getMessage();
        }
        return out;
    }

    // ---- Field parsing and coercion ----

    private class FieldUpdate {
        String fieldApiName;
        Object value; // can be null (clear) or a String
        Boolean isPresent;
    }

    private class CoercedField {
        Schema.SObjectField field;
        Object value;
        // True when this is a Date/DateTime field. Date fields are rejected by
        // the platform on one-time order lines ("You can't specify EndDate for
        // one-time order products"), so we skip them for OneTime selling models.
        Boolean isDateType = false;
    }

    @TestVisible
    private static List<FieldUpdate> parseFieldUpdates(String jsonText) {
        List<FieldUpdate> updates = new List<FieldUpdate>();
        if (String.isBlank(jsonText)) {
            return updates;
        }
        try {
            List<Object> items = (List<Object>) JSON.deserializeUntyped(jsonText);
            for (Object item : items) {
                Map<String, Object> entry = (Map<String, Object>) item;
                FieldUpdate fu = new FieldUpdate();
                fu.fieldApiName = (String) entry.get('fieldApiName');
                fu.isPresent = entry.containsKey('value');
                fu.value = entry.get('value');
                if (String.isBlank(fu.fieldApiName)) {
                    continue;
                }
                updates.add(fu);
            }
        } catch (Exception e) {
            throw new IllegalArgumentException('Invalid field updates JSON: ' + e.getMessage());
        }
        return updates;
    }

    @TestVisible
    private static Map<String, CoercedField> validateAndCoerce(
        String objectType, List<FieldUpdate> fieldUpdates
    ) {
        Schema.DescribeSObjectResult objDescribe;
        try {
            objDescribe = Schema.getGlobalDescribe().get(objectType).getDescribe();
        } catch (Exception e) {
            throw new IllegalArgumentException('Unknown object type: ' + objectType);
        }

        Map<String, Schema.SObjectField> fieldMap = objDescribe.fields.getMap();
        Map<String, CoercedField> coerced = new Map<String, CoercedField>();

        for (FieldUpdate fu : fieldUpdates) {
            String apiName = resolveFieldApiName(fu.fieldApiName, fieldMap);
            if (apiName == null) {
                throw new IllegalArgumentException('Unknown field: ' + fu.fieldApiName + ' on ' + objectType);
            }
            Schema.SObjectField field = fieldMap.get(apiName);
            Schema.DescribeFieldResult dfr = field.getDescribe();
            if (!dfr.isUpdateable()) {
                throw new IllegalArgumentException(
                    'Field ' + fu.fieldApiName + ' cannot be edited (read-only or system field).'
                );
            }

            CoercedField cf = new CoercedField();
            cf.field = field;
            Schema.DisplayType cfType = dfr.getType();
            cf.isDateType = (cfType == Schema.DisplayType.DATE || cfType == Schema.DisplayType.DATETIME);

            // Handle clear semantics: omitted key=preserve, explicit null/""=clear
            if (!fu.isPresent) {
                // Key not present — preserve existing value (skip)
                continue;
            }
            if (fu.value == null || (fu.value instanceof String && String.isBlank((String) fu.value))) {
                // Explicit clear
                if (!dfr.isNillable()) {
                    throw new IllegalArgumentException(
                        'Field ' + fu.fieldApiName + ' cannot be cleared (required field).'
                    );
                }
                cf.value = null;
            } else {
                // Coerce by display type
                cf.value = coerceValue(dfr, String.valueOf(fu.value));
            }
            coerced.put(apiName, cf);
        }

        return coerced;
    }

    private static String resolveFieldApiName(
        String userSupplied, Map<String, Schema.SObjectField> fieldMap
    ) {
        // Case-insensitive match
        for (String apiName : fieldMap.keySet()) {
            if (apiName.equalsIgnoreCase(userSupplied)) {
                return apiName;
            }
        }
        return null;
    }

    private static Object coerceValue(Schema.DescribeFieldResult dfr, String rawValue) {
        Schema.DisplayType dt = dfr.getType();
        if (dt == Schema.DisplayType.DATE) {
            try {
                return Date.valueOf(rawValue);
            } catch (Exception e) {
                throw new IllegalArgumentException(
                    'Invalid date value for ' + dfr.getName() + '. Use the format YYYY-MM-DD.'
                );
            }
        }
        if (dt == Schema.DisplayType.DATETIME) {
            try {
                return DateTime.valueOf(rawValue);
            } catch (Exception e) {
                throw new IllegalArgumentException(
                    'Invalid datetime value for ' + dfr.getName() + '.'
                );
            }
        }
        if (dt == Schema.DisplayType.BOOLEAN) {
            return Boolean.valueOf(rawValue);
        }
        if (dt == Schema.DisplayType.INTEGER) {
            try {
                return Integer.valueOf(rawValue);
            } catch (Exception e) {
                throw new IllegalArgumentException(
                    'Invalid integer value for ' + dfr.getName() + '.'
                );
            }
        }
        if (dt == Schema.DisplayType.DOUBLE || dt == Schema.DisplayType.CURRENCY || dt == Schema.DisplayType.PERCENT) {
            try {
                return Decimal.valueOf(rawValue);
            } catch (Exception e) {
                throw new IllegalArgumentException(
                    'Invalid number value for ' + dfr.getName() + '.'
                );
            }
        }
        if (dt == Schema.DisplayType.PICKLIST || dt == Schema.DisplayType.MULTIPICKLIST) {
            // Label-or-API-value tolerance (DECISION 3)
            List<Schema.PicklistEntry> entries = dfr.getPicklistValues();
            Map<String, String> labelToValue = new Map<String, String>();
            Set<String> apiValues = new Set<String>();
            for (Schema.PicklistEntry pe : entries) {
                if (pe.isActive()) {
                    apiValues.add(pe.getValue());
                    labelToValue.put(pe.getLabel().toLowerCase(), pe.getValue());
                }
            }
            String lowerValue = rawValue.toLowerCase();
            if (apiValues.contains(rawValue)) {
                return rawValue; // exact API value match
            }
            if (labelToValue.containsKey(lowerValue)) {
                return labelToValue.get(lowerValue); // label match
            }
            // Neither matched
            List<String> validOptions = new List<String>(apiValues);
            throw new IllegalArgumentException(
                'Invalid picklist value "' + rawValue + '" for ' + dfr.getName() +
                '. Valid options: ' + String.join(validOptions, ', ')
            );
        }
        // Default: String
        return rawValue;
    }

    @TestVisible
    private static void applyFields(SObject rec, Map<String, CoercedField> coercedFields) {
        for (CoercedField cf : coercedFields.values()) {
            rec.put(cf.field, cf.value);
        }
    }

    /**
     * Returns the subset of coercedFields that may be applied to this specific
     * record. The only gate today: date fields (EndDate, etc.) are dropped for
     * one-time selling-model quote lines, which the platform forbids. Non-date
     * fields and non-OneTime lines pass through unchanged.
     */
    private static Map<String, CoercedField> fieldsForRecord(
        String typeName, SObject rec, Map<String, CoercedField> coercedFields
    ) {
        if (typeName != 'QuoteLineItem' || !isOneTimeLine(rec)) {
            return coercedFields;
        }
        Map<String, CoercedField> applicable = new Map<String, CoercedField>();
        for (String fieldName : coercedFields.keySet()) {
            CoercedField cf = coercedFields.get(fieldName);
            if (cf.isDateType) {
                continue; // dates do not apply to one-time order products
            }
            applicable.put(fieldName, cf);
        }
        return applicable;
    }

    /** True when the line's product selling model is OneTime. */
    @TestVisible
    private static Boolean isOneTimeLine(SObject rec) {
        QuoteLineItem qli = (QuoteLineItem) rec;
        if (testForceOneTimeLineIds != null && qli.Id != null
                && testForceOneTimeLineIds.contains(qli.Id)) {
            return true;
        }
        if (qli.ProductSellingModel == null) {
            return false;
        }
        return qli.ProductSellingModel.SellingModelType == 'OneTime';
    }

    // ---- Target resolution ----

    private static List<SObject> resolveTargets(
        Id quoteId, String typeName, UpdateFieldsInput input, UpdateFieldsOutput out
    ) {
        if (typeName == 'Quote') {
            // Quote header edit — target the quote itself
            List<Quote> quotes = [
                SELECT Id, Name, Status, ExpirationDate
                FROM Quote
                WHERE Id = :quoteId
                WITH USER_MODE
                LIMIT 1
            ];
            if (quotes.isEmpty()) {
                out.errorMessage = 'Quote not found.';
                return null;
            }
            return (List<SObject>) quotes;
        }

        // QuoteLineItem or other object — resolve via targeting
        if (typeName == 'QuoteLineItem') {
            return resolveQuoteLineTargets(quoteId, input, out);
        }

        // Generic object — resolve by Id if provided
        if (input.quoteLineItemIds != null && !input.quoteLineItemIds.isEmpty()) {
            Set<Id> requestedIds = new Set<Id>();
            for (String rawId : input.quoteLineItemIds) {
                Id parsed = RLM_AI_ConfigServiceUtils.toIdOrNull(rawId);
                if (parsed != null) {
                    requestedIds.add(parsed);
                }
            }
            if (requestedIds.isEmpty()) {
                out.errorMessage = 'No valid record Ids were supplied.';
                return null;
            }
            String soql = 'SELECT Id FROM ' + typeName + ' WHERE Id IN :requestedIds WITH USER_MODE LIMIT 200';
            return Database.query(soql);
        }

        out.errorMessage = 'Specify which record(s) to update.';
        return null;
    }

    private static List<SObject> resolveQuoteLineTargets(
        Id quoteId, UpdateFieldsInput input, UpdateFieldsOutput out
    ) {
        // Explicit Ids
        if (input.quoteLineItemIds != null && !input.quoteLineItemIds.isEmpty()) {
            return resolveLinesByIds(quoteId, input.quoteLineItemIds, out);
        }

        // Display ordinals
        List<Integer> ordinals = parseIntArray(input.selectedDisplayNumbersJson);
        if (!ordinals.isEmpty()) {
            return resolveLinesByOrdinals(quoteId, ordinals, input.pendingSelectionJsonIn, out);
        }

        // Apply to all
        if (input.applyToAll == true) {
            return queryAllLines(quoteId);
        }

        // Product name — DISAMBIGUATION if >1 match
        if (String.isNotBlank(input.productName)) {
            List<QuoteLineItem> matches = RLM_AI_ConfigServiceUtils.matchLinesByProductName(
                quoteId, input.productName
            );
            if (matches.size() > 1) {
                // Multi-match → disambiguation
                populateDisambiguation(out, matches);
                return null;
            }
            return (List<SObject>) matches;
        }

        // No targeting
        out.errorMessage = 'Specify which line(s) to update.';
        return null;
    }

    private static List<SObject> resolveLinesByIds(
        Id quoteId, List<String> rawIds, UpdateFieldsOutput out
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
            SELECT Id, Product2.Name, Quantity, UnitPrice, LineNumber,
                   ProductSellingModel.SellingModelType
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId AND Id IN :requested
            WITH USER_MODE
            ORDER BY LineNumber ASC
        ];
        if (lines.size() != requested.size()) {
            out.errorMessage = 'One or more of the selected lines do not belong to this quote.';
            return null;
        }
        return (List<SObject>) lines;
    }

    private static List<SObject> resolveLinesByOrdinals(
        Id quoteId, List<Integer> ordinals, String pendingSelectionJson, UpdateFieldsOutput out
    ) {
        Map<String, Object> ordinalMap = parsePendingSelection(pendingSelectionJson);
        List<String> idsToResolve = new List<String>();

        if (!ordinalMap.isEmpty()) {
            for (Integer ord : ordinals) {
                Object idVal = ordinalMap.get(String.valueOf(ord));
                if (idVal == null) {
                    out.errorMessage = 'Selection ' + ord
                        + ' was not in the list shown. Ask the user to pick from the displayed lines.';
                    return null;
                }
                idsToResolve.add(String.valueOf(idVal));
            }
            return resolveLinesByIds(quoteId, idsToResolve, out);
        }

        // Fallback: ordinals index into fresh candidate list
        List<QuoteLineItem> all = queryAllLines(quoteId);
        if (all.isEmpty()) {
            out.errorMessage = 'This quote has no lines to update.';
            return null;
        }
        List<SObject> chosen = new List<SObject>();
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
            SELECT Id, Product2.Name, Quantity, UnitPrice, LineNumber,
                   ProductSellingModel.SellingModelType
            FROM QuoteLineItem
            WHERE QuoteId = :quoteId
            WITH USER_MODE
            ORDER BY LineNumber ASC, Product2.Name ASC
            LIMIT 200
        ];
    }

    private static void populateDisambiguation(UpdateFieldsOutput out, List<QuoteLineItem> lines) {
        out.needsDisambiguation = true;
        List<String> display = new List<String>();
        display.add('Which line would you like to update? Pick a number.');
        Map<String, String> ordinalToId = new Map<String, String>();
        Integer ordinal = 1;
        for (QuoteLineItem qli : lines) {
            display.add(ordinal + '. ' + lineLabel(qli));
            ordinalToId.put(String.valueOf(ordinal), String.valueOf(qli.Id));
            ordinal++;
        }
        out.candidateQuoteLineSummariesDisplay = String.join(display, '\n');
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

    private static String recordLabel(String typeName, SObject rec) {
        if (typeName == 'QuoteLineItem') {
            QuoteLineItem qli = (QuoteLineItem) rec;
            String name = qli.Product2 != null && String.isNotBlank(qli.Product2.Name)
                ? qli.Product2.Name
                : 'Unnamed Product';
            return '**' + name + '** (Qty ' + formatQuantity(qli.Quantity) + ')';
        }
        if (typeName == 'Quote') {
            Quote q = (Quote) rec;
            String name = String.isNotBlank(q.Name) ? q.Name : 'Unnamed Quote';
            return '**' + name + '**';
        }
        return '**Record ' + rec.Id + '**';
    }

    private static String lineLabel(QuoteLineItem qli) {
        String name = qli.Product2 != null && String.isNotBlank(qli.Product2.Name)
            ? qli.Product2.Name
            : 'Unnamed Product';
        return '**' + name + '** (Qty ' + formatQuantity(qli.Quantity) + ')';
    }

    private static String summarizeChanges(SObject rec, Map<String, CoercedField> coercedFields) {
        List<String> parts = new List<String>();
        for (String fieldName : coercedFields.keySet()) {
            CoercedField cf = coercedFields.get(fieldName);
            Object newValue = rec.get(cf.field);
            parts.add(fieldName + '=' + (newValue == null ? '(cleared)' : String.valueOf(newValue)));
        }
        return String.join(parts, ', ');
    }

    private static String buildResultsDisplay(
        List<String> success, List<String> failed, List<String> skipped
    ) {
        List<String> parts = new List<String>();
        if (!success.isEmpty()) {
            parts.add('Updated:');
            Integer ordinal = 1;
            for (String line : success) {
                parts.add(ordinal + '. ' + line);
                ordinal++;
            }
        }
        if (skipped != null && !skipped.isEmpty()) {
            if (!parts.isEmpty()) {
                parts.add('');
            }
            parts.add('Skipped (dates do not apply to one-time products):');
            for (String line : skipped) {
                parts.add('- ' + line);
            }
        }
        if (!failed.isEmpty()) {
            parts.add('');
            parts.add('Could not update:');
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

    private static String summarizeErrors(List<Database.Error> errors) {
        if (errors == null || errors.isEmpty()) {
            return 'Update failed.';
        }
        List<String> msgs = new List<String>();
        for (Database.Error e : errors) {
            msgs.add(e.getMessage());
        }
        return String.join(msgs, '; ');
    }
}
