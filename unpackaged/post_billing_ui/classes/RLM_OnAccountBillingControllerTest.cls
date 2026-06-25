@isTest
private class RLM_OnAccountBillingControllerTest {

    @isTest
    static void getBillingSummary_nullAccount_returnsEmptyMap() {
        Test.startTest();
        Map<String, Object> result = RLM_OnAccountBillingController.getBillingSummary(null);
        Test.stopTest();
        System.assertNotEquals(null, result, 'A non-null map should always be returned.');
        System.assertEquals(0, result.size(), 'A null account id should short-circuit to an empty map.');
    }

    // Invoices/DebitMemos/CreditMemos/Payments/Refunds are system-managed and not insertable
    // in Apex tests. An Account with no billing activity drives every aggregate and count down
    // its empty path, verifying the summary returns zero balances and clean status flags.
    @isTest
    static void getBillingSummary_accountWithNoBilling_returnsZeroBalances() {
        Account acc = new Account(Name = 'RLM On-Account Billing Test');
        insert acc;

        Test.startTest();
        Map<String, Object> result = RLM_OnAccountBillingController.getBillingSummary(acc.Id);
        Test.stopTest();

        System.assertNotEquals(null, result, 'A result map should be returned.');
        System.assertEquals(0, (Decimal) result.get('invoiceBalance'), 'No invoices -> zero balance.');
        System.assertEquals(0, (Decimal) result.get('debitMemoBalance'), 'No debit memos -> zero balance.');
        System.assertEquals(0, (Decimal) result.get('creditMemoBalance'), 'No credit memos -> zero balance.');
        System.assertEquals(0, (Decimal) result.get('paymentBalance'), 'No payments -> zero balance.');
        System.assertEquals(0, (Decimal) result.get('netAccountBalance'), 'No activity -> zero net balance.');
        System.assertEquals(0, (Integer) result.get('totalInvoices'), 'No invoices -> zero count.');
        System.assertEquals(0, (Integer) result.get('overdueCount'), 'No invoices -> zero overdue.');
        System.assertEquals(false, (Boolean) result.get('inCollections'),
            'No collection plans -> account is not in collections.');
    }
}
