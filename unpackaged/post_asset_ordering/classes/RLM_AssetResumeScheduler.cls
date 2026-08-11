/**
 * Phase 3 - unattended auto-resume.
 *
 * Schedulable that flips assets whose scheduled resume date has arrived back to
 * Active. Native billing already auto-resumes at the resumptionDate passed to
 * blngSvcSuspendBilling; this keeps the console's custom status
 * (RLM_Asset_Status__c) consistent without a manual resume.
 *
 * Schedule (example - daily at 01:00):
 *   System.schedule('RLM Asset Auto-Resume', '0 0 1 * * ?', new RLM_AssetResumeScheduler());
 */
public with sharing class RLM_AssetResumeScheduler implements Schedulable {

    public void execute(SchedulableContext sc) {
        resumeDueAssets();
    }

    /** Package-visible so it can be invoked directly (tests / manual run). */
    public static Integer resumeDueAssets() {
        Date today = Date.today();
        List<Asset> due = [
            SELECT Id, RLM_Asset_Status__c, RLM_Suspension_Resume_Date__c
            FROM Asset
            WHERE RLM_Asset_Status__c = 'Suspended'
              AND RLM_Suspension_Resume_Date__c <= :today
            WITH SYSTEM_MODE
        ];
        if (due.isEmpty()) return 0;
        for (Asset a : due) {
            a.RLM_Asset_Status__c = 'Active';
            a.RLM_Suspension_Resume_Date__c = null;
        }
        update due;
        return due.size();
    }
}
