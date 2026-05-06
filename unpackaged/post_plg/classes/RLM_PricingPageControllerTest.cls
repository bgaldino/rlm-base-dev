@isTest
private class RLM_PricingPageControllerTest {

    @isTest
    static void testConstructor() {
        RLM_PricingPageController ctrl = new RLM_PricingPageController();
        System.assertNotEquals(null, ctrl);
    }

    @isTest
    static void testStartFreeTrial_FlowNotFound() {
        Map<String, Object> result = RLM_PricingPageController.startFreeTrial(
            'Jane', 'Smith', 'jane@test.com', 'Test Corp', 'Pro'
        );
        System.assertEquals(false, result.get('success'),
            'Should fail gracefully when Flow is not deployed');
    }

    @isTest
    static void testRequestQuote_FlowNotFound() {
        Map<String, Object> result = RLM_PricingPageController.requestQuote(
            'Jane', 'Smith', 'jane@test.com', 'Test Corp',
            '+1555123456', 'Enterprise', 10, 'Need enterprise plan'
        );
        System.assertEquals(false, result.get('success'),
            'Should fail gracefully when Flow is not deployed');
    }

    @isTest
    static void testConvertTrial_FlowNotFound() {
        Account acc = new Account(Name = 'Test Corp');
        insert acc;

        Map<String, Object> result = RLM_PricingPageController.convertTrialToPaid(
            acc.Id, 'Pro', 5, 'annual'
        );
        System.assertEquals(false, result.get('success'),
            'Should fail gracefully when Flow is not deployed');
    }

    @isTest
    static void testGetRealtimePricing() {
        Test.setMock(HttpCalloutMock.class, new RevenueCloudMock());
        Test.startTest();
        Map<String, Object> result = RLM_PricingPageController.getRealtimePricing(
            'Pro', 5, 'annual'
        );
        Test.stopTest();
        System.assertNotEquals(null, result);
    }

    @isTest
    static void testRLM_SearchProductsAction() {
        Test.setMock(HttpCalloutMock.class, new RevenueCloudMock());
        RLM_SearchProductsAction.Request req = new RLM_SearchProductsAction.Request();
        req.keyword = 'Pro';
        Test.startTest();
        List<RLM_SearchProductsAction.Result> results =
            RLM_SearchProductsAction.execute(new List<RLM_SearchProductsAction.Request>{ req });
        Test.stopTest();
        System.assertEquals(1, results.size());
    }

    @isTest
    static void testRLM_CalculatePricingAction() {
        Test.setMock(HttpCalloutMock.class, new RevenueCloudMock());
        RLM_CalculatePricingAction.Request req = new RLM_CalculatePricingAction.Request();
        req.productName = 'Pro';
        req.quantity = 5;
        req.billingFrequency = 'annual';
        Test.startTest();
        List<RLM_CalculatePricingAction.Result> results =
            RLM_CalculatePricingAction.execute(new List<RLM_CalculatePricingAction.Request>{ req });
        Test.stopTest();
        System.assertEquals(1, results.size());
    }

    @isTest
    static void testRLM_PlaceSalesTransactionAction() {
        Test.setMock(HttpCalloutMock.class, new RevenueCloudMock());
        Account acc = new Account(Name = 'Test Corp');
        insert acc;

        RLM_PlaceSalesTransactionAction.Request req = new RLM_PlaceSalesTransactionAction.Request();
        req.accountId = acc.Id;
        req.transactionType = 'Trial';
        req.productName = 'Pro';
        req.quantity = 1;
        Test.startTest();
        List<RLM_PlaceSalesTransactionAction.Result> results =
            RLM_PlaceSalesTransactionAction.execute(new List<RLM_PlaceSalesTransactionAction.Request>{ req });
        Test.stopTest();
        System.assertEquals(1, results.size());
    }

    @isTest
    static void testRLM_NotifySalesRepAction() {
        Account acc = new Account(Name = 'Test Corp');
        insert acc;
        Opportunity opp = new Opportunity(
            Name = 'Test Opp', AccountId = acc.Id,
            StageName = 'Prospecting', CloseDate = Date.today().addDays(30)
        );
        insert opp;

        RLM_NotifySalesRepAction.Request req = new RLM_NotifySalesRepAction.Request();
        req.recordId = opp.Id;
        req.salesRepUserId = UserInfo.getUserId();
        Test.startTest();
        List<RLM_NotifySalesRepAction.Result> results =
            RLM_NotifySalesRepAction.execute(new List<RLM_NotifySalesRepAction.Request>{ req });
        Test.stopTest();
        System.assertEquals(1, results.size());
        System.assertEquals(true, results[0].isSuccess);
    }

    private class RevenueCloudMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            res.setStatusCode(200);
            res.setBody('{"id":"txn123","transactionNumber":"Q-2026-00001","totalAmount":3540}');
            return res;
        }
    }
}