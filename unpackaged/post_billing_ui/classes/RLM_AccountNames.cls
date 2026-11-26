/**
 * Account names for rows that carry an Account id, read in USER_MODE. A user who cannot read
 * Account (no object access) gets an empty result instead of an exception, so the caller keeps its
 * rows. Names are read here rather than through an Account.Name relationship in the caller's own
 * query, because a refused relationship read fails that whole query and drops the section with it.
 * The result's unavailable(Id) tells a name that could not be read from no account.
 */
public with sharing class RLM_AccountNames {
    public class Result {
        public Map<Id, String> names = new Map<Id, String>();
        // True when the Account read was refused or failed: a missing name is then not available, not "none".
        public Boolean unreadable = false;

        // Whether an account's name is not available to this user: the read was refused or failed, or the account
        // is missing from it. Account.Name is required, so an account that was asked for and is missing is one the
        // user cannot see (sharing), not one without a name. Null (no account) has no name to show.
        public Boolean unavailable(Id accountId) {
            return accountId != null && (unreadable || !names.containsKey(accountId));
        }
    }

    public static Result read(Set<Id> accountIds) {
        Result result = new Result();
        if (accountIds == null || accountIds.isEmpty()) return result;
        try {
            for (Account a : [SELECT Id, Name FROM Account WHERE Id IN :accountIds WITH USER_MODE]) {
                result.names.put(a.Id, a.Name);
            }
        } catch (QueryException e) {
            // Fixed behavior, no user text: the detail stays in the debug log.
            System.debug(LoggingLevel.WARN, 'RLM_AccountNames.read: ' + e.getMessage());
            result.unreadable = true;
        }
        return result;
    }
}
