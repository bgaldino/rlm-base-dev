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
            return daysRemaining(objList.isEmpty() ? null : objList[0].TrialExpirationDate, Date.today());
        } catch (Exception e) {
            throw new AuraHandledException(e.getMessage());
        }
    }

    // The days from today to the trial's expiry. An org either has a trial expiry or not, so a test
    // passes the value to reach both paths in one org.
    @TestVisible
    private static Integer daysRemaining(Datetime trialExpiration, Date today) {
        // Non-trial orgs (e.g. Enterprise) have no TrialExpirationDate; return
        // null so the welcome UI omits the countdown instead of throwing.
        if (trialExpiration == null) {
            return null;
        }
        // TrialExpirationDate is a Datetime; take its date portion.
        Integer days = today.daysBetween(trialExpiration.date());
        // Clamp so an already-expired org never shows negative "days remaining".
        return days < 0 ? 0 : days;
    }
}