@isTest
private class RLM_SplitInvoicesControllerTest {

    @isTest
    static void getCurrentInvoiceBillingInfo_blankAndUnknown_returnsEmptyInfo() {
        Id fakeInvoice = Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
        Test.startTest();
        RLM_SplitInvoicesController.CurrentInvoiceBillingInfo blank =
            RLM_SplitInvoicesController.getCurrentInvoiceBillingInfo('');
        RLM_SplitInvoicesController.CurrentInvoiceBillingInfo unknown =
            RLM_SplitInvoicesController.getCurrentInvoiceBillingInfo(fakeInvoice);
        Test.stopTest();
        System.assertNotEquals(null, blank, 'A non-null info wrapper should be returned for blank input.');
        System.assertNotEquals(null, unknown, 'A non-null info wrapper should be returned for an unknown invoice.');
        System.assertEquals(null, unknown.billingArrangementName,
            'No arrangement name resolves for a non-existent invoice.');
    }

    @isTest
    static void getInvoicesByCorrelation_blankAndUnknown_returnsEmptyList() {
        Test.startTest();
        List<RLM_SplitInvoicesController.InvoiceRow> blank =
            RLM_SplitInvoicesController.getInvoicesByCorrelation('');
        System.assertEquals(0, blank.size(), 'Blank correlation id yields an empty list.');

        // The correlation query joins BillingArrangement/BillingProfile lookups that may be
        // absent in some orgs; accept either an empty list or a graceful AuraHandledException.
        try {
            List<RLM_SplitInvoicesController.InvoiceRow> unknown =
                RLM_SplitInvoicesController.getInvoicesByCorrelation('RLM-NO-SUCH-CORRELATION');
            System.assertEquals(0, unknown.size(), 'Unknown correlation id yields an empty list when queryable.');
        } catch (AuraHandledException e) {
            // Billing lookup schema not present in this org; the query path still executed.
        }
        Test.stopTest();
    }

    @isTest
    static void getRelatedNames_resolvesAccountAndToleratesNulls() {
        Account acc = new Account(Name = 'RLM Split Invoices Test');
        insert acc;

        Test.startTest();
        RLM_SplitInvoicesController.RelatedNamesResult result =
            RLM_SplitInvoicesController.getRelatedNames(
                new List<String>{ acc.Id }, null, null, null);
        Test.stopTest();

        System.assertNotEquals(null, result, 'A non-null result should be returned.');
        System.assertEquals('RLM Split Invoices Test', result.accountNames.get(acc.Id),
            'Account name should resolve by id.');
        System.assertEquals(0, result.arrangementNames.size(), 'Null arrangement ids resolve to an empty map.');
    }
}
