@isTest
private class RLM_CollectionsConsoleControllerTest {

    // Invoice and the downstream PaymentSchedule/CollectionPlanItem/Dispute records are
    // system-managed and not insertable in Apex tests. With no qualifying invoices visible
    // (SeeAllData=false), the worklist query returns empty and the dispute/schedule lookups
    // are skipped — this verifies the method runs clean and returns a safe empty result.
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
                new List<Invoice>{ i1, i2 }, ptp, planName, planIds, disputes);
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
