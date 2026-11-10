/**
 * Not covered: the OneTime exclusion. OrderItem.ProductSellingModelId cannot be set by DML, and
 * an order item inserted by an Apex test stays without a selling model even when its price book
 * entry has one (a quote line on the same entry does get it). So every line here counts as a
 * subscription line, and each fixture asserts that as a PRECONDITION.
 *
 * Production gaps are pinned below with "Known gap:" assertions.
 */
@IsTest
private class RLM_OrderItemContractingUtilityTest {

    private static Id accountId() {
        Account acct = new Account(Name = 'RLM Contract Info Account');
        insert acct;
        return acct.Id;
    }

    /** A product priced on the standard price book under a monthly term-defined selling model. */
    private static PricebookEntry termedEntry() {
        Product2 product = new Product2(Name = 'RLM Contract Info Product', IsActive = true);
        insert product;
        ProductSellingModel psm = new ProductSellingModel(
            Name = 'RLM Contract Info Term Monthly',
            SellingModelType = 'TermDefined',
            PricingTermUnit = 'Months',
            PricingTerm = 1,
            Status = 'Active'
        );
        insert psm;
        insert new ProductSellingModelOption(Product2Id = product.Id, ProductSellingModelId = psm.Id, IsDefault = true);
        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = Test.getStandardPricebookId(),
            Product2Id = product.Id,
            ProductSellingModelId = psm.Id,
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
            EndDate = endDate,
            BillingFrequency2 = 'Monthly'
        );
    }

    private static void assertNoSellingModel(Set<Id> orderIds) {
        for (OrderItem oi : [SELECT ProductSellingModelId FROM OrderItem WHERE OrderId IN :orderIds]) {
            Assert.isNull(oi.ProductSellingModelId, 'PRECONDITION: test order items carry no selling model');
        }
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
        PricebookEntry pbe = termedEntry();
        Order o = newOrder(accountId(), Date.newInstance(2026, 1, 1));
        insert o;
        insert new List<OrderItem>{
            newItem(o.Id, pbe, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 6, 30)),
            newItem(o.Id, pbe, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31))
        };
        assertNoSellingModel(new Set<Id>{ o.Id });

        Test.startTest();
        List<RLM_OrderItemContractingUtility.OrderInfoResults> results = run(new List<Id>{ o.Id });
        Test.stopTest();

        Assert.areEqual(1, results.size(), 'One result per order');
        RLM_OrderItemContractingUtility.OrderInfoResults r = results[0];
        Assert.areEqual(Date.newInstance(2026, 12, 31), r.outEndDate, 'The latest end date is used');
        // Jan 1 -> Dec 31 is 11 whole months; the end day (31) is past the start day (1), so it rounds up.
        Assert.areEqual(12, r.outContractTerm, 'A partial final month counts as a month');
        Assert.areEqual(
            1, r.subscriptionItemCount,
            'Known gap: two items, but the LIMIT 1 subquery caps subscriptionItemCount at 1; '
                + 'update this test when it is fixed'
        );
    }

    @IsTest
    static void termRoundsUpOnlyWhenEndDayIsPastStartDay() {
        PricebookEntry pbe = termedEntry();
        Id acctId = accountId();
        Order before = newOrder(acctId, Date.newInstance(2026, 1, 15));
        Order sameDay = newOrder(acctId, Date.newInstance(2026, 1, 15));
        Order after = newOrder(acctId, Date.newInstance(2026, 1, 15));
        insert new List<Order>{ before, sameDay, after };
        insert new List<OrderItem>{
            newItem(before.Id, pbe, Date.newInstance(2026, 1, 15), Date.newInstance(2027, 1, 14)),
            newItem(sameDay.Id, pbe, Date.newInstance(2026, 1, 15), Date.newInstance(2027, 1, 15)),
            newItem(after.Id, pbe, Date.newInstance(2026, 1, 15), Date.newInstance(2027, 1, 20))
        };
        assertNoSellingModel(new Set<Id>{ before.Id, sameDay.Id, after.Id });

        Test.startTest();
        List<RLM_OrderItemContractingUtility.OrderInfoResults> results =
            run(new List<Id>{ before.Id, sameDay.Id, after.Id });
        Test.stopTest();

        Assert.areEqual(3, results.size(), 'One result per order');
        Map<Date, Integer> termByEndDate = new Map<Date, Integer>();
        for (RLM_OrderItemContractingUtility.OrderInfoResults r : results) {
            termByEndDate.put(r.outEndDate, r.outContractTerm);
        }
        Assert.areEqual(
            12, termByEndDate.get(Date.newInstance(2027, 1, 14)), 'End day 14 before start day 15: no round-up'
        );
        Assert.areEqual(
            12, termByEndDate.get(Date.newInstance(2027, 1, 15)), 'End day equal to start day: no round-up'
        );
        Assert.areEqual(
            13, termByEndDate.get(Date.newInstance(2027, 1, 20)), 'End day 20 past start day 15: rounds up'
        );
    }

    @IsTest
    static void orderActionsAreCountedByType() {
        Order o = newOrder(accountId(), Date.newInstance(2026, 1, 1));
        insert o;
        List<OrderAction> actions = new List<OrderAction>();
        for (String actionType : new List<String>{ 'Add', 'Add', 'Amend', 'Renew' }) {
            actions.add(new OrderAction(OrderId = o.Id, Type = actionType));
        }
        insert actions;

        Test.startTest();
        List<RLM_OrderItemContractingUtility.OrderInfoResults> results = run(new List<Id>{ o.Id });
        Test.stopTest();

        Assert.areEqual(1, results.size(), 'One result per order');
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
        Integer queriesUsed;
        Test.startTest();
        System.runAs(noAccess) {
            Assert.isFalse(
                Schema.SObjectType.Order.fields.EffectiveDate.isAccessible(),
                'PRECONDITION: the user cannot read Order.EffectiveDate'
            );
            Integer queriesBefore = Limits.getQueries();
            results = run(new List<Id>{ o.Id });
            queriesUsed = Limits.getQueries() - queriesBefore;
        }
        Test.stopTest();

        // No query ran, so the empty result comes from the field-access check, not record sharing.
        Assert.areEqual(0, queriesUsed, 'The field-access check returns before any query');
        Assert.isTrue(results.isEmpty(), 'Without access to the order fields the utility returns no result');
    }

    /** A Minimum Access user: no object access to Order, OrderItem or OrderAction. */
    private static User minimumAccessUser() {
        List<Profile> profiles = [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
        Assert.isFalse(profiles.isEmpty(), 'PRECONDITION: the standard Minimum Access - Salesforce profile exists');
        Profile minimal = profiles[0];
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
