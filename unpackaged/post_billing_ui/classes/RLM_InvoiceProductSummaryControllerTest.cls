@isTest
private class RLM_InvoiceProductSummaryControllerTest {

    private static Id fakeInvoiceId() {
        return Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
    }

    // Invoices/InvoiceLines are system-managed and not insertable in Apex tests. A non-existent
    // invoice makes the single-row Invoice query throw, surfaced as an AuraHandledException.
    @isTest
    static void getInvoiceProductSummary_unknownInvoice_throws() {
        Boolean threw = false;
        Test.startTest();
        try {
            RLM_InvoiceProductSummaryController.getInvoiceProductSummary(fakeInvoiceId());
        } catch (AuraHandledException e) {
            threw = true;
        }
        Test.stopTest();
        System.assert(threw, 'A non-existent invoice should raise an AuraHandledException.');
    }

    // No invoice lines -> nothing to update; the method must return without writing any records.
    @isTest
    static void saveLineAttributes_unknownInvoice_noOp() {
        Test.startTest();
        Integer rowsBefore = Limits.getDmlRows();
        RLM_InvoiceProductSummaryController.saveLineAttributes(fakeInvoiceId());
        Integer rowsAfter = Limits.getDmlRows();
        Test.stopTest();
        System.assertEquals(rowsBefore, rowsAfter,
            'A non-existent invoice has no lines, so no records may be updated.');
    }

    // saveLineAttributes needs the line's BillingScheduleGroup to find its asset. For a user who
    // can't read BillingScheduleGroup, the save must fail rather than write nothing and report
    // success; the summary must still render, without attributes. A Billing-licensed user with
    // only RLM_BillingUI is such a user: the object also needs a billing role's user
    // permissions. The premise is checked first, so a platform change that opens the object
    // fails here as a broken premise rather than as a controller regression.
    @isTest
    static void bsgLookup_failsTheSaveButNotTheSummary_whenTheUserCannotReadIt() {
        User u = RLM_BillingUITestUsers.create(
            new List<String>{ 'RLM_BillingUI' },
            new List<String>{ RLM_BillingUITestUsers.BILLING_PSL });
        Id fakeBsg = Id.valueOf(BillingScheduleGroup.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
        Boolean premise = false;
        Boolean saveThrew = false;
        Map<Id, Id> summaryResult;
        System.runAs(u) {
            try {
                Database.query('SELECT Id FROM BillingScheduleGroup LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException e) {
                premise = true;
            }
            try {
                RLM_InvoiceProductSummaryController.resolveBsgToAsset(new Set<Id>{ fakeBsg }, true);
            } catch (QueryException e) {
                saveThrew = true;
            }
            summaryResult = RLM_InvoiceProductSummaryController.resolveBsgToAsset(new Set<Id>{ fakeBsg }, false);
        }
        Assert.isTrue(premise, 'Premise: this user must be unable to read BillingScheduleGroup.');
        Assert.isTrue(saveThrew, 'The save path must surface a BillingScheduleGroup read it may not run.');
        Assert.isTrue(summaryResult.isEmpty(), 'The summary path degrades to no assets.');
    }
}
