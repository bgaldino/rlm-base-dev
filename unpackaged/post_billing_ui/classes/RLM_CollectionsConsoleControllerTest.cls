@isTest
private class RLM_CollectionsConsoleControllerTest {

    // Invoice is system-managed and not insertable in Apex tests, and the schedule, plan-item and
    // dispute lookups only run for the invoices found. With no qualifying invoices visible
    // (SeeAllData=false), the worklist query returns empty and those lookups are skipped; this
    // verifies the method runs clean and returns a safe empty result.
    @isTest
    static void getHighValueDelinquents_noData_returnsEmptyList() {
        Test.startTest();
        List<RLM_CollectionsConsoleController.DelinquentWrapper> rows =
            RLM_CollectionsConsoleController.getHighValueDelinquents();
        Test.stopTest();
        System.assertNotEquals(null, rows, 'A non-null list must always be returned.');
        System.assertEquals(0, rows.size(),
            'With no qualifying invoices in the test context, the worklist should be empty.');
    }

    // Exercises the wrapper projection with synthetic invoices + related-record maps, since
    // Invoice can't be inserted. Verifies field mapping plus the dispute/plan default fallbacks.
    @isTest
    static void buildDelinquents_projectsFieldsAndDefaults() {
        Id acctId = mintId(Account.SObjectType);
        Id inv1   = mintId(Invoice.SObjectType);
        Id inv2   = mintId(Invoice.SObjectType);
        Id planId = mintId(Account.SObjectType); // plan record id is stored, not validated

        Invoice i1 = synthInvoice(inv1, acctId, 'Acme Corp', 5000, 45, 'INV-001');
        Invoice i2 = synthInvoice(inv2, acctId, 'Beta LLC', 3200, 31, 'INV-002');

        Map<Id, Date>   ptp      = new Map<Id, Date>{ inv1 => Date.today() };
        Map<Id, String> planName = new Map<Id, String>{ inv1 => 'Plan A' };
        Map<Id, Id>     planIds  = new Map<Id, Id>{ inv1 => planId };
        Map<Id, String> disputes = new Map<Id, String>{ inv2 => 'Billing Error - Overcharge' };

        Test.startTest();
        List<RLM_CollectionsConsoleController.DelinquentWrapper> rows =
            RLM_CollectionsConsoleController.buildDelinquents(
                new List<Invoice>{ i1, i2 }, ptp, planName, planIds, disputes,
                new Map<Id, String>{ acctId => 'Acme Corp' });
        Test.stopTest();

        System.assertEquals(2, rows.size(), 'Both invoices should produce a wrapper.');

        RLM_CollectionsConsoleController.DelinquentWrapper w1 = rows[0];
        System.assertEquals(5000, w1.balance, 'Balance projected.');
        System.assertEquals(45, w1.overdueDays, 'Overdue days projected.');
        System.assertEquals('INV-001', w1.documentNumber, 'Document number projected.');
        System.assertEquals('Acme Corp', w1.businessAccount, 'Related account name projected.');
        System.assertEquals('Plan A', w1.collectionPlanId, 'Plan name projected.');
        System.assertEquals(planId, w1.collectionPlanRecordId, 'Plan record id projected.');
        System.assertEquals(Date.today(), w1.ptpDate, 'PTP date projected.');
        System.assertEquals('-', w1.disputeReason, 'No dispute -> default dash.');

        RLM_CollectionsConsoleController.DelinquentWrapper w2 = rows[1];
        System.assertEquals('Billing Error - Overcharge', w2.disputeReason, 'Dispute reason projected.');
        System.assertEquals('', w2.collectionPlanId, 'No plan -> empty string.');
        System.assertEquals(null, w2.ptpDate, 'No PTP -> null.');
    }

