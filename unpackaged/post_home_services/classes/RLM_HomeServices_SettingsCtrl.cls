// without sharing: org-default Custom Setting must be writable regardless of caller's profile
public without sharing class RLM_HomeServices_SettingsCtrl {

    @AuraEnabled(cacheable=true)
    public static Boolean getEnabled() {
        return RLM_HomeServices_Settings__c.getOrgDefaults().RLM_Enabled__c;
    }

    @AuraEnabled
    public static void setEnabled(Boolean enabled) {
        RLM_HomeServices_Settings__c settings = RLM_HomeServices_Settings__c.getOrgDefaults();
        settings.RLM_Enabled__c = enabled;
        upsert settings;
    }
}
