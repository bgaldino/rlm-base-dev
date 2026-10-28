/**
 * Test users for the Billing UI access tests: a Minimum Access user holding the given
 * permission set licenses and permission sets, and nothing else. System Administrator
 * bypasses object and field access, so a USER_MODE test proves nothing unless it runs as
 * one of these.
 *
 * Each user takes a seat of every license it is given. An org whose Billing or Billing
 * Advanced seats are all assigned fails these tests on the license, not on access.
 */
@IsTest
public class RLM_BillingUITestUsers {

    public static final String BILLING_PSL = 'RevLifecycleMgmtBillingPsl';
    public static final String BILLING_ADVANCED_PSL = 'BillingAdvancedPsl';

    public static User create(List<String> permissionSets, List<String> licenses) {
        Map<String, Id> setIds = new Map<String, Id>();
        for (PermissionSet ps : [SELECT Id, Name FROM PermissionSet WHERE Name IN :permissionSets]) {
            setIds.put(ps.Name, ps.Id);
        }
        for (String name : permissionSets) {
            Assert.isTrue(setIds.containsKey(name), 'Permission set not in this org: ' + name);
        }
        List<PermissionSetLicense> psls = [
            SELECT Id FROM PermissionSetLicense WHERE DeveloperName IN :licenses
        ];
        Assert.areEqual(licenses.size(), psls.size(), 'Permission set license missing from this org: ' + licenses);

        Profile minimal = [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
        String stamp = String.valueOf(Crypto.getRandomInteger()).remove('-');
        User u = new User(
            ProfileId = minimal.Id,
            LastName = 'BillingUI',
            Email = 'rlm.billingui@example.com',
            Username = 'rlm.billingui.' + stamp + '@example.com',
            Alias = 'rlmbui',
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
