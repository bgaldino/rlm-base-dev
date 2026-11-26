/**
 * Tests for RLM_AccountUtilities.delAccountRelatedObjects. The reset is for admins only:
 * a user without both Modify All Data and View All Data is refused before anything is
 * read or changed. The refusal tests run, with System.runAs, as users built from
 * profiles picked by those permissions (and, for View All Data alone, a permission
 * set); every other test that resets runs as the running user, and skips, with the
 * reason logged, when the running user lacks either.
 *
 * WHAT IS WORTH TESTING HERE
 * --------------------------
 * The class has exactly one public entry point and a few dozen private helpers,
 * so the only contract a test can hold it to is the invocable's own: the input
 * guards, which categories of record each flag is allowed to delete, and the
 * Result it reports. That flag gating is also the part that has actually broken
 * -- AssetRateCardEntry rows were once removed while the asset was kept, leaving
 * a usage asset that could never rate again -- so it is where the assertions
 * are concentrated.
 *
 * AVOIDING A VACUOUS PASS
 * -----------------------
 * Every deletion test asserts its PRECONDITION first: that the record really
 * exists before the reset runs. Without that, a setup failure would leave
 * nothing to delete and the "it was deleted" assertion would pass for the wrong
 * reason -- the class of defect this repository produces most often, where a
 * check silently validates an empty set.
 *
 * COVERAGE
 * --------
 * Salesforce enforces 75% across ALL Apex in the org for a production deploy,
 * not per class, so this class's figure does not by itself block a deploy.
 * The usage tests build entitlement accounts, entitlements and buckets
 * (newEntitlementAccount, newEntitlement and newBucket, over loadUsageFixture).
 * Among the paths these tests do not reach, and why:
 *  - Deletes of the other usage rows (entries, billing period items, summaries,
 *    journals, commitment junction rows), asset rate card entries and the
 *    fulfillment records: no fixtures, so they run against empty sets.
 *  - The entitlement-side bottom-up retry (deleteTransactionUsageEntitlement) is
 *    reached, with another account's entitlement under the account's bucket: it
 *    deletes only the account's own entitlements, and keeps (and reports) a bucket
 *    that holds another account's, and the buckets above it. The same holds for the
 *    entitlement-account retry and the asset step's bucket walk.
 *  - The asset step's entitlement-account delete: in these fixtures phase 2's
 *    entitlement-account retry has already removed them.
 *  - An unexpected exception in phase 1. (Running out of rows, statements or queries
 *    in either phase is reached, with the limits lowered or spent down.)
 *
 * Three objects cannot be created in a unit test at all: Invoice and
 * BillingScheduleGroup are createable=false, and a CreditMemo's required
 * BillingAccountId and Status are not createable. So deleting invoices and
 * credit memos can only be verified live. The tests here cover what surrounds
 * it: the permission check that decides whether posted invoices go, payments
 * being kept and reported, and the documents cleanup. Nor can a test post a
 * debit memo, which needs a tax treatment on every line, so keeping posted and
 * void debit memos is verified live too.
 *
 * The live verification that covers rated usage (summaries, entries,
 * journals) is scripts/apex/validateRatedUsage.apex plus the usage-consumption
 * skill; the DeleteAssets gating below was additionally confirmed end-to-end
 * against a real rated asset with AssetRateCardEntry rows.
 */
