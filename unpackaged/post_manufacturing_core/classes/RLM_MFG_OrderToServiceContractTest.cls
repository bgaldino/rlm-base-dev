@isTest
private class RLM_MFG_OrderToServiceContractTest {

    // Builds an order + quote with `parentCount` covered-asset service-contract parent
    // lines. Child/bundle quote lines are not created here because
    // QuoteLineItem.ParentQuoteLineItemId is not writeable from Apex — the maintenance
    // expansion logic is covered directly via copiesForChild() instead.
    private static Id buildScenario(Integer parentCount) {
        Account acct = new Account(
            Name = 'Test Account',
            BillingStreet = '1 Market St', BillingCity = 'San Francisco',
            BillingState = 'CA', BillingPostalCode = '94105', BillingCountry = 'US',
            ShippingStreet = '1 Market St', ShippingCity = 'San Francisco',
            ShippingState = 'CA', ShippingPostalCode = '94105', ShippingCountry = 'US'
        );
        insert acct;

        Contact con = new Contact(LastName = 'Tester', AccountId = acct.Id);
        insert con;

        Id stdPbId = Test.getStandardPricebookId();

        Product2 scProd = new Product2(Name = 'Generator Service Contract', IsActive = true);
        insert scProd;

        PricebookEntry scPbe = new PricebookEntry(
            Pricebook2Id = stdPbId, Product2Id = scProd.Id, UnitPrice = 100, IsActive = true);
        insert scPbe;

        Opportunity opp = new Opportunity(
            Name = 'Test Opp', StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30), AccountId = acct.Id, Pricebook2Id = stdPbId);
        insert opp;

        Quote qt = new Quote(
            Name = 'Test Quote', OpportunityId = opp.Id, Pricebook2Id = stdPbId, ContactId = con.Id);
        insert qt;

        Order ord = new Order(
            AccountId = acct.Id, QuoteId = qt.Id, Pricebook2Id = stdPbId,
            EffectiveDate = Date.today(), Status = 'Draft');
        insert ord;

        if (parentCount > 0) {
            List<Asset> assets = new List<Asset>();
            for (Integer i = 0; i < parentCount; i++) {
                assets.add(new Asset(Name = 'Asset ' + i, AccountId = acct.Id, Product2Id = scProd.Id));
            }
            insert assets;

            List<QuoteLineItem> parents = new List<QuoteLineItem>();
            for (Integer i = 0; i < parentCount; i++) {
                parents.add(new QuoteLineItem(
                    QuoteId = qt.Id, Product2Id = scProd.Id, PricebookEntryId = scPbe.Id,
                    Quantity = 1, UnitPrice = 100,
                    StartDate = Date.today(), EndDate = Date.today().addYears(1),
                    RLM_MFG_Covered_Asset__c = assets[i].Id));
            }
            insert parents;
        }

        return ord.Id;
    }

    private static RLM_MFG_OrderToServiceContract.Request makeRequest(Id orderId) {
        RLM_MFG_OrderToServiceContract.Request req = new RLM_MFG_OrderToServiceContract.Request();
        req.orderId = orderId;
        return req;
    }

    // Fabricates a QuoteLineItem with the read-only formula field populated.
    private static QuoteLineItem fakeChild(String productName, Decimal qty) {
        Map<String, Object> m = new Map<String, Object>{
            'RLM_MFG_Product_Name_formula__c' => productName,
            'Quantity' => qty
        };
        return (QuoteLineItem) JSON.deserialize(JSON.serialize(m), QuoteLineItem.class);
    }

    @isTest
    static void singleParentLine_createsContractAndLine() {
        Id orderId = buildScenario(1);

        Test.startTest();
        List<RLM_MFG_OrderToServiceContract.Result> results =
            RLM_MFG_OrderToServiceContract.createServiceContracts(
                new List<RLM_MFG_OrderToServiceContract.Request>{ makeRequest(orderId) });
        Test.stopTest();

        System.assertEquals(1, results.size(), 'One result expected');
        System.assertEquals(1, results[0].serviceContractIds.size(), 'One service contract expected');
        System.assertEquals(1, [SELECT COUNT() FROM ServiceContract], 'One service contract');
        System.assertEquals(1, [SELECT COUNT() FROM ContractLineItem], 'One contract line item');
    }

    @isTest
    static void multipleParentLines_createOneContractEach() {
        Id orderId = buildScenario(2);

        Test.startTest();
        List<RLM_MFG_OrderToServiceContract.Result> results =
            RLM_MFG_OrderToServiceContract.createServiceContracts(
                new List<RLM_MFG_OrderToServiceContract.Request>{ makeRequest(orderId) });
        Test.stopTest();

        System.assertEquals(2, results[0].serviceContractIds.size(), 'Two service contracts expected');
        System.assertEquals(2, [SELECT COUNT() FROM ServiceContract], 'Two service contracts');
        System.assertEquals(2, [SELECT COUNT() FROM ContractLineItem], 'Two contract line items');
    }

    @isTest
    static void noServiceContractLines_throws() {
        Id orderId = buildScenario(0);

        Test.startTest();
        Boolean threw = false;
        try {
            RLM_MFG_OrderToServiceContract.createServiceContracts(
                new List<RLM_MFG_OrderToServiceContract.Request>{ makeRequest(orderId) });
        } catch (RLM_MFG_OrderToServiceContract.RLM_MFG_OrderToServiceContractException e) {
            threw = true;
        }
        Test.stopTest();

        System.assert(threw, 'Expected exception when no service contract quote lines exist');
    }

    @isTest
    static void nullRequest_throws() {
        Test.startTest();
        Boolean threw = false;
        try {
            RLM_MFG_OrderToServiceContract.createServiceContracts(null);
        } catch (RLM_MFG_OrderToServiceContract.RLM_MFG_OrderToServiceContractException e) {
            threw = true;
        }
        Test.stopTest();

        System.assert(threw, 'Expected exception for null request');
    }

    @isTest
    static void maintenanceLine_expandsByQuantity() {
        System.assertEquals(3, RLM_MFG_OrderToServiceContract.copiesForChild(
            fakeChild('Annual Maintenance Visit', 3)), 'Maintenance line expands to qty');
        System.assertEquals(1, RLM_MFG_OrderToServiceContract.copiesForChild(
            fakeChild('Maintenance Visit', null)), 'Null qty maintenance defaults to 1');
        System.assertEquals(1, RLM_MFG_OrderToServiceContract.copiesForChild(
            fakeChild('Inspection Report', 5)), 'Non-maintenance line yields exactly one');
    }
}
