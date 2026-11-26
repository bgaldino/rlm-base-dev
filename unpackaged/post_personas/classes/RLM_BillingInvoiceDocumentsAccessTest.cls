/**
 * What a billing persona (RLM Billing Admin, RLM Billing Operations) needs to generate invoice
 * documents, batch (Generate Invoice Documents on an Invoice Batch Run) and on demand (Generate
 * Invoice Document on an Invoice), checked as that persona (todo 292). Measured on a 264 org as
 * Minimum Access users holding the Billing license and a persona group:
 * - Neither group reaches Document Template, Document Generation Process or Document Generation
 *   Batch Process ("Access to entity ... denied"). The DocGen sets need the DocGen Designer
 *   permission set license, so they are assigned next to the group, not put in it: existing holders
 *   of the billing groups may lack that license, and the build creates no billing persona user with it.
 * - With DocGen User the persona reads templates and may create a Document Generation Process (on
 *   demand) but not a Document Generation Batch Process ("DML operation INSERT not allowed on
 *   DocGenerationBatchProcess"), the create behind batch generation. DocGen Designer opens it.
 * - The managed Billing Admin set has no access to Invoice Batch Run, the record the batch action
 *   runs from; the managed Billing Operations set reads it. RLM_BillingInvoiceDocuments, in both
 *   groups, grants it with View All (the object is Private).
 * - The invoice template's file is in the Docgen Document Template Library and is read as the
 *   generating user. A library member needs Access Libraries (ContentWorkspaces), which the
 *   Minimum Access profile lacks; RLM_BillingInvoiceDocuments grants it. This class checks only that
 *   the set carries the permission: the file read itself depends on org data and configuration (the
 *   template, its library, an admin's choice of library members), so it was proved by check-only
 *   probes and is not a deploy gate here.
 *
 * Which tests check what:
 * - the group itself: the *Group* methods. A group that is Updating or Outdated cannot be assigned,
 *   and a deploy that changes a group leaves it Updating, so these skip (with a "SKIPPED, NOT
 *   CHECKED" WARN debug line) and then prove nothing. A Failed group fails the test.
 * - the managed role set plus RLM_BillingInvoiceDocuments (the group's content, minus its
 *   field-access set): the Invoice Batch Run reads and the DocGen access.
 * - the set's metadata: View All on the run chain, Access Libraries, and membership of both groups.
 * The Billing Operations run-read methods are regression checks: the managed Operations set already
 * reads the runs, and the View All the set adds is checked only by the metadata test.
 * Checks that would fail only because Salesforce grants MORE than today (the Billing Admin role
 * alone reading the runs, DocGen User alone creating a batch process) are WARN debug lines, not
 * assertions, so a platform change cannot block a deploy that runs local tests.
 *
 * Admin tests prove nothing here: System Administrator bypasses object access. Each test user needs
 * a Salesforce user license and takes a seat of every permission set license it is given (Billing;
 * DocGen Designer for the DocGen checks); no method holds more than two users at once. An org with no
 * free seat fails on the license, not on access.
 */
@IsTest
private class RLM_BillingInvoiceDocumentsAccessTest {

    private static final String BILLING_PSL = 'RevLifecycleMgmtBillingPsl';
    private static final String DOCGEN_PSL = 'DocGenDesignerPsl';
    private static final String INVOICE_DOCS_SET = 'RLM_BillingInvoiceDocuments';
    private static final String DOCGEN_USER = 'DocGenUser';
    private static final String DOCGEN_DESIGNER = 'DocGenDesigner';

    private static final String ADMIN_GROUP = 'RLM_Billing_Admin';
    private static final String OPERATIONS_GROUP = 'RLM_Billing_Operations';
    private static final String ADMIN_ROLE = 'RevenueLifecycleManagementBillingAdmin';
    private static final String OPERATIONS_ROLE = 'RevenueLifecycleManagementBillingOperations';
    // Read on Invoice Batch Run needs read on the scheduler, and that needs read on a run-criteria
    // object (deploy-enforced), so all three are checked.
    private static final List<String> BATCH_RUN_OBJECTS = new List<String>{
        'InvoiceBatchRun', 'BillingBatchScheduler', 'InvoiceBatchRunCriteria'
    };

    // ---- The set and the groups (metadata) ---------------------------------------------------

