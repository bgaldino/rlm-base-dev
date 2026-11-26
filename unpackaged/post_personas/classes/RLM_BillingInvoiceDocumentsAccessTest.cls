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
 * - the group itself: the *Group* methods. A group that is not Updated cannot be assigned. Inside a
 *   deploy that changes the group it reads Outdated (measured on a 264 org), and an API edit of its
 *   components leaves it Updating for a while (seen in todo 292's earlier work), so these skip (with
 *   a "SKIPPED, NOT CHECKED" WARN debug line) and then prove nothing. A Failed group fails the test.
 * - the managed role set plus RLM_BillingInvoiceDocuments (the group's content, minus its
 *   field-access set): the Invoice Batch Run reads and the DocGen access.
 * - the set's metadata: View All on the run chain, Access Libraries, and membership of both groups.
 * The Billing Operations run-read methods are regression checks: the managed Operations set already
 * reads the runs, and the View All the set adds is checked only by the metadata test.
 * Nothing here fails because Salesforce grants MORE than today: the only such note (DocGen User
 * gaining the DocGen Designer permission) reads metadata and creates no user.
 * The batch process insert is real, because only it meets the DocGen Designer user-permission gate.
 * Batch generation needs two org settings (DocumentGenerationSetting.IsBatchDocGnrnEnabled and
 * IsServerSideDocGenEnabled), which deploy with docgen, not personas. The test reads them first. With
 * both on, any refusal of the insert fails. Otherwise, or with no setting row, only INVALID_INPUT is a
 * "SKIPPED, NOT CHECKED" WARN line and any other code fails. Measured on a 264 org: with batch off the
 * persona gets INVALID_INPUT "Enable the batch document generation setting.", and with batch on and
 * server-side off (client-side mechanism) INVALID_INPUT "Enable the server-side document generation
 * setting."; in both, a user without DocGen Designer still gets CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY,
 * because the access checks answer first. The other settings do not matter here (measured): with both
 * flags on, the insert succeeds with the client-side generation mechanism and with an hourly batch
 * limit of 0. The measured org has one setting row and Help speaks of "a Document Generation Setting
 * record"; one row is not guaranteed, so the query orders by CreatedDate and reads the oldest. batchRefusalSkipsOnlyForInvalidInputWithBatchOff and
 * batchGenerationNeedsBothSettings pin the split by status code and settings, not by message text.
 *
 * Admin tests prove nothing here: System Administrator bypasses object access. Each test user needs
 * a Salesforce user license and takes a seat of every permission set license it is given (Billing;
 * DocGen Designer for the DocGen checks); no method creates more than one user. An org with no
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
            INVOICE_DOCS_SET + ' grants Access Libraries, without which a library member did not read the default invoice template file (measured)');
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
            // Outdated inside a deploy that changes the group (measured); Updating after an API edit of its components.
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
        Boolean batchEnabled = batchGenerationEnabled(
            [SELECT IsBatchDocGnrnEnabled, IsServerSideDocGenEnabled FROM DocumentGenerationSetting
             ORDER BY CreatedDate LIMIT 1]);
        List<String> failures = new List<String>();
        System.runAs(u) {
            // A real insert, because only it meets the DocGen Designer user-permission gate (describe
            // does not show it). With batch or server-side generation off it is refused for configuration
            // (see skipsBatchRefusal); those settings deploy with docgen, this class with personas.
            Database.SaveResult batch = Database.insert(new DocGenerationBatchProcess(), false, AccessLevel.USER_MODE);
            if (!batch.isSuccess()) {
                Database.Error error = batch.getErrors()[0];
                String statusCode = String.valueOf(error.getStatusCode());
                if (skipsBatchRefusal(batchEnabled, statusCode)) {
                    System.debug(LoggingLevel.WARN, 'SKIPPED, NOT CHECKED: ' + roleSet + ' batch process create:'
                        + ' batch or server-side document generation is off (' + statusCode + ': ' + error.getMessage() + ').'
                        + ' The access checks run before that one, so the DocGen Designer gate already passed;'
                        + ' the create itself was not checked.');
                } else {
                    failures.add('batch process create (batch generation settings '
                        + (batchEnabled ? 'on' : 'off') + '): ' + statusCode + ': ' + error.getMessage());
                }
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
    }

    // Batch generation is on only when the org has a setting row with both batch and server-side
    // generation on. Measured on a 264 org: either one off makes the persona's insert INVALID_INPUT.
    // (Batch on with server-side off and the server-side mechanism is refused at deploy: "To select
    // Server-Side for the Generation Mechanism, you must select the ServerSide Docgen Enabled option.")
    @TestVisible
    private static Boolean batchGenerationEnabled(List<DocumentGenerationSetting> settings) {
        return !settings.isEmpty() && settings[0].IsBatchDocGnrnEnabled && settings[0].IsServerSideDocGenEnabled;
    }

    @IsTest
    static void batchGenerationNeedsBothSettings() {
        Assert.isFalse(batchGenerationEnabled(new List<DocumentGenerationSetting>()), 'no setting row counts as off');
        Assert.isTrue(batchGenerationEnabled(new List<DocumentGenerationSetting>{ setting(true, true) }), 'both on');
        Assert.isFalse(batchGenerationEnabled(new List<DocumentGenerationSetting>{ setting(false, true) }), 'batch off (measured)');
        Assert.isFalse(batchGenerationEnabled(new List<DocumentGenerationSetting>{ setting(true, false) }), 'server-side off (measured)');
    }

    // An in-memory row, as the query would return it (never inserted).
    private static DocumentGenerationSetting setting(Boolean batch, Boolean serverSide) {
        return new DocumentGenerationSetting(IsBatchDocGnrnEnabled = batch, IsServerSideDocGenEnabled = serverSide);
    }

    // Whether a refused batch process insert is a visible skip rather than a failure: only INVALID_INPUT
    // with batch generation off (see batchGenerationEnabled). Measured on a 264 org with the setting
    // off: a user without DocGen Designer still gets CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY (the access
    // check answers first), and the persona with DocGen Designer gets INVALID_INPUT "Enable the batch
    // document generation setting.". With the setting on the persona's insert succeeds, so any refusal
    // then is a regression. Decided by status code and setting only, never by message text.
    @TestVisible
    private static Boolean skipsBatchRefusal(Boolean batchEnabled, String statusCode) {
        return batchEnabled != true && statusCode == 'INVALID_INPUT';
    }

    @IsTest
    static void batchRefusalSkipsOnlyForInvalidInputWithBatchOff() {
        // Measured on a 264 org: batch off, or server-side off, persona with DocGen Designer.
        Assert.isTrue(skipsBatchRefusal(false, 'INVALID_INPUT'), 'batch generation off is configuration');
        // Measured on a 264 org: access refusals, setting on or off.
        Assert.isFalse(skipsBatchRefusal(false, 'CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY'), 'access refusal with the setting off');
        Assert.isFalse(skipsBatchRefusal(true, 'CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY'), 'access refusal with the setting on');
        // Not measured (synthetic): with the setting on nothing skips, and other codes never skip.
        Assert.isFalse(skipsBatchRefusal(true, 'INVALID_INPUT'), 'setting on: any refusal fails');
        Assert.isFalse(skipsBatchRefusal(false, 'INSUFFICIENT_ACCESS_OR_READONLY'), 'synthetic access code');
        Assert.isFalse(skipsBatchRefusal(false, 'UNKNOWN_EXCEPTION'), 'synthetic unknown error');
    }

    // Metadata only, no user: a note if DocGen User starts carrying the DocGen Designer permission.
    @IsTest
    static void docGenUserDesignerPermissionNote() {
        List<PermissionSet> sets = [SELECT PermissionsDocGenDesigner FROM PermissionSet WHERE Name = :DOCGEN_USER];
        if (!sets.isEmpty() && sets[0].PermissionsDocGenDesigner) {
            System.debug(LoggingLevel.WARN, 'NOTE: DocGenUser now carries the DocGen Designer permission;'
                + ' DocGenDesigner may no longer be needed for the batch create.');
        }
        Assert.areEqual(1, sets.size(), 'DocGenUser is in this org (it ships with the DocGen Designer license)');
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
