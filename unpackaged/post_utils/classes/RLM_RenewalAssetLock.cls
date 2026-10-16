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
 * platform's lock timeout the query throws, and if any asset can't be locked (deleted,
 * or no longer visible to the user) this throws; either way the flow shows its fault
 * screen before anything is renewed.
 *
 * `with sharing` and WITH USER_MODE: the flows pass only root assets the user has
 * already read, so the lock needs no wider access than that. RLM_RenewalQuotes
 * grants Asset read along with access to this class.
 */
public with sharing class RLM_RenewalAssetLock {

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
        List<Asset> locked = [SELECT Id FROM Asset WHERE Id IN :assetIds WITH USER_MODE FOR UPDATE];
        // A user-mode query returns only the assets the user can still see, so a
        // short result would leave the rest unlocked: fail instead, before anything
        // is renewed.
        if (locked.size() != assetIds.size()) {
            throw new LockException(
                'Only ' + locked.size() + ' of the ' + assetIds.size()
                + ' assets to renew could be locked. One may have been deleted or is no longer shared with you.'
            );
        }
    }

    public class LockException extends Exception {}
}
