public with sharing class EnvironmentMappingUtil {
    public static String getOrg62Url() {
        String navigationURL = null;
        String sandboxName = System.DomainParser.parse(URL.getOrgDomainUrl()).getSandboxName();
        if (sandboxName == null) {
            sandboxName = 'prod';
            Organization org = [SELECT IsSandbox, TrialExpirationDate FROM Organization WITH SECURITY_ENFORCED LIMIT 1];
            Boolean isScratchOrg = org.IsSandbox && (org.TrialExpirationDate != null);
            if (isScratchOrg) {
                sandboxName = 'scratchOrg';
            }
        }
        Environment_Mapping__mdt emRecord = null;
        if (Schema.sObjectType.Environment_Mapping__mdt.isAccessible()) {
            emRecord = Environment_Mapping__mdt.getInstance(sandboxName);
        }    
        if (emRecord != null && emRecord.Org62_Environment_URL__c != null) {
            navigationURL = emRecord.Org62_Environment_URL__c;
        }
        return navigationURL;
    }
}