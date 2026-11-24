/**
 * Builds the users the docgen runAs tests run as, on the "Minimum Access - Salesforce" profile:
 * salesRepresentative() adds RLM_QuantumBit_Sales_Representative and the platform's document
 * generation runtime grant (the DocGenDesignerPsl license plus the standard DocGenUser set);
 * withNoGrants() adds nothing, for the tests of a refused query or insert.
 *
 * The runtime grant is added because the Sales Representative set cannot carry it: the
 * DocGenRuntimeUser user permission needs that license, and a set with no license is refused it.
 * Without it DocumentTemplate is not visible to the user at all. The persona gets it the same way,
 * through the RLM_Sales_Representative group, which includes DocGenUser.
 *
 * DocGenUser also grants DocumentTemplate read and DocumentGenerationProcess create, so a runAs
 * test passing as salesRepresentative() does not show where each grant came from. The test in this
 * class reads the Sales Representative set's own object and field permissions instead, so the set
 * is shown to carry every grant the invocables need without relying on DocGenUser.
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
        return build(true, true);
    }

    public static User withNoGrants() {
        return build(false, false);
    }

    private static User build(Boolean withSalesRepSet, Boolean withRuntime) {
        List<Profile> profiles = [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
        Assert.areEqual(1, profiles.size(),
            'PRECONDITION: this test needs the English standard profile "Minimum Access - Salesforce"');
        List<Id> setIds = new List<Id>();
        if (withSalesRepSet) {
            setIds.add(permissionSetId(SALES_REP_SET));
        }
        Id licenseId;
        if (withRuntime) {
            setIds.add(permissionSetId(RUNTIME_SET));
            List<PermissionSetLicense> licenses =
                [SELECT Id FROM PermissionSetLicense WHERE DeveloperName = :RUNTIME_LICENSE LIMIT 1];
            Assert.areEqual(1, licenses.size(), 'PRECONDITION: license not in this org: ' + RUNTIME_LICENSE);
            licenseId = licenses[0].Id;
        }

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
            if (licenseId != null) {
                insert new PermissionSetLicenseAssign(AssigneeId = u.Id, PermissionSetLicenseId = licenseId);
            }
            List<PermissionSetAssignment> assignments = new List<PermissionSetAssignment>();
            for (Id setId : setIds) {
                assignments.add(new PermissionSetAssignment(AssigneeId = u.Id, PermissionSetId = setId));
            }
            insert assignments;
        }
        return u;
    }

    private static Id permissionSetId(String name) {
        List<PermissionSet> sets = [SELECT Id FROM PermissionSet WHERE Name = :name LIMIT 1];
        Assert.areEqual(1, sets.size(), 'PRECONDITION: permission set not in this org: ' + name);
        return sets[0].Id;
    }

    // The Sales Representative set itself carries every object and field grant the three
    // invocables use as the running user. ContentVersion is not listed: it has no object
    // permission row (files follow sharing), so there is nothing to grant.
    @IsTest
    static void salesRepresentativeSetCarriesEveryDocgenGrant() {
        Map<String, ObjectPermissions> objects = new Map<String, ObjectPermissions>();
        for (ObjectPermissions op : [
            SELECT SobjectType, PermissionsRead, PermissionsCreate FROM ObjectPermissions
            WHERE Parent.Name = :SALES_REP_SET
            AND SobjectType IN ('DocumentTemplate', 'DocumentGenerationProcess', 'Quote', 'Opportunity')
        ]) {
            objects.put(op.SobjectType, op);
        }
        for (String readable : new List<String>{ 'DocumentTemplate', 'Quote', 'Opportunity' }) {
            Assert.isTrue(objects.containsKey(readable) && objects.get(readable).PermissionsRead,
                SALES_REP_SET + ' grants read on ' + readable);
        }
        Assert.isTrue(objects.containsKey('DocumentGenerationProcess')
            && objects.get('DocumentGenerationProcess').PermissionsCreate,
            SALES_REP_SET + ' grants create on DocumentGenerationProcess');

        Map<String, FieldPermissions> fields = new Map<String, FieldPermissions>();
        for (FieldPermissions fp : [
            SELECT Field, PermissionsRead, PermissionsEdit FROM FieldPermissions
            WHERE Parent.Name = :SALES_REP_SET
            AND SobjectType IN ('DocumentTemplate', 'DocumentGenerationProcess')
        ]) {
            fields.put(fp.Field, fp);
        }
        Assert.isTrue(fields.containsKey('DocumentTemplate.TokenMappingMethodType')
            && fields.get('DocumentTemplate.TokenMappingMethodType').PermissionsRead,
            SALES_REP_SET + ' grants read on DocumentTemplate.TokenMappingMethodType');
        // The ReferenceObject reference is stored as ReferenceObjectId in FieldPermissions
        // (measured on a 264 org; the permission set source names it ReferenceObject).
        for (String editable : new List<String>{
            'DocumentGenerationProcess.ReferenceObjectId',
            'DocumentGenerationProcess.RequestText',
            'DocumentGenerationProcess.PdfDocIdentifiersList'
        }) {
            Assert.isTrue(fields.containsKey(editable) && fields.get(editable).PermissionsEdit,
                SALES_REP_SET + ' grants edit on ' + editable);
        }
    }
}
