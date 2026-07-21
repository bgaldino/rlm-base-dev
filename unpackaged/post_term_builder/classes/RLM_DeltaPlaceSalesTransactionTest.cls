@IsTest
private class RLM_DeltaPlaceSalesTransactionTest {

    /**
     * revalidate is the best-effort reprice appended to every direct-DML mutation. Its contract:
     * NEVER throw (a reprice failure must not roll back the committed mutation) and always return a
     * decided Result. A null quote id short-circuits to a non-success Result without touching PST.
     */
    @IsTest
    static void testRevalidateNullQuoteIsNonSuccessAndDoesNotThrow() {
        Test.startTest();
        RLM_DeltaPlaceSalesTransaction.Result res = RLM_DeltaPlaceSalesTransaction.revalidate(null);
        Test.stopTest();

        System.assertNotEquals(null, res, 'revalidate always returns a Result');
        System.assertEquals(false, res.isSuccess, 'A null quote id cannot be revalidated');
        System.assertNotEquals(null, res.errorMessage, 'A non-success Result carries an error message');
    }

    /**
     * With a real quote id, revalidate builds a header-only PST graph and commits. PST does not fully
     * run in the test context, so isSuccess is not asserted — the guarantee under test is that the
     * method RETURNS a decided Result rather than propagating an exception (the try/catch backstop),
     * which is what keeps the caller's already-committed DML safe.
     */
    @IsTest
    static void testRevalidateRealQuoteReturnsDecidedResultWithoutThrowing() {
        Account acct = new Account(Name = 'Revalidate Test Account');
        insert acct;
        Opportunity opp = new Opportunity(
            Name = 'Revalidate Test Opp', StageName = 'Prospecting', CloseDate = Date.today().addDays(30), AccountId = acct.Id
        );
        insert opp;
        Quote q = new Quote(Name = 'Revalidate Test Quote', OpportunityId = opp.Id, Pricebook2Id = Test.getStandardPricebookId());
        insert q;

        Test.startTest();
        RLM_DeltaPlaceSalesTransaction.Result res = RLM_DeltaPlaceSalesTransaction.revalidate(q.Id);
        Test.stopTest();

        System.assertNotEquals(null, res, 'revalidate returns a decided Result for a real quote (never throws)');
    }
}
