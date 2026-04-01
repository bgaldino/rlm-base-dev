public with sharing class RLM_Utils_AccountResetController {

    @AuraEnabled
    public static RLM_Utils_StepResult deleteUsageAndBindings(Id accountId) {
        String stepName = 'Usage and Bindings';
        try {
            RLM_Utils_AccountUsageDeleter.deleteAllSummaries(String.valueOf(accountId));
            RLM_Utils_AccountUsageDeleter.deleteEntitlements(String.valueOf(accountId));
            RLM_Utils_AccountBindingDeleter.deleteAll(String.valueOf(accountId));
            RLM_Utils_AccountUsageDeleter.deleteTransactionJournals(String.valueOf(accountId));
            return RLM_Utils_StepResult.success(stepName, 'Usage, entitlement, binding, and journal records processed.');
        } catch (Exception e) {
            return RLM_Utils_StepResult.failure(stepName, e);
        }
    }

    @AuraEnabled
    public static RLM_Utils_StepResult deleteBillingOnly(Id accountId, Boolean deleteBilling) {
        String stepName = 'Billing';
        if (deleteBilling != true) {
            return RLM_Utils_StepResult.skipped(stepName, 'Billing deletion not selected (Draft Invoices + Billing Schedule Groups).');
        }
        try {
            // Keep Billing scoped and explicit: billing schedule groups + draft invoices only.
            RLM_Utils_AccountBillingDeleter.deleteBillingScheduleGroups(String.valueOf(accountId));
            RLM_Utils_AccountBillingDeleter.deleteInvoices(String.valueOf(accountId));
            return RLM_Utils_StepResult.success(stepName, 'Processed Billing Schedule Groups and Draft Invoices.');
        } catch (Exception e) {
            return RLM_Utils_StepResult.failure(stepName, e);
        }
    }

    @AuraEnabled
    public static RLM_Utils_StepResult deleteContractsOnly(Id accountId, Boolean deleteContracts) {
        String stepName = 'Contracts';
        if (deleteContracts != true) {
            return RLM_Utils_StepResult.skipped(stepName, 'Contract deletion not selected.');
        }
        try {
            RLM_Utils_AccountBillingDeleter.deleteContracts(String.valueOf(accountId));
            return RLM_Utils_StepResult.success(stepName, 'Contract data processed.');
        } catch (Exception e) {
            return RLM_Utils_StepResult.failure(stepName, e);
        }
    }

    @AuraEnabled
    public static RLM_Utils_StepResult deleteFulfillment(Id accountId, Boolean deleteFulfillment) {
        String stepName = 'Fulfillment';
        if (deleteFulfillment != true) {
            return RLM_Utils_StepResult.skipped(stepName, 'Fulfillment deletion not selected.');
        }
        try {
            RLM_Utils_AccountOrderDeleter.deleteFulfillment(String.valueOf(accountId));
            return RLM_Utils_StepResult.success(stepName, 'Fulfillment data processed.');
        } catch (Exception e) {
            return RLM_Utils_StepResult.failure(stepName, e);
        }
    }

    @AuraEnabled
    public static RLM_Utils_StepResult deleteOrders(Id accountId, Boolean deleteOrders) {
        String stepName = 'Orders';
        if (deleteOrders != true) {
            return RLM_Utils_StepResult.skipped(stepName, 'Order deletion not selected.');
        }
        try {
            RLM_Utils_AccountOrderDeleter.deleteOrders(String.valueOf(accountId));
            return RLM_Utils_StepResult.success(stepName, 'Order data processed.');
        } catch (Exception e) {
            return RLM_Utils_StepResult.failure(stepName, e);
        }
    }

    @AuraEnabled
    public static RLM_Utils_StepResult deleteAssets(Id accountId, Boolean deleteAssets) {
        String stepName = 'Assets';
        if (deleteAssets != true) {
            return RLM_Utils_StepResult.skipped(stepName, 'Asset deletion not selected.');
        }
        try {
            RLM_Utils_AccountAssetDeleter.deleteAll(String.valueOf(accountId));
            return RLM_Utils_StepResult.success(stepName, 'Asset data processed.');
        } catch (Exception e) {
            return RLM_Utils_StepResult.failure(stepName, e);
        }
    }

    @AuraEnabled
    public static RLM_Utils_StepResult deleteQuotesOnly(Id accountId, Boolean deleteQuotes) {
        String stepName = 'Quotes';
        if (deleteQuotes != true) {
            return RLM_Utils_StepResult.skipped(stepName, 'Quote deletion not selected.');
        }
        try {
            RLM_Utils_AccountCrmDeleter.deleteQuotes(String.valueOf(accountId));
            return RLM_Utils_StepResult.success(stepName, 'Quote data processed.');
        } catch (Exception e) {
            return RLM_Utils_StepResult.failure(stepName, e);
        }
    }

    @AuraEnabled
    public static RLM_Utils_StepResult deleteOpportunitiesOnly(Id accountId, Boolean deleteOpps) {
        String stepName = 'Opportunities';
        if (deleteOpps != true) {
            return RLM_Utils_StepResult.skipped(stepName, 'Opportunity deletion not selected.');
        }
        try {
            RLM_Utils_AccountCrmDeleter.deleteOpportunities(String.valueOf(accountId));
            return RLM_Utils_StepResult.success(stepName, 'Opportunity data processed.');
        } catch (Exception e) {
            return RLM_Utils_StepResult.failure(stepName, e);
        }
    }
}
