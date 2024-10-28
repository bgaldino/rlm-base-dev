public with sharing class GetOrg62UrlFlowAction {
    @InvocableMethod(label='Get Org62 URL mapped to current OrgSF instance')
    public static List<String> flowActionGetOrg62Url() {
        return new List<String>{EnvironmentMappingUtil.getOrg62Url()};
    }
}