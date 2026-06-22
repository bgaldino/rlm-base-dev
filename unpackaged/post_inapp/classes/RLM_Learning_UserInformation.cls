public with sharing class RLM_Learning_UserInformation {
    @AuraEnabled(cacheable=true)
    public static String getName() {
        return UserInfo.getFirstName();
    }

    @AuraEnabled(cacheable=true)
    public static String getTiming() {
        return timingForHour(System.now().hour());
    }

    @TestVisible
    private static String timingForHour(Integer hour) {
        if (hour < 12) {
            return 'Morning';
        } else if (hour >= 12 && hour < 17) {
            return 'Afternoon';
        }
        return 'Evening';
    }

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
            Date earliestDate = Date.valueOf(objList[0].TrialExpirationDate);
            Integer daysBetween = Date.today().daysBetween(earliestDate);
            // Clamp so an already-expired org never shows negative "days remaining".
            return daysBetween < 0 ? 0 : daysBetween;
        } catch (Exception e) {
            throw new AuraHandledException(e.getMessage());
        }
    }
}