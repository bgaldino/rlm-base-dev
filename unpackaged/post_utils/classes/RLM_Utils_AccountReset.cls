/**
 * RLM_Utils_AccountReset
 *
 * Orchestrator that deletes all related objects for an account in dependency order.
 * Invoked via the Account.RLM_ResetAccount Quick Action (screen flow).
 *
 * Deletion is delegated to six helper classes:
 *   RLM_Utils_AccountUsageDeleter   — usage summaries, TUE, UEA, UEB
 *   RLM_Utils_AccountBindingDeleter — BindingObjUsageRsrcPlcy, BindingObjectRateCardEntry, AssetRateCardEntry
 *   RLM_Utils_AccountAssetDeleter   — assets and their restrict-delete children
 *   RLM_Utils_AccountOrderDeleter   — orders, order items, fulfillment objects
 *   RLM_Utils_AccountBillingDeleter — invoices, billing schedule groups, contracts
 *   RLM_Utils_AccountCrmDeleter     — quotes, opportunities
 *
 * @author John Rozsits, Brian Galdino, Anthropic Claude
 * @date 2025-06-10
 */
public class RLM_Utils_AccountReset {

    public class InputVariables {
        @InvocableVariable(required=true)
        public String accountId;

        @InvocableVariable(required=true)
        public Boolean DeleteAssets;

        @InvocableVariable(required=true)
        public Boolean DeleteFulfillment;

        @InvocableVariable(required=true)
        public Boolean DeleteBilling;

        @InvocableVariable(required=false)
        public Boolean DeleteOrders;

        @InvocableVariable(required=false)
        public Boolean DeleteContracts;

        @InvocableVariable(required=false)
        public Boolean DeleteOpportunities;

        @InvocableVariable(required=false)
        public Boolean DeleteQuotes;
    }

    @InvocableMethod(label='Reset Account Related Objects' description='Deletes all related objects for an account in the correct order')
    public static void delAccountRelatedObjects(List<InputVariables> request) {
        if (request == null || request.isEmpty()) return;

        InputVariables vars = request.get(0);
        String accountId       = vars.accountId;
        Boolean deleteAssets   = vars.DeleteAssets;
        Boolean deleteFulfill  = vars.DeleteFulfillment;
        Boolean deleteBilling  = vars.DeleteBilling;
        Boolean deleteOrders   = vars.DeleteOrders != null ? vars.DeleteOrders : true;
        Boolean deleteContracts = vars.DeleteContracts != null ? vars.DeleteContracts : true;
        Boolean deleteOpps     = vars.DeleteOpportunities != null ? vars.DeleteOpportunities : true;
        Boolean deleteQuotes   = vars.DeleteQuotes != null ? vars.DeleteQuotes : true;

        Savepoint sp = Database.setSavepoint();
        try {
            // 1. Usage summaries FIRST (UAG→UBPI→UEB restrict-delete chain)
            RLM_Utils_AccountUsageDeleter.deleteAllSummaries(accountId);

            // 2. Entitlements: UEB bottom-up, then TUE, then UEA
            RLM_Utils_AccountUsageDeleter.deleteEntitlements(accountId);

            // 3. Binding objects + asset rate card entries
            RLM_Utils_AccountBindingDeleter.deleteAll(accountId);

            // 4. Transaction journals (restrict on Asset)
            RLM_Utils_AccountUsageDeleter.deleteTransactionJournals(accountId);

            // 5. Billing schedule groups (always)
            RLM_Utils_AccountBillingDeleter.deleteBillingScheduleGroups(accountId);

            // 6. Invoices (conditional)
            if (deleteBilling) {
                RLM_Utils_AccountBillingDeleter.deleteInvoices(accountId);
            }

            // 7. Fulfillment (conditional — before orders)
            if (deleteFulfill) {
                RLM_Utils_AccountOrderDeleter.deleteFulfillment(accountId);
            }

            // 8. Orders (conditional)
            if (deleteOrders) {
                RLM_Utils_AccountOrderDeleter.deleteOrders(accountId);
            }

            // 9. Contracts (conditional)
            if (deleteContracts) {
                RLM_Utils_AccountBillingDeleter.deleteContracts(accountId);
            }

            // 10. Assets (conditional)
            if (deleteAssets) {
                RLM_Utils_AccountAssetDeleter.deleteAll(accountId);
            }

            // 11. Quotes (conditional)
            if (deleteQuotes) {
                RLM_Utils_AccountCrmDeleter.deleteQuotes(accountId);
            }

            // 12. Opportunities (conditional)
            if (deleteOpps) {
                RLM_Utils_AccountCrmDeleter.deleteOpportunities(accountId);
            }
        } catch (Exception e) {
            Database.rollback(sp);
            throw e;
        }
    }
}
