/**
 * What a billing persona (RLM Billing Admin, RLM Billing Operations) needs to generate invoice
 * documents, batch (Generate Invoice Documents on an Invoice Batch Run) and on demand (Generate
 * Invoice Document on an Invoice), proved as that persona (todo 292).
 *
 * Measured on a 264 org as Minimum Access users holding the Billing license and a persona group:
 * - Neither group reaches Document Template, Document Generation Process or Document Generation
 *   Batch Process ("Access to entity ... denied"): the managed billing role sets carry no DocGen
 *   access. The DocGen sets need the DocGen Designer permission set license, so they are assigned
 *   next to the group, never put in it (a group containing a licensed set fails to deploy while a
 *   holder lacks the license: measured for Billing Advanced in todo 452, assumed for this one).
 * - With DocGen User the persona reads templates and may create a Document Generation Process (on
 *   demand) but not a Document Generation Batch Process ("DML operation INSERT not allowed on
 *   DocGenerationBatchProcess"), the create behind batch generation. DocGen Designer grants it;
 *   object create on that object in a custom set does not (measured: the insert is still refused).
 * - The managed Billing Admin set has no access to Invoice Batch Run, the record the batch action
 *   runs from; the managed Billing Operations set reads it. RLM_BillingInvoiceDocuments, in both
 *   groups, grants it with View All (the object is Private).
 * - The invoice template's file is in the Docgen Document Template Library and is read as the
 *   generating user. A persona reads it as a library member (create_docgen_library makes every
 *   internal user one, through the RLM_DocGen_Template_Users group) that also has Access Libraries
 *   (ContentWorkspaces), which the Minimum Access profile lacks; RLM_BillingInvoiceDocuments grants it.
 *
 * Admin tests prove nothing here: System Administrator bypasses object access. Each user takes a
 * seat of every license it is given, so an org with no free Billing or DocGen Designer seat fails
 * these tests on the license, not on access.
 */
@IsTest
private class RLM_BillingInvoiceDocumentsAccessTest {

    private static final String BILLING_PSL = 'RevLifecycleMgmtBillingPsl';
    private static final String DOCGEN_PSL = 'DocGenDesignerPsl';
    private static final String INVOICE_DOCS_SET = 'RLM_BillingInvoiceDocuments';
    private static final String DOCGEN_USER = 'DocGenUser';
    private static final String DOCGEN_DESIGNER = 'DocGenDesigner';
    private static final String TEMPLATE_LIBRARY = 'DocgenDocumentTemplateLibrary';
    private static final String DEFAULT_INVOICE_TEMPLATE = 'DefaultInvoiceTemplate';

    // Each persona group and the managed role set it is built on.
    private static final Map<String, String> ROLE_SET_BY_GROUP = new Map<String, String>{
        'RLM_Billing_Admin' => 'RevenueLifecycleManagementBillingAdmin',
        'RLM_Billing_Operations' => 'RevenueLifecycleManagementBillingOperations'
    };
    // Read on Invoice Batch Run needs read on the scheduler, and that needs read on a run-criteria
    // object (deploy-enforced), so all three are checked.
    private static final List<String> BATCH_RUN_OBJECTS = new List<String>{
        'InvoiceBatchRun', 'BillingBatchScheduler', 'InvoiceBatchRunCriteria'
    };

    // ---- Invoice Batch Run read -------------------------------------------------------------

    @IsTest
    static void billingAdminRoleAloneCannotReadInvoiceBatchRuns() {
        User u = user(new List<String>{ ROLE_SET_BY_GROUP.get('RLM_Billing_Admin') }, null,
            new List<String>{ BILLING_PSL });
        System.runAs(u) {
            Assert.isFalse(unreadable(BATCH_RUN_OBJECTS).isEmpty(),
                'The managed Billing Admin set now reads Invoice Batch Run; RLM_BillingInvoiceDocuments may no longer be needed for it');
        }
    }

