/**
 * Not covered: the OneTime exclusion. OrderItem.ProductSellingModelId is not createable, and on a
 * live 264 org an order item inserted by an Apex test stayed without a selling model even when its
 * price book entry had one (a quote line on the same entry did get it). So the fixtures use plain
 * price book entries, and every line here counts as a subscription line.
 *
 * Results are one per input, in input order, and carry the order id they belong to.
 */
@IsTest
private class RLM_OrderItemContractingUtilityTest {

    private static Id accountId() {
        Account acct = new Account(Name = 'RLM Contract Info Account');
        insert acct;
        return acct.Id;
    }

    /** A product on the standard price book, with no selling model. */
    private static PricebookEntry standardEntry() {
        Product2 product = new Product2(Name = 'RLM Contract Info Product', IsActive = true);
        insert product;
        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = Test.getStandardPricebookId(), Product2Id = product.Id, UnitPrice = 100, IsActive = true
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
            newItem(o.Id, pbe, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31))
        };

        Test.startTest();
        List<RLM_OrderItemContractingUtility.OrderInfoResults> results = run(new List<Id>{ o.Id });
        Test.stopTest();

        Assert.areEqual(1, results.size(), 'One result per order');
        RLM_OrderItemContractingUtility.OrderInfoResults r = results[0];
        Assert.areEqual(Date.newInstance(2026, 12, 31), r.outEndDate, 'The latest end date is used');
        // Jan 1 -> Dec 31 is 11 whole months; the end day (31) is past the start day (1), so it rounds up.
        Assert.areEqual(12, r.outContractTerm, 'A partial final month counts as a month');
        Assert.areEqual(2, r.subscriptionItemCount, 'Every subscription item is counted');
        Assert.areEqual(o.Id, r.orderId, 'The result names its order');
    }

    @IsTest
    static void orderWithMoreThanTwoHundredItemsIsCountedWithoutAnAggregateError() {
        PricebookEntry pbe = standardEntry();
        Order o = newOrder(accountId(), Date.newInstance(2026, 1, 1));
        insert o;
        List<OrderItem> items = new List<OrderItem>();
        for (Integer i = 0; i < 201; i++) {
            items.add(newItem(o.Id, pbe, Date.newInstance(2026, 1, 1), Date.newInstance(2026, 12, 31)));
        }
        insert items;

        List<RLM_OrderItemContractingUtility.OrderInfoResults> results = run(new List<Id>{ o.Id });

        Assert.areEqual(1, results.size(), 'One result per order');
        Assert.isNull(results[0].errorMessage, 'No error');
        Assert.areEqual(201, results[0].subscriptionItemCount, 'Every subscription item is counted');
        Assert.areEqual(Date.newInstance(2026, 12, 31), results[0].outEndDate, 'The latest end date is used');
    }

    @IsTest
    static void termRoundsUpOnlyWhenEndDayIsPastStartDay() {
        PricebookEntry pbe = standardEntry();
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

        Test.startTest();
        List<RLM_OrderItemContractingUtility.OrderInfoResults> results =
            run(new List<Id>{ before.Id, sameDay.Id, after.Id });
        Test.stopTest();

        Assert.areEqual(3, results.size(), 'One result per order');
        Assert.areEqual(before.Id, results[0].orderId, 'Results follow input order (first)');
        Assert.areEqual(sameDay.Id, results[1].orderId, 'Results follow input order (second)');
        Assert.areEqual(after.Id, results[2].orderId, 'Results follow input order (third)');
        Assert.areEqual(12, results[0].outContractTerm, 'End day 14 before start day 15: no round-up');
        Assert.areEqual(12, results[1].outContractTerm, 'End day equal to start day: no round-up');
        Assert.areEqual(13, results[2].outContractTerm, 'End day 20 past start day 15: rounds up');
    }

    @IsTest
    static void duplicateOrderIdsEachGetAResult() {
        Order o = newOrder(accountId(), Date.newInstance(2026, 1, 1));
        insert o;

        List<RLM_OrderItemContractingUtility.OrderInfoResults> results = run(new List<Id>{ o.Id, o.Id });

        Assert.areEqual(2, results.size(), 'Two inputs get two outputs, or a calling flow faults');
        Assert.areEqual(o.Id, results[0].orderId, 'The first output names the order');
        Assert.areEqual(o.Id, results[1].orderId, 'The second output names the order');
    }

    @IsTest
    static void unknownOrderGetsAnErrorResultInPlace() {
        Order o = newOrder(accountId(), Date.newInstance(2026, 1, 1));
        insert o;
        Id missing = Order.SObjectType.getDescribe().getKeyPrefix() + '000000000001';

        List<RLM_OrderItemContractingUtility.OrderInfoResults> results = run(new List<Id>{ missing, o.Id });

        Assert.areEqual(2, results.size(), 'One result per input');
        Assert.areEqual(missing, results[0].orderId, 'The unknown order keeps its place');
        Assert.isNotNull(results[0].errorMessage, 'The unknown order says why it has no data');
        Assert.isNull(results[0].subscriptionItemCount, 'An unreadable order has no count, so a flow cannot read it as zero');
        Assert.areEqual(o.Id, results[1].orderId, 'The next order is unaffected');
        Assert.isNull(results[1].errorMessage, 'A readable order carries no error');
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

        Assert.areEqual(2, queriesUsed, 'All orders are read in two queries: orders, and item counts');
        Assert.areEqual(200, results.size(), 'Every order gets a result');
        for (Integer i = 0; i < results.size(); i++) {
            RLM_OrderItemContractingUtility.OrderInfoResults r = results[i];
            Assert.areEqual(orderIds[i], r.orderId, 'Results follow input order');
            Assert.areEqual(1, r.outContractTerm, 'Orders without items default to a one-month term');
            Assert.areEqual(0, r.addOrderActionCount, 'No Add actions counted');
            Assert.areEqual(0, r.amendOrderActionCount, 'No Amend actions counted');
            Assert.areEqual(0, r.renewOrderActionCount, 'No Renew actions counted');
        }
    }

    @IsTest
    static void userWithoutOrderFieldAccessGetsAnErrorResult() {
        Order o = newOrder(accountId(), Date.newInstance(2026, 1, 1));
        insert o;
        Assert.areEqual(
            1, run(new List<Id>{ o.Id }).size(), 'PRECONDITION: the running user gets a result for this order'
        );
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

        // No query ran, so the error result comes from the field-access check, not from a refused query.
        Assert.areEqual(0, queriesUsed, 'The field-access check returns before any query');
        Assert.areEqual(1, results.size(), 'The input still gets an output');
        Assert.areEqual(o.Id, results[0].orderId, 'The output names its order');
        Assert.isNotNull(results[0].errorMessage, 'The output says why it has no data');
        Assert.isNull(results[0].subscriptionItemCount, 'An unreadable order has no count, so a flow cannot read it as zero');
    }

    /**
     * Reaches the user-mode query fallback: the user can read the Order, OrderItem and OrderAction fields the
     * pre-check names, but not ProductSellingModel, which only the query itself reads. The assertions prove the
     * fallback ran; they do not identify which refused part of the query raised the QueryException.
     */
    @IsTest
    static void userWhoCannotReadTheSellingModelGetsAnErrorResultFromTheQuery() {
        Order o = newOrder(accountId(), Date.newInstance(2026, 1, 1));
        insert o;
        User limited = minimumAccessUser();
        PermissionSet readOrders = new PermissionSet(Name = 'RLM_Test_Read_Orders_Only', Label = 'RLM test read orders only');
        System.runAs(new User(Id = UserInfo.getUserId())) {
            insert readOrders;
            // Measured on a 264 org with Minimum Access users: ObjectPermissions.SobjectType is a restricted
            // picklist that lists Order but neither OrderItem nor OrderAction, so OrderItem access can only
            // come from its parents. Order Read alone leaves OrderItem unreadable; Order Read plus Product2
            // Read plus Pricebook2 Read makes it readable, and neither of the two extra reads works alone.
            // OrderAction is readable with Order Read. A field grant on an OrderItem field has no effect
            // until the object is readable, and OrderItem.ServiceDate and EndDate then need their own field
            // grants (OrderItem.Quantity does not). ProductSellingModel stays unreadable throughout.
            // The preconditions below assert the outcome, so a change in platform behaviour fails the test
            // instead of passing it.
            insert new List<ObjectPermissions>{
                new ObjectPermissions(ParentId = readOrders.Id, SobjectType = 'Order', PermissionsRead = true),
                new ObjectPermissions(ParentId = readOrders.Id, SobjectType = 'Product2', PermissionsRead = true),
                new ObjectPermissions(ParentId = readOrders.Id, SobjectType = 'Pricebook2', PermissionsRead = true)
            };
            insert new List<FieldPermissions>{
                new FieldPermissions(ParentId = readOrders.Id, SobjectType = 'OrderItem', Field = 'OrderItem.ServiceDate', PermissionsRead = true),
                new FieldPermissions(ParentId = readOrders.Id, SobjectType = 'OrderItem', Field = 'OrderItem.EndDate', PermissionsRead = true)
            };
            insert new PermissionSetAssignment(AssigneeId = limited.Id, PermissionSetId = readOrders.Id);
        }

        List<RLM_OrderItemContractingUtility.OrderInfoResults> results;
        Test.startTest();
        System.runAs(limited) {
            Assert.isTrue(
                Schema.SObjectType.Order.fields.EffectiveDate.isAccessible()
                    && Schema.SObjectType.OrderItem.fields.ServiceDate.isAccessible()
                    && Schema.SObjectType.OrderItem.fields.EndDate.isAccessible()
                    && Schema.SObjectType.OrderAction.fields.Type.isAccessible(),
                'PRECONDITION: the user passes the field-access pre-check'
            );
            Assert.isFalse(
                Schema.SObjectType.ProductSellingModel.fields.SellingModelType.isAccessible(),
                'PRECONDITION: the user cannot read ProductSellingModel.SellingModelType'
            );
            results = run(new List<Id>{ o.Id });
        }
        Test.stopTest();

        Assert.areEqual(1, results.size(), 'The input still gets an output');
        Assert.areEqual(o.Id, results[0].orderId, 'The output names its order');
        Assert.isNotNull(results[0].errorMessage, 'The output says why it has no data');
        Assert.areEqual(
            'The order could not be read as the running user.', results[0].errorMessage,
            'The message is the fixed query-fallback sentence (not the pre-check, no query text)'
        );
        Assert.isNull(results[0].subscriptionItemCount, 'An unreadable order has no count, so a flow cannot read it as zero');
    }

    /**
     * A Minimum Access user: no object access to Order, OrderItem or OrderAction. The test fails, never
     * skips, when the precondition cannot be built: standard profile names can be translated, so this
     * needs the English profile name "Minimum Access - Salesforce" and a free seat for the user insert.
     */
    private static User minimumAccessUser() {
        List<Profile> profiles = [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
        Assert.areEqual(
            1, profiles.size(),
            'PRECONDITION: this test needs the English standard profile "Minimum Access - Salesforce"'
        );
        String stamp = String.valueOf(Crypto.getRandomInteger()).remove('-');
        User u = new User(
            ProfileId = profiles[0].Id,
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
