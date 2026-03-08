public class RLM_Utils_AccountCrmDeleter {

    public static void deleteQuotes(String accountId) {
        Id acctId = accountId;
        List<Quote> toDelete = [SELECT Id FROM Quote WHERE QuoteAccountId = :acctId];
        if (!toDelete.isEmpty()) {
            Database.delete(toDelete, false);
        }
    }

    public static void deleteOpportunities(String accountId) {
        Id acctId = accountId;
        List<Opportunity> toDelete = [SELECT Id FROM Opportunity WHERE AccountId = :acctId];
        if (!toDelete.isEmpty()) {
            Database.delete(toDelete, false);
        }
    }
}
