/**
 * Builds the user the docgen runAs tests run as: the "Minimum Access - Salesforce" profile,
 * RLM_QuantumBit_Sales_Representative, and the platform's document generation runtime grant (the
 * DocGenDesignerPsl license plus the standard DocGenUser set) and nothing else.
 *
 * The runtime grant is added because the Sales Representative set cannot carry it: the
 * DocGenRuntimeUser user permission needs that license, and a set with no license is refused it.
 * Without it DocumentTemplate is not visible to the user at all. The persona gets it the same way,
 * through the RLM_Sales_Representative group, which includes DocGenUser. Every object and field
 * grant the invocables need comes from the Sales Representative set alone, so a passing test shows
 * that set is enough on top of the runtime grant.
 *
 * The test fails, never skips, when the user cannot be built: standard profile names can be
 * translated, so this needs the English profile name, the license and a free seat.
 */
@IsTest
public class RLM_DocGenTestUsers {
    public static final String SALES_REP_SET = 'RLM_QuantumBit_Sales_Representative';
    public static final String RUNTIME_SET = 'DocGenUser';
    public static final String RUNTIME_LICENSE = 'DocGenDesignerPsl';

    public static User salesRepresentative() {
        List<Profile> profiles = [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
        Assert.areEqual(1, profiles.size(),
            'PRECONDITION: this test needs the English standard profile "Minimum Access - Salesforce"');
        List<PermissionSet> sets = [SELECT Id FROM PermissionSet WHERE Name = :SALES_REP_SET LIMIT 1];
        Assert.areEqual(1, sets.size(), 'PRECONDITION: permission set not in this org: ' + SALES_REP_SET);
        List<PermissionSet> runtime = [SELECT Id FROM PermissionSet WHERE Name = :RUNTIME_SET LIMIT 1];
        Assert.areEqual(1, runtime.size(), 'PRECONDITION: permission set not in this org: ' + RUNTIME_SET);
        List<PermissionSetLicense> licenses =
            [SELECT Id FROM PermissionSetLicense WHERE DeveloperName = :RUNTIME_LICENSE LIMIT 1];
        Assert.areEqual(1, licenses.size(), 'PRECONDITION: license not in this org: ' + RUNTIME_LICENSE);

        String stamp = String.valueOf(Crypto.getRandomInteger()).remove('-');
        User u = new User(
            ProfileId = profiles[0].Id,
            LastName = 'DocGenRep',
            Email = 'rlm.docgenrep@example.com',
            Username = 'rlm.docgenrep.' + stamp + '@example.com',
            Alias = 'rlmdg',
            TimeZoneSidKey = 'America/Los_Angeles',
            LocaleSidKey = 'en_US',
            EmailEncodingKey = 'UTF-8',
            LanguageLocaleKey = 'en_US'
        );
        // Setup-object DML after the test's records needs its own runAs context (mixed DML).
        System.runAs(new User(Id = UserInfo.getUserId())) {
            insert u;
            insert new PermissionSetLicenseAssign(AssigneeId = u.Id, PermissionSetLicenseId = licenses[0].Id);
            insert new List<PermissionSetAssignment>{
                new PermissionSetAssignment(AssigneeId = u.Id, PermissionSetId = sets[0].Id),
                new PermissionSetAssignment(AssigneeId = u.Id, PermissionSetId = runtime[0].Id)
            };
        }
        return u;
    }
}