    // An invoice without a billing account shows a dash for the account, and no related records
    // leave the defaults: a dash for the dispute, a blank plan, no promise to pay.
    @isTest
    static void buildDelinquents_invoiceWithoutBillingAccount_usesDefaults() {
        Id invId = mintId(Invoice.SObjectType);
        Invoice inv = (Invoice) JSON.deserialize(JSON.serialize(new Map<String, Object>{
            'attributes' => new Map<String, Object>{ 'type' => 'Invoice' },
            'Id' => invId,
            'Balance' => 2500,
            'DaysInvoiceOverdue' => 40
        }), Invoice.class);

        Test.startTest();
        List<RLM_CollectionsConsoleController.DelinquentWrapper> rows =
            RLM_CollectionsConsoleController.buildDelinquents(new List<Invoice>{ inv },
                new Map<Id, Date>(), new Map<Id, String>(), new Map<Id, Id>(), new Map<Id, String>(), new Map<Id, String>());
        Test.stopTest();

        Assert.areEqual(1, rows.size(), 'One row per invoice.');
        Assert.areEqual(invId, rows[0].Id, 'The row is the invoice.');
        Assert.areEqual('—', rows[0].businessAccount, 'No billing account, a dash.');
        Assert.isNull(rows[0].accountId, 'No billing account id.');
        Assert.areEqual('-', rows[0].disputeReason, 'No dispute, a dash.');
        Assert.areEqual('', rows[0].collectionPlanId, 'No plan, blank.');
        Assert.isNull(rows[0].collectionPlanRecordId, 'No plan record.');
        Assert.isNull(rows[0].ptpDate, 'No promise to pay.');
        assertAmount(2500, rows[0].balance, 'The balance is the invoice balance.');
        assertAmount(2500, rows[0].invoiceBalance, 'The invoice balance is the invoice balance.');
        Assert.areEqual(40, rows[0].overdueDays, 'Days overdue come from the invoice.');
        Assert.isNull(rows[0].documentNumber, 'No document number on the invoice, none on the row.');
    }

    // A user who cannot read Account gets no names back, and the rows are still built, with a
    // dash for the account rather than an exception or a dropped row.
    @isTest
    static void buildDelinquents_forAUserWhoCannotReadAccounts_keepsRowsWithDashNames() {
        User noAccess = RLM_BillingUITestUsers.create(new List<String>(), new List<String>());
        Id acctId = mintId(Account.SObjectType);
        Invoice i1 = synthInvoice(mintId(Invoice.SObjectType), acctId, 'Acme Corp', 5000, 45, 'INV-001');
        List<RLM_CollectionsConsoleController.DelinquentWrapper> rows;

        Test.startTest();
        System.runAs(noAccess) {
            Assert.isFalse(Schema.SObjectType.Account.isAccessible(), 'PRECONDITION: the user cannot read Account.');
            Map<Id, String> names = RLM_AccountNames.forIds(new Set<Id>{ acctId });
            Assert.isTrue(names.isEmpty(), 'A refused Account read gives no names, not an exception.');
            rows = RLM_CollectionsConsoleController.buildDelinquents(new List<Invoice>{ i1 },
                new Map<Id, Date>(), new Map<Id, String>(), new Map<Id, Id>(), new Map<Id, String>(), names);
        }
        Test.stopTest();

        Assert.areEqual(1, rows.size(), 'The row is kept.');
        Assert.areEqual('—', rows[0].businessAccount, 'The name shows a dash.');
        Assert.areEqual(acctId, rows[0].accountId, 'The row still names its account by id.');
    }

    @isTest
    static void buildDelinquents_noInvoices_returnsEmpty() {
        Test.startTest();
        List<RLM_CollectionsConsoleController.DelinquentWrapper> rows =
            RLM_CollectionsConsoleController.buildDelinquents(new List<Invoice>(),
                new Map<Id, Date>(), new Map<Id, String>(), new Map<Id, Id>(), new Map<Id, String>(), new Map<Id, String>());
        Test.stopTest();

        Assert.isNotNull(rows, 'A list is returned for no invoices.');
        Assert.isTrue(rows.isEmpty(), 'No invoices, no rows.');
    }

