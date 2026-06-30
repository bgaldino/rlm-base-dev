/**
 * Invocable service that saves product attribute selections and triggers full
 * Revenue Cloud configuration and pricing via the Place Sales Transaction (PST)
 * Apex API (RevSalesTrxn.PlaceSalesTransactionExecutor).
 *
 * PST with ConfigurationExecutionEnum.SYSTEM runs the complete bundle configurator
 * ("Configure for Quote with root product") which:
 *   - Saves the QuoteLineItemAttribute values
 *   - Re-evaluates all BOM/bundle rules (adds/removes child products)
 *   - Re-runs the full pricing procedure
 *
 * TWO-STEP PST SEQUENCING
 * -----------------------
 * When both Number and Picklist attributes are submitted together in a single PST
 * call, the BOM configurator evaluates them atomically. For certain duty-rating +
 * kW combinations (e.g. DCC + 1500 kW), the Picklist rule evaluates the existing
 * BOM component and derives the Number attribute from it, silently overriding the
 * submitted value. Submitting Number attributes FIRST (in an isolated PST call)
 * lets the BOM resolver freely upgrade the component (e.g. FESBA_900 → FESBA_1500).
 * The Picklist attributes are then submitted in a SECOND PST call, which applies
 * duty-rating-specific BOM refinements on top of the already-resolved component.
 *
 * POST-SAVE READBACK
 * ------------------
 * savedAttributesJson is built from an actual DB query after both PST calls
 * complete, not from the input map. This ensures the agent and confirmation email
 * reflect what was truly persisted.
 */