@IsTest
private without sharing class RLM_AccountUtilitiesTest {
    // `without sharing` per .cursor/rules/apex-classes.mdc, which requires an explicit
    // keyword on every class. It matches the class under test: RLM_AccountUtilities is
    // itself declared `without sharing`, deliberately, so that the reset can clear an
    // account's entire related graph including records owned by other users. Declaring
    // this entry point `with sharing` (or `inherited sharing`, which behaves as
    // `with sharing` at an entry point) would not change the utility's own context —
    // it pins its own — but it would make the fixtures run under sharing while the
    // code under test does not, which is a needless divergence from how the demo
    // reset actually runs.

    private static Account newAccount() {
        Account a = new Account(Name = 'RLM Utilities Test Account');
        insert a;
        return a;
    }

    private static Opportunity newOpportunity(Id accountId, String name) {
        Opportunity o = new Opportunity(
            Name = name,
            AccountId = accountId,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert o;
        return o;
    }

    private static Id seedAccountWithContracts() {
        Account account = newAccount();
        Product2 product = new Product2(
            Name = 'RLM Reset Test Product',
            IsActive = true
        );
        insert product;

        Date contractStart = Date.today().addDays(-7);
        Contract priced = new Contract(
            AccountId = account.Id,
            StartDate = contractStart,
            ContractTerm = 12,
            Status = 'Draft'
        );
        Contract unpriced = new Contract(
            AccountId = account.Id,
            StartDate = contractStart,
            ContractTerm = 12,
            Status = 'Draft'
        );
        insert new List<Contract>{ priced, unpriced };

        SObject cip = Schema.getGlobalDescribe().get('ContractItemPrice').newSObject();
        cip.put('ContractId', priced.Id);
        cip.put('ItemId', product.Id);
        cip.put('StartDate', System.now());
        cip.put('Price', 100.0);
        insert cip;
        return account.Id;
    }

    // Processed is the status a payment ends in, and the one that cannot be deleted.
    private static Payment newProcessedPayment(Id accountId) {
        Payment p = new Payment(
            AccountId = accountId,
            Amount = 10,
            Status = 'Processed',
            Type = 'Sale',
            ProcessingMode = 'External'
        );
        insert p;
        return p;
    }

    private static Id newFile(String title, Id parentId) {
        ContentVersion version = new ContentVersion(
            Title = title,
            PathOnClient = title + '.txt',
            VersionData = Blob.valueOf(title),
            FirstPublishLocationId = parentId
        );
        insert version;
        return [SELECT ContentDocumentId FROM ContentVersion WHERE Id = :version.Id].ContentDocumentId;
    }

    private static RLM_AccountUtilities.InputVariables request(
        Id accountId, Boolean deleteAssets, Boolean deleteFulfillment, Boolean deleteBilling
    ) {
        RLM_AccountUtilities.InputVariables iv = new RLM_AccountUtilities.InputVariables();
        iv.accountId = accountId;
        iv.DeleteAssets = deleteAssets;
        iv.DeleteFulfillment = deleteFulfillment;
        iv.DeleteBilling = deleteBilling;
        return iv;
    }

    // The reset is for admins only, and the tests run it as the running user, as the
    // deploying user, who holds the org's Revenue Cloud permission set licenses and sets
    // that the reset's reads need. A test that resets starts with runnerIsAdmin(): a
    // runner without Modify All Data and View All Data skips it, with the reason logged,
    // as a test skips where Collections or Contract Pricing is not enabled. An Apex
    // deploy user is in practice an org admin, so the tests run.
    private static Boolean runnerIsAdmin() {
        UserPermissionAccess access = [
            SELECT PermissionsModifyAllData, PermissionsViewAllData FROM UserPermissionAccess LIMIT 1
        ];
        Boolean admin = access.PermissionsModifyAllData == true && access.PermissionsViewAllData == true;
        if (!admin) {
            skipped('the running user lacks Modify All Data or View All Data, and the reset is for admins only');
        }
        return admin;
    }

    private static void skipped(String reason) {
        System.debug(LoggingLevel.WARN, 'RLM_AccountUtilitiesTest: skipped, ' + reason);
    }

    private static RLM_AccountUtilities.Result run(RLM_AccountUtilities.InputVariables iv) {
        List<RLM_AccountUtilities.Result> results = RLM_AccountUtilities.delAccountRelatedObjects(
            new List<RLM_AccountUtilities.InputVariables>{ iv }
        );
        System.assertEquals(1, results.size(), 'One request must return one Result');
        return results[0];
    }

    // How a summary names `count` rows of an object.
    private static String entry(Schema.SObjectType type, Integer count) {
        return type.getDescribe().getLabelPlural() + ': ' + count;
    }

    private static String entry(String objectName, Integer count) {
        return entry(Schema.getGlobalDescribe().get(objectName), count);
    }

    private static Boolean available(List<String> objectNames) {
        Map<String, Schema.SObjectType> types = Schema.getGlobalDescribe();
        for (String objectName : objectNames) {
            if (!types.containsKey(objectName)) {
                return false;
            }
        }
        return true;
    }

    // Collection plans, disputes and debit memos are created by name, as the class
    // queries them, so this class still compiles in an org without them.
    private static SObject newRecord(String objectName, Map<String, Object> values) {
        SObject record = Schema.getGlobalDescribe().get(objectName).newSObject();
        for (String field : values.keySet()) {
            record.put(field, values.get(field));
        }
        insert record;
        return record;
    }

    private static Integer countOf(String objectName, Id recordId) {
        return Database.countQuery('SELECT COUNT() FROM ' + objectName + ' WHERE Id = \'' + recordId + '\'');
    }

    private class UsageFixture {
        Id resourceId;
        Id uomId;
        Id pricebookEntryId;
    }

    private static final String USAGE_PRODUCT = 'RLM Reset Usage Product';
    private static final String RESOURCE_CODE = 'RLM_AU_TEST_UR';

    // Built once for the class, so EVERY test method starts with these rows: an
    // active standard price book, a unit of measure, a usage resource, a product
    // and its standard price book entry. None is linked to an account, so the
    // reset never touches them. The usage and order tests read them back with
    // loadUsageFixture.
    @TestSetup
    static void setupUsageFixture() {
        update new Pricebook2(Id = Test.getStandardPricebookId(), IsActive = true);

        UnitOfMeasureClass uomClass = new UnitOfMeasureClass(
            Name = 'RLM Reset Volume', Code = 'RLM_AU_TEST_UOMC', Type = 'Usage', Status = 'Draft'
        );
        insert uomClass;
        uomClass.Status = 'Active';
        update uomClass;

        UnitOfMeasure uom = new UnitOfMeasure(
            Name = 'RLM Reset Unit', UnitCode = 'RLMAUTU', Type = 'Usage',
            UnitOfMeasureClassId = uomClass.Id, Status = 'Draft'
        );
        insert uom;
        uom.Status = 'Active';
        update uom;

        UsageResource resource = new UsageResource(
            Name = 'RLM Reset Resource', Code = RESOURCE_CODE, Category = 'Usage', Status = 'Draft',
            DefaultUnitOfMeasureId = uom.Id, UnitOfMeasureClassId = uomClass.Id
        );
        insert resource;
        resource.Status = 'Active';
        update resource;

        Product2 product = new Product2(Name = USAGE_PRODUCT, IsActive = true);
        insert product;
        insert new PricebookEntry(
            Pricebook2Id = Test.getStandardPricebookId(), Product2Id = product.Id, UnitPrice = 1, IsActive = true
        );
    }

    private static UsageFixture loadUsageFixture() {
        UsageResource resource = [SELECT Id, DefaultUnitOfMeasureId FROM UsageResource WHERE Code = :RESOURCE_CODE];
        Id standardPricebookId = Test.getStandardPricebookId();
        UsageFixture f = new UsageFixture();
        f.resourceId = resource.Id;
        f.uomId = resource.DefaultUnitOfMeasureId;
        f.pricebookEntryId = [
            SELECT Id FROM PricebookEntry
            WHERE Product2.Name = :USAGE_PRODUCT AND Pricebook2Id = :standardPricebookId
        ].Id;
        return f;
    }

    // ------------------------------------------------------------------ guards

    @IsTest
    static void nullRequestIsANoOp() {
        Test.startTest();
        List<RLM_AccountUtilities.Result> results = RLM_AccountUtilities.delAccountRelatedObjects(null);
        Test.stopTest();
        // The invocable is called by a Flow, where a null input must not surface as an error.
        System.assertEquals(0, results.size(), 'A null request must return quietly, with no Result');
    }

    @IsTest
    static void emptyRequestIsANoOp() {
        Test.startTest();
        List<RLM_AccountUtilities.Result> results = RLM_AccountUtilities.delAccountRelatedObjects(
            new List<RLM_AccountUtilities.InputVariables>()
        );
        Test.stopTest();
        System.assertEquals(0, results.size(), 'An empty request must return quietly, with no Result');
    }

    @IsTest
    static void multipleRequestsAreRejected() {
        Account a = newAccount();
        List<RLM_AccountUtilities.InputVariables> two = new List<RLM_AccountUtilities.InputVariables>{
            request(a.Id, false, false, false),
            request(a.Id, false, false, false)
        };

        Test.startTest();
        Boolean threw = false;
        String message = '';
        try {
            RLM_AccountUtilities.delAccountRelatedObjects(two);
        } catch (IllegalArgumentException e) {
            threw = true;
            message = e.getMessage();
        }
        Test.stopTest();

        System.assert(threw, 'A bulk request must be rejected, not silently half-processed');
        System.assert(
            message.contains('only one request at a time'),
            'Rejection must say why. Got: ' + message
        );
    }

    @IsTest
    static void malformedIdIsReportedNotThrown() {
        if (!runnerIsAdmin()) return;
        RLM_AccountUtilities.InputVariables iv = request(null, true, true, true);
        iv.accountId = 'not-an-id';

        Test.startTest();
        RLM_AccountUtilities.Result result = run(iv);
        Test.stopTest();

        System.assertEquals(false, result.completed, 'A malformed Id must not count as a completed reset');
        System.assertEquals(false, result.cleared, 'A malformed Id must not count as a cleared account');
        System.assert(
            result.reason.startsWith('Not an Account Id'),
            'The flow shows the reason, so it must name the problem. Got: ' + result.reason
        );
    }

    @IsTest
    static void idOfAnotherObjectIsRejected() {
        if (!runnerIsAdmin()) return;
        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(UserInfo.getUserId(), true, true, true));
        Test.stopTest();

        System.assertEquals(false, result.completed, 'A User Id is not an account to reset');
        System.assert(
            result.reason.startsWith('Not an Account Id'),
            'The reason must say the Id is not an account. Got: ' + result.reason
        );
    }

    @IsTest
    static void nullAccountIdIsReportedNotThrown() {
        if (!runnerIsAdmin()) return;
        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(null, true, true, true));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A null Id must not count as a completed reset');
        Assert.areEqual(false, result.cleared, 'A null Id must not count as a cleared account');
        Assert.isTrue(
            result.reason.startsWith('Not an Account Id'),
            'A null Id must be rejected with the guard\'s reason. Got: ' + result.reason
        );
    }

    // ------------------------------------------------------- baseline teardown

    @IsTest
    static void accountWithNoRelatedRecordsRunsClean() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        // Every helper runs against empty result sets. The assertion is that the
        // convergent teardown terminates and the account itself is untouched --
        // the utility clears an account's related records, it never deletes the
        // account.
        System.assertEquals(
            1,
            [SELECT COUNT() FROM Account WHERE Id = :a.Id],
            'The reset must not delete the account it was pointed at'
        );
        System.assertEquals(true, result.completed, 'Nothing to delete is a completed reset');
        System.assertEquals(true, result.cleared, 'Nothing was kept, so the account is cleared');
        System.assertEquals(null, result.reason, 'A completed reset has no reason to report');
        System.assertEquals(null, result.removedSummary, 'Nothing was removed');
        System.assertEquals(null, result.retainedSummary, 'Nothing was kept');
    }

    // ------------------------------------------------- always-deleted category

    @IsTest
    static void opportunitiesAreAlwaysDeleted() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Test Opp');

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'PRECONDITION: the opportunity must exist before the reset runs'
        );

        Test.startTest();
        // All three flags false: opportunity removal is not gated by any of them.
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        System.assertEquals(
            0,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'Opportunities are removed regardless of the DeleteAssets/Fulfillment/Billing flags'
        );
        System.assertEquals(
            entry(Opportunity.SObjectType, 1),
            result.removedSummary,
            'The Result must report what the reset removed'
        );
    }

    // ------------------------------------------------------- DeleteAssets gate

    @IsTest
    static void assetSurvivesWhenDeleteAssetsIsFalse() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Asset asset = new Asset(Name = 'RLM Utilities Test Asset', AccountId = a.Id);
        insert asset;

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id],
            'PRECONDITION: the asset must exist before the reset runs'
        );

        Test.startTest();
        run(request(a.Id, false, true, true));
        Test.stopTest();

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id],
            'DeleteAssets=false must keep the asset. AssetRateCardEntry rows are '
                + 'generated at asset creation and never regenerated for an existing '
                + 'asset, so anything that removes them while keeping the asset '
                + 'leaves a usage asset that can never rate again'
        );
    }

    @IsTest
    static void assetIsRemovedWhenDeleteAssetsIsTrue() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Asset asset = new Asset(Name = 'RLM Utilities Test Asset', AccountId = a.Id);
        insert asset;

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id],
            'PRECONDITION: the asset must exist before the reset runs'
        );

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        System.assertEquals(
            0,
            [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id],
            'DeleteAssets=true must remove the asset'
        );
        System.assert(
            result.removedSummary.contains(entry(Schema.Asset.SObjectType, 1)),
            'The removed asset must be reported. Got: ' + result.removedSummary
        );
    }

    // ------------------------------------------ contracted-price preservation

    private static Boolean contractItemPriceAvailable() {
        return Schema.getGlobalDescribe().containsKey('ContractItemPrice');
    }

    @IsTest
    static void preserveOnKeepsPricedContract() {
        if (!runnerIsAdmin()) return;
        if (!contractItemPriceAvailable()) return;
        Id accountId = seedAccountWithContracts();
        RLM_AccountUtilities.InputVariables iv = request(accountId, true, true, true);
        iv.PreserveContractsWithContractedPrices = true;

        System.assertEquals(
            2,
            [SELECT COUNT() FROM Contract WHERE AccountId = :accountId],
            'PRECONDITION: both contracts must exist before the reset runs'
        );

        Test.startTest();
        run(iv);
        Test.stopTest();

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Contract WHERE AccountId = :accountId],
            'Only the contract with a contracted price should remain'
        );
        System.assertEquals(
            1,
            Database.countQuery(
                'SELECT COUNT() FROM ContractItemPrice WHERE Contract.AccountId = \'' +
                String.escapeSingleQuotes(accountId) + '\''),
            'The contracted price must survive with its contract'
        );
    }

    @IsTest
    static void preserveOffDeletesAllContracts() {
        if (!runnerIsAdmin()) return;
        if (!contractItemPriceAvailable()) return;
        Id accountId = seedAccountWithContracts();
        RLM_AccountUtilities.InputVariables iv = request(accountId, true, true, true);
        iv.PreserveContractsWithContractedPrices = false;

        Test.startTest();
        run(iv);
        Test.stopTest();

        System.assertEquals(
            0,
            [SELECT COUNT() FROM Contract WHERE AccountId = :accountId],
            'Preserve=false must retain the legacy delete-all behavior'
        );
        System.assertEquals(
            0,
            Database.countQuery(
                'SELECT COUNT() FROM ContractItemPrice WHERE Contract.AccountId = \'' +
                String.escapeSingleQuotes(accountId) + '\''),
            'Contracted prices must cascade-delete with their contracts'
        );
    }

    @IsTest
    static void omittedPreserveFlagDeletesAllContracts() {
        if (!runnerIsAdmin()) return;
        if (!contractItemPriceAvailable()) return;
        Id accountId = seedAccountWithContracts();

        Test.startTest();
        run(request(accountId, true, true, true));
        Test.stopTest();

        System.assertEquals(
            0,
            [SELECT COUNT() FROM Contract WHERE AccountId = :accountId],
            'A null preserve flag must behave like preserve=false'
        );
    }

    // ---------------------------------------------------------- Delete Billing

    @IsTest
    static void processedPaymentIsKeptAndReported() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Payment payment = newProcessedPayment(a.Id);

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Payment WHERE Id = :payment.Id],
            'Salesforce does not allow deleting a processed payment, so the reset must leave it'
        );
        System.assertEquals(true, result.completed, 'A kept payment does not stop the reset');
        System.assertEquals(false, result.cleared, 'An account that keeps a payment is not cleared');
        System.assert(
            result.retainedSummary != null && result.retainedSummary.contains(entry(Schema.Payment.SObjectType, 1)),
            'The kept payment must be reported, so the user knows the account is not clean. Got: '
                + result.retainedSummary
        );
    }

    @IsTest
    static void paymentsAreNotReportedWithoutDeleteBilling() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        newProcessedPayment(a.Id);

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, false));
        Test.stopTest();

        // Billing records were not asked for, so keeping them is not news.
        System.assertEquals(true, result.cleared, 'DeleteBilling=false leaves billing out of the reset and its report');
        System.assertEquals(null, result.retainedSummary, 'Nothing the reset was asked to delete was kept');
    }

    @IsTest
    static void postedInvoicePermissionIsReadForTheRunningUser() {
        // A user without admin permissions, picked by permission.
        Profile neither = profileWith(false, false);
        if (neither == null) return;
        User u = newUserFrom(neither, 'rlmrst');

        Boolean minimalUser;
        System.runAs(u) {
            minimalUser = RLM_AccountUtilities.canDeletePostedInvoices();
        }
        System.assertEquals(
            false,
            minimalUser,
            'A user without Delete Invoice and Invoice Lines must not be treated as able to '
                + 'delete posted invoices'
        );

        // The positive case is the running user. A fresh user cannot be given the
        // permission: its user license does not allow BillingInvoiceSuperUser. So the
        // check is compared with what the running user is assigned, which in a
        // billing org (through RLM_RCB) includes it.
        Id me = UserInfo.getUserId();
        Boolean assigned;
        try {
            assigned = Database.countQuery('SELECT COUNT() FROM PermissionSetAssignment WHERE AssigneeId = :me '
                + 'AND PermissionSet.PermissionsBillingInvoiceSuperUser = true') > 0;
        } catch (QueryException e) {
            // A release without the permission: nobody has it.
            assigned = false;
        }
        System.assertEquals(
            assigned,
            RLM_AccountUtilities.canDeletePostedInvoices(),
            'The check must agree with the running user\'s permission set assignments'
        );
    }

    // A Draft debit memo with one line. Draft is the only status one can be created in.
    private static SObject newDebitMemo(Id accountId) {
        SObject memo = newRecord('DebitMemo', new Map<String, Object>{
            'AccountId' => accountId, 'Status' => 'Draft', 'InvoiceGenerationStatus' => 'None'
        });
        newRecord('DebitMemoLine', new Map<String, Object>{
            'Name' => 'RLM Reset Test Line', 'DebitMemoId' => memo.Id, 'ChargeAmount' => 10
        });
        return memo;
    }

    @IsTest
    static void draftAndCanceledDebitMemosAreDeleted() {
        if (!runnerIsAdmin()) return;
        if (!available(new List<String>{ 'DebitMemo', 'DebitMemoLine' })) return;
        Account a = newAccount();
        SObject draft = newDebitMemo(a.Id);
        SObject canceled = newDebitMemo(a.Id);
        canceled.put('Status', 'Canceled');
        update canceled;

        System.assertEquals(
            2,
            Database.countQuery('SELECT COUNT() FROM DebitMemoLine WHERE DebitMemo.AccountId = \'' + a.Id + '\''),
            'PRECONDITION: both debit memos and their lines must exist before the reset runs'
        );

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        System.assertEquals(0, countOf('DebitMemo', draft.Id), 'A Draft debit memo must be deleted');
        System.assertEquals(0, countOf('DebitMemo', canceled.Id), 'A Canceled debit memo must be deleted');
        System.assertEquals(
            0,
            Database.countQuery('SELECT COUNT() FROM DebitMemoLine WHERE DebitMemoId IN (\''
                + draft.Id + '\', \'' + canceled.Id + '\')'),
            'The lines must go with their debit memos'
        );
        System.assertEquals(true, result.cleared, 'Nothing was kept. Retained: ' + result.retainedSummary);
        System.assert(
            result.removedSummary.contains(entry('DebitMemo', 2)),
            'The deleted debit memos must be reported. Got: ' + result.removedSummary
        );
    }

    @IsTest
    static void debitMemosStayWithoutDeleteBilling() {
        if (!runnerIsAdmin()) return;
        if (!available(new List<String>{ 'DebitMemo', 'DebitMemoLine' })) return;
        Account a = newAccount();
        SObject memo = newDebitMemo(a.Id);

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, false));
        Test.stopTest();

        System.assertEquals(1, countOf('DebitMemo', memo.Id), 'DeleteBilling=false must leave debit memos alone');
        System.assertEquals(null, result.removedSummary, 'Nothing was removed');
    }

    // ------------------------------------------------- Delete Collection Plans

    private static final List<String> COLLECTION_OBJECTS = new List<String>{
        'CollectionPlan', 'CollectionPlanItem', 'Dispute', 'DisputeItem'
    };

    @IsTest
    static void collectionPlansGoWithTheirCasesAndDisputes() {
        if (!runnerIsAdmin()) return;
        if (!available(COLLECTION_OBJECTS)) return;
        Account a = newAccount();
        Account bystander = new Account(Name = 'RLM Utilities Bystander Account');
        insert bystander;
        // No CollectionPlanReason: with one, RLM_Create_Case_for_Collection raises
        // the plan's case itself, from org data a unit test cannot see.
        SObject plan = newRecord('CollectionPlan', new Map<String, Object>{
            'AccountId' => a.Id, 'UsageType' => 'Billing'
        });
        PaymentSchedule promise = new PaymentSchedule(
            ReferenceEntityId = plan.Id,
            Type = 'PromiseToPay',
            UsageType = 'CollectionPlan',
            Status = 'Draft',
            TotalRequestedAmount = 10
        );
        insert promise;

        Case planCase = new Case(AccountId = a.Id, Subject = 'Plan case');
        Case othersPlanCase = new Case(AccountId = bystander.Id, Subject = 'Plan case on another account');
        Case disputeCase = new Case(AccountId = a.Id, Subject = 'Dispute case');
        Case unrelatedCase = new Case(AccountId = a.Id, Subject = 'Unrelated case');
        planCase.put('SourceId', plan.Id);
        othersPlanCase.put('SourceId', plan.Id);
        insert new List<Case>{ planCase, othersPlanCase, disputeCase, unrelatedCase };

        SObject dispute = newRecord('Dispute', new Map<String, Object>{
            'AccountId' => a.Id, 'CaseId' => disputeCase.Id, 'ReceivedDate' => Date.today()
        });
        SObject disputeItem = newRecord('DisputeItem', new Map<String, Object>{
            'DisputeId' => dispute.Id, 'TransactionDate' => Date.today()
        });

        System.assertEquals(1, countOf('CollectionPlan', plan.Id), 'PRECONDITION: the plan must exist');
        System.assertEquals(1, countOf('DisputeItem', disputeItem.Id), 'PRECONDITION: the dispute item must exist');

        RLM_AccountUtilities.InputVariables iv = request(a.Id, false, false, false);
        iv.DeleteCollectionPlans = true;
        Test.startTest();
        RLM_AccountUtilities.Result result = run(iv);
        Test.stopTest();

        System.assertEquals(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        System.assertEquals(0, countOf('CollectionPlan', plan.Id), 'The collection plan must be deleted');
        System.assertEquals(
            0,
            [SELECT COUNT() FROM PaymentSchedule WHERE Id = :promise.Id],
            'A promise to pay outlives its plan unless it is deleted first'
        );
        System.assertEquals(0, countOf('Case', planCase.Id), 'The plan\'s case must be deleted');
        System.assertEquals(0, countOf('Dispute', dispute.Id), 'The dispute must be deleted');
        System.assertEquals(0, countOf('DisputeItem', disputeItem.Id), 'The dispute item must go with its dispute');
        System.assertEquals(0, countOf('Case', disputeCase.Id), 'The dispute\'s case must be deleted');
        System.assertEquals(1, countOf('Case', unrelatedCase.Id), 'A case of neither a plan nor a dispute is kept');
        System.assertEquals(
            1,
            countOf('Case', othersPlanCase.Id),
            'A destructive utility must not reach past the account it was given, even through the plan'
        );
        for (String removed : new List<String>{
            entry('CollectionPlan', 1), entry('Dispute', 1), entry(Case.SObjectType, 2)
        }) {
            System.assert(
                result.removedSummary.contains(removed),
                'Expected "' + removed + '" in the removed summary. Got: ' + result.removedSummary
            );
        }
    }

    @IsTest
    static void collectionPlansStayUnlessSelected() {
        if (!runnerIsAdmin()) return;
        if (!available(COLLECTION_OBJECTS)) return;
        Account a = newAccount();
        SObject plan = newRecord('CollectionPlan', new Map<String, Object>{
            'AccountId' => a.Id, 'UsageType' => 'Billing'
        });
        // A dispute needs a case.
        Case disputeCase = new Case(AccountId = a.Id, Subject = 'Dispute case');
        insert disputeCase;
        SObject dispute = newRecord('Dispute', new Map<String, Object>{
            'AccountId' => a.Id, 'CaseId' => disputeCase.Id, 'ReceivedDate' => Date.today()
        });

        Test.startTest();
        // Every other option on, and DeleteCollectionPlans omitted, as an older caller would.
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        System.assertEquals(1, countOf('CollectionPlan', plan.Id), 'An omitted DeleteCollectionPlans must keep plans');
        System.assertEquals(1, countOf('Dispute', dispute.Id), 'An omitted DeleteCollectionPlans must keep disputes');
        System.assertEquals(true, result.cleared, 'Records the reset was not asked to delete are not reported');
    }

    // ------------------------------------------------------------- documents

    @IsTest
    static void quoteFilesAreDeletedUnlessSharedElsewhere() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Opportunity o = newOpportunity(a.Id, 'RLM Utilities Quote Opp');
        update new Pricebook2(Id = Test.getStandardPricebookId(), IsActive = true);
        Quote q = new Quote(
            Name = 'RLM Utilities Test Quote',
            OpportunityId = o.Id,
            Pricebook2Id = Test.getStandardPricebookId(),
            Status = 'Draft'
        );
        insert q;
        Id quoteOnly = newFile('Quote only', q.Id);
        Id shared = newFile('Shared with the account', q.Id);
        insert new ContentDocumentLink(ContentDocumentId = shared, LinkedEntityId = a.Id, ShareType = 'V');

        System.assertEquals(
            2,
            [SELECT COUNT() FROM ContentDocument WHERE Id IN (:quoteOnly, :shared)],
            'PRECONDITION: both files must exist before the reset runs'
        );

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        System.assertEquals(0, [SELECT COUNT() FROM Quote WHERE Id = :q.Id], 'The quote must be deleted');
        System.assertEquals(
            0,
            [SELECT COUNT() FROM ContentDocument WHERE Id = :quoteOnly],
            'A file only the quote used must go with it, or it is orphaned'
        );
        System.assertEquals(
            1,
            [SELECT COUNT() FROM ContentDocument WHERE Id = :shared],
            'A file also linked to another record must be kept'
        );
        System.assert(
            result.removedSummary.contains(entry(ContentDocument.SObjectType, 1)),
            'The deleted file must be reported. Got: ' + result.removedSummary
        );
    }

    @IsTest
    static void fileLookupTakesTwoQueriesForAnyNumberOfRecords() {
        Account a = newAccount();
        Id file = newFile('Account only', a.Id);
        // 200 Ids of records that don't exist take the set past a 200-row chunk,
        // so a query per chunk would show, without inserting 200 records.
        Set<Id> parentIds = new Set<Id>{ a.Id };
        for (Integer i = 1; i <= 200; i++) {
            parentIds.add(Id.valueOf('001' + String.valueOf(i).leftPad(12, '0')));
        }

        Test.startTest();
        Map<Id, Set<Id>> files = RLM_AccountUtilities.exclusiveFiles(parentIds);
        Integer queries = Limits.getQueries();
        Test.stopTest();

        System.assertEquals(new Set<Id>{ file }, files.keySet(), 'The account\'s file is linked to nothing else');
        System.assertEquals(
            2,
            queries,
            'Phase 2 keeps back a fixed number of queries, so the file lookup must not take more for a larger account'
        );
    }

    // ------------------------------------------------------------ stopped runs

    @IsTest
    static void phaseTwoFailureRollsBackAndSaysSo() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Rollback Opp');
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        System.assertEquals(
            1,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'A failure late in phase 2 must roll back what phase 2 had deleted'
        );
        System.assertEquals(false, result.completed, 'A rolled-back reset did not complete');
        System.assert(
            result.reason.contains('rolled back') && result.reason.contains('Forced phase 2 failure'),
            'The reason must say what was rolled back, and why. Got: ' + result.reason
        );
        System.assertEquals(
            null,
            result.removedSummary,
            'Records that were rolled back must not be reported as removed'
        );
    }

    @IsTest
    static void runningOutOfDmlRowsStopsCleanly() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Budget Opp 1');
        newOpportunity(a.Id, 'RLM Utilities Budget Opp 2');
        // Room for one row: the two opportunities do not fit.
        RLM_AccountUtilities.dmlRowLimitForTest = 1;

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        // Reaching this line is part of the assertion: the platform's own limit
        // throws a LimitException, which cannot be caught and fails the flow.
        System.assertEquals(false, result.completed, 'A run that ran out of DML rows did not complete');
        // Phase 1 deleted nothing, so phase 2's rollback leaves the account as it was, and
        // a rerun would stop at the same point: the reason must not promise otherwise.
        System.assert(
            result.reason.contains('limit on record changes')
                && result.reason.contains(RLM_AccountUtilities.PHASE_TWO_STOPPED_NO_PROGRESS)
                && result.reason.contains('The largest groups it reached: ' + entry(Opportunity.SObjectType, 2))
                && !result.reason.contains('continues from where this run stopped'),
            'The reason must name the limit and say a rerun stops at the same point. Got: ' + result.reason
        );
        System.assertEquals(
            2,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'Phase 2 rolls back as a whole, so neither opportunity may be half-deleted'
        );
    }

    @IsTest
    static void aPhaseTwoStopAfterUsageDeletesSaysARerunGetsFurther() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        BindingObjUsageRsrcPlcy policy = new BindingObjUsageRsrcPlcy(BindingObjectId = a.Id,
            UsageResourceId = f.resourceId, EffectiveStartDate = Datetime.now().addDays(-10));
        insert policy;
        newOpportunity(a.Id, 'RLM Utilities Budget Opp 1');
        newOpportunity(a.Id, 'RLM Utilities Budget Opp 2');
        // Room for two rows: phase 1 deletes the policy, then the two opportunities do not fit.
        RLM_AccountUtilities.dmlRowLimitForTest = 2;

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A run that ran out of DML rows did not complete');
        Assert.isTrue(
            result.reason.contains('limit on record changes')
                && result.reason.contains(RLM_AccountUtilities.PHASE_TWO_STOPPED_AFTER_USAGE),
            'Phase 1 kept its deletes, so a rerun gets further, and the reason says why. Got: ' + result.reason
        );
        Assert.areEqual(0, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE Id = :policy.Id],
            'Phase 1\'s delete stays');
        Assert.areEqual(2, [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id], 'Phase 2 rolled back');
    }

    // Leaves `left` DML statements, without side effects: a savepoint counts as one.
    private static void spendDmlStatementsDownTo(Integer left) {
        while (Limits.getLimitDmlStatements() - Limits.getDmlStatements() > left) {
            Database.setSavepoint();
        }
    }

    @IsTest
    static void phaseOneLeavesTheStatementsPhaseTwosSavepointAndRollbackNeed() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        BindingObjUsageRsrcPlcy policy = new BindingObjUsageRsrcPlcy(BindingObjectId = a.Id,
            UsageResourceId = f.resourceId, EffectiveStartDate = Datetime.now().addDays(-10));
        insert policy;
        newOpportunity(a.Id, 'RLM Utilities Statements Opp');

        Test.startTest();
        // Two statements left: deleting the policy in phase 1 would leave phase 2's
        // savepoint the last one, and its rollback none. With only one kept, this run ends
        // in a LimitException.
        spendDmlStatementsDownTo(2);
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        // Reaching this line is part of the assertion: a LimitException cannot be caught.
        Assert.areEqual(false, result.completed, 'A run out of DML statements did not complete');
        Assert.isTrue(result.reason.contains(RLM_AccountUtilities.STATEMENT_LIMIT)
            && result.reason.contains('nothing else was touched'),
            'Phase 1 stops before its delete. Got: ' + result.reason);
        Assert.areEqual(1, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE Id = :policy.Id], 'Nothing was deleted');
    }

    // Orders that do not fit when they are set back to Draft are named in the stop message.
    @IsTest
    static void anUpdateThatDoesNotFitNamesItsGroup() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Id pricebookEntryId = loadUsageFixture().pricebookEntryId;
        List<Order> orders = new List<Order>();
        for (Integer i = 0; i < 2; i++) {
            orders.add(new Order(AccountId = a.Id, EffectiveDate = Date.today(), Status = 'Draft',
                Pricebook2Id = Test.getStandardPricebookId()));
        }
        insert orders;
        List<OrderItem> lines = new List<OrderItem>();
        for (Order o : orders) {
            lines.add(new OrderItem(OrderId = o.Id, PricebookEntryId = pricebookEntryId, Quantity = 1, UnitPrice = 1));
            o.Status = 'Activated';
        }
        insert lines;
        update orders;
        // Room for one row: the two orders going back to Draft do not fit.
        RLM_AccountUtilities.dmlRowLimitForTest = 1;

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'The run stops');
        Assert.isTrue(result.reason.contains('The largest groups it reached: ' + entry(Order.SObjectType, 2)),
            'The orders that did not fit are named. Got: ' + result.reason);
    }

    @IsTest
    static void aPhaseTwoStopNamesTheLargestGroupsLargestFirst() {
        List<Account> accounts = new List<Account>();
        for (Integer i = 0; i < 4; i++) {
            accounts.add(new Account(Name = 'RLM Utilities Group ' + i));
        }
        insert accounts;
        Account a = accounts[0];
        List<Opportunity> opportunities = new List<Opportunity>{
            newOpportunity(a.Id, 'RLM Utilities Group Opp 1'), newOpportunity(a.Id, 'RLM Utilities Group Opp 2'),
            newOpportunity(a.Id, 'RLM Utilities Group Opp 3')
        };
        Contact c = new Contact(LastName = 'RLM Utilities Group', AccountId = a.Id);
        insert c;
        RLM_AccountUtilities.phaseTwoRows = new Map<String, Set<Id>>();
        // Two opportunities tried five times (a retried group) count as two, not ten.
        List<Opportunity> retried = new List<Opportunity>{ opportunities[0], opportunities[1] };
        for (Integer round = 0; round < 5; round++) {
            RLM_AccountUtilities.notePhaseTwoRows(retried);
        }
        RLM_AccountUtilities.notePhaseTwoRows(accounts);
        RLM_AccountUtilities.notePhaseTwoRows(new List<Contact>{ c });
        Assert.areEqual(' The largest groups it reached: '
            + entry(Account.SObjectType, 4) + '; ' + entry(Opportunity.SObjectType, 2) + '; '
            + entry(Contact.SObjectType, 1) + '.',
            RLM_AccountUtilities.largestGroups(), 'Each row once, the three largest, largest first');
        RLM_AccountUtilities.phaseTwoRows = null;
        Assert.areEqual('', RLM_AccountUtilities.largestGroups(), 'Nothing outside phase 2');
    }

    // Exactly two statements kept: with seven left, the run needs every one but the two.
    // Phase 1's policy delete, phase 2's savepoint, then the file, the quote and the
    // opportunity: the last leaves two. Keeping three would stop the run there (the
    // phase-1 test above fails if only one is kept).
    // It assumes no automation in the org does DML when a quote, opportunity or file is
    // deleted: such a trigger or flow would spend statements this count does not include.
    @IsTest
    static void aRunWithExactlyTheStatementsItNeedsCompletes() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        insert new BindingObjUsageRsrcPlcy(BindingObjectId = a.Id, UsageResourceId = f.resourceId,
            EffectiveStartDate = Datetime.now().addDays(-10));
        Opportunity o = newOpportunity(a.Id, 'RLM Utilities Statements Quote Opp');
        Quote q = new Quote(Name = 'RLM Utilities Statements Quote', OpportunityId = o.Id);
        insert q;
        newFile('RLM Statements File', q.Id);

        Test.startTest();
        spendDmlStatementsDownTo(7);
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Integer left = Limits.getLimitDmlStatements() - Limits.getDmlStatements();
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The run has the statements it needs. Reason: ' + result.reason);
        Assert.areEqual(RLM_AccountUtilities.STATEMENTS_KEPT, left, 'It used all but the ones kept');
        Assert.areEqual(0, [SELECT COUNT() FROM Quote WHERE Id = :q.Id], 'The quote is deleted');
    }

    // Out of statements in phase 2: phase 2's savepoint leaves two, which are kept, so the
    // first delete stops the run, and the stop says statements ran out, not rows.
    @IsTest
    static void aPhaseTwoStopOnStatementsSaysSo() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Opportunity o = newOpportunity(a.Id, 'RLM Utilities Statements Stop Opp');
        Quote q = new Quote(Name = 'RLM Utilities Statements Stop Quote', OpportunityId = o.Id);
        insert q;
        newFile('RLM Statements Stop File', q.Id);

        Test.startTest();
        spendDmlStatementsDownTo(3);
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A run out of statements did not complete');
        Assert.isTrue(result.reason.contains(RLM_AccountUtilities.STATEMENT_LIMIT)
            && result.reason.contains(RLM_AccountUtilities.PHASE_TWO_STATEMENTS_NO_PROGRESS)
            && !result.reason.contains('largest groups'),
            'The stop names statements and gives their advice. Got: ' + result.reason);
        Assert.areEqual(1, [SELECT COUNT() FROM Quote WHERE Id = :q.Id], 'Phase 2 rolled back');
    }

    // Out of rows, with three statements left: the trimmed delete spends one, leaving the
    // two that are kept. The stop is still for rows, decided before that delete.
    @IsTest
    static void aRowsStopThatSpendsTheLastStatementBeforeTheKeptOnesIsStillForRows() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        Datetime start = Datetime.now().addDays(-10);
        insert new List<BindingObjUsageRsrcPlcy>{
            new BindingObjUsageRsrcPlcy(BindingObjectId = a.Id, UsageResourceId = f.resourceId,
                EffectiveStartDate = start, EffectiveEndDate = start.addDays(4)),
            new BindingObjUsageRsrcPlcy(BindingObjectId = a.Id, UsageResourceId = f.resourceId,
                EffectiveStartDate = start.addDays(5))
        };
        // Room for one of the two policies.
        RLM_AccountUtilities.dmlRowLimitForTest = 1;
        Test.startTest();
        spendDmlStatementsDownTo(3);
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.isTrue(result.reason.contains(RLM_AccountUtilities.DML_LIMIT)
            && !result.reason.contains(RLM_AccountUtilities.STATEMENT_LIMIT),
            'The stop is for rows. Got: ' + result.reason);
        Assert.areEqual(1, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE BindingObjectId = :a.Id],
            'One policy went, in the trimmed delete');
    }

    @IsTest
    static void aPhaseTwoStopGetsTheAdviceForItsCause() {
        RLM_AccountUtilities.phaseTwoRows = null;
        Assert.areEqual(RLM_AccountUtilities.PHASE_TWO_STOPPED_NO_PROGRESS,
            RLM_AccountUtilities.phaseTwoStopAdvice(RLM_AccountUtilities.DML_LIMIT, false), 'Rows: thin the largest groups');
        Assert.areEqual(RLM_AccountUtilities.PHASE_TWO_QUERIES_NO_PROGRESS,
            RLM_AccountUtilities.phaseTwoStopAdvice(RLM_AccountUtilities.QUERY_LIMIT, false), 'Queries: the bucket walk');
        Assert.areEqual(RLM_AccountUtilities.PHASE_TWO_STATEMENTS_NO_PROGRESS,
            RLM_AccountUtilities.phaseTwoStopAdvice(RLM_AccountUtilities.STATEMENT_LIMIT, false), 'Statements');
        for (String cause : new List<String>{
            RLM_AccountUtilities.DML_LIMIT, RLM_AccountUtilities.QUERY_LIMIT, RLM_AccountUtilities.STATEMENT_LIMIT
        }) {
            Assert.areEqual(RLM_AccountUtilities.PHASE_TWO_STOPPED_AFTER_USAGE,
                RLM_AccountUtilities.phaseTwoStopAdvice(cause, true), 'After phase 1 deleted something, a rerun helps');
        }
    }

    // A record alert on a journal blocks the journal's delete (measured live 264). Phase 1's
    // rounds cannot delete the journal, so phase 2 deletes the alert, then the journal.
    @IsTest
    static void aJournalWithARecordAlertIsDeleted() {
        if (!runnerIsAdmin()) return;
        if (Schema.getGlobalDescribe().get('RecordAlert') == null) return;
        Account a = newAccount();
        TransactionJournal journal = new TransactionJournal(AccountId = a.Id, ActivityDate = Date.today());
        insert journal;
        SObject alert = Schema.getGlobalDescribe().get('RecordAlert').newSObject();
        alert.put('WhatId', journal.Id);
        alert.put('EffectiveDate', Datetime.now());
        alert.put('ValidUntilDate', Datetime.now().addDays(5));
        insert alert;

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM TransactionJournal WHERE Id = :journal.Id],
            'The journal is deleted. Kept: ' + result.retainedSummary);
        Assert.areEqual(0, Database.countQuery('SELECT COUNT() FROM RecordAlert WHERE Id = \'' + alert.Id + '\''),
            'Its alert is deleted first');
    }

    @IsTest
    static void noQueryBudgetForATeardownRoundStopsBeforePhaseTwo() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Query Budget Opp');

        Test.startTest();
        // A teardown round starts only while its own 9 queries plus the 53 phase 2
        // keeps back are left. Leaving 55 here, less the 4 spent before the loop (the
        // admins-only permission check and phase 1's 3 lookups), means the first round
        // cannot start: the state a usage graph too large for one run reaches after
        // several rounds.
        Integer spend = Limits.getLimitQueries() - 55;
        for (Integer i = 0; i < spend; i++) {
            countOf('Account', a.Id);
        }
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A run stopped for its query budget did not complete');
        Assert.isTrue(
            result.reason.contains('limit on queries')
                && !result.reason.contains('more usage records than one run can remove')
                && result.reason.contains('nothing else was touched')
                && result.reason.contains('Run the reset again'),
            'The reason must be phase 1\'s stop message. Got: ' + result.reason
        );
        Assert.areEqual(
            1,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'The opportunity must survive a run that stopped in phase 1'
        );
    }

    @IsTest
    static void phaseOneOutOfRowsKeepsWhatItDeleted() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        // Two consecutive periods: policies for one object and resource may not overlap.
        Datetime start = Datetime.now().addDays(-10);
        insert new List<BindingObjUsageRsrcPlcy>{
            new BindingObjUsageRsrcPlcy(BindingObjectId = a.Id, UsageResourceId = f.resourceId,
                EffectiveStartDate = start, EffectiveEndDate = start.addDays(4)),
            new BindingObjUsageRsrcPlcy(BindingObjectId = a.Id, UsageResourceId = f.resourceId,
                EffectiveStartDate = start.addDays(5))
        };
        Assert.areEqual(2, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE BindingObjectId = :a.Id],
            'PRECONDITION: both binding policies must exist before the reset runs');
        // Room for one of the two policies, the first delete of the run.
        RLM_AccountUtilities.dmlRowLimitForTest = 1;

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A run that ran out of DML rows did not complete');
        Assert.isTrue(
            result.reason.contains('limit on record changes')
                && result.reason.contains('stay deleted')
                && result.reason.contains('Run the reset again'),
            'The reason must be phase 1\'s row-limit stop message. Got: ' + result.reason
        );
        Assert.areEqual(1, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE BindingObjectId = :a.Id],
            'One policy must be deleted and the other kept');
        Assert.areEqual(entry(BindingObjUsageRsrcPlcy.SObjectType, 1), result.removedSummary,
            'The policy that went must be reported');
    }

    // ------------------------------------------------------------- usage graph
    //
    // A usage entitlement bucket hangs off an entitlement account (ParentId) or
    // another bucket. Under a bucket it must hold a transaction usage entitlement;
    // directly under an entitlement account it may hold none, and must have a zero
    // balance (platform validation, 264). The teardown loop finds buckets only
    // through their entitlement's account, so a bucket with no entitlement is
    // invisible to it: the entitlement account above it refuses every round, the
    // loop ends with rows left (usageDrained stays false), and phase 2 retries
    // the entitlement account's buckets along the hierarchy, leaves first.

    // An entitlement's external order line must be unique, and test methods can run
    // in parallel, so each method's entitlements carry their own token.
    private static final String TOKEN = String.valueOf(Crypto.getRandomInteger()).remove('-');

    private static UsageEntitlementAccount newEntitlementAccount(Id accountId, UsageFixture f) {
        Datetime start = Datetime.now().addDays(-10);
        UsageEntitlementAccount uea = new UsageEntitlementAccount(
            AccountId = accountId,
            GrantBindingTargetId = accountId,
            PricebookEntryId = f.pricebookEntryId,
            EffectiveStartDateTime = start,
            BillDayOfMonth = 1,
            BillingPeriodStartDateTime = start,
            BillingPeriodEndDateTime = start.addMonths(1),
            BillingPeriodUnit = 'MONTH',
            BillingPeriodTerm = 1
        );
        insert uea;
        return uea;
    }

    private static Integer entitlementCount = 0;

    private static TransactionUsageEntitlement newEntitlement(Id accountId, Id bindingTargetId, Id assetId, UsageFixture f) {
        entitlementCount++;
        TransactionUsageEntitlement tue = new TransactionUsageEntitlement(
            AccountId = accountId,
            GrantBindingTargetId = bindingTargetId,
            AssetId = assetId,
            UsageResourceId = f.resourceId,
            PricebookEntryId = f.pricebookEntryId,
            EntitlementUomId = f.uomId,
            EffectiveStartDateTime = Datetime.now().addDays(-10),
            TransactionQuantity = 1,
            EntitlementQuantity = 100,
            NetQuantity = 100,
            ValidityPeriodTerm = 1,
            ActionType = 'New',
            // An entitlement must name the order line that granted it, and no two may
            // name the same one. An external line saves building an order.
            ExternalOrderItem = 'RLM-RESET-' + TOKEN + '-' + entitlementCount
        );
        insert tue;
        return tue;
    }

    private static UsageEntitlementBucket newBucket(Id parentId, Id entitlementId, UsageFixture f) {
        UsageEntitlementBucket bucket = new UsageEntitlementBucket(
            ParentId = parentId,
            TransactionUsageEntitlementId = entitlementId,
            UsageResourceId = f.resourceId,
            BucketBalanceUomId = f.uomId,
            // The platform requires a zero balance on a bucket directly under an
            // entitlement account.
            BucketBalance = parentId.getSObjectType() == UsageEntitlementAccount.SObjectType ? 0 : 100,
            EffectiveStartDateTime = Datetime.now().addDays(-10)
        );
        insert bucket;
        return bucket;
    }

    @IsTest
    static void bucketsAndEntitlementsUnderAnEntitlementAccountAreAllRemoved() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        TransactionUsageEntitlement tue = newEntitlement(a.Id, a.Id, null, f);
        TransactionUsageEntitlement childTue = newEntitlement(a.Id, a.Id, null, f);
        // The entitlement account holds two buckets: one with an entitlement and a
        // child bucket (with its own) below it, which the loop finds through those
        // entitlements, and one with no entitlement, which only phase 2's retry finds.
        UsageEntitlementBucket held = newBucket(uea.Id, tue.Id, f);
        UsageEntitlementBucket child = newBucket(held.Id, childTue.Id, f);
        UsageEntitlementBucket loose = newBucket(uea.Id, null, f);

        Assert.areEqual(
            3,
            [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:held.Id, :child.Id, :loose.Id)],
            'PRECONDITION: all three buckets must exist before the reset runs'
        );
        Assert.areEqual(2, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id IN (:tue.Id, :childTue.Id)],
            'PRECONDITION: both entitlements must exist before the reset runs');
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :uea.Id],
            'PRECONDITION: the entitlement account must exist before the reset runs');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(
            0,
            [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:held.Id, :child.Id, :loose.Id)],
            'All three buckets must be deleted'
        );
        Assert.areEqual(0, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id IN (:tue.Id, :childTue.Id)],
            'Both entitlements must be deleted');
        Assert.areEqual(0, [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :uea.Id],
            'The entitlement account must be deleted');
        Assert.areEqual(true, result.cleared,
            'Nothing must be reported kept. Retained: ' + result.retainedSummary);
        for (String removed : new List<String>{
            entry(UsageEntitlementBucket.SObjectType, 3),
            entry(TransactionUsageEntitlement.SObjectType, 2),
            entry(UsageEntitlementAccount.SObjectType, 1)
        }) {
            Assert.isTrue(
                result.removedSummary.contains(removed),
                'Expected "' + removed + '" in the removed summary. Got: ' + result.removedSummary
            );
        }
    }

    @IsTest
    static void rollbackRestoresPhaseOneRefusals() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        // The loop deletes this bucket and its entitlement in phase 1. The bucket
        // with no entitlement keeps the entitlement account refused, so phase 2's
        // retry (usageDrained false) deletes them and the rollback restores them;
        // bucketsAndEntitlementsUnderAnEntitlementAccountAreAllRemoved shows the
        // retry deleting them.
        TransactionUsageEntitlement tue = newEntitlement(a.Id, a.Id, null, f);
        UsageEntitlementBucket held = newBucket(uea.Id, tue.Id, f);
        UsageEntitlementBucket loose = newBucket(uea.Id, null, f);
        Assert.areEqual(2, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:held.Id, :loose.Id)],
            'PRECONDITION: both buckets must exist before the reset runs');
        Assert.areEqual(1, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id = :tue.Id],
            'PRECONDITION: the entitlement must exist before the reset runs');
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A rolled-back reset did not complete');
        Assert.isTrue(
            result.reason.contains('rolled back') && result.reason.contains('Forced phase 2 failure'),
            'The run must have reached phase 2 and rolled it back. Got: ' + result.reason
        );
        Assert.areEqual(0, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id = :held.Id],
            'Phase 1\'s delete of the bucket must survive the rollback');
        Assert.areEqual(0, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id = :tue.Id],
            'Phase 1\'s delete of the entitlement must survive the rollback');
        Assert.areEqual(
            2,
            [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :uea.Id]
                + [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id = :loose.Id],
            'Phase 2\'s deletes of the entitlement account and its bucket must be rolled back'
        );
        Assert.areEqual(
            entry(UsageEntitlementBucket.SObjectType, 1) + '; ' + entry(TransactionUsageEntitlement.SObjectType, 1),
            result.removedSummary,
            'Only phase 1\'s deletes may be reported removed after the rollback'
        );
        String kept = entry(UsageEntitlementAccount.SObjectType, 1) + ' (could not be deleted: ';
        Assert.isTrue(
            result.retainedSummary != null && result.retainedSummary.contains(kept),
            'The entitlement account must be reported kept, with the reason. Got: '
                + result.retainedSummary
        );
    }

    @IsTest
    static void phaseOneDeletesAnEntitlementAccountItEmptied() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        TransactionUsageEntitlement tue = newEntitlement(a.Id, a.Id, null, f);
        UsageEntitlementBucket held = newBucket(uea.Id, tue.Id, f);
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id = :held.Id],
            'PRECONDITION: the bucket must exist before the reset runs');
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :uea.Id],
            'PRECONDITION: the entitlement account must exist before the reset runs');
        // With every bucket reachable, the loop deletes the bucket, the entitlement
        // and then the entitlement account. Failing phase 2 shows those deletes are
        // phase 1's: a rollback would restore anything phase 2 deleted.
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A rolled-back reset did not complete');
        Assert.isTrue(
            result.reason.contains('rolled back') && result.reason.contains('Forced phase 2 failure'),
            'The run must have reached phase 2 and rolled it back. Got: ' + result.reason
        );
        Assert.areEqual(0, [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :uea.Id],
            'Phase 1\'s delete of the entitlement account must survive the rollback');
        Assert.areEqual(
            entry(UsageEntitlementBucket.SObjectType, 1) + '; '
                + entry(TransactionUsageEntitlement.SObjectType, 1) + '; '
                + entry(UsageEntitlementAccount.SObjectType, 1),
            result.removedSummary,
            'Phase 1\'s deletes must be reported removed'
        );
    }

    @IsTest
    static void entitlementsBoundToTheAssetFromAnotherAccountAreDeletedWithIt() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Account previousOwner = new Account(Name = 'RLM Utilities Previous Owner');
        insert previousOwner;
        UsageFixture f = loadUsageFixture();
        Asset asset = new Asset(Name = 'RLM Utilities Moved Asset', AccountId = a.Id);
        insert asset;
        // The entitlements still name the account the asset was granted on. The
        // teardown loop follows the reset account, so only the asset step finds
        // them: one through AssetId, one through GrantBindingTargetId. This is the one
        // exception to "a reset never touches another account's data": an entitlement
        // bound to an asset this reset deletes goes with the asset, with its bucket.
        UsageEntitlementAccount othersUea = newEntitlementAccount(previousOwner.Id, f);
        TransactionUsageEntitlement byAsset = newEntitlement(previousOwner.Id, previousOwner.Id, asset.Id, f);
        TransactionUsageEntitlement byGrant = newEntitlement(previousOwner.Id, asset.Id, null, f);
        UsageEntitlementBucket assetBucket = newBucket(othersUea.Id, byAsset.Id, f);
        UsageEntitlementBucket grantBucket = newBucket(othersUea.Id, byGrant.Id, f);
        // An entitlement account of the reset account's own, which the loop cannot
        // clear (its bucket has no entitlement). It must be gone after the reset;
        // this test does not pin which step removes it.
        UsageEntitlementAccount ownUea = newEntitlementAccount(a.Id, f);
        newBucket(ownUea.Id, null, f);
        Assert.areEqual(1, [SELECT COUNT() FROM TransactionUsageEntitlement
                WHERE Id = :byAsset.Id AND AccountId = :previousOwner.Id AND AssetId = :asset.Id
                AND GrantBindingTargetId = :previousOwner.Id],
            'PRECONDITION: one entitlement, on the previous owner, must name the asset only in AssetId');
        Assert.areEqual(1,
            [SELECT COUNT() FROM TransactionUsageEntitlement
                WHERE Id = :byGrant.Id AND AccountId = :previousOwner.Id AND GrantBindingTargetId = :asset.Id
                AND AssetId = null],
            'PRECONDITION: the other, on the previous owner, must name the asset only in GrantBindingTargetId');
        Assert.areEqual(2, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:assetBucket.Id, :grantBucket.Id)],
            'PRECONDITION: both entitlements\' buckets must exist before the reset runs');
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :ownUea.Id],
            'PRECONDITION: the reset account\'s entitlement account must exist before the reset runs');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM Asset WHERE Id = :asset.Id], 'DeleteAssets=true must remove the asset');
        Assert.areEqual(0, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id = :byAsset.Id],
            'The entitlement bound through AssetId must be deleted');
        Assert.areEqual(0, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id = :byGrant.Id],
            'The entitlement bound through GrantBindingTargetId must be deleted');
        Assert.areEqual(0, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:assetBucket.Id, :grantBucket.Id)],
            'Both entitlements\' buckets must be deleted too');
        Assert.areEqual(0, [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :ownUea.Id],
            'The reset account\'s own entitlement account must be removed');
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :othersUea.Id],
            'The other account\'s entitlement account must be kept');
        // Buckets: the two entitlements' buckets and the reset account's own bucket.
        for (String removed : new List<String>{
            entry(TransactionUsageEntitlement.SObjectType, 2),
            entry(UsageEntitlementBucket.SObjectType, 3),
            entry(UsageEntitlementAccount.SObjectType, 1),
            entry(Schema.Asset.SObjectType, 1)
        }) {
            Assert.isTrue(
                result.removedSummary.contains(removed),
                'Expected "' + removed + '" in the removed summary. Got: ' + result.removedSummary
            );
        }
    }

    @IsTest
    static void phaseTwoKeepsABucketHiddenUnderABucketThatHoldsAnotherAccountsEntitlement() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Account other = new Account(Name = 'RLM Utilities Other Account');
        insert other;
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        // A bucket under a bucket must hold an entitlement. This one holds another
        // account's, so the loop (which follows the reset account's entitlements)
        // sees neither bucket, and only phase 2's walk down from the entitlement
        // account finds the child. A reset never touches another account's data: the
        // child stays, and so does the bucket above it.
        TransactionUsageEntitlement othersTue = newEntitlement(other.Id, other.Id, null, f);
        UsageEntitlementBucket parent = newBucket(uea.Id, null, f);
        UsageEntitlementBucket child = newBucket(parent.Id, othersTue.Id, f);
        Assert.areEqual(2, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:parent.Id, :child.Id)],
            'PRECONDITION: both buckets must exist before the reset runs');
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :uea.Id],
            'PRECONDITION: the entitlement account must exist before the reset runs');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(2, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:parent.Id, :child.Id)],
            'The bucket holding another account\'s entitlement, and the one above it, must stay');
        Assert.areEqual(1, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id = :othersTue.Id],
            'Another account\'s entitlement must be kept');
        Assert.areEqual(false, result.cleared, 'Something was kept. Reason: ' + result.reason);
        Assert.isTrue(
            result.retainedSummary != null
                && result.retainedSummary.contains(entry(UsageEntitlementBucket.SObjectType, 2)
                    + ' (kept: holds, or is above, another account\'s entitlement)'),
            'Both buckets must be reported kept, with the reason. Got: ' + result.retainedSummary
        );
        Assert.isFalse(
            String.valueOf(result.retainedSummary).contains(other.Name),
            'The report must not name the other account'
        );
    }

    @IsTest
    static void phaseTwoRetryKeepsAnotherAccountsEntitlementUnderOurBucket() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Account other = new Account(Name = 'RLM Utilities Other Account 438');
        insert other;
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        TransactionUsageEntitlement ownTue = newEntitlement(a.Id, a.Id, null, f);
        TransactionUsageEntitlement othersTue = newEntitlement(other.Id, other.Id, null, f);
        // Our entitlement's bucket has a child that holds another account's entitlement.
        // The child keeps the bucket refused in the loop, so phase 2's entitlement-side
        // retry walks the tree: the child and our bucket stay, and so does the
        // entitlement our bucket holds.
        UsageEntitlementBucket held = newBucket(uea.Id, ownTue.Id, f);
        UsageEntitlementBucket child = newBucket(held.Id, othersTue.Id, f);
        Assert.areEqual(2, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:held.Id, :child.Id)],
            'PRECONDITION: both buckets must exist before the reset runs');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(1, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id = :othersTue.Id],
            'Another account\'s entitlement must not be deleted by the retry');
        Assert.areEqual(2, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:held.Id, :child.Id)],
            'The bucket holding another account\'s entitlement, and the one above it, must stay');
        Assert.areEqual(false, result.cleared, 'Something was kept. Reason: ' + result.reason);
        String kept = entry(UsageEntitlementBucket.SObjectType, 2)
            + ' (kept: holds, or is above, another account\'s entitlement)';
        Assert.isTrue(
            result.retainedSummary != null && result.retainedSummary.contains(kept),
            'The two buckets must be reported kept once, with the reason. Got: ' + result.retainedSummary
        );
        Assert.areEqual(1, result.retainedSummary.split(
            UsageEntitlementBucket.SObjectType.getDescribe().getLabelPlural() + ': ').size() - 1,
            'The buckets must be one row, not a refused row plus a foreign row. Got: ' + result.retainedSummary);
    }

    @IsTest
    static void aForeignBucketTheAssetStepDeletesIsNotReportedKept() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Account previousOwner = new Account(Name = 'RLM Utilities Previous Owner 438');
        insert previousOwner;
        UsageFixture f = loadUsageFixture();
        Asset asset = new Asset(Name = 'RLM Utilities Moved Asset 438', AccountId = a.Id);
        insert asset;
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        TransactionUsageEntitlement ownTue = newEntitlement(a.Id, a.Id, null, f);
        // The previous owner's entitlement is bound to our asset, so the asset step deletes
        // it with the asset. Its bucket sits under a bucket of ours that holds our own
        // entitlement: the loop refuses that parent, so the retries mark both foreign
        // before the asset step deletes the child.
        TransactionUsageEntitlement movedTue = newEntitlement(previousOwner.Id, previousOwner.Id, asset.Id, f);
        UsageEntitlementBucket held = newBucket(uea.Id, ownTue.Id, f);
        UsageEntitlementBucket child = newBucket(held.Id, movedTue.Id, f);

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:held.Id, :child.Id)],
            'Both buckets must be gone once the asset step has deleted the bound entitlement');
        Assert.areEqual(true, result.cleared, 'Nothing is left, so nothing is reported kept. Got: ' + result.retainedSummary);
        Assert.areEqual(null, result.retainedSummary, 'A deleted bucket must not be reported kept');
    }

    @IsTest
    static void rollbackReasonSaysNothingWasDeletedWhenPhaseOneDeletedNothing() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Rollback Wording Opp');
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        Assert.areEqual(null, result.removedSummary, 'PRECONDITION: phase 1 deleted nothing');
        Assert.isTrue(
            result.reason.contains('Nothing was deleted') && !result.reason.contains('Only what the usage'),
            'The reason must not claim usage records were deleted. Got: ' + result.reason
        );
    }

    @IsTest
    static void rollbackReasonPointsToPhaseOnesDeletesWhenThereWereSome() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        Datetime start = Datetime.now().addDays(-10);
        insert new BindingObjUsageRsrcPlcy(BindingObjectId = a.Id, UsageResourceId = f.resourceId,
            EffectiveStartDate = start);
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        Assert.isNotNull(result.removedSummary, 'PRECONDITION: phase 1 deleted the policy');
        Assert.isTrue(
            result.reason.contains('Only what the usage cleanup deleted stays deleted')
                && !result.reason.contains('Nothing was deleted'),
            'The reason must point to what phase 1 deleted. Got: ' + result.reason
        );
    }

    // The asset step marks a bucket foreign (retries, against the account's own TUEs) and
    // then sees it as the account's (the TUE is bound to the asset) and tries to delete
    // it. When that delete is refused, the TUE stays, the asset cannot go, and the run
    // rolls back: deleteRows drops the foreign mark when a delete is refused, and the
    // rollback listing then reports the chain once. Phase 2's own report is discarded by
    // the rollback, so only the listing's rows can be observed here.
    @IsTest
    static void aRefusedBucketDeleteInTheAssetStepLeavesOneRowPerBucketAfterTheRollback() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Account previousOwner = new Account(Name = 'RLM Utilities Previous Owner 438b');
        insert previousOwner;
        UsageFixture f = loadUsageFixture();
        Asset asset = new Asset(Name = 'RLM Utilities Moved Asset 438b', AccountId = a.Id);
        insert asset;
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        TransactionUsageEntitlement ownTue = newEntitlement(a.Id, a.Id, null, f);
        TransactionUsageEntitlement movedTue = newEntitlement(previousOwner.Id, asset.Id, null, f);
        UsageEntitlementBucket held = newBucket(uea.Id, ownTue.Id, f);
        UsageEntitlementBucket child = newBucket(held.Id, movedTue.Id, f);
        // A usage summary of the previous owner's holds the child bucket, and no step of
        // the reset deletes it (the loop and the asset step find summaries through the
        // reset account or its assets), so the asset step's delete of the bucket is refused.
        insert new UsageSummary(
            UsageEntitlementBucketId = child.Id, AccountId = previousOwner.Id, UomId = f.uomId,
            StartDateTime = Datetime.now().addDays(-5), EndDateTime = Datetime.now().addDays(-1),
            DebitedUnits = 0, ConsumptionUnits = 0, OverageUnits = 0, Status = 'New'
        );

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'The asset cannot go while its entitlement stays');
        Assert.areEqual(2, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:held.Id, :child.Id)],
            'Both buckets must survive the rolled-back run');
        Assert.isNotNull(result.retainedSummary, 'The kept buckets must be reported');
        Assert.areEqual(1, result.retainedSummary.split(
            UsageEntitlementBucket.SObjectType.getDescribe().getLabelPlural() + ': ').size() - 1,
            'The two buckets must be one row. Got: ' + result.retainedSummary);
        Assert.isTrue(result.retainedSummary.contains(entry(UsageEntitlementBucket.SObjectType, 2)
            + ' (not deleted: the run was rolled back; the bucket holds, or is above, another account\'s entitlement)'),
            'Both buckets get the same reason. Got: ' + result.retainedSummary);
    }

    // The completed-run path: the retries mark `held` and `child` foreign (against the
    // account's own TUEs), then the asset step sees both as the account's (the TUE is
    // bound to its asset) and deletes `child`. A previous owner's usage summary holds
    // `held`, so that delete is refused; the entitlement under `child` is gone, so the
    // asset can go and the run completes. `held` must be reported once, as refused.
    @IsTest
    static void aBucketTheAssetStepIsRefusedIsReportedOnceAsRefusedNotAlsoAsForeign() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Account previousOwner = new Account(Name = 'RLM Utilities Previous Owner 438c');
        insert previousOwner;
        UsageFixture f = loadUsageFixture();
        Asset asset = new Asset(Name = 'RLM Utilities Moved Asset 438c', AccountId = a.Id);
        insert asset;
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        TransactionUsageEntitlement ownTue = newEntitlement(a.Id, a.Id, null, f);
        TransactionUsageEntitlement movedTue = newEntitlement(previousOwner.Id, previousOwner.Id, asset.Id, f);
        UsageEntitlementBucket held = newBucket(uea.Id, ownTue.Id, f);
        UsageEntitlementBucket child = newBucket(held.Id, movedTue.Id, f);
        insert new UsageSummary(
            UsageEntitlementBucketId = held.Id, AccountId = previousOwner.Id, UomId = f.uomId,
            StartDateTime = Datetime.now().addDays(-5), EndDateTime = Datetime.now().addDays(-1),
            DebitedUnits = 0, ConsumptionUnits = 0, OverageUnits = 0, Status = 'New'
        );

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id = :child.Id],
            'PRECONDITION: the asset step deleted the child bucket');
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id = :held.Id],
            'PRECONDITION: the summary refused the delete of the bucket above it');
        Assert.isNotNull(result.retainedSummary, 'The kept bucket must be reported');
        Assert.isFalse(result.retainedSummary.contains('kept: holds, or is above'),
            'A refused bucket is not also reported as foreign. Got: ' + result.retainedSummary);
        Assert.areEqual(1, result.retainedSummary.split(
            UsageEntitlementBucket.SObjectType.getDescribe().getLabelPlural() + ': ').size() - 1,
            'The bucket must be one row. Got: ' + result.retainedSummary);
        Assert.isTrue(result.retainedSummary.contains(entry(UsageEntitlementBucket.SObjectType, 1) + ' (could not be deleted: '),
            'The bucket must be reported as refused. Got: ' + result.retainedSummary);
    }

    @IsTest
    static void rollbackGivesOneReasonToARefusedBucketAboveAForeignChild() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Account other = new Account(Name = 'RLM Utilities Rollback Chain 438');
        insert other;
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        TransactionUsageEntitlement ownTue = newEntitlement(a.Id, a.Id, null, f);
        UsageEntitlementBucket held = newBucket(uea.Id, ownTue.Id, f);
        newBucket(held.Id, newEntitlement(other.Id, other.Id, null, f).Id, f);
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A rolled-back reset did not complete');
        Assert.isTrue(
            result.retainedSummary.contains(entry(UsageEntitlementBucket.SObjectType, 2)
                + ' (not deleted: the run was rolled back; the bucket holds, or is above, another account\'s entitlement)'),
            'The loop-refused bucket and its foreign child are one chain with one reason. Got: ' + result.retainedSummary
        );
        Assert.isFalse(result.retainedSummary.contains('could not be deleted: ') && result.retainedSummary.contains(
            UsageEntitlementBucket.SObjectType.getDescribe().getLabelPlural() + ': 1 (could'),
            'The refused bucket must not also get the platform error. Got: ' + result.retainedSummary);
    }

    @IsTest
    static void rollbackReportsABucketTheLoopNeverSaw() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        // No entitlement: the loop never queries this bucket.
        UsageEntitlementBucket loose = newBucket(uea.Id, null, f);
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A rolled-back reset did not complete');
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id = :loose.Id],
            'The bucket is still there after the rollback');
        Assert.isTrue(
            result.retainedSummary != null
                && result.retainedSummary.contains(entry(UsageEntitlementBucket.SObjectType, 1)
                    + ' (not deleted: the run was rolled back)'),
            'The bucket must be reported kept. Got: ' + result.retainedSummary
        );
    }

    @IsTest
    static void rollbackSaysTheBucketListMayBeIncompleteWhenQueriesRunOut() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        newBucket(uea.Id, null, f);
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        // No queries to list the buckets with, as after a phase 2 that spent nearly all.
        RLM_AccountUtilities.unseenQueriesForTest = 0;
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();
        Assert.areEqual(0, RLM_AccountUtilities.unseenListQueriesSpentForTest, 'Stopped before any lookup');

        Assert.areEqual(false, result.completed, 'A rolled-back reset did not complete');
        Assert.isTrue(
            result.retainedSummary != null && result.retainedSummary.contains('may be incomplete'),
            'A bucket list cut short must say so. Got: ' + result.retainedSummary
        );
    }

    @IsTest
    static void rollbackSaysTheBucketListMayBeIncompleteWhenTheWalkRunsOutPartWay() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        seedDeepUndrainedTree(a, f);
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        // The two lookups and two levels of the tree fit (4 queries); the third level does not.
        RLM_AccountUtilities.unseenQueriesForTest = 4;
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A rolled-back reset did not complete');
        Assert.areEqual(4, RLM_AccountUtilities.unseenListQueriesSpentForTest,
            'The listing must have run its lookups and part of the walk, not stopped up front');
        Assert.isTrue(
            result.retainedSummary != null && result.retainedSummary.contains('may be incomplete'),
            'A walk cut short part way must say so. Got: ' + result.retainedSummary
        );
    }

    @IsTest
    static void rollbackSaysABucketThatHoldsAnotherAccountsEntitlementWouldBeKeptAnyway() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Account other = new Account(Name = 'RLM Utilities Rollback Other 438');
        insert other;
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        UsageEntitlementBucket parent = newBucket(uea.Id, null, f);
        newBucket(parent.Id, newEntitlement(other.Id, other.Id, null, f).Id, f);
        UsageEntitlementBucket loose = newBucket(uea.Id, null, f);
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A rolled-back reset did not complete');
        Assert.isTrue(
            result.retainedSummary.contains(entry(UsageEntitlementBucket.SObjectType, 2)
                + ' (not deleted: the run was rolled back; the bucket holds, or is above, another account\'s entitlement)'),
            'The two buckets a completed run would keep must say so. Got: ' + result.retainedSummary
        );
        Assert.isTrue(
            result.retainedSummary.contains(entry(UsageEntitlementBucket.SObjectType, 1)
                + ' (not deleted: the run was rolled back)'),
            'The loose bucket a completed run would delete is reported as rolled back. Got: ' + result.retainedSummary
        );
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id = :loose.Id], 'Rolled back');
    }

    @IsTest
    static void usageTooLargeStopsTheRunWhenTheRoundCapBindsFirst() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        newBucket(uea.Id, newEntitlement(a.Id, a.Id, null, f).Id, f);
        newOpportunity(a.Id, 'RLM Utilities Round Cap Opp');
        // One round removes the bucket and entitlement, which is progress, so a second
        // would be needed to confirm nothing is left.
        RLM_AccountUtilities.maxTeardownRoundsForTest = 1;

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A run stopped by the round cap did not complete');
        Assert.isTrue(
            result.reason.contains('more usage records than one run can remove')
                && result.reason.contains('Run the reset again')
                && !result.reason.contains('limit on queries'),
            'The reason must be the usage-too-large stop. Got: ' + result.reason
        );
        Assert.areEqual(1, [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'The opportunity must survive a run that stopped in phase 1');
    }

    // Every option on, with an asset and an opportunity so the asset step runs.
    private static RLM_AccountUtilities.InputVariables allOn(Id accountId) {
        RLM_AccountUtilities.InputVariables iv = request(accountId, true, true, true);
        iv.DeleteCollectionPlans = true;
        iv.PreserveContractsWithContractedPrices = true;
        return iv;
    }

    private static void seedAssetAndOpportunity(Account a) {
        insert new Asset(Name = 'RLM Utilities Budget Asset', AccountId = a.Id);
        newOpportunity(a.Id, 'RLM Utilities Budget Opp');
    }

    // A three-level tree under an entitlement account, none of it reachable by the
    // teardown loop (every bucket under the first holds another account's entitlement),
    // and a tree under one of the account's own entitlements: the undrained retries
    // walk both, a level per query.
    private static List<UsageEntitlementBucket> seedDeepUndrainedTree(Account a, UsageFixture f) {
        Account other = new Account(Name = 'RLM Utilities Deep Tree Other');
        insert other;
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        UsageEntitlementBucket b1 = newBucket(uea.Id, null, f);
        UsageEntitlementBucket b2 = newBucket(b1.Id, newEntitlement(other.Id, other.Id, null, f).Id, f);
        UsageEntitlementBucket b3 = newBucket(b2.Id, newEntitlement(other.Id, other.Id, null, f).Id, f);
        UsageEntitlementBucket held = newBucket(uea.Id, newEntitlement(a.Id, a.Id, null, f).Id, f);
        UsageEntitlementBucket c1 = newBucket(held.Id, newEntitlement(other.Id, other.Id, null, f).Id, f);
        UsageEntitlementBucket c2 = newBucket(c1.Id, newEntitlement(other.Id, other.Id, null, f).Id, f);
        return new List<UsageEntitlementBucket>{ b1, b2, b3, held, c1, c2 };
    }

    private static void spendQueriesDownTo(Integer left, Id accountId) {
        Integer spend = Limits.getLimitQueries() - Limits.getQueries() - left;
        for (Integer i = 0; i < spend; i++) {
            countOf('Account', accountId);
        }
    }

    // The 46 is counted from the code with data in every branch (see the constants in
    // RLM_AccountUtilities); this test measures only the empty-data path with one asset, held exactly. It holds
    // the reserve against the 46 and the measurement against both, but it cannot catch
    // growth in the data-dependent branches (collections, posted invoices, files,
    // generated documents, contracts, quotes): recount those when a query is added.
    // Phase 2's queries with every option on, an opportunity and no other data, counted from
    // the code: order data 10, collection plans and disputes 1 each where the org has them,
    // schedule groups 1, debit memos 1 where the org has them, credit memos 1, payments 1,
    // fulfillment 2, contracts 1, the asset step without assets 2 (policies, account rate
    // card entries), quotes 1, opportunities 1. Measured 23 on tkdef (264), which has all three.
    private static Integer phaseTwoQueriesWithoutAssets() {
        return 20 + present(new List<String>{ 'CollectionPlan', 'Dispute', 'DebitMemo' });
    }

    // What the asset step adds for one asset with no usage: entitlements bound to it 1, work
    // orders and cases 1 each where the org has them, its policies 1, asset rate card entries
    // 1, entries sourced from it 1, relationships 1, assets 1. Measured 8 on tkdef.
    private static Integer assetStepQueriesForOneAsset() {
        return 6 + present(new List<String>{ 'WorkOrder', 'Case' });
    }

    private static Integer present(List<String> objectNames) {
        Integer n = 0;
        for (String objectName : objectNames) {
            if (Schema.getGlobalDescribe().containsKey(objectName)) {
                n++;
            }
        }
        return n;
    }

    @IsTest
    static void phaseTwosAssetStepQueriesNothingForAnAccountWithoutAssets() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities No Asset Opp');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(allOn(a.Id));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(phaseTwoQueriesWithoutAssets(), RLM_AccountUtilities.phaseTwoQueriesForTest,
            'Phase 2\'s queries with no asset changed: the asset step\'s queries must stay guarded on its assets');
    }

    @IsTest
    static void phaseTwosFixedQueriesStayWithinTheReserveKeptForThem() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        seedAssetAndOpportunity(a);

        Test.startTest();
        RLM_AccountUtilities.Result result = run(allOn(a.Id));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        // Exact, so a query added to this path fails here and its count is revisited.
        Assert.areEqual(phaseTwoQueriesWithoutAssets() + assetStepQueriesForOneAsset(),
            RLM_AccountUtilities.phaseTwoQueriesForTest,
            'Phase 2\'s queries on empty data with every option on changed: recount PHASE_TWO_FIXED_MAX, '
                + 'RETRY_TAIL and ASSET_TAIL');
        Assert.isTrue(
            RLM_AccountUtilities.phaseTwoQueriesForTest <= RLM_AccountUtilities.PHASE_TWO_FIXED_MAX,
            'Phase 2 spent ' + RLM_AccountUtilities.phaseTwoQueriesForTest
                + ' queries on empty data with every option on; the counted worst case is '
                + RLM_AccountUtilities.PHASE_TWO_FIXED_MAX
        );
        Assert.areEqual(46 + 7, RLM_AccountUtilities.QUERY_RESERVE,
            'The reserve covers phase 2\'s counted worst case, 46, with seven spare');
        Assert.areEqual(46, RLM_AccountUtilities.PHASE_TWO_FIXED_MAX, 'Phase 2\'s counted worst case');
        // The counts after each guard (see the constants): 28 after the journal guard, 14
        // after the asset step's last one, each with three spare.
        Assert.areEqual(28 + 3, RLM_AccountUtilities.RETRY_TAIL, 'RETRY_TAIL is the 28 counted plus three spare');
        Assert.areEqual(14 + 3, RLM_AccountUtilities.ASSET_TAIL, 'ASSET_TAIL is the 14 counted plus three spare');
    }

    @IsTest
    static void aDeepUndrainedTreeAtTheLowestBudgetEndsWithAReasonNotALimitException() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        seedAssetAndOpportunity(a);
        List<UsageEntitlementBucket> tree = seedDeepUndrainedTree(a, f);

        Test.startTest();
        // The least a run can have and still reach phase 2: the first teardown round
        // needs its 9 queries plus the 53 kept back, and 4 are spent before it (the
        // admins-only permission check; the asset lookup; the account's policies and rate
        // card entries).
        spendQueriesDownTo(66, a.Id);
        RLM_AccountUtilities.Result result = run(allOn(a.Id));
        Integer queriesLeft = Limits.getLimitQueries() - Limits.getQueries();
        Test.stopTest();

        // Reaching this line is part of the assertion: a LimitException cannot be caught.
        Assert.isTrue(queriesLeft >= 0, 'The run must stay within the query limit');
        Assert.isNotNull(RLM_AccountUtilities.phaseTwoQueriesForTest,
            'The run must reach phase 2, whose walk guards this test is for. Reason: ' + result.reason);
        Assert.areEqual(false, result.completed, 'The tree cannot be cleared: it holds another account\'s entitlements');
        Assert.isNotNull(result.reason, 'A run that did not complete must say why');
        Assert.isTrue(
            result.reason.contains('limit on queries')
                && !result.reason.contains('nothing else was touched')
                && (result.reason.contains(RLM_AccountUtilities.PHASE_TWO_STOPPED_AFTER_USAGE)
                    || result.reason.contains(RLM_AccountUtilities.PHASE_TWO_QUERIES_NO_PROGRESS)),
            'The reason must be phase 2\'s query-limit stop. Got: ' + result.reason
        );
        Assert.areEqual(1, [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'A stopped phase 2 rolls back as a whole');
        Assert.areEqual(6, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN :new Map<Id, UsageEntitlementBucket>(tree).keySet()],
            'No bucket may be deleted by a run that stopped in phase 2');
    }

    // ------------------------------------------------------------------ orders

    @IsTest
    static void activatedOrdersAreDeleted() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        // The class-wide setup's standard price book entry.
        Id pricebookEntryId = loadUsageFixture().pricebookEntryId;
        Order o = new Order(
            AccountId = a.Id, EffectiveDate = Date.today(), Status = 'Draft',
            Pricebook2Id = Test.getStandardPricebookId()
        );
        insert o;
        insert new OrderItem(OrderId = o.Id, PricebookEntryId = pricebookEntryId, Quantity = 1, UnitPrice = 1);
        o.Status = 'Activated';
        update o;

        Assert.areEqual('Activated', [SELECT Status FROM Order WHERE Id = :o.Id].Status,
            'PRECONDITION: the order must be activated');

        Test.startTest();
        // DeleteFulfillment on, so the fulfillment lookup runs against a real order
        // and order line. This test checks only the order's removal.
        RLM_AccountUtilities.Result result = run(request(a.Id, false, true, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM Order WHERE Id = :o.Id], 'The activated order must be deleted');
        Assert.isTrue(
            result.removedSummary.contains(entry(Order.SObjectType, 1)),
            'The deleted order must be reported. Got: ' + result.removedSummary
        );
    }

    @IsTest
    static void anOrderAlreadyInDraftIsNotUpdated() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Id pricebookEntryId = loadUsageFixture().pricebookEntryId;
        List<Order> orders = new List<Order>{
            new Order(AccountId = a.Id, EffectiveDate = Date.today(), Status = 'Draft',
                Pricebook2Id = Test.getStandardPricebookId()),
            new Order(AccountId = a.Id, EffectiveDate = Date.today(), Status = 'Draft',
                Pricebook2Id = Test.getStandardPricebookId())
        };
        insert orders;
        insert new OrderItem(OrderId = orders[0].Id, PricebookEntryId = pricebookEntryId, Quantity = 1, UnitPrice = 1);
        orders[0].Status = 'Activated';
        update orders[0];

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(1, RLM_AccountUtilities.ordersSetToDraftForTest,
            'Only the activated order is set back to Draft');
        Assert.areEqual(0, [SELECT COUNT() FROM Order WHERE AccountId = :a.Id], 'Both orders must be deleted');
    }

    @IsTest
    static void aKeptAssetOrContractKeepsItsBindingPolicies() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        Asset asset = new Asset(Name = 'RLM Utilities Kept Asset Policy', AccountId = a.Id);
        insert asset;
        Datetime start = Datetime.now().addDays(-10);
        BindingObjUsageRsrcPlcy assetPolicy = new BindingObjUsageRsrcPlcy(BindingObjectId = asset.Id,
            UsageResourceId = f.resourceId, EffectiveStartDate = start);
        BindingObjUsageRsrcPlcy accountPolicy = new BindingObjUsageRsrcPlcy(BindingObjectId = a.Id,
            UsageResourceId = f.resourceId, EffectiveStartDate = start);
        insert new List<BindingObjUsageRsrcPlcy>{ assetPolicy, accountPolicy };

        Test.startTest();
        // Delete Assets off: the asset stays, and so does its policy.
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(1, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE Id = :assetPolicy.Id],
            'A kept asset keeps its binding policy');
        Assert.areEqual(0, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE Id = :accountPolicy.Id],
            'The account\'s own policy goes');
    }

    // A contract the run deletes and, with Delete Assets, an asset take their binding policies.
    @IsTest
    static void aDeletedContractOrAssetTakesItsBindingPolicies() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        List<BindingObjUsageRsrcPlcy> policies = seedContractAssetAndAccountPolicies(a);

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM Contract WHERE AccountId = :a.Id], 'The contract is deleted');
        Assert.areEqual(0, [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id], 'The asset is deleted');
        Assert.areEqual(0, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE Id IN :policies],
            'The contract\'s, the asset\'s and the account\'s policies go');
    }

    // Phase 2 deletes a contract's and an asset's policies with them, so its rollback keeps
    // them; only the account's own, which phase 1 deletes, stay deleted.
    @IsTest
    static void aPhaseTwoRollbackKeepsTheContractsAndAssetsBindingPolicies() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        List<BindingObjUsageRsrcPlcy> policies = seedContractAssetAndAccountPolicies(a);
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, true, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'Phase 2 was rolled back');
        Assert.areEqual(1, [SELECT COUNT() FROM Contract WHERE AccountId = :a.Id], 'The contract stays');
        Assert.areEqual(1, [SELECT COUNT() FROM Asset WHERE AccountId = :a.Id], 'The asset stays');
        Assert.areEqual(1, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE Id = :policies[0].Id],
            'The contract keeps its policy');
        Assert.areEqual(1, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE Id = :policies[1].Id],
            'The asset keeps its policy');
        Assert.areEqual(0, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE Id = :policies[2].Id],
            'The account\'s own policy went in phase 1, which a rollback does not undo');
    }

    // A contract, an asset and the account, each with one binding policy: [contract, asset, account].
    private static List<BindingObjUsageRsrcPlcy> seedContractAssetAndAccountPolicies(Account a) {
        UsageFixture f = loadUsageFixture();
        Contract c = new Contract(AccountId = a.Id, StartDate = Date.today().addDays(-7), ContractTerm = 12, Status = 'Draft');
        insert c;
        Asset asset = new Asset(Name = 'RLM Utilities Policy Asset', AccountId = a.Id);
        insert asset;
        Datetime start = Datetime.now().addDays(-10);
        List<BindingObjUsageRsrcPlcy> policies = new List<BindingObjUsageRsrcPlcy>();
        for (Id boundTo : new List<Id>{ c.Id, asset.Id, a.Id }) {
            policies.add(new BindingObjUsageRsrcPlcy(BindingObjectId = boundTo, UsageResourceId = f.resourceId,
                EffectiveStartDate = start));
        }
        insert policies;
        Assert.areEqual(3, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE Id IN :policies],
            'PRECONDITION: the three policies exist');
        return policies;
    }

    @IsTest
    static void aContractPreservedForItsPricesKeepsItsBindingPolicies() {
        if (!runnerIsAdmin()) return;
        if (!contractItemPriceAvailable()) return;
        Id accountId = seedAccountWithContracts();
        UsageFixture f = loadUsageFixture();
        Contract priced = [SELECT Id FROM Contract WHERE AccountId = :accountId
            AND Id IN (SELECT ContractId FROM ContractItemPrice) LIMIT 1];
        BindingObjUsageRsrcPlcy policy = new BindingObjUsageRsrcPlcy(BindingObjectId = priced.Id,
            UsageResourceId = f.resourceId, EffectiveStartDate = Datetime.now().addDays(-10));
        insert policy;
        RLM_AccountUtilities.InputVariables iv = request(accountId, true, false, false);
        iv.PreserveContractsWithContractedPrices = true;

        Test.startTest();
        RLM_AccountUtilities.Result result = run(iv);
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(1, [SELECT COUNT() FROM Contract WHERE Id = :priced.Id], 'PRECONDITION: the contract is kept');
        Assert.areEqual(1, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE Id = :policy.Id],
            'A contract kept for its prices keeps its binding policy');
    }

    // A binding rate card entry, bound to `bindingId`, sourced from `assetId`.
    private static BindingObjectRateCardEntry newSourcedRateCardEntry(Id bindingId, Id assetId, UsageFixture f) {
        Datetime start = Datetime.now().addDays(-10);
        // A rate's unit must be of a Token or Currency class (platform validation, 264).
        UnitOfMeasureClass currencyClass = new UnitOfMeasureClass(Name = 'RLM Reset Currency',
            Code = 'RLM_AU_TEST_CUR', Type = 'Currency', Status = 'Draft');
        insert currencyClass;
        currencyClass.Status = 'Active';
        update currencyClass;
        UnitOfMeasure currencyUnit = new UnitOfMeasure(Name = 'RLM Reset Currency Unit', UnitCode = 'RLMAUCU',
            Type = 'Currency', UnitOfMeasureClassId = currencyClass.Id, Status = 'Draft');
        insert currencyUnit;
        currencyUnit.Status = 'Active';
        update currencyUnit;
        RateCard card = new RateCard(Name = 'RLM Utilities Rate Card', Type = 'Base', EffectiveFrom = start);
        insert card;
        RateCardEntry cardEntry = new RateCardEntry(RateCardId = card.Id, EffectiveFrom = start,
            RateUnitOfMeasureId = currencyUnit.Id, UsageResourceId = f.resourceId, Rate = 1);
        insert cardEntry;
        // A binding entry needs an active rate card entry, which is created as Draft.
        update new RateCardEntry(Id = cardEntry.Id, Status = 'Active');
        BindingObjectRateCardEntry entry = new BindingObjectRateCardEntry(BindingObjectId = bindingId,
            RateCardEntryId = cardEntry.Id, EffectiveFrom = start, SourceAssetId = assetId);
        insert entry;
        return entry;
    }

    // Live 264, a binding rate card entry sourced from an asset blocked the asset's delete,
    // whatever it was bound to. One bound to a contract the run keeps goes with the asset.
    @IsTest
    static void aRateCardEntrySourcedFromADeletedAssetGoesWithIt() {
        if (!runnerIsAdmin()) return;
        if (!contractItemPriceAvailable()) return;
        Id accountId = seedAccountWithContracts();
        UsageFixture f = loadUsageFixture();
        Contract priced = [SELECT Id FROM Contract WHERE AccountId = :accountId
            AND Id IN (SELECT ContractId FROM ContractItemPrice) LIMIT 1];
        Asset asset = new Asset(Name = 'RLM Utilities Sourced Asset', AccountId = accountId);
        insert asset;
        BindingObjectRateCardEntry sourced = newSourcedRateCardEntry(priced.Id, asset.Id, f);
        RLM_AccountUtilities.InputVariables iv = request(accountId, true, false, false);
        iv.PreserveContractsWithContractedPrices = true;

        Test.startTest();
        RLM_AccountUtilities.Result result = run(iv);
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The asset can go. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM Asset WHERE Id = :asset.Id], 'The asset is deleted');
        Assert.areEqual(0, [SELECT COUNT() FROM BindingObjectRateCardEntry WHERE Id = :sourced.Id],
            'The entry sourced from it goes with it');
        Assert.areEqual(1, [SELECT COUNT() FROM Contract WHERE Id = :priced.Id], 'The priced contract is kept');
    }

    // ------------------------------------------------------------ admins only

    // A standard profile with exactly the given Modify All Data and View All Data, picked by
    // those permissions, never by name: on the running user's license if it has one there,
    // otherwise on another license; either way one with a free seat, the first by Id. Null,
    // with the reason logged, when there is none.
    private static Profile profileWith(Boolean modifyAllData, Boolean viewAllData) {
        Id runnersLicense = [SELECT UserLicenseId FROM Profile WHERE Id = :UserInfo.getProfileId()].UserLicenseId;
        Profile elsewhere;
        for (Profile candidate : [
            SELECT Id, UserLicenseId, UserLicense.TotalLicenses, UserLicense.UsedLicenses FROM Profile
            WHERE UserType = 'Standard' AND PermissionsModifyAllData = :modifyAllData
                AND PermissionsViewAllData = :viewAllData
            ORDER BY Id
        ]) {
            if (candidate.UserLicense.UsedLicenses >= candidate.UserLicense.TotalLicenses) {
                continue;
            }
            if (candidate.UserLicenseId == runnersLicense) {
                return candidate;
            }
            if (elsewhere == null) {
                elsewhere = candidate;
            }
        }
        if (elsewhere == null) {
            skipped('no standard profile with Modify All Data ' + modifyAllData + ' and View All Data '
                + viewAllData + ' has a free seat');
        }
        return elsewhere;
    }

    private static User newUserFrom(Profile profile, String alias) {
        User u = new User(
            ProfileId = profile.Id, LastName = 'Reset ' + alias, Email = 'rlm.reset.' + alias + '@example.com',
            Username = 'rlm.reset.' + alias + '.' + Datetime.now().getTime() + '@example.com', Alias = alias,
            TimeZoneSidKey = 'America/Los_Angeles', LocaleSidKey = 'en_US', EmailEncodingKey = 'UTF-8',
            LanguageLocaleKey = 'en_US'
        );
        insert u;
        return u;
    }

    // A user with View All Data and without Modify All Data, as a read-only auditor has.
    // From such a profile when one has a free seat; otherwise from a profile with neither,
    // plus a permission set that grants View All Data. View All Data depends on Read and View
    // All on every object and on six system permissions (platform validation, 264), so the
    // set grants those on the objects a profile with both reads, plus every object Apex
    // describes (one the profile reads only through View All Data, such as Location, has no
    // row of its own), retrying each pass the rows whose own dependency a pass granted. The
    // update that adds View All Data then says whether that was all: if the platform refuses
    // it, the test skips with the reason logged. Null then, and when the org has no profile
    // to build from. Setup objects, so in its own runAs (no mixed DML with the test's data).
    private static User newViewAllDataOnlyUser() {
        Profile viewAllOnly = profileWith(false, true);
        if (viewAllOnly != null) {
            return newUserFrom(viewAllOnly, 'rlmvad');
        }
        Profile neither = profileWith(false, false);
        Profile admin = profileWith(true, true);
        if (neither == null || admin == null) {
            return null;
        }
        User u;
        System.runAs(new User(Id = UserInfo.getUserId())) {
            PermissionSet viewAll = new PermissionSet(Name = 'RLM_Reset_Test_View_All', Label = 'RLM Reset Test View All');
            insert viewAll;
            Set<String> objects = new Set<String>();
            for (ObjectPermissions read : [
                SELECT SobjectType FROM ObjectPermissions WHERE PermissionsRead = true AND Parent.ProfileId = :admin.Id
            ]) {
                objects.add(read.SobjectType);
            }
            for (Schema.SObjectType objectType : Schema.getGlobalDescribe().values()) {
                objects.add(String.valueOf(objectType));
            }
            while (!objects.isEmpty() && objects.size() <= Limits.getLimitDmlRows() - Limits.getDmlRows() - 100) {
                List<String> names = new List<String>(objects);
                List<ObjectPermissions> grants = new List<ObjectPermissions>();
                for (String name : names) {
                    grants.add(new ObjectPermissions(
                        ParentId = viewAll.Id, SobjectType = name, PermissionsRead = true, PermissionsViewAllRecords = true
                    ));
                }
                Database.SaveResult[] results = Database.insert(grants, false);
                Integer granted = 0;
                for (Integer i = 0; i < results.size(); i++) {
                    if (results[i].isSuccess()) {
                        objects.remove(names[i]);
                        granted++;
                    }
                }
                if (granted == 0) {
                    break;
                }
            }
            viewAll.PermissionsViewAllData = true;
            viewAll.PermissionsViewAllForecasts = true;
            viewAll.PermissionsViewEventLogFiles = true;
            viewAll.PermissionsViewPublicDashboards = true;
            viewAll.PermissionsViewPublicReports = true;
            viewAll.PermissionsViewRoles = true;
            viewAll.PermissionsViewSetup = true;
            Database.SaveResult added = Database.update(viewAll, false);
            if (added.isSuccess()) {
                u = newUserFrom(neither, 'rlmvad');
                insert new PermissionSetAssignment(AssigneeId = u.Id, PermissionSetId = viewAll.Id);
            } else {
                skipped('a permission set cannot be given View All Data here: ' + added.getErrors()[0].getMessage().left(300));
            }
        }
        return u;
    }

    private static void assertRefusedAndUnchanged(User u, Account a) {
        RLM_AccountUtilities.Result result;
        Boolean admin;
        System.runAs(u) {
            admin = RLM_AccountUtilities.seesAndDeletesEverything();
            Test.startTest();
            result = run(request(a.Id, true, true, true));
            Test.stopTest();
        }
        Assert.areEqual(false, admin, 'PRECONDITION: the user lacks Modify All Data or View All Data');
        Assert.areEqual(false, result.completed, 'The reset must be refused');
        Assert.areEqual(RLM_AccountUtilities.ADMIN_ONLY, result.reason, 'The refusal says it is for administrators');
        Assert.isNull(result.removedSummary, 'Nothing was removed');
        Assert.isNull(result.retainedSummary, 'Nothing about the account is reported');
        Assert.areEqual(1, [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id], 'Nothing may change');
    }

    @IsTest
    static void anAdminResets() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Admin Opp');
        Assert.isTrue(RLM_AccountUtilities.seesAndDeletesEverything(),
            'PRECONDITION: the running user has Modify All Data and View All Data');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id], 'The opportunity is deleted');
    }

    // Modify All Data depends on View All Data, so no user has the first alone; these two
    // cover a user with neither and one with View All Data alone.
    @IsTest
    static void aUserWithoutModifyAllOrViewAllIsRefused() {
        Profile neither = profileWith(false, false);
        if (neither == null) return;
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Refused Opp');
        assertRefusedAndUnchanged(newUserFrom(neither, 'rlmnone'), a);
    }

    @IsTest
    static void aUserWithViewAllDataButNotModifyAllDataIsRefused() {
        User u = newViewAllDataOnlyUser();
        if (u == null) return;
        UserPermissionAccess access;
        System.runAs(u) {
            access = [SELECT PermissionsModifyAllData, PermissionsViewAllData FROM UserPermissionAccess LIMIT 1];
        }
        Assert.isTrue(access.PermissionsViewAllData == true && access.PermissionsModifyAllData != true,
            'PRECONDITION: the user has View All Data and not Modify All Data');
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Refused View All Opp');
        assertRefusedAndUnchanged(u, a);
    }

    // Live 264: a usage entitlement on an order line blocks the order's delete. The order
    // is set back to Draft first, so the result must say it was left in Draft.
    @IsTest
    static void anOrderSetBackToDraftAndThenRefusedIsReportedLeftInDraft() {
        if (!runnerIsAdmin()) return;
        Account a = newAccount();
        Account other = new Account(Name = 'RLM Utilities Line Holder');
        insert other;
        UsageFixture f = loadUsageFixture();
        Order o = new Order(AccountId = a.Id, EffectiveDate = Date.today(), Status = 'Draft',
            Pricebook2Id = Test.getStandardPricebookId());
        insert o;
        OrderItem line = new OrderItem(OrderId = o.Id, PricebookEntryId = f.pricebookEntryId, Quantity = 1, UnitPrice = 1);
        insert line;
        o.Status = 'Activated';
        update o;
        insert new TransactionUsageEntitlement(
            AccountId = other.Id, GrantBindingTargetId = other.Id, UsageResourceId = f.resourceId,
            PricebookEntryId = f.pricebookEntryId, EntitlementUomId = f.uomId,
            EffectiveStartDateTime = Datetime.now().addDays(-10), TransactionQuantity = 1, EntitlementQuantity = 100,
            NetQuantity = 100, ValidityPeriodTerm = 1, ActionType = 'New', OrderItemId = line.Id
        );

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual('Draft', [SELECT Status FROM Order WHERE Id = :o.Id].Status, 'PRECONDITION: the order stays, in Draft');
        Assert.isTrue(result.retainedSummary != null
            && result.retainedSummary.contains(entry(Order.SObjectType, 1) + ' (' + RLM_AccountUtilities.LEFT_IN_DRAFT),
            'The order is reported left in Draft. Got: ' + result.retainedSummary);
        Assert.isFalse(result.retainedSummary.contains('(could not be deleted: '),
            'It is reported once, as left in Draft. Got: ' + result.retainedSummary);
    }

    // ------------------------------------------------------------ scope guard

    @IsTest
    static void otherAccountsAreUntouched() {
        if (!runnerIsAdmin()) return;
        Account target = newAccount();
        Account bystander = new Account(Name = 'RLM Utilities Bystander Account');
        insert bystander;

        insert new List<Opportunity>{
            new Opportunity(Name = 'Target Opp', AccountId = target.Id,
                StageName = 'Prospecting', CloseDate = Date.today().addDays(30)),
            new Opportunity(Name = 'Bystander Opp', AccountId = bystander.Id,
                StageName = 'Prospecting', CloseDate = Date.today().addDays(30))
        };

        Test.startTest();
        run(request(target.Id, true, true, true));
        Test.stopTest();

        System.assertEquals(
            0,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :target.Id],
            'The target account must be cleared'
        );
        System.assertEquals(
            1,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :bystander.Id],
            'A destructive utility must not reach past the account it was given'
        );
    }
}
