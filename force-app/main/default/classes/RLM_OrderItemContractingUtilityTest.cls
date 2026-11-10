/**
 * Order items inserted by an Apex test carry no product selling model (the platform does not
 * derive it from the price book entry in a test context), so the lines here have none. The
 * utility only excludes OneTime items, so these lines count as subscription lines.
 */
@IsTest
private class RLM_OrderItemContractingUtilityTest {

    private static Id accountId() {
        Account acct = new Account(Name = 'RLM Contract Info Account');
        insert acct;
        return acct.Id;
    }

    private static PricebookEntry standardEntry() {
        Product2 product = new Product2(Name = 'RLM Contract Info Product', IsActive = true);
        insert product;
        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = Test.getStandardPricebookId(),
            Product2Id = product.Id,
            UnitPrice = 100,
            IsActive = true
        );
        insert pbe;
        return pbe;
    }

    private static Order newOrder(Id acctId, Date effectiveDate) {
        return new Order(
            AccountId = acctId,
            Status = 'Draft',
            EffectiveDate = effectiveDate,
            Pricebook2Id = Test.getStandardPricebookId()
        );
    }

    private static OrderItem newItem(Id orderId, PricebookEntry pbe, Date serviceDate, Date endDate) {
        return new OrderItem(
            OrderId = orderId,
            PricebookEntryId = pbe.Id,
            Product2Id = pbe.Product2Id,
            Quantity = 1,
            UnitPrice = 100,
            ServiceDate = serviceDate,
            EndDate = endDate
        );
    }

    private static List<RLM_OrderItemContractingUtility.OrderInfoResults> run(List<Id> orderIds) {
        return RLM_OrderItemContractingUtility.calculateOrderInfoForContract(orderIds);
    }

    @IsTest
    static void emptyInputReturnsNoResults() {
        Assert.isTrue(run(new List<Id>()).isEmpty(), 'No order ids yields no results');
    }

    @IsTest
    static void latestEndDateDrivesContractTerm() {
        PricebookEntry pbe = standardEntry();
        Order o = newOrder(accountId(), Date.newInstance(2026, 1, 1));
        insert o;
        insert new List<OrderItem>{
            newItem(o.Id, pbe, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 6, 30)),
            newItem(o.Id, pbe, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31)),
            newItem(o.Id, pbe, Date.newInstance(2026, 1, 1), null)
        };
        for (OrderItem oi : [SELECT ProductSellingModelId FROM OrderItem WHERE OrderId = :o.Id]) {
            Assert.isNull(oi.ProductSellingModelId, 'PRECONDITION: test order items carry no selling model');
        }

        Test.startTest();
        List<RLM_OrderItemContractingUtility.OrderInfoResults> results = run(new List<Id>{ o.Id });
        Test.stopTest();

        Assert.areEqual(1, results.size(), 'One result per order');
        RLM_OrderItemContractingUtility.OrderInfoResults r = results[0];
        Assert.areEqual(Date.newInstance(2026, 12, 31), r.outEndDate, 'The latest end date is used; open-ended items are skipped');
        // Jan 1 -> Dec 31 is 11 whole months; the end day (31) is past the start day (1), so it rounds up.
        Assert.areEqual(12, r.outContractTerm, 'A partial final month counts as a month');
        Assert.areEqual(1, r.subscriptionItemCount, 'The latest item was found');
    }

    @IsTest
    static void termRoundsUpOnlyWhenEndDayIsPastStartDay() {
        PricebookEntry pbe = standardEntry();
        Id acctId = accountId();
        Order exact = newOrder(acctId, Date.newInstance(2026, 1, 15));
        Order over = newOrder(acctId, Date.newInstance(2026, 1, 15));
        insert new List<Order>{ exact, over };
        insert new List<OrderItem>{
            newItem(exact.Id, pbe, Date.newInstance(2026, 1, 15), Date.newInstance(2027, 1, 14)),
            newItem(over.Id, pbe, Date.newInstance(2026, 1, 15), Date.newInstance(2027, 1, 20))
        };

        Test.startTest();
        List<RLM_OrderItemContractingUtility.OrderInfoResults> results = run(new List<Id>{ exact.Id, over.Id });
        Test.stopTest();

        Assert.areEqual(2, results.size(), 'One result per order');
        Map<Date, Integer> termByEndDate = new Map<Date, Integer>();
        for (RLM_OrderItemContractingUtility.OrderInfoResults r : results) {
            termByEndDate.put(r.outEndDate, r.outContractTerm);
        }
        Assert.areEqual(12, termByEndDate.get(Date.newInstance(2027, 1, 14)), 'End day 14 before start day 15: no round-up');
        Assert.areEqual(13, termByEndDate.get(Date.newInstance(2027, 1, 20)), 'End day 20 past start day 15: rounds up');
    }

    @IsTest
    static void orderActionsAreCountedByType() {
        Order o = newOrder(accountId(), Date.newInstance(2026, 1, 1));
        insert o;
        List<OrderAction> actions = new List<OrderAction>();
        for (String actionType : new List<String>{ 'Add', 'Add', 'Amend', 'Renew' }) {
            OrderAction action = new OrderAction();
            action.put('OrderId', o.Id);
            action.put('Type', actionType);
            actions.add(action);
        }
        insert actions;

        Test.startTest();
        List<RLM_OrderItemContractingUtility.OrderInfoResults> results = run(new List<Id>{ o.Id });
        Test.stopTest();

        RLM_OrderItemContractingUtility.OrderInfoResults r = results[0];
        Assert.areEqual(2, r.addOrderActionCount, 'Two Add actions');
        Assert.areEqual(1, r.amendOrderActionCount, 'One Amend action');
        Assert.areEqual(1, r.renewOrderActionCount, 'One Renew action');
        Assert.isNull(r.outEndDate, 'No items means no end date');
        Assert.areEqual(1, r.outContractTerm, 'No items means the default term');
        Assert.areEqual(0, r.subscriptionItemCount, 'No items means no subscription items');
    }

    @IsTest
    static void bulkOrdersEachGetAResult() {
        Id acctId = accountId();
        List<Order> orders = new List<Order>();
        for (Integer i = 0; i < 200; i++) {
            orders.add(newOrder(acctId, Date.newInstance(2026, 1, 1)));
        }
        insert orders;
        List<Id> orderIds = new List<Id>(new Map<Id, Order>(orders).keySet());

        Test.startTest();
        Integer queriesBefore = Limits.getQueries();
        List<RLM_OrderItemContractingUtility.OrderInfoResults> results = run(orderIds);
        Integer queriesUsed = Limits.getQueries() - queriesBefore;
        Test.stopTest();

        Assert.areEqual(1, queriesUsed, 'All orders are read in one query');
        Assert.areEqual(200, results.size(), 'Every order gets a result');
        for (RLM_OrderItemContractingUtility.OrderInfoResults r : results) {
            Assert.areEqual(1, r.outContractTerm, 'Orders without items default to a one-month term');
            Assert.areEqual(0, r.addOrderActionCount, 'No actions counted');
            Assert.areEqual(0, r.amendOrderActionCount, 'No actions counted');
            Assert.areEqual(0, r.renewOrderActionCount, 'No actions counted');
        }
    }

    @IsTest
    static void userWithoutOrderAccessGetsNoResults() {
        Order o = newOrder(accountId(), Date.newInstance(2026, 1, 1));
        insert o;
        Assert.areEqual(1, run(new List<Id>{ o.Id }).size(), 'PRECONDITION: an admin gets a result for this order');
        User noAccess = minimumAccessUser();

        List<RLM_OrderItemContractingUtility.OrderInfoResults> results;
        Test.startTest();
        System.runAs(noAccess) {
            results = run(new List<Id>{ o.Id });
        }
        Test.stopTest();

        Assert.isTrue(results.isEmpty(), 'Without read access to the order fields nothing is computed');
    }

    /** A Minimum Access user: no object access to Order, OrderItem or OrderAction. */
    private static User minimumAccessUser() {
        Profile minimal = [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
        String stamp = String.valueOf(Crypto.getRandomInteger()).remove('-');
        User u = new User(
            ProfileId = minimal.Id,
            LastName = 'ContractInfo',
            Email = 'rlm.contractinfo@example.com',
            Username = 'rlm.contractinfo.' + stamp + '@example.com',
            Alias = 'rlmci',
            TimeZoneSidKey = 'America/Los_Angeles',
            LocaleSidKey = 'en_US',
            EmailEncodingKey = 'UTF-8',
            LanguageLocaleKey = 'en_US'
        );
        // Setup-object DML after the orders above needs its own runAs context (mixed DML).
        System.runAs(new User(Id = UserInfo.getUserId())) {
            insert u;
        }
        return u;
    }
}
