/**
 * Asset-Based Ordering orchestrator.
 *
 * Drives Revenue Cloud's NATIVE asset-lifecycle actions through the standard
 * invocable action framework (Invocable.Action.createStandardAction). No asset
 * state, pricing, or assetization logic is re-implemented here - every mutation
 * is delegated to the platform actions the RLM_ARC_Assets flow also uses:
 *   - initiateAmendment   (Amend / Upgrade / Downgrade via actionSubtype)
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
        }
        return result;
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
        // amendAssetIds / renewAssetIds / cancelAssetIds are declared STRING on
        // the standard actions; multiple ids are passed comma-delimited.
        String assetIdCsv = String.join(new List<Id>(grp.assetIds), ',');
        Datetime effective = toStartOfDay(req.effectiveDate);
        Boolean skip = (req.skipPricing == true);

        String at = req.actionType;
        if (at == ACTION_AMEND || at == ACTION_UPGRADE || at == ACTION_DOWNGRADE) {
            inv.standardActionName = STD_AMEND;
            inv.outputParamName = 'amendRecordId';
            inv.params.put('amendAssetIds', assetIdCsv);
            inv.params.put('amendStartDate', effective);
            inv.params.put('quantityChange', req.quantityChange == null ? 0 : req.quantityChange);
            inv.params.put('amendOutputType', outputType);
            inv.params.put('skipPricing', skip);
            if (grp.contractId != null) inv.params.put('amendContractId', grp.contractId);
            if (existingRecordId != null) inv.params.put('amendRecordId', existingRecordId);
            // Upgrade/Downgrade are amendment subtypes (no separate std action
            // exists). Subtype values are live-verified in Phase 1.
            if (at == ACTION_UPGRADE)   inv.params.put('actionSubtype', 'Upgrade');
            if (at == ACTION_DOWNGRADE) inv.params.put('actionSubtype', 'Downgrade');
        } else if (at == ACTION_RENEW) {
            inv.standardActionName = STD_RENEW;
            inv.outputParamName = 'renewRecordId';
            inv.params.put('renewAssetIds', assetIdCsv);
            inv.params.put('renewOutputType', outputType);
            inv.params.put('skipPricing', skip);
            if (req.effectiveDate != null)  inv.params.put('renewStartDate', effective);
            if (req.renewalEndDate != null) inv.params.put('renewEndDate', toStartOfDay(req.renewalEndDate));
            if (grp.contractId != null) inv.params.put('renewContractId', grp.contractId);
            if (existingRecordId != null) inv.params.put('renewRecordId', existingRecordId);
        } else if (at == ACTION_CANCEL) {
            inv.standardActionName = STD_CANCEL;
            inv.outputParamName = 'cancelRecordId';
            inv.params.put('cancelAssetIds', assetIdCsv);
            inv.params.put('cancelStartDate', effective);
            inv.params.put('cancelOutputType', outputType);
            inv.params.put('skipPricing', skip);
            if (grp.contractId != null) inv.params.put('cancelContractId', grp.contractId);
            if (existingRecordId != null) inv.params.put('cancelRecordId', existingRecordId);
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

    private static Datetime toStartOfDay(Date d) {
        Date eff = (d == null) ? Date.today() : d;
        return Datetime.newInstance(eff, Time.newInstance(0, 0, 0, 0));
    }

    public class AssetOrderingException extends Exception {}
}
