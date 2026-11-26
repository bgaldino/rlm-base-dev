/**
 * Tests for RLM_AccountUtilities.delAccountRelatedObjects.
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
 *    fulfillment records: no fixtures, so their groups in the plan are empty.
 *  - Invoices, posted credit memos and lifecycle-managed assets cannot be created in
 *    a test, so the plan's rules for them are tested through invoiceBlocker,
 *    assetBlocker and orderBlocker, and the per-record classification through
 *    blockerReason.
 *  - Running out of DML statements partway through phase 2, a plan that reaches the
 *    query row bound, and an unexpected exception in phase 1.
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

    private static User newMinimalAccessUser() {
        Profile leastPrivileged = [
            SELECT Id
            FROM Profile
            WHERE Name IN ('Minimum Access - Salesforce', 'Standard User')
            ORDER BY Name ASC
            LIMIT 1
        ];
        User u = new User(
            ProfileId = leastPrivileged.Id,
            LastName = 'Reset',
            Email = 'rlm.reset.minimal@example.com',
            Username = 'rlm.reset.minimal.' + Datetime.now().getTime() + '@example.com',
            Alias = 'rlmrst',
            TimeZoneSidKey = 'America/Los_Angeles',
            LocaleSidKey = 'en_US',
            EmailEncodingKey = 'UTF-8',
            LanguageLocaleKey = 'en_US'
        );
        insert u;
        return u;
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
        User u = newMinimalAccessUser();

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
            'The plan reads files in a fixed number of queries, so the lookup must not take more for a larger account'
        );
    }

    // ------------------------------------------------------------ stopped runs

    @IsTest
    static void phaseTwoFailureRollsBackAndSaysSo() {
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
        System.assert(
            result.reason.contains('limit on record changes') && result.reason.contains('Run the reset again'),
            'The reason must name the limit and say a rerun continues. Got: ' + result.reason
        );
        System.assertEquals(
            2,
            [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'Phase 2 rolls back as a whole, so neither opportunity may be half-deleted'
        );
    }

    @IsTest
    static void tooFewQueriesToPlanChangesNothing() {
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Query Budget Opp');

        Test.startTest();
        // The plan does all of the run's reading; with too few queries left for it, the
        // run stops before changing anything.
        Integer spend = Limits.getLimitQueries() - 3;
        for (Integer i = 0; i < spend; i++) {
            countOf('Account', a.Id);
        }
        RLM_AccountUtilities.Result result = run(request(a.Id, true, true, true));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A run stopped while planning did not complete');
        Assert.isTrue(
            result.reason.startsWith('The reset was not run, and nothing was changed')
                && result.reason.contains('Running it again as the same user stops at the same point'),
            'The reason must be the plan\'s stop and say what a rerun does. Got: ' + result.reason
        );
        Assert.isNull(result.removedSummary, 'Nothing was removed');
        Assert.areEqual(1, [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id],
            'The opportunity must survive a run the plan stopped');
    }

    @IsTest
    static void phaseOneOutOfRowsKeepsWhatItDeleted() {
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
    // balance (platform validation, 264). The plan finds buckets through the
    // account's entitlements and by walking down from its entitlement accounts, so a
    // bucket with no entitlement is planned too; phase 1 retries the planned rows
    // until a round removes nothing, so parents go after their children.

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
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        TransactionUsageEntitlement tue = newEntitlement(a.Id, a.Id, null, f);
        TransactionUsageEntitlement childTue = newEntitlement(a.Id, a.Id, null, f);
        // The entitlement account holds two buckets: one with an entitlement and a
        // child bucket (with its own) below it, and one with no entitlement, which the
        // plan finds by walking down from the entitlement account.
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
    static void phaseOneDeletesThePlannedUsageGraphAndItSurvivesARollback() {
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        // The plan walks the buckets down from the entitlement account, so a bucket with
        // no entitlement is planned with the rest, and phase 1 deletes all of it.
        TransactionUsageEntitlement tue = newEntitlement(a.Id, a.Id, null, f);
        UsageEntitlementBucket held = newBucket(uea.Id, tue.Id, f);
        UsageEntitlementBucket loose = newBucket(uea.Id, null, f);
        RLM_AccountUtilities.phaseTwoFailureForTest = new DmlException('Forced phase 2 failure');

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A rolled-back reset did not complete');
        Assert.isTrue(
            result.reason.contains('rolled back') && result.reason.contains('Forced phase 2 failure'),
            'The run must have reached phase 2 and rolled it back. Got: ' + result.reason
        );
        Assert.areEqual(0, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id IN (:held.Id, :loose.Id)],
            'Phase 1\'s deletes of both buckets must survive the rollback');
        Assert.areEqual(0, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id = :tue.Id],
            'Phase 1\'s delete of the entitlement must survive the rollback');
        Assert.areEqual(0, [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :uea.Id],
            'Phase 1\'s delete of the entitlement account must survive the rollback');
        Assert.isTrue(result.removedSummary.contains(entry(UsageEntitlementBucket.SObjectType, 2)),
            'Phase 1\'s deletes must be reported removed. Got: ' + result.removedSummary);
    }

    @IsTest
    static void phaseOneDeletesAnEntitlementAccountItEmptied() {
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        TransactionUsageEntitlement tue = newEntitlement(a.Id, a.Id, null, f);
        UsageEntitlementBucket held = newBucket(uea.Id, tue.Id, f);
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id = :held.Id],
            'PRECONDITION: the bucket must exist before the reset runs');
        Assert.areEqual(1, [SELECT COUNT() FROM UsageEntitlementAccount WHERE Id = :uea.Id],
            'PRECONDITION: the entitlement account must exist before the reset runs');
        // With every bucket planned, phase 1 deletes the bucket, the entitlement
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
    static void aBucketUnderABucketHoldingAnotherAccountsEntitlementIsKept() {
        Account a = newAccount();
        Account other = new Account(Name = 'RLM Utilities Other Account');
        insert other;
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        // A bucket under a bucket must hold an entitlement. This one holds another
        // account's. The plan finds both by walking down from the entitlement
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
    static void anotherAccountsEntitlementUnderOurBucketKeepsTheBucketChain() {
        Account a = newAccount();
        Account other = new Account(Name = 'RLM Utilities Other Account 438');
        insert other;
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        TransactionUsageEntitlement ownTue = newEntitlement(a.Id, a.Id, null, f);
        TransactionUsageEntitlement othersTue = newEntitlement(other.Id, other.Id, null, f);
        // Our entitlement's bucket has a child that holds another account's entitlement.
        // The plan leaves out a bucket holding another account's entitlement and every
        // bucket above it: the child and our bucket stay, and so does the
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
            'Another account\'s entitlement must not be deleted');
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
        // entitlement: the plan counts the moved entitlement as the account's (it is bound
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

    // The completed-run path: the plan counts the moved entitlement as the account's (the
    // account's own TUEs), then the asset step sees both as the account's (the TUE is
    // bound to its asset) and deletes `child`. A previous owner's usage summary holds
    // `held`, so that delete is refused; the entitlement under `child` is gone, so the
    // asset can go and the run completes. `held` must be reported once, as refused.
    @IsTest
    static void aBucketTheAssetStepIsRefusedIsReportedOnceAsRefusedNotAlsoAsForeign() {
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
    static void usageTooLargeStopsTheRunWhenTheRoundCapBindsFirst() {
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        // Two levels of buckets: a bucket cannot go while its child is there, so one
        // round removes the child and the next the rest.
        UsageEntitlementBucket parent = newBucket(uea.Id, newEntitlement(a.Id, a.Id, null, f).Id, f);
        newBucket(parent.Id, newEntitlement(a.Id, a.Id, null, f).Id, f);
        newOpportunity(a.Id, 'RLM Utilities Round Cap Opp');
        RLM_AccountUtilities.maxTeardownRoundsForTest = 1;

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'A run stopped by the round cap did not complete');
        Assert.isTrue(
            result.reason.contains('more usage records than one run can remove')
                && result.reason.contains('Run the reset again'),
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

    // ------------------------------------------------------------------ orders

    @IsTest
    static void activatedOrdersAreDeleted() {
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

    // --------------------------------------------- preflight (todo 397)

    private static User newStandardUser() {
        Profile standard = [SELECT Id FROM Profile WHERE Name = 'Standard User' LIMIT 1];
        User u = new User(
            ProfileId = standard.Id, LastName = 'Reset Standard', Email = 'rlm.reset.standard@example.com',
            Username = 'rlm.reset.standard.' + Datetime.now().getTime() + '@example.com', Alias = 'rlmstd',
            TimeZoneSidKey = 'America/Los_Angeles', LocaleSidKey = 'en_US', EmailEncodingKey = 'UTF-8',
            LanguageLocaleKey = 'en_US'
        );
        insert u;
        return u;
    }

    // What a refused run must leave: every record of the account, usage included.
    private class Snapshot {
        Integer opportunities;
        Integer assets;
        Integer entitlementAccounts;
        Integer buckets;
        Integer entitlements;
        Snapshot(Id accountId) {
            opportunities = [SELECT COUNT() FROM Opportunity WHERE AccountId = :accountId];
            assets = [SELECT COUNT() FROM Asset WHERE AccountId = :accountId];
            entitlementAccounts = [SELECT COUNT() FROM UsageEntitlementAccount WHERE AccountId = :accountId];
            buckets = [SELECT COUNT() FROM UsageEntitlementBucket WHERE TransactionUsageEntitlement.AccountId = :accountId];
            entitlements = [SELECT COUNT() FROM TransactionUsageEntitlement WHERE AccountId = :accountId];
        }
        String describe() {
            return opportunities + '/' + assets + '/' + entitlementAccounts + '/' + buckets + '/' + entitlements;
        }
    }

    // An account with an opportunity, an asset and a usage tree, so a refusal can be shown
    // to leave usage records alone as well.
    private static Account seedRefusable() {
        Account a = newAccount();
        seedAssetAndOpportunity(a);
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        newBucket(uea.Id, newEntitlement(a.Id, a.Id, null, f).Id, f);
        return a;
    }

    private static void assertRefusedAndUnchanged(RLM_AccountUtilities.Result result, Snapshot before, Id accountId,
        String expectedEntry) {
        Assert.areEqual(false, result.completed, 'A refused reset did not complete');
        Assert.isTrue(result.reason.startsWith('The reset was not run, and nothing was changed'),
            'The reason must say the reset was not run. Got: ' + result.reason);
        Assert.isTrue(result.reason.contains(expectedEntry),
            'The reason must list ' + expectedEntry + '. Got: ' + result.reason);
        Assert.isNull(result.removedSummary, 'Nothing was removed');
        Assert.areEqual(before.describe(), new Snapshot(accountId).describe(),
            'A refused reset must change nothing, usage records included');
    }

    @IsTest
    static void aRecordWhoseObjectTheUserMayNotDeleteRefusesTheReset() {
        Account a = seedRefusable();
        Snapshot before = new Snapshot(a.Id);
        // (a) The running admin may delete everything; the seam takes away delete on Opportunity.
        RLM_AccountUtilities.undeletableForTest = new Set<String>{ 'Opportunity' };

        Test.startTest();
        RLM_AccountUtilities.Result result = run(allOn(a.Id));
        Test.stopTest();

        assertRefusedAndUnchanged(result, before, a.Id,
            entry(Opportunity.SObjectType, 1) + ' (no permission to delete this kind of record: RLM Utilities Budget Opp)');
    }

    @IsTest
    static void anObjectTheUserCannotReadThatHasRecordsRefusesTheReset() {
        Account a = seedRefusable();
        Snapshot before = new Snapshot(a.Id);
        // (d) Counted, not named: the user cannot read them.
        RLM_AccountUtilities.unreadableForTest = new Set<String>{ 'UsageEntitlementAccount' };

        Test.startTest();
        RLM_AccountUtilities.Result result = run(allOn(a.Id));
        Test.stopTest();

        assertRefusedAndUnchanged(result, before, a.Id,
            entry(UsageEntitlementAccount.SObjectType, 1) + ' (the user running the reset cannot read this kind of record)');
    }

    @IsTest
    static void anObjectTheUserCannotReadWithoutRecordsDoesNotRefuse() {
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Test Opp');
        RLM_AccountUtilities.unreadableForTest = new Set<String>{ 'Invoice', 'BillingScheduleGroup', 'FulfillmentOrder' };

        Test.startTest();
        RLM_AccountUtilities.Result result = run(allOn(a.Id));
        Test.stopTest();

        // Live 264 the salesrep persona's reset failed on every run: "sObject type
        // 'Invoice' is not supported". Nothing of those objects here, so it resets.
        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id], 'The opportunity must go');
    }

    @IsTest
    static void aRecordTheUserCannotDeleteOrSeeRefusesTheReset() {
        Account a = seedRefusable();
        Snapshot before = new Snapshot(a.Id);
        User other = newStandardUser();
        // (b) and (c): the records belong to the admin. A Standard User can see a record
        // under public sharing but not delete it, and cannot see it under private sharing.
        // Which one the opportunity is depends on the org, so the expected entry is read
        // from UserRecordAccess for that user, as the preflight reads it.
        Id opportunityId = [SELECT Id FROM Opportunity WHERE AccountId = :a.Id].Id;
        UserRecordAccess access = [
            SELECT RecordId, HasReadAccess FROM UserRecordAccess WHERE UserId = :other.Id AND RecordId = :opportunityId
        ];
        String expected = access.HasReadAccess
            ? entry(Opportunity.SObjectType, 1) + ' (no delete access to these records: RLM Utilities Budget Opp)'
            : entry(Opportunity.SObjectType, 1) + ' (not visible to the user running the reset)';
        RLM_AccountUtilities.Result result;
        System.runAs(other) {
            Test.startTest();
            result = run(allOn(a.Id));
            Test.stopTest();
        }
        assertRefusedAndUnchanged(result, before, a.Id, expected);
        if (!access.HasReadAccess) {
            Assert.isFalse(result.reason.contains('RLM Utilities Budget Opp'),
                'A record the user cannot see must never be named. Got: ' + result.reason);
        }
    }

    @IsTest
    static void aRecordTheUserCanSeeButNotDeleteIsNamed() {
        Account a = newAccount();
        Opportunity theirs = newOpportunity(a.Id, 'RLM Utilities Visible Not Deletable');
        User other = newStandardUser();
        // Shared for reading, whatever the org's opportunity sharing: an explicit share row
        // where sharing is private; under public sharing the record is visible already.
        String model = [SELECT InternalSharingModel FROM EntityDefinition WHERE QualifiedApiName = 'Opportunity']
            .InternalSharingModel;
        if (model == 'Private') {
            insert new OpportunityShare(OpportunityId = theirs.Id, UserOrGroupId = other.Id, OpportunityAccessLevel = 'Read');
        }
        Assert.isTrue([SELECT RecordId, HasReadAccess FROM UserRecordAccess WHERE UserId = :other.Id
            AND RecordId = :theirs.Id].HasReadAccess, 'PRECONDITION: the user can see the record');
        RLM_AccountUtilities.Result result;
        System.runAs(other) {
            Test.startTest();
            result = run(request(a.Id, false, false, false));
            Test.stopTest();
        }
        Assert.areEqual(false, result.completed, 'A record the user cannot delete must refuse the reset');
        Assert.isTrue(result.reason.contains(entry(Opportunity.SObjectType, 1) + ' (')
            && result.reason.contains('RLM Utilities Visible Not Deletable'),
            'A record the user can see must be named, with the reason. Got: ' + result.reason);
        Assert.areEqual(1, [SELECT COUNT() FROM Opportunity WHERE Id = :theirs.Id], 'Nothing may change');
    }

    @IsTest
    static void aRecordIsNamedOnlyWhenTheUserCanSeeIt() {
        Account a = newAccount();
        newOpportunity(a.Id, 'RLM Utilities Named Or Not');
        Id opportunityId = [SELECT Id FROM Opportunity WHERE AccountId = :a.Id].Id;
        User other = newStandardUser();
        UserRecordAccess access = [
            SELECT RecordId, HasReadAccess FROM UserRecordAccess WHERE UserId = :other.Id AND RecordId = :opportunityId
        ];
        // No delete permission on the object, for every org: the record is named only if
        // this user can see it, whatever the org's opportunity sharing.
        RLM_AccountUtilities.undeletableForTest = new Set<String>{ 'Opportunity' };
        RLM_AccountUtilities.Result result;
        System.runAs(other) {
            Test.startTest();
            result = run(request(a.Id, false, false, false));
            Test.stopTest();
        }
        Assert.areEqual(false, result.completed, 'The reset must be refused');
        Assert.areEqual(access.HasReadAccess, result.reason.contains('RLM Utilities Named Or Not'),
            'Named if and only if the user can see it (HasReadAccess ' + access.HasReadAccess + '). Got: '
                + result.reason);
    }

    @IsTest
    static void anActivatedOrderNeedsEditActivatedOrders() {
        Account a = newAccount();
        Order o = new Order(
            AccountId = a.Id, EffectiveDate = Date.today(), Status = 'Draft', Pricebook2Id = Test.getStandardPricebookId()
        );
        insert o;
        insert new OrderItem(OrderId = o.Id, PricebookEntryId = loadUsageFixture().pricebookEntryId, Quantity = 1,
            UnitPrice = 1);
        o.Status = 'Activated';
        update o;
        String orderNumber = [SELECT OrderNumber FROM Order WHERE Id = :o.Id].OrderNumber;
        RLM_AccountUtilities.withoutPermissionForTest = new Set<String>{ 'PermissionsEditActivatedOrders' };

        Test.startTest();
        RLM_AccountUtilities.Result result = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, result.completed, 'The reset must be refused');
        Assert.isTrue(result.reason.contains(entry(Order.SObjectType, 1) + ' (activated; setting them back to Draft '
            + 'needs the Edit Activated Orders permission: ' + orderNumber + ')'),
            'The order must be named with the permission it needs. Got: ' + result.reason);
        Assert.areEqual('Activated', [SELECT Status FROM Order WHERE Id = :o.Id].Status, 'Nothing may change');
    }

    @IsTest
    static void permissionBlockersFollowTheStatusAndThePermission() {
        // Invoices cannot be created in a test (createable=false), nor a lifecycle-managed
        // asset, so the rules the plan applies to them are tested directly.
        RLM_AccountUtilities.withoutPermissionForTest = new Set<String>{
            'PermissionsBillingInvoiceSuperUser', 'PermissionsCalmSobjectAccessUser', 'PermissionsEditActivatedOrders'
        };
        Assert.isTrue(RLM_AccountUtilities.invoiceBlocker('Posted').contains('Delete Invoice and Invoice Lines'),
            'A posted invoice needs Delete Invoice and Invoice Lines');
        Assert.isTrue(RLM_AccountUtilities.invoiceBlocker('In Progress').startsWith('still processing'),
            'An invoice still processing blocks the reset whoever runs it');
        Assert.isTrue(RLM_AccountUtilities.invoiceBlocker('Processing').startsWith('still processing'),
            'An invoice still processing blocks the reset whoever runs it');
        Assert.isNull(RLM_AccountUtilities.invoiceBlocker('Draft'), 'A Draft invoice needs no extra permission');
        Assert.isNull(RLM_AccountUtilities.invoiceBlocker('Canceled'), 'A Canceled invoice needs no extra permission');
        Assert.isTrue(RLM_AccountUtilities.assetBlocker(true).contains('Access Lifecycle-Managed Assets'),
            'A lifecycle-managed asset needs Access Lifecycle-Managed Assets');
        Assert.isNull(RLM_AccountUtilities.assetBlocker(false), 'Any other asset needs no extra permission');
        Assert.isTrue(RLM_AccountUtilities.orderBlocker('Activated').contains('Edit Activated Orders'),
            'An activated order needs Edit Activated Orders');
        Assert.isNull(RLM_AccountUtilities.orderBlocker('Draft'), 'A Draft order needs no extra permission');

        RLM_AccountUtilities.withoutPermissionForTest = new Set<String>();
        RLM_AccountUtilities.startRun();
        Assert.areEqual(RLM_AccountUtilities.canDeletePostedInvoices(), RLM_AccountUtilities.invoiceBlocker('Posted') == null,
            'With Delete Invoice and Invoice Lines, a posted invoice is not blocked');
        Assert.isTrue(RLM_AccountUtilities.invoiceBlocker('In Progress') != null,
            'Still processing blocks even with the permission');
    }

    @IsTest
    static void aHiddenRecordIsCountedNotNamed() {
        // The classification, on any org: a record the user cannot see is counted as not
        // visible whatever else applies, so it is never named.
        for (Boolean objectDeletable : new List<Boolean>{ true, false }) {
            for (String special : new List<String>{ null, 'a permission it needs' }) {
                for (Boolean deletable : new List<Boolean>{ true, false }) {
                    Assert.areEqual(RLM_AccountUtilities.NOT_VISIBLE,
                        RLM_AccountUtilities.blockerReason('Opportunity', false, objectDeletable, special, deletable),
                        'A record the user cannot see is counted, never named');
                }
            }
        }
        Assert.areEqual(RLM_AccountUtilities.NO_PERMISSION,
            RLM_AccountUtilities.blockerReason('Opportunity', true, false, 'x', true), 'Object permission comes first');
        Assert.areEqual(RLM_AccountUtilities.MEMO_NEEDS_PERMISSION,
            RLM_AccountUtilities.blockerReason('CreditMemo', true, false, null, true),
            'Credit memos name the permission they need');
        Assert.areEqual('x', RLM_AccountUtilities.blockerReason('Order', true, true, 'x', true),
            'A permission the run needs comes before record access');
        Assert.areEqual(RLM_AccountUtilities.NO_ACCESS, RLM_AccountUtilities.blockerReason('Order', true, true, null, false),
            'Then record access');
        Assert.isNull(RLM_AccountUtilities.blockerReason('Order', true, true, null, true), 'Nothing blocks');

        // And end to end, where the org's sharing hides another user's opportunity.
        Account a = newAccount();
        Opportunity hidden = newOpportunity(a.Id, 'RLM Utilities Hidden Opp');
        User other = newStandardUser();
        Boolean visible = [SELECT RecordId, HasReadAccess FROM UserRecordAccess WHERE UserId = :other.Id
            AND RecordId = :hidden.Id].HasReadAccess;
        RLM_AccountUtilities.Result result;
        System.runAs(other) {
            Test.startTest();
            result = run(request(a.Id, false, false, false));
            Test.stopTest();
        }
        Assert.areEqual(false, result.completed, 'Another user\'s opportunity must refuse the reset');
        Assert.areEqual(visible, result.reason.contains('RLM Utilities Hidden Opp'),
            'Named only when visible (visible: ' + visible + '). Got: ' + result.reason);
        Assert.areEqual(!visible, result.reason.contains(entry(Opportunity.SObjectType, 1)
            + ' (not visible to the user running the reset)'), 'Counted when hidden. Got: ' + result.reason);
    }

    @IsTest
    static void aNonAdminResetsAnAccountTheyOwnWithAnActivatedOrder() {
        // A user who is not an admin, with what RLM_UtilitiesPermset grants for orders:
        // Edit Activated Orders and the Activate Orders it depends on. Live 264 the
        // persona's own activated order read HasDeleteAccess true, so nothing blocks.
        User rep = newStandardUser();
        // Activate Orders depends on Read and Edit on Order, so the object grant goes first.
        PermissionSet orders = new PermissionSet(Name = 'RLM_Utilities_Test_Orders_' + TOKEN,
            Label = 'RLM Utilities Test Orders');
        insert orders;
        insert new ObjectPermissions(ParentId = orders.Id, SobjectType = 'Order', PermissionsRead = true,
            PermissionsCreate = true, PermissionsEdit = true, PermissionsDelete = true);
        orders.PermissionsActivateOrder = true;
        orders.PermissionsEditActivatedOrders = true;
        update orders;
        insert new PermissionSetAssignment(AssigneeId = rep.Id, PermissionSetId = orders.Id);
        Id pricebookEntryId = loadUsageFixture().pricebookEntryId;
        Account a;
        Order o;
        RLM_AccountUtilities.Result result;
        System.runAs(rep) {
            a = new Account(Name = 'RLM Utilities Rep Owned');
            insert a;
            insert new Opportunity(Name = 'RLM Utilities Rep Opp', AccountId = a.Id, StageName = 'Prospecting',
                CloseDate = Date.today().addDays(30));
            o = new Order(AccountId = a.Id, EffectiveDate = Date.today(), Status = 'Draft',
                Pricebook2Id = Test.getStandardPricebookId());
            insert o;
            insert new OrderItem(OrderId = o.Id, PricebookEntryId = pricebookEntryId, Quantity = 1, UnitPrice = 1);
            o.Status = 'Activated';
            update o;
            Test.startTest();
            result = run(request(a.Id, false, false, false));
            Test.stopTest();
        }
        Assert.areEqual(true, result.completed, 'The user owns everything, so the reset must run. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM Order WHERE Id = :o.Id], 'The activated order must go');
        Assert.areEqual(0, [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id], 'The opportunity must go');
    }

    @IsTest
    static void recordAccessIsReadInChunksOf200() {
        List<Opportunity> opportunities = new List<Opportunity>();
        Account a = newAccount();
        for (Integer i = 0; i < 201; i++) {
            opportunities.add(new Opportunity(Name = 'RLM Utilities Chunk ' + i, AccountId = a.Id,
                StageName = 'Prospecting', CloseDate = Date.today().addDays(30)));
        }
        insert opportunities;
        User other = newStandardUser();
        RLM_AccountUtilities.Result result;
        System.runAs(other) {
            Test.startTest();
            result = run(request(a.Id, false, false, false));
            Test.stopTest();
        }
        // 201 records the user cannot delete (or see), read in two chunks: all are counted.
        Assert.isTrue(result.reason.contains(entry(Opportunity.SObjectType, 201) + ' ('),
            'Every record across both reads must be counted. Got: ' + result.reason);
        Assert.isTrue(!result.reason.contains('RLM Utilities Chunk 6,') || result.reason.contains('and 196 more'),
            'At most five names are listed. Got: ' + result.reason);
        Assert.areEqual(201, [SELECT COUNT() FROM Opportunity WHERE AccountId = :a.Id], 'Nothing may change');
    }

    @IsTest
    static void canReadFollowsTheRunningUsersObjectAccess() {
        User u = newMinimalAccessUser();
        Boolean minimalReadsInvoices;
        System.runAs(u) {
            minimalReadsInvoices = RLM_AccountUtilities.canRead('Invoice');
        }
        Assert.areEqual(false, minimalReadsInvoices, 'A user without billing access cannot read invoices');
        Assert.areEqual(Account.SObjectType.getDescribe().isAccessible(), RLM_AccountUtilities.canRead('Account'),
            'canRead must agree with the running user\'s access');
        Assert.areEqual(false, RLM_AccountUtilities.canRead('RLM_No_Such_Object__c'),
            'An object the org does not have cannot be read');
    }

    @IsTest
    static void entitlementsBoundToTheAssetConvergeWhenReadInBatches() {
        Account a = newAccount();
        Account previousOwner = new Account(Name = 'RLM Utilities Batch Owner');
        insert previousOwner;
        UsageFixture f = loadUsageFixture();
        Asset asset = new Asset(Name = 'RLM Utilities Batched Asset', AccountId = a.Id);
        insert asset;
        // Two of another account's entitlements bound to the asset, read one a run. The
        // asset cannot go while either remains, so each run must delete what it read.
        TransactionUsageEntitlement first = newEntitlement(previousOwner.Id, previousOwner.Id, asset.Id, f);
        TransactionUsageEntitlement second = newEntitlement(previousOwner.Id, previousOwner.Id, asset.Id, f);
        RLM_AccountUtilities.usageBatchForTest = 1;

        Test.startTest();
        RLM_AccountUtilities.Result firstRun = run(request(a.Id, true, false, false));
        Integer leftAfterFirst = [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id IN (:first.Id, :second.Id)];
        RLM_AccountUtilities.Result secondRun = run(request(a.Id, true, false, false));
        Test.stopTest();

        Assert.areEqual(false, firstRun.completed, 'The first run read part of the usage and asks for another');
        Assert.isTrue(firstRun.reason.contains('Run the reset again'), 'It says so. Got: ' + firstRun.reason);
        Assert.areEqual(1, leftAfterFirst, 'The first run must delete the entitlement it read');
        Assert.areEqual(true, secondRun.completed, 'The second run finishes. Reason: ' + secondRun.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM Asset WHERE Id = :asset.Id], 'The asset must go');
        Assert.areEqual(0, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id IN (:first.Id, :second.Id)],
            'Both entitlements must go');
    }

    @IsTest
    static void aKeptContractOrAssetKeepsItsBindingPolicies() {
        if (!contractItemPriceAvailable()) return;
        Id accountId = seedAccountWithContracts();
        UsageFixture f = loadUsageFixture();
        Contract priced = [SELECT Id FROM Contract WHERE AccountId = :accountId
            AND Id IN (SELECT ContractId FROM ContractItemPrice) LIMIT 1];
        Asset asset = new Asset(Name = 'RLM Utilities Kept Asset Policy', AccountId = accountId);
        insert asset;
        Datetime start = Datetime.now().addDays(-10);
        insert new List<BindingObjUsageRsrcPlcy>{
            new BindingObjUsageRsrcPlcy(BindingObjectId = priced.Id, UsageResourceId = f.resourceId, EffectiveStartDate = start),
            new BindingObjUsageRsrcPlcy(BindingObjectId = asset.Id, UsageResourceId = f.resourceId, EffectiveStartDate = start)
        };
        RLM_AccountUtilities.InputVariables iv = request(accountId, false, false, false);
        iv.PreserveContractsWithContractedPrices = true;

        Test.startTest();
        RLM_AccountUtilities.Result result = run(iv);
        Test.stopTest();

        Assert.areEqual(true, result.completed, 'The reset must complete. Reason: ' + result.reason);
        Assert.areEqual(2, [SELECT COUNT() FROM BindingObjUsageRsrcPlcy WHERE BindingObjectId IN (:priced.Id, :asset.Id)],
            'The kept contract and the kept asset keep their binding policies');
    }

    @IsTest
    static void invoicesStillProcessingAreAWaitNotAnAccessProblem() {
        Assert.isTrue(RLM_AccountUtilities.invoiceBlocker('In Progress').startsWith('still processing'),
            'PRECONDITION: an invoice still processing blocks');
        RLM_AccountUtilities.Blocker waiting = new RLM_AccountUtilities.Blocker();
        waiting.reason = RLM_AccountUtilities.INVOICE_IN_PROGRESS;
        RLM_AccountUtilities.Blocker access = new RLM_AccountUtilities.Blocker();
        access.reason = RLM_AccountUtilities.NO_ACCESS;

        String waitOnly = RLM_AccountUtilities.refusal(new List<RLM_AccountUtilities.Blocker>{ waiting }, 'X');
        Assert.isTrue(waitOnly.startsWith(RLM_AccountUtilities.NOT_YET)
            && waitOnly.contains(RLM_AccountUtilities.NOT_YET_ADVICE)
            && !waitOnly.contains(RLM_AccountUtilities.REFUSED_ADVICE),
            'Invoices still processing alone are a wait, not an access problem. Got: ' + waitOnly);

        String both = RLM_AccountUtilities.refusal(new List<RLM_AccountUtilities.Blocker>{ waiting, access }, 'X');
        Assert.isTrue(both.startsWith(RLM_AccountUtilities.REFUSED)
            && both.contains(RLM_AccountUtilities.REFUSED_ADVICE)
            && both.contains(RLM_AccountUtilities.NOT_YET_ADVICE),
            'With an access problem as well, both pieces of advice. Got: ' + both);

        String accessOnly = RLM_AccountUtilities.refusal(new List<RLM_AccountUtilities.Blocker>{ access }, 'X');
        Assert.isTrue(accessOnly.startsWith(RLM_AccountUtilities.REFUSED)
            && !accessOnly.contains(RLM_AccountUtilities.NOT_YET_ADVICE),
            'An access problem alone says nothing about waiting. Got: ' + accessOnly);
    }

    @IsTest
    static void aPermissionTheOrgDoesNotHaveReadsAsFalseAndNothingElse() {
        // Each permission outside the core set is read on its own, so a field this org or
        // release lacks reads as false without hiding the others.
        Assert.areEqual(false, RLM_AccountUtilities.hasUserPermission('PermissionsRlmResetNoSuchPermission'),
            'A permission field the org does not have reads as false');
        Boolean admin = [SELECT PermissionsModifyAllData FROM UserPermissionAccess LIMIT 1].PermissionsModifyAllData == true;
        Assert.areEqual(admin, RLM_AccountUtilities.hasUserPermission('PermissionsModifyAllData'),
            'The core permissions still read as they are');
    }

    @IsTest
    static void aFileGoesOnlyWhenTheUserRunningTheResetOwnsIt() {
        // Live 264 (as the salesrep persona): UserRecordAccess said a file the user owned
        // could not be deleted, yet the delete succeeded; another user's file was refused.
        User rep = newStandardUser();
        PermissionSet quotes = new PermissionSet(Name = 'RLM_Utilities_Test_Quotes_' + TOKEN,
            Label = 'RLM Utilities Test Quotes');
        insert quotes;
        insert new ObjectPermissions(ParentId = quotes.Id, SobjectType = 'Quote', PermissionsRead = true,
            PermissionsCreate = true, PermissionsEdit = true, PermissionsDelete = true);
        insert new PermissionSetAssignment(AssigneeId = rep.Id, PermissionSetId = quotes.Id);
        Account a;
        Quote q;
        Id repFile;
        System.runAs(rep) {
            a = new Account(Name = 'RLM Utilities Rep Files');
            insert a;
            Opportunity o = new Opportunity(Name = 'RLM Utilities Rep Files Opp', AccountId = a.Id,
                StageName = 'Prospecting', CloseDate = Date.today().addDays(30));
            insert o;
            q = new Quote(Name = 'RLM Utilities Rep Files Quote', OpportunityId = o.Id);
            insert q;
            repFile = newFile('RLM Rep File', q.Id);
        }
        Id adminFile = newFile('RLM Admin File', q.Id);

        RLM_AccountUtilities.Result refused;
        System.runAs(rep) {
            refused = run(request(a.Id, false, false, false));
        }
        Assert.areEqual(false, refused.completed, 'Another user\'s file must refuse the reset');
        Assert.isTrue(refused.reason.contains(entry(ContentDocument.SObjectType, 1))
            && !refused.reason.contains('RLM Rep File'),
            'Only the other user\'s file blocks. Got: ' + refused.reason);
        Assert.areEqual(2, [SELECT COUNT() FROM ContentDocument WHERE Id IN (:repFile, :adminFile)], 'Nothing may change');

        delete new ContentDocument(Id = adminFile);
        RLM_AccountUtilities.Result result;
        System.runAs(rep) {
            Test.startTest();
            result = run(request(a.Id, false, false, false));
            Test.stopTest();
        }
        Assert.areEqual(true, result.completed, 'The user owns the rest, so the reset runs. Reason: ' + result.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM ContentDocument WHERE Id = :repFile], 'The user\'s own file goes');
        Assert.areEqual(0, [SELECT COUNT() FROM Quote WHERE Id = :q.Id], 'The quote goes');
    }

    @IsTest
    static void anOwnEntitlementNotReadThisRunIsNotReportedAsAnotherAccounts() {
        Account a = newAccount();
        UsageFixture f = loadUsageFixture();
        UsageEntitlementAccount uea = newEntitlementAccount(a.Id, f);
        // Two of the account's entitlements, read one a run; a bucket under its entitlement
        // account holds the second. When the first run reads only the first, the bucket
        // holds an entitlement the plan has not read: the account's own, not another's.
        TransactionUsageEntitlement first = newEntitlement(a.Id, a.Id, null, f);
        TransactionUsageEntitlement second = newEntitlement(a.Id, a.Id, null, f);
        UsageEntitlementBucket held = newBucket(uea.Id, second.Id, f);
        RLM_AccountUtilities.usageBatchForTest = 1;

        Test.startTest();
        RLM_AccountUtilities.Result firstRun = run(request(a.Id, false, false, false));
        RLM_AccountUtilities.Result secondRun = run(request(a.Id, false, false, false));
        Test.stopTest();

        Assert.areEqual(false, firstRun.completed, 'The first run read part of the usage and asks for another');
        String reported = firstRun.reason + ' ' + firstRun.retainedSummary;
        Assert.isFalse(reported.contains('another account'),
            'The account\'s own entitlement must not be reported as another account\'s. Got: ' + reported);
        Assert.areEqual(true, secondRun.completed, 'The second run finishes. Reason: ' + secondRun.reason);
        Assert.areEqual(0, [SELECT COUNT() FROM UsageEntitlementBucket WHERE Id = :held.Id], 'The bucket goes');
        Assert.areEqual(0, [SELECT COUNT() FROM TransactionUsageEntitlement WHERE Id IN (:first.Id, :second.Id)],
            'Both entitlements go');
    }

    @IsTest
    static void otherAccountsAreUntouched() {
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
