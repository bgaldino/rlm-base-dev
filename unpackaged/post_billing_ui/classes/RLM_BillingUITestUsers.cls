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

    // The billing persona groups (unpackaged/post_personas) and the standalone collections set their
    // users are assigned next to the group (owner decision, todo 452).
    public static final List<String> BILLING_PERSONA_GROUPS = new List<String>{
        'RLM_Billing_Operations', 'RLM_Billing_Admin', 'RLM_Credit_Memo_Operations'
    };
    public static final String COLLECTIONS_READ_SET = 'RLM_BillingCollectionsRead';

    /**
     * A billing persona user who reads collection plans, built as the persona is assigned: the
     * persona's permission set group itself, the standalone RLM_BillingCollectionsRead set,
     * RLM_BillingUI, and the Billing and Billing Advanced licenses (the set's Collections and
     * Recovery Specialist user permission needs Billing Advanced). Returns null, with a visible
     * skip, where the personas bundle is not deployed (personas off) or the group is not yet
     * recalculated (status not Updated), so callers skip rather than fail.
     */
    public static User billingPersonaWithCollectionsRead(String groupName) {
        List<PermissionSetGroup> groups = [SELECT Id, Status FROM PermissionSetGroup WHERE DeveloperName = :groupName];
        if (groups.isEmpty() || [SELECT COUNT() FROM PermissionSet WHERE Name = :COLLECTIONS_READ_SET] == 0) {
            System.debug(LoggingLevel.WARN, 'SKIPPED: ' + groupName + ' or ' + COLLECTIONS_READ_SET
                + ' is not deployed (personas off), so that persona\'s collections read is not tested.');
            return null;
        }
        if (groups[0].Status != 'Updated') {
            // A release or deploy can leave a group Outdated until it is recalculated, and an
            // Outdated group cannot be assigned: skip visibly rather than fail a test-on-deploy.
            System.debug(LoggingLevel.WARN, 'SKIPPED: ' + groupName + ' is ' + groups[0].Status
                + ', not Updated, so it cannot be assigned; recalculate it to run this check.');
            return null;
        }
        User u = create(new List<String>{ 'RLM_BillingUI', COLLECTIONS_READ_SET },
            new List<String>{ BILLING_PSL, BILLING_ADVANCED_PSL });
        System.runAs(new User(Id = UserInfo.getUserId())) {
            insert new PermissionSetAssignment(AssigneeId = u.Id, PermissionSetGroupId = groups[0].Id);
        }
        return u;
    }

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

    /**
     * A billing user that holds exactly the given object reads: the given licenses, and one
     * custom permission set that carries the platform's Billing access user permission
     * (RlmBillingAccess) plus read on the listed objects.
     *
     * The user permission is what makes the Billing objects visible. Measured on a 264 org
     * with a Minimum Access user: read on BillingAccount, PaymentSchedule or PaymentScheduleItem
     * granted through a custom set does nothing without it, and with it that read is all the
     * user gets (no read on the other billing objects, none on Account). Every managed Billing
     * role set carries the user permission and also reads the link objects, so none of them
     * can stand for a user who reads some billing objects but not others.
     *
     * @param licenses permission set license developer names the user is assigned
     * @param readObjects objects the set grants read on
     * @param viewAllObjects objects the set grants read and view-all on
     */
    public static User createWithBillingAccess(
        List<String> licenses, List<String> readObjects, List<String> viewAllObjects
    ) {
        return createWithBillingAccess(licenses, readObjects, viewAllObjects, new List<String>());
    }

    /** As above, plus field read grants given as Object.Field (for example Account.BillingAddress). */
    public static User createWithBillingAccess(
        List<String> licenses, List<String> readObjects, List<String> viewAllObjects, List<String> readFields
    ) {
        User u = create(new List<String>(), licenses);
        String stamp = String.valueOf(Crypto.getRandomInteger()).remove('-');
        System.runAs(new User(Id = UserInfo.getUserId())) {
            PermissionSet ps = new PermissionSet(
                Name = 'RLM_TestBillingAccess_' + stamp,
                Label = 'RLM Test Billing Access ' + stamp,
                PermissionsRlmBillingAccess = true
            );
            insert ps;
            List<ObjectPermissions> grants = new List<ObjectPermissions>();
            for (String objectName : readObjects) {
                grants.add(new ObjectPermissions(ParentId = ps.Id, SobjectType = objectName, PermissionsRead = true));
            }
            for (String objectName : viewAllObjects) {
                grants.add(new ObjectPermissions(
                    ParentId = ps.Id, SobjectType = objectName, PermissionsRead = true, PermissionsViewAllRecords = true));
            }
            insert grants;
            List<FieldPermissions> fields = new List<FieldPermissions>();
            for (String fieldName : readFields) {
                fields.add(new FieldPermissions(
                    ParentId = ps.Id, SobjectType = fieldName.substringBefore('.'), Field = fieldName, PermissionsRead = true));
            }
            insert fields;
            insert new PermissionSetAssignment(AssigneeId = u.Id, PermissionSetId = ps.Id);
        }
        return u;
    }

    /**
     * Lets a test user see every record of the given objects. The shipped Billing sets grant object
     * and field access only; which records a user sees comes from the org's sharing, which a fresh
     * test user (not the owner of the admin-created rows) does not satisfy on BillingAccount (measured:
     * the user reads zero rows with the shipped sets). Used to test the role's access without it.
     */
    public static void grantViewAll(User u, List<String> objects) {
        String stamp = String.valueOf(Crypto.getRandomInteger()).remove('-');
        System.runAs(new User(Id = UserInfo.getUserId())) {
            PermissionSet ps = new PermissionSet(Name = 'RLM_TestViewAll_' + stamp, Label = 'RLM Test View All ' + stamp);
            insert ps;
            List<ObjectPermissions> grants = new List<ObjectPermissions>();
            for (String objectName : objects) {
                grants.add(new ObjectPermissions(
                    ParentId = ps.Id, SobjectType = objectName, PermissionsRead = true, PermissionsViewAllRecords = true));
            }
            insert grants;
            insert new PermissionSetAssignment(AssigneeId = u.Id, PermissionSetId = ps.Id);
        }
    }
}