    // Payment schedules, plan items and disputes on invoices cannot exist in a test (Invoice is
    // not insertable), so these pass rows built with JSON.deserialize, child subquery included.
    private static PaymentSchedule schedule(Id invoiceId, Date newestItemDate) {
        List<Object> items = newestItemDate == null
            ? new List<Object>()
            : new List<Object>{ new Map<String, Object>{ 'TargetPaymentProcessingDate' => newestItemDate } };
        return (PaymentSchedule) JSON.deserialize(JSON.serialize(new Map<String, Object>{
            'ReferenceEntityId' => invoiceId,
            'PaymentScheduleItems' => new Map<String, Object>{
                'totalSize' => items.size(), 'done' => true, 'records' => items }
        }), PaymentSchedule.class);
    }

    // An invoice's promise-to-pay date is the newest item date across its schedules; a schedule
    // with no dated item adds nothing.
    @isTest
    static void latestPromiseDates_keepsEachInvoicesNewestItemDate() {
        Id invoiceA = mintId(Invoice.SObjectType);
        Id invoiceB = mintId(Invoice.SObjectType);
        Id invoiceC = mintId(Invoice.SObjectType);
        Date d = Date.newInstance(2026, 6, 1);

        Test.startTest();
        Map<Id, Date> dates = RLM_CollectionsConsoleController.latestPromiseDates(new List<PaymentSchedule>{
            schedule(invoiceA, d.addDays(10)),
            schedule(invoiceA, d.addDays(30)),
            schedule(invoiceA, d.addDays(20)),
            schedule(invoiceB, d),
            schedule(invoiceC, null)
        });
        Test.stopTest();

        Assert.areEqual(d.addDays(30), dates.get(invoiceA), 'The newest date across the invoice\'s schedules wins');
        Assert.areEqual(d, dates.get(invoiceB), 'A single schedule gives its own date');
        Assert.isFalse(dates.containsKey(invoiceC), 'A schedule with no dated item adds nothing');
    }

    // Each invoice keeps the first collection plan found for it, by name and by id together.
    @isTest
    static void addFirstCollectionPlans_keepsTheFirstPlanPerInvoice() {
        Id invoiceA = mintId(Invoice.SObjectType);
        Id invoiceB = mintId(Invoice.SObjectType);
        Id firstPlan = mintId(CollectionPlan.SObjectType);
        Id secondPlan = mintId(CollectionPlan.SObjectType);
        Id otherPlan = mintId(CollectionPlan.SObjectType);
        List<CollectionPlanItem> items = new List<CollectionPlanItem>();
        for (List<Object> r : new List<List<Object>>{
            new List<Object>{ invoiceA, firstPlan, 'Plan One' },
            new List<Object>{ invoiceA, secondPlan, 'Plan Two' },
            new List<Object>{ invoiceB, otherPlan, 'Plan Three' }
        }) {
            items.add((CollectionPlanItem) JSON.deserialize(JSON.serialize(new Map<String, Object>{
                'InvoiceId' => r[0], 'CollectionPlanId' => r[1],
                'CollectionPlan' => new Map<String, Object>{ 'Id' => r[1], 'Name' => r[2] }
            }), CollectionPlanItem.class));
        }
        Map<Id, String> names = new Map<Id, String>();
        Map<Id, Id> ids = new Map<Id, Id>();

        Test.startTest();
        RLM_CollectionsConsoleController.addFirstCollectionPlans(items, names, ids);
        Test.stopTest();

        Assert.areEqual('Plan One', names.get(invoiceA), 'The first plan found for an invoice is kept');
        Assert.areEqual(firstPlan, ids.get(invoiceA), 'The plan id matches the kept name');
        Assert.areEqual('Plan Three', names.get(invoiceB), 'Each invoice gets its own plan');
        Assert.areEqual(otherPlan, ids.get(invoiceB), 'Each invoice gets its own plan id');
    }

