/**
 * Phase 3 - Suspend / Resume.
 *
 * Combines the NATIVE billing suspension standard action (blngSvcSuspendBilling,
 * verified present on v67) with a custom per-asset status
 * (Asset.RLM_Asset_Status__c) so the console can show and drive a suspend/resume
 * window:
 *   - suspend(): groups the selected assets by account, invokes
 *     blngSvcSuspendBilling(accountId, suspensionDate, resumptionDate) once per
 *     account (native billing pause with a scheduled resume), then stamps
 *     RLM_Asset_Status__c = 'Suspended' and RLM_Suspension_Resume_Date__c on the
 *     assets via "as user" DML.
 *   - resume(): flips the custom status back to Active immediately (billing also
 *     auto-resumes at the native resumptionDate).
 *
 * RLM_AssetResumeScheduler performs the unattended flip on the resume date.
 *
 * The native action call uses the @TestVisible mock seam (invoking billing
 * actions needs live billing data). Behavioral changes MUST be live-verified.
 */
public with sharing class RLM_AssetSuspensionService {

    private static final String STD_SUSPEND = 'blngSvcSuspendBilling';

    public class SuspensionResult {
        @AuraEnabled public Boolean isSuccess;
        @AuraEnabled public Integer assetsUpdated;
        @AuraEnabled public List<String> messages;
        public SuspensionResult() {
            isSuccess = true;
            assetsUpdated = 0;
            messages = new List<String>();
        }
    }

    /** Outcome of one native suspend-billing invocation (mockable in tests). */
    public class SuspendOutcome {
        public Boolean isSuccess = true;
        public String info;
    }

    @TestVisible
    private static SuspendOutcome mockSuspendOutcome;

    // ------------------------------------------------------------------
    // Suspend
    // ------------------------------------------------------------------
    public static SuspensionResult suspend(List<Id> assetIds, Date suspensionDate, Date resumptionDate) {
        SuspensionResult result = new SuspensionResult();
        if (assetIds == null || assetIds.isEmpty()) {
            result.isSuccess = false;
            result.messages.add('Select at least one asset.');
            return result;
        }
        if (resumptionDate == null) {
            result.isSuccess = false;
            result.messages.add('A resumption date is required.');
            return result;
        }
        Date effSuspend = (suspensionDate == null) ? Date.today() : suspensionDate;

        Set<Id> ids = new Set<Id>();
        for (Id raw : assetIds) ids.add(Id.valueOf(raw));

        List<Asset> assets = [
            SELECT Id, AccountId, RLM_Asset_Status__c, RLM_Suspension_Resume_Date__c
            FROM Asset
            WHERE Id IN :ids
            WITH USER_MODE
        ];
        if (assets.isEmpty()) {
            result.isSuccess = false;
            result.messages.add('No matching assets.');
            return result;
        }

        // One native billing-suspend call per distinct account.
        Set<Id> accountIds = new Set<Id>();
        for (Asset a : assets) {
            if (a.AccountId != null) accountIds.add(a.AccountId);
        }
        for (Id acctId : accountIds) {
            SuspendOutcome outcome = invokeSuspend(acctId, effSuspend, resumptionDate);
            if (!outcome.isSuccess) {
                result.isSuccess = false;
                result.messages.add('Billing suspend failed for account ' + acctId +
                    (String.isBlank(outcome.info) ? '' : (': ' + outcome.info)));
                return result;
            }
        }

        // Stamp custom status via as-user DML.
        for (Asset a : assets) {
            a.RLM_Asset_Status__c = 'Suspended';
            a.RLM_Suspension_Resume_Date__c = resumptionDate;
        }
        update as user assets;
        result.assetsUpdated = assets.size();
        return result;
    }

    // ------------------------------------------------------------------
    // Resume (manual / immediate)
    // ------------------------------------------------------------------
    public static SuspensionResult resume(List<Id> assetIds) {
        SuspensionResult result = new SuspensionResult();
        if (assetIds == null || assetIds.isEmpty()) {
            result.isSuccess = false;
            result.messages.add('Select at least one asset.');
            return result;
        }
        Set<Id> ids = new Set<Id>();
        for (Id raw : assetIds) ids.add(Id.valueOf(raw));

        List<Asset> assets = [
            SELECT Id, RLM_Asset_Status__c, RLM_Suspension_Resume_Date__c
            FROM Asset
            WHERE Id IN :ids
            WITH USER_MODE
        ];
        for (Asset a : assets) {
            a.RLM_Asset_Status__c = 'Active';
            a.RLM_Suspension_Resume_Date__c = null;
        }
        update as user assets;
        result.assetsUpdated = assets.size();
        return result;
    }

    // ------------------------------------------------------------------
    // Native invocation with test seam
    // ------------------------------------------------------------------
    private static SuspendOutcome invokeSuspend(Id accountId, Date suspensionDate, Date resumptionDate) {
        if (Test.isRunningTest()) {
            return (mockSuspendOutcome != null) ? mockSuspendOutcome : new SuspendOutcome();
        }
        SuspendOutcome outcome = new SuspendOutcome();
        try {
            Invocable.Action action = Invocable.Action.createStandardAction(STD_SUSPEND);
            action.setInvocationParameter('accountId', accountId);
            action.setInvocationParameter('suspensionDate', suspensionDate);
            action.setInvocationParameter('resumptionDate', resumptionDate);
            List<Invocable.Action.Result> results = action.invoke();
            if (results == null || results.isEmpty() || !results[0].isSuccess()) {
                outcome.isSuccess = false;
                if (results != null && !results.isEmpty()) {
                    for (Invocable.Action.Error e : results[0].getErrors()) {
                        outcome.info = e.getMessage();
                    }
                }
                return outcome;
            }
            Map<String, Object> out = results[0].getOutputParameters();
            if (out != null && out.get('isSuccess') == false) {
                outcome.isSuccess = false;
                Object addl = out.get('additionalInformation');
                outcome.info = (addl == null) ? null : String.valueOf(addl);
            }
        } catch (Exception ex) {
            outcome.isSuccess = false;
            outcome.info = ex.getTypeName() + ': ' + ex.getMessage();
        }
        return outcome;
    }
}