    @IsTest
    static void invoiceDocumentsSetGivesEachBillingRoleTheRunReads() {
        List<String> failures = new List<String>();
        for (String roleSet : ROLE_SET_BY_GROUP.values()) {
            User u = user(new List<String>{ roleSet, INVOICE_DOCS_SET }, null, new List<String>{ BILLING_PSL });
            System.runAs(u) {
                for (String failure : unreadable(BATCH_RUN_OBJECTS)) {
                    failures.add(roleSet + ' + ' + INVOICE_DOCS_SET + ': ' + failure);
                }
            }
        }
        Assert.isTrue(failures.isEmpty(), 'Invoice Batch Run reads refused:\n' + String.join(failures, '\n'));
    }

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
        Assert.isTrue(groupsWithSet.containsAll(ROLE_SET_BY_GROUP.keySet()),
            'Each billing persona group contains ' + INVOICE_DOCS_SET + '; found in: ' + groupsWithSet);
    }

    @IsTest
    static void everyBillingPersonaGroupReadsInvoiceBatchRuns() {
        List<String> failures = new List<String>();
        for (String groupName : ROLE_SET_BY_GROUP.keySet()) {
            PermissionSetGroup g = assignableGroup(groupName);
            if (g == null) {
                continue;
            }
            System.runAs(user(new List<String>(), g.Id, new List<String>{ BILLING_PSL })) {
                for (String failure : unreadable(BATCH_RUN_OBJECTS)) {
                    failures.add(groupName + ': ' + failure);
                }
            }
        }
        Assert.isTrue(failures.isEmpty(), 'Invoice Batch Run reads refused:\n' + String.join(failures, '\n'));
    }

    // ---- Document generation ----------------------------------------------------------------

    @IsTest
    static void docGenUserAloneCannotStartBatchGeneration() {
        for (String roleSet : ROLE_SET_BY_GROUP.values()) {
            System.runAs(persona(roleSet, new List<String>{ DOCGEN_USER })) {
                Database.SaveResult result = Database.insert(new DocGenerationBatchProcess(), false, AccessLevel.USER_MODE);
                Assert.isFalse(result.isSuccess(),
                    roleSet + ' with DocGen User created a batch process; DocGen Designer may no longer be needed');
            }
        }
    }

    @IsTest
    static void billingPersonaWithBothDocGenSetsHasBatchAndOnDemandAccess() {
        List<String> failures = new List<String>();
        for (String roleSet : ROLE_SET_BY_GROUP.values()) {
            System.runAs(persona(roleSet, new List<String>{ DOCGEN_USER, DOCGEN_DESIGNER })) {
                Database.SaveResult batch = Database.insert(new DocGenerationBatchProcess(), false, AccessLevel.USER_MODE);
                if (!batch.isSuccess()) {
                    failures.add(roleSet + ': batch process create: ' + batch.getErrors()[0].getMessage());
                }
                if (!Schema.SObjectType.DocumentGenerationProcess.isCreateable()) {
                    failures.add(roleSet + ': Document Generation Process create (on-demand generation)');
                }
                if (!Schema.SObjectType.DocumentTemplate.isAccessible()) {
                    failures.add(roleSet + ': Document Template read');
                }
                failures.addAll(prefixed(roleSet + ': ', unreadable(BATCH_RUN_OBJECTS)));
            }
        }
        Assert.isTrue(failures.isEmpty(), 'Invoice document generation access missing:\n' + String.join(failures, '\n'));
    }

    // The default invoice template's file is read as the generating user, and it sits in the template
    // library, so a persona reads it as a library member with Access Libraries. The build makes every
    // internal user a member through the RLM_DocGen_Template_Users group (create_docgen_library); in a
    // test that membership does not reach a user created in the same test (measured on a 264 org: such
    // a user read none of the files through a group holding All Internal Users, while an existing user
    // read them), so the test makes each user a direct read-only member. The control user is the same
    // persona without RLM_BillingInvoiceDocuments: as a member it still reads nothing, so the set's
    // Access Libraries is what opens the file. SeeAllData: the template, its file and the library are
    // org data.
    @IsTest(SeeAllData=true)
    static void billingPersonaReadsTheInvoiceTemplateFileAsALibraryMember() {
        List<DocumentTemplate> templates = [
            SELECT Id FROM DocumentTemplate WHERE Name = :DEFAULT_INVOICE_TEMPLATE AND IsActive = true LIMIT 1
        ];
        List<ContentWorkspace> libraries = [SELECT Id FROM ContentWorkspace WHERE DeveloperName = :TEMPLATE_LIBRARY LIMIT 1];
        if (templates.isEmpty() || libraries.isEmpty()) {
            // Billing document generation off, or the running user is not a library member (only
            // members see a library): nothing on this org to check.
            System.debug(LoggingLevel.WARN, 'SKIPPED: no active ' + DEFAULT_INVOICE_TEMPLATE + ' or no visible '
                + TEMPLATE_LIBRARY + ', so the invoice template file read is not tested.');
            return;
        }
        Set<Id> fileIds = new Set<Id>();
        for (DocumentTemplateContentDoc doc : [
            SELECT ContentDocumentId, ContentDocument.ParentId FROM DocumentTemplateContentDoc
            WHERE DocumentTemplateId = :templates[0].Id
        ]) {
            Assert.areEqual(libraries[0].Id, doc.ContentDocument.ParentId,
                'The default invoice template file is in ' + TEMPLATE_LIBRARY + ', so library access covers it');
            fileIds.add(doc.ContentDocumentId);
        }
        Assert.isFalse(fileIds.isEmpty(), DEFAULT_INVOICE_TEMPLATE + ' has a template file');

        List<String> failures = new List<String>();
        for (String roleSet : ROLE_SET_BY_GROUP.values()) {
            User u = persona(roleSet, new List<String>{ DOCGEN_USER, DOCGEN_DESIGNER });
            User control = user(new List<String>{ roleSet, DOCGEN_USER, DOCGEN_DESIGNER }, null,
                new List<String>{ BILLING_PSL, DOCGEN_PSL });
            makeLibraryReaders(libraries[0].Id, new List<Id>{ u.Id, control.Id });
            System.runAs(u) {
                Integer files = templateFilesRead(fileIds);
                if (files != fileIds.size()) {
                    failures.add(roleSet + ': read ' + files + ' of ' + fileIds.size() + ' template file(s)');
                }
                if ([SELECT COUNT() FROM DocumentTemplate WHERE Id = :templates[0].Id WITH USER_MODE] != 1) {
                    failures.add(roleSet + ': ' + DEFAULT_INVOICE_TEMPLATE + ' not readable');
                }
            }
            System.runAs(control) {
                Integer files = templateFilesRead(fileIds);
                if (files != 0) {
                    failures.add(roleSet + ' without ' + INVOICE_DOCS_SET + ': read ' + files
                        + ' template file(s); Access Libraries may no longer be needed');
                }
            }
        }
        Assert.isTrue(failures.isEmpty(), 'Invoice template access:\n' + String.join(failures, '\n'));
    }

    // ---- helpers ----------------------------------------------------------------------------

    // A persona as the groups make it (the role set plus RLM_BillingInvoiceDocuments; the group's
    // field-access set is not involved here), with the DocGen sets assigned next to it.
    private static User persona(String roleSet, List<String> docGenSets) {
        List<String> sets = new List<String>{ roleSet, INVOICE_DOCS_SET };
        sets.addAll(docGenSets);
        return user(sets, null, new List<String>{ BILLING_PSL, DOCGEN_PSL });
    }

    // The group, or null (with a visible skip) when it cannot be assigned: a release or deploy can
    // leave a group Outdated or Updating until it is recalculated.
    private static PermissionSetGroup assignableGroup(String groupName) {
        List<PermissionSetGroup> groups = [SELECT Id, Status FROM PermissionSetGroup WHERE DeveloperName = :groupName];
        Assert.areEqual(1, groups.size(), groupName + ' is deployed with this class (unpackaged/post_personas)');
        if (groups[0].Status != 'Updated') {
            System.debug(LoggingLevel.WARN, 'SKIPPED: ' + groupName + ' is ' + groups[0].Status
                + ', not Updated, so it cannot be assigned; recalculate it to run this check.');
            return null;
        }
        return groups[0];
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

    private static List<String> prefixed(String prefix, List<String> lines) {
        List<String> out = new List<String>();
        for (String line : lines) {
            out.add(prefix + line);
        }
        return out;
    }

    private static Integer templateFilesRead(Set<Id> fileIds) {
        return [SELECT COUNT() FROM ContentVersion WHERE ContentDocumentId IN :fileIds AND IsLatest = true WITH USER_MODE];
    }

    // Read-only library membership: a library permission with every flag off, as create_docgen_library
    // gives its group.
    private static void makeLibraryReaders(Id libraryId, List<Id> userIds) {
        String stamp = String.valueOf(Crypto.getRandomInteger()).remove('-');
        System.runAs(new User(Id = UserInfo.getUserId())) {
            ContentWorkspacePermission viewer = new ContentWorkspacePermission(
                Name = 'RLM Test Template Viewer ' + stamp,
                PermissionsManageWorkspace = false, PermissionsAddContent = false, PermissionsAddContentOBO = false,
                PermissionsArchiveContent = false, PermissionsDeleteContent = false, PermissionsFeatureContent = false,
                PermissionsViewComments = false, PermissionsAddComment = false, PermissionsModifyComments = false,
                PermissionsTagContent = false, PermissionsDeliverContent = false, PermissionsChatterSharing = false,
                PermissionsOrganizeFileAndFolder = false
            );
            insert viewer;
            List<ContentWorkspaceMember> members = new List<ContentWorkspaceMember>();
            for (Id userId : userIds) {
                members.add(new ContentWorkspaceMember(
                    ContentWorkspaceId = libraryId, MemberId = userId, ContentWorkspacePermissionId = viewer.Id));
            }
            insert members;
        }
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