    // An invoice's dispute reason is the first dispute's type, with " - " and its subtype when it
    // has one.
    @isTest
    static void disputeReasons_typeThenSubtypeFromTheFirstDispute() {
        if (!RLM_CollectionsConsoleController.disputeFieldAvailable('InvoiceId')) {
            // No Dispute.InvoiceId in this org: the console never reads dispute reasons here.
            return;
        }
        Id invoiceA = mintId(Invoice.SObjectType);
        Id invoiceB = mintId(Invoice.SObjectType);
        List<Dispute> disputes = new List<Dispute>();
        for (List<Object> r : new List<List<Object>>{
            new List<Object>{ invoiceA, 'Billing', 'Wrong Amount' },
            new List<Object>{ invoiceA, 'Service', null },
            new List<Object>{ invoiceB, 'Service', ' ' }
        }) {
            disputes.add((Dispute) JSON.deserialize(JSON.serialize(new Map<String, Object>{
                'InvoiceId' => r[0], 'DisputeType' => r[1], 'DisputeSubtype' => r[2]
            }), Dispute.class));
        }

        Test.startTest();
        Map<Id, String> reasons = RLM_CollectionsConsoleController.disputeReasons(disputes);
        Test.stopTest();

        Assert.areEqual('Billing - Wrong Amount', reasons.get(invoiceA), 'The first dispute wins: type, then subtype');
        Assert.areEqual('Service', reasons.get(invoiceB), 'A blank subtype leaves the type alone');
    }

    // Smoke test: for an invoice with no schedules, plan items or disputes, the related-record
    // lookups run without throwing and leave every map empty. The query count is not checked:
    // the dispute query runs only where the org has Dispute.InvoiceId, and in user mode it may
    // fail and be caught, so the count varies by org.
    @isTest
    static void loadRelatedRecords_findsNothingForUnknownInvoices() {
        Set<Id> invoiceIds = new Set<Id>{ mintId(Invoice.SObjectType) };
        Map<Id, Date> ptp = new Map<Id, Date>();
        Map<Id, String> planNames = new Map<Id, String>();
        Map<Id, Id> planIds = new Map<Id, Id>();
        Map<Id, String> reasons = new Map<Id, String>();

        Test.startTest();
        RLM_CollectionsConsoleController.loadRelatedRecords(invoiceIds, ptp, planNames, planIds, reasons);
        Test.stopTest();

        Assert.isTrue(ptp.isEmpty() && planNames.isEmpty() && planIds.isEmpty() && reasons.isEmpty(),
            'Nothing is found for an invoice with no related records');
    }

    // A user who cannot read payment schedules or collection plan items (here, RLM_BillingUI and the
    // Billing license without a billing role: both read as "not supported") still gets the related
    // lookups: each refused query is caught on its own instead of failing the call.
    @isTest
    static void loadRelatedRecords_withoutAccess_skipsEachRefusedColumn() {
        User noRole = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        Map<Id, Date> ptp = new Map<Id, Date>();
        Map<Id, String> planNames = new Map<Id, String>();
        Map<Id, Id> planIds = new Map<Id, Id>();
        Map<Id, String> reasons = new Map<Id, String>();
        Boolean scheduleRefused = false;
        Boolean planItemRefused = false;
        String failed;

        Test.startTest();
        System.runAs(noRole) {
            try { Database.query('SELECT Id FROM PaymentSchedule LIMIT 1', AccessLevel.USER_MODE); }
            catch (QueryException e) { scheduleRefused = true; }
            try { Database.query('SELECT Id FROM CollectionPlanItem LIMIT 1', AccessLevel.USER_MODE); }
            catch (QueryException e) { planItemRefused = true; }
            try {
                RLM_CollectionsConsoleController.loadRelatedRecords(
                    new Set<Id>{ mintId(Invoice.SObjectType) }, ptp, planNames, planIds, reasons);
            } catch (Exception e) {
                failed = e.getTypeName() + ': ' + e.getMessage();
            }
        }
        Test.stopTest();

        Assert.isTrue(scheduleRefused, 'PRECONDITION: this user cannot read PaymentSchedule in user mode');
        Assert.isTrue(planItemRefused, 'PRECONDITION: this user cannot read CollectionPlanItem in user mode');
        Assert.isNull(failed, 'Each refused lookup is skipped instead of failing the call: ' + failed);
    }

