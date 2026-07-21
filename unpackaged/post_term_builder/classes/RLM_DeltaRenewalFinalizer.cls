/**
 * Flow-invocable back half of the Delta Term Builder renewal-from-contract path. After the orchestrating
 * flow (DL_InitiateRenewalFromContract) has run the standard initiateRenewal core action, this method
 * takes the minted renewal Quote and finishes it: re-stamps the negotiated line fidelity from the source
 * quote, renames to "&lt;source&gt; - Renewal", resets to Draft, nulls ContractId, sets the derived
 * EndDate, and reprices once through PST so the rep gets a validated renewal.
 *
 * MINTED-ID RESOLUTION: the flow passes initiateRenewal's renewRecordId as renewalQuoteId. We prefer the
 * proven account-scoped pre/post id-diff (preExistingQuoteIds vs. a fresh snapshot) for identification,
 * using the flow-bound id only to disambiguate when the diff finds more than one new quote, and as a
 * fallback when the diff finds none. This mirrors the original in-Apex logic that distrusted the flow's
 * bound id alone.
 *
 * The heavy lifting (restoreClonedLineFidelity, loadQuote, quoteIdsForAccount) lives in reusable
 * RLM_DeltaTermBuilderController helpers. Errors do NOT throw — the flow branches on Result.isSuccess.
 *
 * "with sharing" preserves the running rep's record access (unlike the ARC validator's "without sharing").
 */
public with sharing class RLM_DeltaRenewalFinalizer {

    @InvocableMethod(
        label='Finalize Term Builder Renewal'
        description='Identifies the minted renewal Quote, re-stamps negotiated discount/fare-code line fidelity from the source quote, renames + resets to Draft with ContractId null and the derived EndDate, and reprices via PST. Returns isSuccess=false with a message on failure (does not throw).'
    )
    public static List<Result> finalizeRenewal(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            results.add(finalizeOne(req));
        }
        return results;
    }

    private static Result finalizeOne(Request req) {
        Result res = new Result();
        try {
            if (req == null) {
                throw new RLM_DeltaTermBuilderController.TermBuilderException('Finalize request is required.');
            }
            if (req.sourceQuoteId == null) {
                throw new RLM_DeltaTermBuilderController.TermBuilderException('sourceQuoteId is required.');
            }
            if (String.isBlank(req.renewalName)) {
                throw new RLM_DeltaTermBuilderController.TermBuilderException('renewalName is required.');
            }
            if (req.scopeAccountId == null) {
                throw new RLM_DeltaTermBuilderController.TermBuilderException('scopeAccountId is required.');
            }

            Id renewalQuoteId = resolveMintedQuoteId(req);

            // initiateRenewal builds the full line structure + asset linkage but does NOT carry the
            // negotiated discount or DL_FareCodes__c. Re-stamp both from the source quote's own lines
            // using the same structural match the deep-clone path uses — the renewal quote is
            // structurally identical (same CustomProductName routes, same ParentQuoteLineItemId nesting).
            RLM_DeltaTermBuilderController.restoreClonedLineFidelity(req.sourceQuoteId, renewalQuoteId);

            // Rename to "<source> - Renewal", reset to Draft, and null ContractId so Term Builder treats
            // the renewal as a fresh negotiation (initiateRenewal stamps the originating ContractId). The
            // standard action populates the header StartDate but leaves EndDate null; complete it from the
            // derived window here (no extra DML — the header update is already happening).
            Quote renewal = RLM_DeltaTermBuilderController.loadQuote(renewalQuoteId);
            update as user new Quote(
                Id = renewalQuoteId, Name = req.renewalName, Status = 'Draft', ContractId = null,
                EndDate = req.endDate
            );
            Id accountId = (renewal.QuoteAccountId != null) ? renewal.QuoteAccountId : renewal.AccountId;

            // The re-stamp + rename above ran through direct DML, so the renewal carries a
            // TransactionIncomplete stamp. Reprice once through PST to hand the rep a validated renewal.
            RLM_DeltaPlaceSalesTransaction.revalidate(renewalQuoteId);

            res.isSuccess = true;
            res.renewalQuoteId = renewalQuoteId;
            res.accountId = accountId;
        } catch (Exception e) {
            res.isSuccess = false;
            res.errorMessage = e.getMessage();
        }
        return res;
    }

    /**
     * Identify the renewal quote the standard action minted. Prefer the account-scoped pre/post id-diff
     * (preExistingQuoteIds vs. a fresh snapshot) — the proven mechanism. Fall back to / disambiguate with
     * the flow's bound renewalQuoteId (parsed as a String → Id, because it flows from a Text core-action
     * output through a String flow variable).
     */
    private static Id resolveMintedQuoteId(Request req) {
        Set<Id> before = (req.preExistingQuoteIds != null)
            ? new Set<Id>(req.preExistingQuoteIds)
            : new Set<Id>();

        List<Id> added = new List<Id>();
        for (Id qId : RLM_DeltaTermBuilderController.quoteIdsForAccount(req.scopeAccountId)) {
            if (!before.contains(qId)) {
                added.add(qId);
            }
        }

        Id boundId = parseBoundId(req.renewalQuoteId);

        if (added.size() == 1) {
            return added[0];
        }
        if (added.size() > 1) {
            // >1 new quote under the account: disambiguate with the flow's bound renewRecordId.
            if (boundId != null) {
                for (Id qId : added) {
                    if (qId == boundId) {
                        return qId;
                    }
                }
            }
            throw new RLM_DeltaTermBuilderController.TermBuilderException(
                'Initiate renewal produced multiple new quotes; cannot identify the renewal.'
            );
        }

        // Diff found nothing (e.g. the snapshot already contained the minted id) → trust the flow-bound id.
        if (boundId != null) {
            return boundId;
        }
        throw new RLM_DeltaTermBuilderController.TermBuilderException(
            'Initiate renewal did not produce a new quote.'
        );
    }

    /** Parse the flow-bound renewal quote id (a String) into an Id, tolerating blank/invalid input. */
    private static Id parseBoundId(String raw) {
        if (String.isBlank(raw) || raw == 'null') {
            return null;
        }
        try {
            return Id.valueOf(raw.trim());
        } catch (Exception ignored) {
            return null;
        }
    }

    public class Request {
        @InvocableVariable(label='Minted Renewal Quote ID (from initiateRenewal)')
        public String renewalQuoteId;

        @InvocableVariable(label='Source Quote ID' required=true)
        public Id sourceQuoteId;

        @InvocableVariable(label='Renewal Name' required=true)
        public String renewalName;

        @InvocableVariable(label='Renewal End Date')
        public Date endDate;

        @InvocableVariable(label='Scope Account ID' required=true)
        public Id scopeAccountId;

        @InvocableVariable(label='Pre-Existing Quote IDs')
        public List<Id> preExistingQuoteIds;
    }

    public class Result {
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess = false;

        @InvocableVariable(label='Error Message')
        public String errorMessage;

        @InvocableVariable(label='Renewal Quote ID')
        public Id renewalQuoteId;

        @InvocableVariable(label='Account ID')
        public Id accountId;
    }
}
