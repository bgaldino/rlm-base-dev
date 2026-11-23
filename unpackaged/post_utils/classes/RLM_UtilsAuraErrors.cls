/**
 * Builds the AuraHandledException an @AuraEnabled method throws. The LWC receives the constructor
 * text either way, but Apex-side getMessage() is "Script-thrown exception" unless setMessage is
 * called, which hides the cause in tests and logs. Every throw in this bundle goes
 * through here. The billing UI bundle has its own copy so each bundle deploys on its own.
 */
public with sharing class RLM_UtilsAuraErrors {
    public static AuraHandledException handled(String message) {
        AuraHandledException e = new AuraHandledException(message);
        e.setMessage(message);
        return e;
    }
}
