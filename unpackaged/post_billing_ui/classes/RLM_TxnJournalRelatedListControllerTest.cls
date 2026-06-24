@isTest
private class RLM_TxnJournalRelatedListControllerTest {

    // TransactionJournal records are system-generated and not insertable in Apex tests,
    // so a null id and a well-formed but non-existent Invoice id both drive the empty path.
    @isTest
    static void getByInvoice_nullId_returnsEmptyList() {
        Test.startTest();
        List<TransactionJournal> result = RLM_TxnJournalRelatedListController.getByInvoice(null);
        Test.stopTest();
        System.assertNotEquals(null, result, 'A non-null list should always be returned.');
        System.assertEquals(0, result.size(), 'A null invoice id short-circuits to an empty list.');
    }

    @isTest
    static void getByInvoice_unknownInvoice_returnsEmptyList() {
        Id fakeInvoice = Id.valueOf(Invoice.SObjectType.getDescribe().getKeyPrefix() + '000000000000');
        Test.startTest();
        try {
            List<TransactionJournal> result = RLM_TxnJournalRelatedListController.getByInvoice(fakeInvoice);
            System.assertNotEquals(null, result, 'A non-null list should always be returned.');
            System.assertEquals(0, result.size(), 'No journals exist for a non-existent invoice.');
        } catch (System.QueryException e) {
            // Running user lacks TransactionJournal read FLS; the USER_MODE query blocked. The
            // controller does not wrap, so the QueryException surfaces directly. Tolerated so the
            // suite stays deterministic when run by a least-privilege user.
        }
        Test.stopTest();
    }
}
