@isTest
private class RLM_MFG_SalesAgreementRLMOrderTest {

    // Builds a saProductListEntries request with one schedule row. PST itself is not
    // exercised here (it cannot run in an isolated unit-test context); these tests cover
    // the invocable's reachable input-validation and early-return branches.
    private static RLM_MFG_SalesAgreementRLMOrder.saProductListEntries makeRequest(
            Id accountId, List<SObject> schedules) {
        RLM_MFG_SalesAgreementRLMOrder.saProductListEntries e =
            new RLM_MFG_SalesAgreementRLMOrder.saProductListEntries();
        e.customerAcctId = accountId;
        e.priceBookId = Test.getStandardPricebookId();
        e.salesAgreementId = null;
        e.orderDate = Date.today();
        e.salesagreementProductSchedules = schedules;
        return e;
    }

    @isTest
    static void nullInput_returnsEmpty() {
        Test.startTest();
        List<String> r = RLM_MFG_SalesAgreementRLMOrder.createOrder(null);
        Test.stopTest();
        System.assertEquals(0, r.size(), 'Null input returns an empty list');
    }

    @isTest
    static void emptySchedules_returnsEmpty() {
        Account acct = new Account(Name = 'Test Account');
        insert acct;

        Test.startTest();
        List<String> r = RLM_MFG_SalesAgreementRLMOrder.createOrder(
            new List<RLM_MFG_SalesAgreementRLMOrder.saProductListEntries>{
                makeRequest(acct.Id, new List<SalesAgreementProductSchedule>())
            });
        Test.stopTest();

        System.assertEquals(0, r.size(), 'Empty schedule list returns an empty list before any PST call');
    }

    @isTest
    static void invalidAccountId_throwsFriendlyError() {
        // A non-Id customerAcctId must surface as the class's own exception, not a raw
        // StringException, before any query or PST call.
        RLM_MFG_SalesAgreementRLMOrder.saProductListEntries e =
            new RLM_MFG_SalesAgreementRLMOrder.saProductListEntries();
        e.customerAcctId = 'not-an-id';
        e.priceBookId = Test.getStandardPricebookId();
        e.orderDate = Date.today();
        e.salesagreementProductSchedules = new List<SalesAgreementProductSchedule>{
            new SalesAgreementProductSchedule()
        };

        Test.startTest();
        Boolean threw = false;
        try {
            RLM_MFG_SalesAgreementRLMOrder.createOrder(
                new List<RLM_MFG_SalesAgreementRLMOrder.saProductListEntries>{ e });
        } catch (RLM_MFG_SalesAgreementRLMOrder.RLM_MFG_SalesAgreementOrderException ex) {
            threw = true;
            System.assert(ex.getMessage().contains('Invalid customer account id'),
                'Expected friendly invalid-id message');
        }
        Test.stopTest();

        System.assert(threw, 'Malformed account id should throw a friendly, catchable error');
    }
}
