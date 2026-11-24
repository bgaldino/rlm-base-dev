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

    /**
     * For a caught exception whose text may name objects, fields or query parts: the user gets
     * the fixed sentence given, the detail goes to the debug log, and the caught exception stays
     * on the result as its cause.
     */
    public static AuraHandledException failed(String message, String context, Exception cause) {
        System.debug(LoggingLevel.ERROR, context + ': ' + cause.getTypeName() + ': ' + cause.getMessage());
        AuraHandledException e = handled(message);
        e.initCause(cause);
        return e;
    }
}