    @IsTest
    static void invoiceDocumentsSetGrantsViewAllOnTheRunChain() {
        Map<String, ObjectPermissions> grants = new Map<String, ObjectPermissions>();
        for (ObjectPermissions op : [
            SELECT SobjectType, PermissionsRead, PermissionsCreate, PermissionsEdit, PermissionsDelete,
                PermissionsViewAllRecords, PermissionsModifyAllRecords
            FROM ObjectPermissions WHERE Parent.Name = :INVOICE_DOCS_SET
        ]) {
            grants.put(op.SobjectType, op);
        }
        Assert.areEqual(new Set<String>(BATCH_RUN_OBJECTS), grants.keySet(),
            INVOICE_DOCS_SET + ' grants exactly the Invoice Batch Run chain');
        for (ObjectPermissions op : grants.values()) {
            Assert.isTrue(op.PermissionsRead && op.PermissionsViewAllRecords,
                op.SobjectType + ': read and View All (Invoice Batch Run is Private)');
            Assert.isFalse(op.PermissionsCreate || op.PermissionsEdit || op.PermissionsDelete
                || op.PermissionsModifyAllRecords, op.SobjectType + ': read only');
        }
    }

    @IsTest
    static void invoiceDocumentsSetGrantsAccessLibraries() {
        PermissionSet ps = [SELECT PermissionsContentWorkspaces FROM PermissionSet WHERE Name = :INVOICE_DOCS_SET];
        Assert.isTrue(ps.PermissionsContentWorkspaces,
            INVOICE_DOCS_SET + ' grants Access Libraries, without which a library member reads none of the template files');
    }

    @IsTest
    static void everyBillingPersonaGroupContainsTheInvoiceDocumentsSet() {
        Set<String> groupsWithSet = new Set<String>();
        for (PermissionSetGroupComponent c : [
            SELECT PermissionSetGroup.DeveloperName FROM PermissionSetGroupComponent
            WHERE PermissionSet.Name = :INVOICE_DOCS_SET
        ]) {
            groupsWithSet.add(c.PermissionSetGroup.DeveloperName);
        }
        Assert.isTrue(groupsWithSet.containsAll(new Set<String>{ ADMIN_GROUP, OPERATIONS_GROUP }),
            'Each billing persona group contains ' + INVOICE_DOCS_SET + '; found in: ' + groupsWithSet);
    }

    // ---- Invoice Batch Run read --------------------------------------------------------------

    @IsTest
    static void billingAdminRoleWithInvoiceDocumentsSetReadsInvoiceBatchRuns() {
        assertReadsRuns(ADMIN_ROLE);
        // Only a note: the role alone is expected to be refused today, and the set is why the persona reads.
        User roleOnly = user(new List<String>{ ADMIN_ROLE }, null, new List<String>{ BILLING_PSL });
        System.runAs(roleOnly) {
            if (unreadable(BATCH_RUN_OBJECTS).isEmpty()) {
                System.debug(LoggingLevel.WARN, 'NOTE: the managed Billing Admin set now reads Invoice Batch Run;'
                    + ' ' + INVOICE_DOCS_SET + ' may no longer be needed for that read.');
            }
        }
    }

    @IsTest
    static void billingOperationsRoleWithInvoiceDocumentsSetReadsInvoiceBatchRuns() {
        assertReadsRuns(OPERATIONS_ROLE);
    }

    @IsTest
    static void billingAdminGroupReadsInvoiceBatchRuns() {
        assertGroupReadsRuns(ADMIN_GROUP);
    }

    @IsTest
    static void billingOperationsGroupReadsInvoiceBatchRuns() {
        assertGroupReadsRuns(OPERATIONS_GROUP);
    }

    // ---- Document generation -----------------------------------------------------------------

    @IsTest
    static void billingAdminWithBothDocGenSetsHasBatchAndOnDemandAccess() {
        assertDocGenAccess(ADMIN_ROLE);
    }

    @IsTest
    static void billingOperationsWithBothDocGenSetsHasBatchAndOnDemandAccess() {
        assertDocGenAccess(OPERATIONS_ROLE);
    }

    // ---- helpers -----------------------------------------------------------------------------

    private static void assertReadsRuns(String roleSet) {
        User u = user(new List<String>{ roleSet, INVOICE_DOCS_SET }, null, new List<String>{ BILLING_PSL });
        System.runAs(u) {
            List<String> failures = unreadable(BATCH_RUN_OBJECTS);
            Assert.isTrue(failures.isEmpty(), roleSet + ' + ' + INVOICE_DOCS_SET
                + ': Invoice Batch Run reads refused:\n' + String.join(failures, '\n'));
        }
    }

