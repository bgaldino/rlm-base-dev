/**
 * Asset-Based Ordering orchestrator.
 *
 * Drives Revenue Cloud's NATIVE asset-lifecycle actions through the standard
 * invocable action framework (Invocable.Action.createStandardAction). No asset
 * state, pricing, or assetization logic is re-implemented here - every mutation
 * is delegated to the platform actions the RLM_ARC_Assets flow also uses:
 *   - initiateAmendment   (Amend / Upgrade / Downgrade - all plain amendments;
 *                          up/down is driven by quantityChange + reconfig, not
 *                          an actionSubtype, which only supports
 *                          StartDateAdjustment / Rollback)
 *   - initiateRenewal
 *   - initiateCancellation
 *
 * Multi-contract consolidation into ONE output (Quote): the native actions
 * expose amendRecordId / renewRecordId / cancelRecordId as BOTH input and
 * output. The first invocation (no record id) creates the output record; each
 * subsequent invocation for another contract's assets passes that record id
 * back in, appending its changes onto the SAME record. See
 * .agents/artifacts/abo-endpoint-verification.md for the verified action
 * schemas.
 *
 * Test isolation: invoking standard actions requires live asset data, so tests
 * inject results through the @TestVisible mock seam (mirrors
 * RLM_RefundController). Behavioral changes here MUST be live-verified on an org
 * with seeded assets before merge (see the feature doc).
 */
