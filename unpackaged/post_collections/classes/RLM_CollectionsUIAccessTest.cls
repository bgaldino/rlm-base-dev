/**
 * Proves RLM_CollectionsUI grants the Collection Plan record page its fields
 * (RLM_Collection_Plan_Record_Page), and that nothing else a collections user holds does.
 *
 * The page shows CollectionPlan fields no Apex controller selects, so RLM_BillingUI (which
 * grants what its controllers read) does not carry them. The managed Billing Collections and
 * Recovery Specialist set gives object access but, measured on a 264 org, none of these
 * fields. System Administrator bypasses field access, so both tests run as a Minimum Access
 * user holding only the licenses and sets named below. The fields list must match the
 * page's Record.* items; tests/test_collection_plan_page_fields.py checks the page against the
 * permission set offline.
 *
 * Each user takes a seat of the Billing and Billing Advanced licenses. An org whose seats are
 * all assigned fails these tests on the license, not on access.
 */
@IsTest
private class RLM_CollectionsUIAccessTest {

    private static final List<String> LICENSES = new List<String>{ 'RevLifecycleMgmtBillingPsl', 'BillingAdvancedPsl' };
    private static final String SPECIALIST = 'BillingCollectionsAndRecoverySpecialist';
    private static final String COLLECTIONS_UI = 'RLM_CollectionsUI';

    private static final List<String> PAGE_ONLY_FIELDS = new List<String>{
        'BillingAccountId', 'CollectionPlanReasonId', 'CollectionPlanSegment', 'ContactId',
        'FirstCallDateTime', 'FirstEmailDateTime', 'FirstSmsDateTime', 'InitialDueAmount',
        'IsClosed', 'PromiseToPayCount', 'RiskScore', 'Status', 'TotalTaxAmount', 'UsageType'
    };

    @IsTest
    static void collectionsUiGrantsEveryPageOnlyField() {
        User u = collectionsUser(new List<String>{ SPECIALIST, COLLECTIONS_UI });
        String failure;
        System.runAs(u) {
            try {
                Database.query('SELECT Id, ' + String.join(PAGE_ONLY_FIELDS, ', ') + ' FROM CollectionPlan LIMIT 1',
                    AccessLevel.USER_MODE);
            } catch (Exception e) {
                failure = e.getMessage().substringBefore(' If you are attempting');
            }
        }
        Assert.isNull(failure, 'CollectionPlan page fields not readable with ' + COLLECTIONS_UI + ': ' + failure);
    }

    // The same user without RLM_CollectionsUI cannot read a page-only field, so the set is
    // what grants them. This holds while no managed set or profile grants RiskScore.
    @IsTest
    static void pageOnlyFieldsAreNotReadableWithoutCollectionsUi() {
        User u = collectionsUser(new List<String>{ SPECIALIST });
        System.runAs(u) {
            Schema.SObjectField f = Schema.SObjectType.CollectionPlan.fields.getMap().get('RiskScore');
            Assert.isTrue(f == null || !f.getDescribe().isAccessible(),
                'CollectionPlan.RiskScore is readable without ' + COLLECTIONS_UI
                + ': the grant is no longer what provides it');
        }
    }

    private static User collectionsUser(List<String> permissionSets) {
        Map<String, Id> setIds = new Map<String, Id>();
        for (PermissionSet ps : [SELECT Id, Name FROM PermissionSet WHERE Name IN :permissionSets]) {
            setIds.put(ps.Name, ps.Id);
        }
        for (String name : permissionSets) {
            Assert.isTrue(setIds.containsKey(name), 'Permission set not in this org: ' + name);
        }
        List<PermissionSetLicense> psls = [SELECT Id FROM PermissionSetLicense WHERE DeveloperName IN :LICENSES];
        Assert.areEqual(LICENSES.size(), psls.size(), 'Permission set license missing from this org: ' + LICENSES);

        Profile minimal = [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
        String stamp = String.valueOf(Crypto.getRandomInteger()).remove('-');
        User u = new User(
            ProfileId = minimal.Id,
            LastName = 'CollectionsUI',
            Email = 'rlm.collectionsui@example.com',
            Username = 'rlm.collectionsui.' + stamp + '@example.com',
            Alias = 'rlmcui',
            TimeZoneSidKey = 'America/Los_Angeles',
            LocaleSidKey = 'en_US',
            EmailEncodingKey = 'UTF-8',
            LanguageLocaleKey = 'en_US'
        );
        System.runAs(new User(Id = UserInfo.getUserId())) {
            insert u;
            List<PermissionSetLicenseAssign> pslas = new List<PermissionSetLicenseAssign>();
            for (PermissionSetLicense psl : psls) {
                pslas.add(new PermissionSetLicenseAssign(AssigneeId = u.Id, PermissionSetLicenseId = psl.Id));
            }
            insert pslas;
            List<PermissionSetAssignment> psas = new List<PermissionSetAssignment>();
            for (Id setId : setIds.values()) {
                psas.add(new PermissionSetAssignment(AssigneeId = u.Id, PermissionSetId = setId));
            }
            insert psas;
        }
        return u;
    }
}
