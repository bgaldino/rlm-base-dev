public class RLM_Utils_AccountBillingDeleter {

    public static void deleteInvoices(String accountId) {
        List<Invoice> toDelete = [
            SELECT Id FROM Invoice WHERE BillingAccountId = :accountId AND Status = 'Draft'
        ];
        if (!toDelete.isEmpty()) {
            Database.delete(toDelete, false);
        }
    }

    public static void deleteBillingScheduleGroups(String accountId) {
        List<BillingScheduleGroup> toDelete = [
            SELECT Id FROM BillingScheduleGroup WHERE BillingAccountId = :accountId
        ];
        if (!toDelete.isEmpty()) {
            Database.delete(toDelete, false);
        }
    }

    public static void deleteContracts(String accountId) {
        // Delete PriceAdjustmentSchedule first (restrict-delete on Contract)
        List<Contract> contracts = [SELECT Id FROM Contract WHERE AccountId = :accountId];
        if (contracts.isEmpty()) return;

        Set<Id> contractIds = new Map<Id, Contract>(contracts).keySet();

        List<PriceAdjustmentSchedule> pas = [
            SELECT Id FROM PriceAdjustmentSchedule WHERE ContractId IN :contractIds
        ];
        if (!pas.isEmpty()) Database.delete(pas, false);

        // Delete RecordAlerts referencing contracts
        List<RecordAlert> alerts = [
            SELECT Id FROM RecordAlert WHERE ParentId IN :contractIds OR WhatId IN :contractIds
        ];
        if (!alerts.isEmpty()) Database.delete(alerts, false);

        // Delete the contracts
        Database.delete(contracts, false);
    }
}