public with sharing class RLM_AssetOrderingService {

    // Action-type tokens accepted from the LWC.
    public static final String ACTION_AMEND     = 'Amend';
    public static final String ACTION_UPGRADE   = 'Upgrade';
    public static final String ACTION_DOWNGRADE = 'Downgrade';
    public static final String ACTION_RENEW     = 'Renew';
    public static final String ACTION_CANCEL    = 'Cancel';

    private static final String STD_AMEND  = 'initiateAmendment';
    private static final String STD_RENEW  = 'initiateRenewal';
    private static final String STD_CANCEL = 'initiateCancellation';

    // ------------------------------------------------------------------
    // Request / response shapes
    // ------------------------------------------------------------------

    /** One consolidation batch: a single action applied across assets that may
     *  span multiple contracts, producing a single output record. */
    public class ConsolidationRequest {
        @AuraEnabled public String actionType;                  // Amend/Upgrade/Downgrade/Renew/Cancel
        @AuraEnabled public String outputType;                  // e.g. Quote (default)
        @AuraEnabled public Date effectiveDate;                 // start/effective date
        @AuraEnabled public Decimal quantityChange;            // amend only
        @AuraEnabled public Date renewalEndDate;               // renew only (optional)
        @AuraEnabled public Boolean skipPricing;
        /** Assets grouped by their owning contract. Key is the ContractId (or
         *  the literal 'none' for assets with no contract relationship). */
        @AuraEnabled public List<ContractAssetGroup> groups;
    }

    public class ContractAssetGroup {
        @AuraEnabled public Id contractId;   // null/none = no contract
        @AuraEnabled public List<Id> assetIds;
    }

    public class ConsolidationResult {
        @AuraEnabled public Boolean isSuccess;
        @AuraEnabled public Id outputRecordId;                 // the single consolidated Quote/Order
        @AuraEnabled public String outputType;
        @AuraEnabled public List<String> requestIdentifiers;
        @AuraEnabled public List<String> messages;

        public ConsolidationResult() {
            isSuccess = true;
            requestIdentifiers = new List<String>();
            messages = new List<String>();
        }
    }

    // ------------------------------------------------------------------
    // Public entry point
    // ------------------------------------------------------------------

    /**
     * Run one consolidation batch. Chains the native action across each
     * contract group, threading the output record id so all groups land on a
     * single output record.
     */
    public static ConsolidationResult runConsolidation(ConsolidationRequest req) {
        ConsolidationResult result = new ConsolidationResult();
        if (req == null || String.isBlank(req.actionType)) {
            result.isSuccess = false;
            result.messages.add('No action specified.');
            return result;
        }
        if (req.groups == null || req.groups.isEmpty()) {
            result.isSuccess = false;
            result.messages.add('Select at least one asset.');
            return result;
        }

        String outputType = String.isBlank(req.outputType) ? 'Quote' : req.outputType;
        result.outputType = outputType;

        Id runningRecordId = null;

        for (ContractAssetGroup grp : req.groups) {
            if (grp == null || grp.assetIds == null || grp.assetIds.isEmpty()) {
                continue;
            }
            ActionInvocation inv = buildInvocation(req, grp, outputType, runningRecordId);

            ActionOutcome outcome = invokeStandardAction(inv);

            if (!outcome.isSuccess) {
                result.isSuccess = false;
                result.messages.addAll(outcome.errors);
                // Stop chaining on first failure so a partial consolidation is
                // not silently produced.
                return result;
            }
            runningRecordId = outcome.outputRecordId;
            if (String.isNotBlank(outcome.requestIdentifier)) {
                result.requestIdentifiers.add(outcome.requestIdentifier);
            }
        }

        result.outputRecordId = runningRecordId;
        if (runningRecordId == null) {
            result.isSuccess = false;
            result.messages.add('No output record was produced by the lifecycle action.');
            return result;
        }

        // One-time products must not inherit the action's start/end dates. The
        // native actions stamp the selected date onto EVERY line the action
        // produces - including a one-time hardware item pulled in by bundle
        // expansion (e.g. a one-time chassis under a subscription bundle). Those
        // dates are meaningless for a one-time purchase, so strip them back off
        // the one-time lines after the output record is built. Best-effort: a
        // cleanup failure is surfaced as a message but does not fail the action,
        // since the consolidated record itself was created successfully.
        neutralizeOneTimeDates(runningRecordId, result);
        return result;
    }

    // ------------------------------------------------------------------
    // Shipment-gated re-anchoring (StartDateAdjustment)
    // ------------------------------------------------------------------

    /**
     * Re-anchor a bundle's subscription start to a new date via the native
     * StartDateAdjustment amendment. Used by shipment-gated billing: bundled
     * software is ordered future-dated (not-yet-started) so billing is deferred,
     * and on the shipment/serialization event the whole bundle is re-anchored to
     * the actual ship date - the customer then gets a full term measured from
     * delivery, and activation regenerates the billing schedule from that date.
     *
     * Live-verified platform rules this relies on (do not "optimize" away):
     *   - StartDateAdjustment only works on a NOT-YET-STARTED subscription
     *     (lifecycle start after today) - callers must gate on that.
     *   - Bundle components cannot be amended alone; pass the TOP-LEVEL (root)
     *     asset. The action cascades the new start to every line in the bundle.
     *   - It is rejected for usage-based / rampable products.
     *   - quantityChange is a required input even for a pure date move (pass 0).
     *
     * Produces a DRAFT Quote for the rep to review and activate (the native ABO
     * norm); the one-time hardware line pulled in by the cascade is date-stripped
     * by neutralizeOneTimeDates, same as every other console action.
     */
    public static ConsolidationResult reanchorStartDate(Id rootAssetId, Date newStart) {
        ConsolidationResult result = new ConsolidationResult();
        if (rootAssetId == null) {
            result.isSuccess = false;
            result.messages.add('No asset specified for start-date re-anchor.');
            return result;
        }
        if (newStart == null) {
            result.isSuccess = false;
            result.messages.add('No new start date specified for re-anchor.');
            return result;
        }

        ActionInvocation inv = new ActionInvocation();
        inv.standardActionName = STD_AMEND;
        inv.outputParamName = 'amendRecordId';
        inv.params.put('amendAssetIds', new List<String>{ String.valueOf(rootAssetId) });
        inv.params.put('amendStartDate', toStartOfDay(newStart));
        inv.params.put('actionSubtype', 'StartDateAdjustment');
        inv.params.put('quantityChange', 0);
        inv.params.put('amendOutputType', 'Quote');
        inv.params.put('skipPricing', false);

        ActionOutcome outcome = invokeStandardAction(inv);
        if (!outcome.isSuccess) {
            result.isSuccess = false;
            result.messages.addAll(outcome.errors);
            return result;
        }
        result.outputType = 'Quote';
        result.outputRecordId = outcome.outputRecordId;
        if (String.isNotBlank(outcome.requestIdentifier)) {
            result.requestIdentifiers.add(outcome.requestIdentifier);
        }
        if (result.outputRecordId == null) {
            result.isSuccess = false;
            result.messages.add('The start-date amendment produced no quote.');
            return result;
        }
        // Strip the cascade's dates off the one-time hardware line, same as the
        // console actions do.
        neutralizeOneTimeDates(result.outputRecordId, result);
        return result;
    }

    // ------------------------------------------------------------------
    // One-time date neutralization
    // ------------------------------------------------------------------

    /**
     * Clear the date fields on any one-time line of the produced output record.
     * Handles both output types: Quote lines (StartDate/EndDate) and Order lines
     * (ServiceDate/EndDate). Selling-model type is read via the line's
     * ProductSellingModel relationship.
     *
     * The read runs WITH USER_MODE (the user just created this record, so can
     * read it), but the corrective update runs in SYSTEM mode. This is a
     * platform-output normalization step, not a user-authored edit: the date is
     * stamped onto the one-time line by the native action, and QuoteLineItem
     * StartDate/EndDate FLS is not granted to standard RLM sales personas, so an
     * `as user` update would fail with a field-inaccessible DmlException. Running
     * it `as system` keeps the feature's permission set free of a broad
     * QuoteLineItem/OrderItem edit grant.
     */
    @TestVisible
    private static void neutralizeOneTimeDates(Id outputRecordId, ConsolidationResult result) {
        if (outputRecordId == null) return;
        try {
            String sobjName = outputRecordId.getSObjectType().getDescribe().getName();
            List<SObject> toUpdate = new List<SObject>();

            if (sobjName == 'Quote') {
                for (QuoteLineItem qli : [
                    SELECT Id, StartDate, EndDate
                    FROM QuoteLineItem
                    WHERE QuoteId = :outputRecordId
                      AND ProductSellingModel.SellingModelType = 'OneTime'
                      AND (StartDate != null OR EndDate != null)
                    WITH USER_MODE
                ]) {
                    qli.StartDate = null;
                    qli.EndDate = null;
                    toUpdate.add(qli);
                }
            } else if (sobjName == 'Order') {
                for (OrderItem oi : [
                    SELECT Id, ServiceDate, EndDate
                    FROM OrderItem
                    WHERE OrderId = :outputRecordId
                      AND ProductSellingModel.SellingModelType = 'OneTime'
                      AND (ServiceDate != null OR EndDate != null)
                    WITH USER_MODE
                ]) {
                    oi.ServiceDate = null;
                    oi.EndDate = null;
                    toUpdate.add(oi);
                }
            }

            if (!toUpdate.isEmpty()) {
                update as system toUpdate;
                result.messages.add(
                    'Cleared start/end dates on ' + toUpdate.size() +
                    ' one-time line(s) so hardware is not re-dated by the action.'
                );
            }
        } catch (Exception ex) {
            result.messages.add(
                'One-time date cleanup skipped: ' + ex.getTypeName() + ': ' + ex.getMessage()
            );
        }
    }

    // ------------------------------------------------------------------
    // Invocation building
    // ------------------------------------------------------------------

    /** Normalized description of one standard-action call. */
    public class ActionInvocation {
        public String standardActionName;
        public Map<String, Object> params = new Map<String, Object>();
        public String outputParamName;   // where the created record id is read back
    }

    private static ActionInvocation buildInvocation(
        ConsolidationRequest req,
        ContractAssetGroup grp,
        String outputType,
        Id existingRecordId
    ) {
        ActionInvocation inv = new ActionInvocation();
        // amendAssetIds / renewAssetIds / cancelAssetIds are declared as String[]
        // on the standard actions (live-verified: passing a scalar String yields
        // "Unexpected data type ... expected String[]"), so pass a List<String>.
        List<String> assetIdList = new List<String>();
        for (Id aid : grp.assetIds) {
            assetIdList.add(String.valueOf(aid));
        }
        // The *ContractId / *RecordId params are declared String on the standard
        // actions (live-verified) - pass String, not Id.
        String contractIdStr = (grp.contractId == null) ? null : String.valueOf(grp.contractId);
        String existingRecordIdStr = (existingRecordId == null) ? null : String.valueOf(existingRecordId);
        String effective = toStartOfDay(req.effectiveDate);
        Boolean skip = (req.skipPricing == true);

        String at = req.actionType;
        if (at == ACTION_AMEND || at == ACTION_UPGRADE || at == ACTION_DOWNGRADE) {
            inv.standardActionName = STD_AMEND;
            inv.outputParamName = 'amendRecordId';
            inv.params.put('amendAssetIds', assetIdList);
            inv.params.put('amendStartDate', effective);
            inv.params.put('quantityChange', req.quantityChange == null ? 0 : req.quantityChange);
            inv.params.put('amendOutputType', outputType);
            inv.params.put('skipPricing', skip);
            if (contractIdStr != null) inv.params.put('amendContractId', contractIdStr);
            if (existingRecordIdStr != null) inv.params.put('amendRecordId', existingRecordIdStr);
            // Upgrade/Downgrade are NOT distinct platform actions or actionSubtypes
            // (live-verified: initiateAmendment.actionSubtype only accepts
            // 'StartDateAdjustment' and 'Rollback'). They are ordinary amendments -
            // the up/down semantics come from the quantityChange sign and any
            // guided reconfiguration on the resulting quote. So all three route
            // through initiateAmendment without an actionSubtype.
        } else if (at == ACTION_RENEW) {
            inv.standardActionName = STD_RENEW;
            inv.outputParamName = 'renewRecordId';
            inv.params.put('renewAssetIds', assetIdList);
            inv.params.put('renewOutputType', outputType);
            inv.params.put('skipPricing', skip);
            if (req.effectiveDate != null)  inv.params.put('renewStartDate', effective);
            if (req.renewalEndDate != null) inv.params.put('renewEndDate', toStartOfDay(req.renewalEndDate));
            if (contractIdStr != null) inv.params.put('renewContractId', contractIdStr);
            if (existingRecordIdStr != null) inv.params.put('renewRecordId', existingRecordIdStr);
        } else if (at == ACTION_CANCEL) {
            inv.standardActionName = STD_CANCEL;
            inv.outputParamName = 'cancelRecordId';
            inv.params.put('cancelAssetIds', assetIdList);
            inv.params.put('cancelStartDate', effective);
            inv.params.put('cancelOutputType', outputType);
            inv.params.put('skipPricing', skip);
            if (contractIdStr != null) inv.params.put('cancelContractId', contractIdStr);
            if (existingRecordIdStr != null) inv.params.put('cancelRecordId', existingRecordIdStr);
        } else {
            throw new AssetOrderingException('Unsupported action type: ' + at);
        }
        return inv;
    }

    // ------------------------------------------------------------------
    // Standard-action invocation (with test seam)
    // ------------------------------------------------------------------

    public class ActionOutcome {
        public Boolean isSuccess = true;
        public Id outputRecordId;
        public String requestIdentifier;
        public List<String> errors = new List<String>();
    }

    /** Injected in tests to avoid invoking live platform actions. */
    @TestVisible
    private static ActionOutcome mockOutcome;

    private static ActionOutcome invokeStandardAction(ActionInvocation inv) {
        if (Test.isRunningTest()) {
            if (mockOutcome != null) return mockOutcome;
            // Deterministic default so tests exercise the chaining path.
            ActionOutcome deflt = new ActionOutcome();
            deflt.outputRecordId = null;
            deflt.isSuccess = false;
            deflt.errors.add('No mockOutcome set for ' + inv.standardActionName);
            return deflt;
        }

        ActionOutcome outcome = new ActionOutcome();
        try {
            Invocable.Action action =
                Invocable.Action.createStandardAction(inv.standardActionName);
            for (String key : inv.params.keySet()) {
                action.setInvocationParameter(key, inv.params.get(key));
            }
            List<Invocable.Action.Result> results = action.invoke();
            if (results == null || results.isEmpty()) {
                outcome.isSuccess = false;
                outcome.errors.add(inv.standardActionName + ' returned no result.');
                return outcome;
            }
            Invocable.Action.Result r = results[0];
            if (!r.isSuccess()) {
                outcome.isSuccess = false;
                for (Invocable.Action.Error e : r.getErrors()) {
                    outcome.errors.add(e.getMessage());
                }
                if (outcome.errors.isEmpty()) {
                    outcome.errors.add(inv.standardActionName + ' failed.');
                }
                return outcome;
            }
            Map<String, Object> out = r.getOutputParameters();
            Object recId = (out == null) ? null : out.get(inv.outputParamName);
            if (recId != null) {
                outcome.outputRecordId = Id.valueOf(String.valueOf(recId));
            }
            Object reqId = (out == null) ? null : out.get('requestIdentifier');
            if (reqId != null) {
                outcome.requestIdentifier = String.valueOf(reqId);
            }
        } catch (Exception ex) {
            outcome.isSuccess = false;
            outcome.errors.add(ex.getTypeName() + ': ' + ex.getMessage());
        }
        return outcome;
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    // The standard actions require the date params as a String in
    // yyyy-MM-dd'T'HH:mm:ss format (live-verified), not a Datetime object.
    private static String toStartOfDay(Date d) {
        Date eff = (d == null) ? Date.today() : d;
        Datetime dt = Datetime.newInstance(eff, Time.newInstance(0, 0, 0, 0));
        return dt.format('yyyy-MM-dd\'T\'HH:mm:ss');
    }

    public class AssetOrderingException extends Exception {}
}
