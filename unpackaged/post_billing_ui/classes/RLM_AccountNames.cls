/**
 * Account names for rows that carry an Account id, read in USER_MODE. A user who cannot read
 * Account (no object access) gets an empty map instead of an exception, so the caller keeps its
 * rows and shows them without a name (callers default the blank to a dash or blank). Names are
 * read here rather than through an Account.Name relationship in the caller's own query, because a
 * refused relationship read fails that whole query and drops the section with it.
 */
public with sharing class RLM_AccountNames {
    public static Map<Id, String> forIds(Set<Id> accountIds) {
        Map<Id, String> names = new Map<Id, String>();
        if (accountIds == null || accountIds.isEmpty()) return names;
        try {
            for (Account a : [SELECT Id, Name FROM Account WHERE Id IN :accountIds WITH USER_MODE]) {
                names.put(a.Id, a.Name);
            }
        } catch (QueryException e) {
            // Fixed behavior, no user text: the detail stays in the debug log.
            System.debug(LoggingLevel.WARN, 'RLM_AccountNames.forIds: ' + e.getMessage());
        }
        return names;
    }
}
