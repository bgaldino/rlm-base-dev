public with sharing class RLM_Learning_UserInformation {
    @AuraEnabled(cacheable=true)
    public static String getName() {
        return UserInfo.getFirstName();
    }

    // Note: part-of-day ("Morning"/"Afternoon"/"Evening") is computed client-side in
    // rlmLearningWelcome from the browser's local time. It is intentionally NOT an Apex
    // method here: a cacheable @AuraEnabled built on System.now() is non-deterministic
    // and its result can be cached and go stale.

    @AuraEnabled(cacheable=true)
    public static Integer getExpiryDays(){
        try {
            List<Organization> objList = [
                SELECT TrialExpirationDate FROM Organization WITH USER_MODE LIMIT 1
            ];
            // Non-trial orgs (e.g. Enterprise) have no TrialExpirationDate; return
            // null so the welcome UI omits the countdown instead of throwing.
            if (objList.isEmpty() || objList[0].TrialExpirationDate == null) {
                return null;
            }
            // TrialExpirationDate is a Datetime; take its date portion.
            Date trialExpirationDate = objList[0].TrialExpirationDate.date();
            Integer daysRemaining = Date.today().daysBetween(trialExpirationDate);
            // Clamp so an already-expired org never shows negative "days remaining".
            return daysRemaining < 0 ? 0 : daysRemaining;
        } catch (Exception e) {
            throw new AuraHandledException(e.getMessage());
        }
    }
}