    private static void assertGroupReadsRuns(String groupName) {
        List<PermissionSetGroup> groups = [SELECT Id, Status FROM PermissionSetGroup WHERE DeveloperName = :groupName];
        Assert.areEqual(1, groups.size(), groupName + ' is deployed with this class (unpackaged/post_personas)');
        Assert.areNotEqual('Failed', groups[0].Status,
            groupName + ' failed to recalculate, so its holders do not get its permissions');
        if (groups[0].Status != 'Updated') {
            // Updating or Outdated: a deploy that changes the group leaves it Updating.
            System.debug(LoggingLevel.WARN, 'SKIPPED, NOT CHECKED: ' + groupName + ' is ' + groups[0].Status
                + ', not Updated, so it cannot be assigned; rerun this test once the group is Updated.');
            return;
        }
        System.debug(LoggingLevel.WARN, 'CHECKED: ' + groupName + ' is Updated; asserting its Invoice Batch Run reads.');
        User u = user(new List<String>(), groups[0].Id, new List<String>{ BILLING_PSL });
        System.runAs(u) {
            List<String> failures = unreadable(BATCH_RUN_OBJECTS);
            Assert.isTrue(failures.isEmpty(), groupName + ': Invoice Batch Run reads refused:\n' + String.join(failures, '\n'));
        }
    }

    private static void assertDocGenAccess(String roleSet) {
        User u = user(new List<String>{ roleSet, INVOICE_DOCS_SET, DOCGEN_USER, DOCGEN_DESIGNER }, null,
            new List<String>{ BILLING_PSL, DOCGEN_PSL });
        List<String> failures = new List<String>();
        System.runAs(u) {
            Database.SaveResult batch = Database.insert(new DocGenerationBatchProcess(), false, AccessLevel.USER_MODE);
            if (!batch.isSuccess()) {
                failures.add('batch process create: ' + batch.getErrors()[0].getMessage());
            }
            if (!Schema.SObjectType.DocumentGenerationProcess.isCreateable()) {
                failures.add('Document Generation Process create (on-demand generation)');
            }
            if (!Schema.SObjectType.DocumentTemplate.isAccessible()) {
                failures.add('Document Template read');
            }
            failures.addAll(unreadable(BATCH_RUN_OBJECTS));
        }
        Assert.isTrue(failures.isEmpty(), roleSet + ': invoice document generation access missing:\n'
            + String.join(failures, '\n'));

        // Only a note: DocGen User alone is expected to be refused the batch create today.
        User docGenUserOnly = user(new List<String>{ roleSet, INVOICE_DOCS_SET, DOCGEN_USER }, null,
            new List<String>{ BILLING_PSL, DOCGEN_PSL });
        System.runAs(docGenUserOnly) {
            if (Database.insert(new DocGenerationBatchProcess(), false, AccessLevel.USER_MODE).isSuccess()) {
                System.debug(LoggingLevel.WARN, 'NOTE: ' + roleSet + ' with DocGen User alone created a batch process;'
                    + ' DocGen Designer may no longer be needed.');
            }
        }
    }

    private static List<String> unreadable(List<String> objectNames) {
        List<String> failures = new List<String>();
        for (String objectName : objectNames) {
            try {
                Database.countQuery('SELECT COUNT() FROM ' + objectName + ' WITH USER_MODE');
            } catch (Exception e) {
                failures.add(objectName + ': ' + e.getMessage());
            }
        }
        return failures;
    }

    // A Minimum Access user holding the given licenses, permission sets and (optionally) group.
    private static User user(List<String> permissionSets, Id groupId, List<String> licenses) {
        Map<String, Id> setIds = new Map<String, Id>();
        for (PermissionSet ps : [SELECT Id, Name FROM PermissionSet WHERE Name IN :permissionSets]) {
            setIds.put(ps.Name, ps.Id);
        }
        for (String name : permissionSets) {
            Assert.isTrue(setIds.containsKey(name), 'Permission set not in this org: ' + name);
        }
        List<PermissionSetLicense> psls = [SELECT Id FROM PermissionSetLicense WHERE DeveloperName IN :licenses];
        Assert.areEqual(licenses.size(), psls.size(), 'Permission set license missing from this org: ' + licenses);
        List<Profile> profiles = [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
        Assert.areEqual(1, profiles.size(), 'This test needs the English standard profile "Minimum Access - Salesforce"');

        String stamp = String.valueOf(Crypto.getRandomInteger()).remove('-');
        User u = new User(
            ProfileId = profiles[0].Id,
            LastName = 'BillingDocs',
            Email = 'rlm.billingdocs@example.com',
            Username = 'rlm.billingdocs.' + stamp + '@example.com',
            Alias = 'rlmbdoc',
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
            if (groupId != null) {
                psas.add(new PermissionSetAssignment(AssigneeId = u.Id, PermissionSetGroupId = groupId));
            }
            insert psas;
        }
        return u;
    }
}
