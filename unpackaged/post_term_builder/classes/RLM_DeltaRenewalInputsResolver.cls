/**
 * Flow-invocable front half of the Delta Term Builder renewal-from-contract path. Given a Contract id
 * (and optional caller-supplied dates), it loads and validates the Contract + its source Quote, resolves
 * the Contract's top-level renewable Assets, derives the renewal date window, builds the renewal name,
 * and snapshots the account's current quote ids — everything the orchestrating flow
 * (DL_InitiateRenewalFromContract) needs to run the standard initiateRenewal core action and then hand
 * off to RLM_DeltaRenewalFinalizer. No DML: this is a pure read + derive step.
 *
 * The heavy lifting lives in reusable RLM_DeltaTermBuilderController helpers (topLevelParentAssetIds,
 * deriveRenewalWindow, buildRenewalName, quoteIdsForAccount) — this class only orchestrates them and
 * shapes the result for the flow.
 *
 * ERROR MODEL: validation failures do NOT throw. The flow branches on Result.isSuccess and surfaces
 * Result.errorMessage, so a bad contract/source-quote/asset state returns isSuccess=false with the exact
 * same user-facing message the original @AuraEnabled method produced (assertions depend on these strings).
 *
 * "with sharing" preserves the running rep's record access (unlike the ARC validator's "without sharing").
 */
public with sharing class RLM_DeltaRenewalInputsResolver {

    @InvocableMethod(
        label='Resolve Term Builder Renewal Inputs'
        description='Loads and validates a Contract + its source Quote, resolves the top-level renewable assets, derives the renewal date window and name, and snapshots the account quote ids for the renewal flow. Returns isSuccess=false with a message on any validation failure (does not throw).'
    )
    public static List<Result> resolve(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            results.add(resolveOne(req));
        }
        return results;
    }

    private static Result resolveOne(Request req) {
        Result res = new Result();
        try {
            if (req == null || req.contractId == null) {
                throw new RLM_DeltaTermBuilderController.TermBuilderException('contractId is required.');
            }

            List<Contract> contracts = [
                SELECT Id, SourceQuoteId, AccountId, RenewalTerm2, RenewalTermUnit
                FROM Contract WHERE Id = :req.contractId WITH USER_MODE LIMIT 1
            ];
            if (contracts.isEmpty()) {
                throw new RLM_DeltaTermBuilderController.TermBuilderException('Contract not found or not accessible.');
            }
            Contract contract = contracts[0];
            Id sourceQuoteId = contract.SourceQuoteId;
            if (sourceQuoteId == null) {
                throw new RLM_DeltaTermBuilderController.TermBuilderException('This contract has no source quote to renew from.');
            }

            // Source quote → name + account scope for the post-renewal id-diff and the discount/fare
            // re-stamp (the source lines are the faithful record of the negotiated discount + codes).
            List<Quote> sources = [
                SELECT Id, Name, QuoteNumber, AccountId, QuoteAccountId
                FROM Quote WHERE Id = :sourceQuoteId WITH USER_MODE LIMIT 1
            ];
            if (sources.isEmpty()) {
                throw new RLM_DeltaTermBuilderController.TermBuilderException('Source quote not found or not accessible.');
            }
            Quote source = sources[0];
            Id scopeAccountId = (source.QuoteAccountId != null)
                ? source.QuoteAccountId
                : (source.AccountId != null ? source.AccountId : contract.AccountId);
            String sourceName = String.isNotBlank(source.Name)
                ? source.Name
                : (String.isNotBlank(source.QuoteNumber) ? source.QuoteNumber : 'Negotiation');
            String renewalName = RLM_DeltaTermBuilderController.buildRenewalName(sourceName);

            // Resolve the Contract's renewable Term-parent Assets (the renewal expands the child fares
            // automatically, so only the parents are passed). No assets → the contract isn't assetized.
            List<String> renewAssetIds = RLM_DeltaTermBuilderController.topLevelParentAssetIds(req.contractId);
            if (renewAssetIds.isEmpty()) {
                throw new RLM_DeltaTermBuilderController.TermBuilderException(
                    'This contract has no renewable assets. Assetize the contract '
                    + '(activate → order → activate → O2A) before renewing.'
                );
            }

            return buildResolvedResult(req, contract, sourceQuoteId, scopeAccountId, renewalName, renewAssetIds);
        } catch (Exception e) {
            res.isSuccess = false;
            res.errorMessage = e.getMessage();
        }
        return res;
    }

    /**
     * Assemble the success Result once the renewable assets are known: derive the date window and snapshot
     * the account's quote ids. Split out from resolveOne so it is unit-testable with real (lifecycle-managed)
     * Assets — the ACR link that topLevelParentAssetIds reads from can't be created synthetically (inserting
     * an AssetContractRelationship fires standard RLM asset-lifecycle automation that throws an uncatchable
     * platform error outside the O2A flow), so a test drives this method directly with the resolved ids and
     * exercises the real deriveRenewalWindow / quoteIdsForAccount logic. The end-to-end ACR resolution is
     * covered by the mandatory live walkthrough (§Verification).
     */
    @TestVisible
    private static Result buildResolvedResult(
        Request req, Contract contract, Id sourceQuoteId, Id scopeAccountId,
        String renewalName, List<String> renewAssetIds
    ) {
        // The standard action, given null dates, mis-derives the renewal term — a 12-MONTH source asset
        // yields a 12-YEAR renewal. Feed it explicit dates (first-class initiateRenewal inputs): start the
        // day after the prior term ends, run for the Contract's own RenewalTerm2/Unit. A caller-supplied
        // date always wins.
        RLM_DeltaTermBuilderController.RenewalWindow window =
            RLM_DeltaTermBuilderController.deriveRenewalWindow(
                renewAssetIds, contract, req.renewStartDate, req.renewEndDate
            );

        Result res = new Result();
        res.isSuccess = true;
        res.renewAssetIds = renewAssetIds;
        res.renewStartDate = window.startDate;
        res.renewEndDate = window.endDate;
        res.sourceQuoteId = sourceQuoteId;
        res.scopeAccountId = scopeAccountId;
        res.renewalName = renewalName;
        res.preExistingQuoteIds = new List<Id>(
            RLM_DeltaTermBuilderController.quoteIdsForAccount(scopeAccountId)
        );
        return res;
    }

    public class Request {
        @InvocableVariable(label='Contract ID' required=true)
        public Id contractId;

        @InvocableVariable(label='Renewal Start Date (optional)')
        public Date renewStartDate;

        @InvocableVariable(label='Renewal End Date (optional)')
        public Date renewEndDate;
    }

    public class Result {
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess = false;

        @InvocableVariable(label='Error Message')
        public String errorMessage;

        @InvocableVariable(label='Renewable Asset IDs')
        public List<String> renewAssetIds;

        @InvocableVariable(label='Renewal Start Date')
        public Date renewStartDate;

        @InvocableVariable(label='Renewal End Date')
        public Date renewEndDate;

        @InvocableVariable(label='Source Quote ID')
        public Id sourceQuoteId;

        @InvocableVariable(label='Scope Account ID')
        public Id scopeAccountId;

        @InvocableVariable(label='Renewal Name')
        public String renewalName;

        @InvocableVariable(label='Pre-Existing Quote IDs')
        public List<Id> preExistingQuoteIds;
    }
}
