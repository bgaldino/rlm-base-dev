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
 * not per class, so this class's figure does not by itself block a deploy. It
 * is still under-tested: the usage-graph and fulfillment teardown --
 * deleteUsageSummaryGraph's delete rounds, deleteUsageEntitlementBucketsBottomUp,
 * deleteTransactionJournal and the fulfillment helpers -- are no-ops unless the
 * matching records exist, and building them needs fixtures this class does not
 * yet have: UsageEntitlementAccount alone requires a PricebookEntry plus
 * billing-period fields, and UsageEntitlementBucket requires a UsageResource
 * and a UnitOfMeasure. Those objects ARE createable, so the coverage is
 * reachable -- it is simply a separate piece of work.
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
 * The live verification that does cover the usage graph is
 * scripts/apex/validateRatedUsage.apex plus the usage-consumption skill; the
 * DeleteAssets gating below was additionally confirmed end-to-end against a
 * real rated asset with AssetRateCardEntry rows.
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

    // ------------------------------------------------------------ scope guard

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