    // A billing operations user without the collections license can read payment schedules but not
    // collection plan items. The refused collection-plan query does not stop the lookups after it:
    // the dispute query still runs (where the org has Dispute.InvoiceId). A query refused as "not
    // supported" does not count toward the query limit (measured on 264), so the count is the
    // payment-schedule query plus the dispute query.
    @isTest
    static void loadRelatedRecords_refusedCollectionPlanStillRunsTheDisputeLookup() {
        User billingOnly = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI', 'RevenueLifecycleManagementBillingOperations' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        Integer queries;
        Integer expected;
        String failed;

        Test.startTest();
        System.runAs(billingOnly) {
            expected = 1 + (RLM_CollectionsConsoleController.disputeFieldAvailable('InvoiceId') ? 1 : 0);
            Integer before = Limits.getQueries();
            try {
                RLM_CollectionsConsoleController.loadRelatedRecords(
                    new Set<Id>{ mintId(Invoice.SObjectType) }, new Map<Id, Date>(), new Map<Id, String>(),
                    new Map<Id, Id>(), new Map<Id, String>());
            } catch (Exception e) {
                failed = e.getTypeName() + ': ' + e.getMessage();
            }
            queries = Limits.getQueries() - before;
        }
        Test.stopTest();

        Assert.isNull(failed, 'The refused collection-plan lookup is skipped: ' + failed);
        Assert.areEqual(expected, queries,
            'The payment-schedule and (where available) dispute queries run after the refused collection-plan query');
    }

    // The dispute-field check is true only for a field the Dispute object has.
    @isTest
    static void disputeFieldAvailable_answersForTheDisputeObjectsOwnFields() {
        Test.startTest();
        Boolean known = RLM_CollectionsConsoleController.disputeFieldAvailable('DisputeType');
        Boolean invoiceOnly = RLM_CollectionsConsoleController.disputeFieldAvailable('DaysInvoiceOverdue');
        Test.stopTest();

        Assert.isTrue(known, 'DisputeType is a Dispute field');
        Assert.isFalse(invoiceOnly, 'An Invoice field is not a Dispute field');
    }

    // Fails on a null amount and names both values in the message; Decimal equality already
    // ignores scale.
    private static void assertAmount(Decimal expected, Decimal actual, String message) {
        Assert.isTrue(actual != null && actual == expected,
            message + ' Expected ' + expected + ', got ' + actual + '.');
    }

    private static Integer seq = 0;

    private static Id mintId(Schema.SObjectType t) {
        seq++;
        String suffix = String.valueOf(seq);
        while (suffix.length() < 12) {
            suffix = '0' + suffix;
        }
        return Id.valueOf(t.getDescribe().getKeyPrefix() + suffix);
    }

    // Invoice fields are not writeable on a constructed sObject; build via JSON to populate
    // Balance/DaysInvoiceOverdue and the BillingAccount.Name relationship.
    private static Invoice synthInvoice(
        Id id, Id acctId, String acctName, Decimal balance, Integer overdue, String docNum
    ) {
        Map<String, Object> m = new Map<String, Object>{
            'attributes'        => new Map<String, Object>{ 'type' => 'Invoice' },
            'Id'                => id,
            'BillingAccountId'  => acctId,
            'Balance'           => balance,
            'DaysInvoiceOverdue'=> overdue,
            'DocumentNumber'    => docNum,
            'BillingAccount'    => new Map<String, Object>{
                'attributes' => new Map<String, Object>{ 'type' => 'Account' },
                'Id'         => acctId,
                'Name'       => acctName
            }
        };
        return (Invoice) JSON.deserialize(JSON.serialize(m), Invoice.class);
    }
}
