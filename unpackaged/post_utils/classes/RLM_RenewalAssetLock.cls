/**
 * Locks the root assets about to be renewed, so two renewal flows for the same
 * assets run one after the other instead of both passing their checks before
 * either quote exists.
 *
 * RLM_CreateQuoteFromRenewalOpp and RLM_ConsolidateRenewalOpportunities call this
 * just before RLM_RenewalPreflightChecks. The lock is held until the flow's
 * transaction ends, and both flows run Initiate Renewal in that same transaction
 * (CurrentTransaction), so a second run waits here until the first one's quote is
 * saved, and its checks then see that quote and stop. If the wait runs past the
 * platform's lock timeout the query throws and the flow shows its fault screen;
 * nothing has been renewed at that point.
 *
 * `without sharing`: it only locks the rows and returns nothing, and the flows
 * pass only root assets the user has already read.
 */
public without sharing class RLM_RenewalAssetLock {

    public class Request {
        @InvocableVariable(label='Asset Ids' required=true)
        public List<String> assetIds;
    }

    @InvocableMethod(label='Lock Renewal Assets' description='Locks the assets until the flow transaction ends, so concurrent renewals of them run one at a time.')
    public static void lockAssets(List<Request> requests) {
        Set<Id> assetIds = new Set<Id>();
        for (Request request : requests) {
            if (request.assetIds == null) {
                continue;
            }
            for (String assetId : request.assetIds) {
                if (String.isNotBlank(assetId)) {
                    assetIds.add(Id.valueOf(assetId));
                }
            }
        }
        if (assetIds.isEmpty()) {
            return;
        }
        List<Asset> locked = [SELECT Id FROM Asset WHERE Id IN :assetIds FOR UPDATE];
    }
}