public with sharing class RLM_AI_ProductAttributeSaveService {

    // ── Input / Output ──────────────────────────────────────────────────────

    public class SaveInput {
        @InvocableVariable(required=true label='Quote Id')
        public String quoteId;

        @InvocableVariable(required=true label='Quote Line Item Id')
        public String quoteLineItemId;

        @InvocableVariable(required=true label='Attribute Selections JSON'
            description='JSON object: keys = attribute developerName, values = selected value.')
        public String attributeSelectionsJson;
    }

    public class SaveOutput {
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;

        @InvocableVariable(label='Is Valid')
        public Boolean isValid;

        @InvocableVariable(label='Saved Attributes JSON')
        public String savedAttributesJson;

        @InvocableVariable(label='Validation Errors JSON')
        public String validationErrorsJson;

        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    // ── Invocable entry point ───────────────────────────────────────────────

    @InvocableMethod(
        label='Save Product Attribute Selections'
        description='Saves attribute values and triggers full bundle configuration and pricing via the Place Sales Transaction API.'
        category='Product Configuration'
    )
    public static List<SaveOutput> saveAttributeSelections(List<SaveInput> inputs) {
        List<SaveOutput> results = new List<SaveOutput>();
        if (inputs == null || inputs.isEmpty()) {
            return results;
        }
        for (SaveInput input : inputs) {
            results.add(doSave(input));
        }
        return results;
    }

    // ── Core save logic ─────────────────────────────────────────────────────

    private static SaveOutput doSave(SaveInput input) {
        SaveOutput out = new SaveOutput();
        try {
            if (input == null) {
                return fail(out, 'Select a quote and quote line item before saving product configuration.');
            }
            Map<String, Object> selections =
                RLM_AI_ConfigServiceUtils.safeDeserializeMap(input.attributeSelectionsJson);

            Id quoteId = RLM_AI_ConfigServiceUtils.toIdOrNull(input.quoteId);
            if (quoteId == null || !String.valueOf(quoteId).startsWith(RLM_AI_ConfigServiceUtils.QUOTE_PREFIX)) {
                return fail(out, 'Select a valid quote before saving product configuration.');
            }
            Id quoteLineItemId = RLM_AI_ConfigServiceUtils.toIdOrNull(input.quoteLineItemId);
            if (quoteLineItemId == null || !String.valueOf(quoteLineItemId).startsWith(RLM_AI_ConfigServiceUtils.QUOTE_LINE_ITEM_PREFIX)) {
                return fail(out, 'Select a valid quote line item before saving product configuration.');
            }
            if (!quoteLineItemBelongsToQuote(quoteLineItemId, quoteId)) {
                return fail(out, 'Select a quote line item that belongs to the current quote before saving product configuration.');
            }

            // ── Step 1: Load existing attributes with definition type + picklist ──
            Map<String, QuoteLineItemAttribute> existingByDevName =
                new Map<String, QuoteLineItemAttribute>();
            Set<Id> picklistIds = new Set<Id>();

            for (QuoteLineItemAttribute qlia : [
                SELECT Id,
                       AttributeDefinition.DeveloperName,
                       AttributeDefinition.DataType,
                       AttributeDefinition.PicklistId
                FROM   QuoteLineItemAttribute
                WHERE  QuoteLineItemId = :quoteLineItemId
            ]) {
                String devName = qlia.AttributeDefinition?.DeveloperName;
                if (devName == null) continue;
                existingByDevName.put(devName, qlia);
                if (qlia.AttributeDefinition.DataType == 'Picklist'
                        && qlia.AttributeDefinition.PicklistId != null) {
                    picklistIds.add(qlia.AttributeDefinition.PicklistId);
                }
            }

            // ── Step 2: Build value → Id map for all relevant picklists ──────────
            Map<Id, Map<String, Id>> pvByPicklist = new Map<Id, Map<String, Id>>();
            if (!picklistIds.isEmpty()) {
                for (AttributePicklistValue apv : [
                    SELECT Id, Name, Value, PicklistId
                    FROM   AttributePicklistValue
                    WHERE  PicklistId IN :picklistIds
                ]) {
                    if (!pvByPicklist.containsKey(apv.PicklistId)) {
                        pvByPicklist.put(apv.PicklistId, new Map<String, Id>());
                    }
                    pvByPicklist.get(apv.PicklistId).put(apv.Value, apv.Id);
                    if (String.isNotBlank(apv.Name) && apv.Name != apv.Value
                        && !pvByPicklist.get(apv.PicklistId).containsKey(apv.Name)) {
                        pvByPicklist.get(apv.PicklistId).put(apv.Name, apv.Id);
                    }
                }
            }

            // ── Step 3: Split selections into Number-type vs Picklist-type ────────
            //
            // Number attributes drive BOM component selection (e.g. requiredKW
            // determines which FESBA unit is used). Picklist attributes (e.g.
            // DutyRating) apply duty-rating-specific BOM refinements. Submitting
            // both types in one PST call causes the Picklist rule to derive the
            // Number attribute from the existing BOM component rather than honoring
            // the submitted value. Sequencing: Number PST first, Picklist PST second.

            Map<String, Object> numberSelections   = new Map<String, Object>();
            Map<String, Object> picklistSelections = new Map<String, Object>();

            for (String devName : selections.keySet()) {
                if (!existingByDevName.containsKey(devName)) continue;
                QuoteLineItemAttribute qlia = existingByDevName.get(devName);
                if (qlia.AttributeDefinition.DataType == 'Picklist') {
                    picklistSelections.put(devName, selections.get(devName));
                } else {
                    numberSelections.put(devName, selections.get(devName));
                }
            }

            // ── Step 4: PST call 1 — Number attributes ───────────────────────────
            if (!numberSelections.isEmpty()) {
                SaveOutput numResult = executePst(
                    String.valueOf(quoteId), String.valueOf(quoteLineItemId),
                    numberSelections, existingByDevName, pvByPicklist);
                if (!numResult.isSuccess) return numResult;
            }

            // ── Step 5: PST call 2 — Picklist attributes ─────────────────────────
            if (!picklistSelections.isEmpty()) {
                SaveOutput plResult = executePst(
                    String.valueOf(quoteId), String.valueOf(quoteLineItemId),
                    picklistSelections, existingByDevName, pvByPicklist);
                if (!plResult.isSuccess) return plResult;
            }

            if (numberSelections.isEmpty() && picklistSelections.isEmpty()) {
                // No matching attributes found in existingByDevName
                out.isSuccess            = true;
                out.isValid              = true;
                out.savedAttributesJson  = JSON.serialize(selections);
                out.validationErrorsJson = '[]';
                return out;
            }

            // ── Step 6: Post-save readback — reflect actual DB state ──────────────
            //
            // Build savedAttributesJson from the database after both PST calls
            // complete. This ensures the agent and confirmation email accurately
            // report what was persisted rather than echoing back the input.

            Set<String> submittedDevNames = selections.keySet();
            Map<String, String> actualValues = new Map<String, String>();
            for (QuoteLineItemAttribute qlia : [
                SELECT AttributeDefinition.DeveloperName, AttributeValue
                FROM   QuoteLineItemAttribute
                WHERE  QuoteLineItemId = :quoteLineItemId
                AND    AttributeDefinition.DeveloperName IN :submittedDevNames
            ]) {
                actualValues.put(qlia.AttributeDefinition.DeveloperName, qlia.AttributeValue);
            }

            out.isSuccess            = true;
            out.isValid              = true;
            out.savedAttributesJson  = JSON.serialize(actualValues);
            out.validationErrorsJson = '[]';

        } catch (Exception e) {
            out.isSuccess    = false;
            out.isValid      = false;
            out.errorMessage = e.getMessage();
        }
        return out;
    }

    private static SaveOutput fail(SaveOutput out, String message) {
        out.isSuccess = false;
        out.isValid = false;
        out.validationErrorsJson = '[]';
        out.errorMessage = message;
        return out;
    }

    private static Boolean quoteLineItemBelongsToQuote(Id quoteLineItemId, Id quoteId) {
        return [
            SELECT COUNT()
            FROM QuoteLineItem
            WHERE Id = :quoteLineItemId
              AND QuoteId = :quoteId
        ] == 1;
    }

    // ── Helper: execute a single PST graph for the given attribute subset ───

    private static SaveOutput executePst(
            String quoteId,
            String quoteLineItemId,
            Map<String, Object> attrSelections,
            Map<String, QuoteLineItemAttribute> existingByDevName,
            Map<Id, Map<String, Id>> pvByPicklist) {

        SaveOutput out = new SaveOutput();

        List<RevSalesTrxn.RecordWithReferenceRequest> graphNodes =
            new List<RevSalesTrxn.RecordWithReferenceRequest>();

        RevSalesTrxn.RecordResource quoteNode =
            new RevSalesTrxn.RecordResource(Quote.getSobjectType(), 'PATCH', quoteId);
        graphNodes.add(new RevSalesTrxn.RecordWithReferenceRequest('refQuote', quoteNode));

        Integer nodeIdx = 0;
        for (String devName : attrSelections.keySet()) {
            if (!existingByDevName.containsKey(devName)) continue;
            QuoteLineItemAttribute qlia = existingByDevName.get(devName);
            String newVal = attrSelections.get(devName) != null
                ? String.valueOf(attrSelections.get(devName)) : '';

            RevSalesTrxn.RecordResource qliaNode =
                new RevSalesTrxn.RecordResource(
                    QuoteLineItemAttribute.getSobjectType(), 'PATCH', qlia.Id);

            Map<String, Object> fields = new Map<String, Object>{
                'AttributeValue' => newVal
            };

            if (qlia.AttributeDefinition.DataType == 'Picklist') {
                Map<String, Id> pvMap =
                    pvByPicklist.get(qlia.AttributeDefinition.PicklistId);
                if (pvMap != null && pvMap.containsKey(newVal)) {
                    fields.put('AttributePicklistValueId', pvMap.get(newVal));
                }
            }
            qliaNode.fieldValues = fields;

            graphNodes.add(new RevSalesTrxn.RecordWithReferenceRequest(
                'refQlia' + nodeIdx++, qliaNode));
        }

        if (graphNodes.size() <= 1) {
            out.isSuccess            = true;
            out.isValid              = true;
            out.savedAttributesJson  = JSON.serialize(attrSelections);
            out.validationErrorsJson = '[]';
            return out;
        }

        RevSalesTrxn.GraphRequest graph =
            new RevSalesTrxn.GraphRequest('configureAndPrice', graphNodes);

        RevSalesTrxn.PlaceSalesTransactionResponse resp =
            RevSalesTrxn.PlaceSalesTransactionExecutor.execute(
                graph,
                RevSalesTrxn.PricingPreferenceEnum.SYSTEM,
                RevSalesTrxn.ConfigurationExecutionEnum.SYSTEM,
                new RevSalesTrxn.ConfigurationOptionsInput(),
                null
            );

        if (!resp.isSuccess) {
            List<String> errs = new List<String>();
            for (Object e : resp.errorResponse) {
                errs.add(JSON.serialize(e));
            }
            out.isSuccess    = false;
            out.isValid      = false;
            out.errorMessage = String.join(errs, '; ');
            return out;
        }

        out.isSuccess = true;
        out.isValid   = true;
        return out;
    }
}
