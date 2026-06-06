@isTest
private class RLM_PreProcessOrderControllerTest {

    @isTest
    static void testIsValidationComplete() {
        System.assertEquals(true, RLM_PreProcessOrderController.isValidationComplete('CNNN'), 'C in bit 0 = complete');
        System.assertEquals(true, RLM_PreProcessOrderController.isValidationComplete('CCCC'), 'all complete');
        System.assertEquals(true, RLM_PreProcessOrderController.isValidationComplete('c'), 'case-insensitive');
        System.assertEquals(false, RLM_PreProcessOrderController.isValidationComplete('NNNN'), 'N in bit 0 = not complete');
        System.assertEquals(false, RLM_PreProcessOrderController.isValidationComplete('QNNN'), 'Q in bit 0 = queued');
        System.assertEquals(false, RLM_PreProcessOrderController.isValidationComplete(null), 'null = not complete');
        System.assertEquals(false, RLM_PreProcessOrderController.isValidationComplete(''), 'blank = not complete');
    }

    @isTest
    static void testStartPreprocess_BlankId() {
        String resp = RLM_PreProcessOrderController.startPreprocess('');
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertEquals(false, m.get('success'), 'Blank id should fail gracefully');
    }

    @isTest
    static void testStartPreprocess_HandlesActionContext() {
        // The standard action is not invocable in test context; the method must
        // still return a structured (non-throwing) result.
        String resp = RLM_PreProcessOrderController.startPreprocess('801000000000000AAA');
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertNotEquals(null, m.get('success'), 'Returns a structured result');
    }

    @isTest
    static void testActivateOrder_BlankId() {
        String resp = RLM_PreProcessOrderController.activateOrder('');
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertEquals(false, m.get('success'), 'Blank id should fail gracefully');
    }

    @isTest
    static void testActivateOrder_InvalidId() {
        String resp = RLM_PreProcessOrderController.activateOrder('801000000000000AAA');
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertEquals(false, m.get('success'), 'Bad id surfaces a structured error');
        System.assertNotEquals(null, m.get('errorMessage'), 'Error message present');
    }

    @isTest
    static void testGetOrderInfo_InvalidId() {
        String resp = RLM_PreProcessOrderController.getOrderInfo('801000000000000AAA');
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertEquals(false, m.get('success'), 'No matching order returns structured error');
    }

    @isTest
    static void testGetStatus_InvalidId() {
        String resp = RLM_PreProcessOrderController.getStatus('801000000000000AAA', null);
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertEquals(false, m.get('success'), 'No matching order returns structured error');
    }

    @isTest
    static void testGetOrderInfo_RealOrder() {
        Order o = buildLargeDealOrder();
        Test.startTest();
        String resp = RLM_PreProcessOrderController.getOrderInfo(o.Id);
        Test.stopTest();
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertEquals(true, m.get('success'), 'Real order info resolves');
        System.assertEquals(true, m.get('isLargeDeal'), 'IsLargeDeal flag surfaced');
    }

    @isTest
    static void testResolveExcludeTreatment_AbsentReturnsNull() {
        // Fresh test org with no seed treatment → resolver returns null and
        // stamping self-skips (preprocess proceeds unchanged).
        System.assertEquals(
            null,
            RLM_PreProcessOrderController.resolveLargeDealExcludeTreatmentId(),
            'Absent seed treatment resolves to null'
        );
    }

    @isTest
    static void testStamp_NoTreatment_NoOp() {
        Order o = buildOrderWithItem(true);
        Test.startTest();
        RLM_PreProcessOrderController.stampLargeDealExcludeTreatment(o.Id);
        Test.stopTest();
        // No seed treatment → nothing stamped, no error.
        for (OrderItem oi : [SELECT BillingTreatmentId FROM OrderItem WHERE OrderId = :o.Id]) {
            System.assertEquals(null, oi.BillingTreatmentId, 'No treatment to stamp when seed absent');
        }
    }

    @isTest
    static void testStamp_LargeDeal_StampsItems() {
        Id treatmentId = seedExcludeTreatment();
        Order o = buildOrderWithItem(true);
        Test.startTest();
        RLM_PreProcessOrderController.stampLargeDealExcludeTreatment(o.Id);
        Test.stopTest();
        List<OrderItem> ois = [SELECT BillingTreatmentId FROM OrderItem WHERE OrderId = :o.Id];
        System.assertNotEquals(0, ois.size(), 'Order has items');
        for (OrderItem oi : ois) {
            System.assertEquals(treatmentId, oi.BillingTreatmentId, 'Large-deal OI stamped with exclude treatment');
        }
    }

    @isTest
    static void testStamp_LargeDeal_BulkItems() {
        // Exercise the list-DML path with many items so the bulk stamp is covered
        // at more than one record (the stamp uses a single `update`, so it is
        // bulk-safe; this guards against a regression to per-record DML).
        Id treatmentId = seedExcludeTreatment();
        Order o = buildOrderWithItems(true, 50);
        Test.startTest();
        RLM_PreProcessOrderController.stampLargeDealExcludeTreatment(o.Id);
        Test.stopTest();
        List<OrderItem> ois = [SELECT BillingTreatmentId FROM OrderItem WHERE OrderId = :o.Id];
        System.assertEquals(50, ois.size(), 'All 50 items present');
        for (OrderItem oi : ois) {
            System.assertEquals(treatmentId, oi.BillingTreatmentId, 'Every large-deal OI stamped');
        }
    }

    @isTest
    static void testStamp_StandardOrder_NoOp() {
        seedExcludeTreatment();
        Order o = buildOrderWithItem(false);
        Test.startTest();
        RLM_PreProcessOrderController.stampLargeDealExcludeTreatment(o.Id);
        Test.stopTest();
        for (OrderItem oi : [SELECT BillingTreatmentId FROM OrderItem WHERE OrderId = :o.Id]) {
            System.assertEquals(null, oi.BillingTreatmentId, 'Standard order is never stamped');
        }
    }

    @isTest
    static void testReprice_StandardOrder_NoOp() {
        // Standard orders gate out before the Place Sales Transaction executor runs
        // (the managed executor isn't invocable in test context). Assert the no-op
        // path leaves the order unchanged rather than asserting a tautology.
        Order o = buildOrderWithItem(false);
        Test.startTest();
        RLM_PreProcessOrderController.repriceLargeDealOrderIfNeeded(o.Id);
        Test.stopTest();
        Order after = [SELECT Id, IsLargeDeal, Status FROM Order WHERE Id = :o.Id];
        System.assertEquals(false, after.IsLargeDeal, 'Standard order remains non-large-deal');
        System.assertEquals('Draft', after.Status, 'Standard order status unchanged by no-op reprice');
    }

    @isTest
    static void testReprice_InvalidId_NoOp() {
        // No matching order → returns before touching the executor (must not throw).
        Boolean threw = false;
        Test.startTest();
        try {
            RLM_PreProcessOrderController.repriceLargeDealOrderIfNeeded(Id.valueOf('801000000000000AAA'));
        } catch (Exception e) {
            threw = true;
        }
        Test.stopTest();
        System.assertEquals(false, threw, 'Unknown order id reprice is a safe no-op (does not throw)');
    }

    /** Minimal large-deal order. Lets setup failures surface as a test failure
     *  (rather than a silent skip) so missing prerequisites are visible. */
    private static Order buildLargeDealOrder() {
        Account a = new Account(Name = 'PreProc Test Account');
        insert a;
        Order o = new Order(
            AccountId = a.Id,
            Status = 'Draft',
            EffectiveDate = Date.today(),
            IsLargeDeal = true
        );
        insert o;
        return o;
    }

    /** Order with `itemCount` order items; isLargeDeal toggles the gating flag. */
    private static Order buildOrderWithItems(Boolean isLargeDeal, Integer itemCount) {
        Account a = new Account(Name = 'PreProc Item Acct');
        insert a;
        Id pbId = Test.getStandardPricebookId();
        List<Product2> prods = new List<Product2>();
        for (Integer i = 0; i < itemCount; i++) {
            prods.add(new Product2(Name = 'PreProc Prod ' + i, IsActive = true));
        }
        insert prods;
        List<PricebookEntry> pbes = new List<PricebookEntry>();
        for (Product2 pr : prods) {
            pbes.add(new PricebookEntry(
                Pricebook2Id = pbId, Product2Id = pr.Id, UnitPrice = 10, IsActive = true
            ));
        }
        insert pbes;
        Order o = new Order(
            AccountId = a.Id,
            Status = 'Draft',
            EffectiveDate = Date.today(),
            IsLargeDeal = isLargeDeal,
            Pricebook2Id = pbId
        );
        insert o;
        List<OrderItem> items = new List<OrderItem>();
        for (PricebookEntry pbe : pbes) {
            items.add(new OrderItem(
                OrderId = o.Id, PricebookEntryId = pbe.Id, Product2Id = pbe.Product2Id,
                Quantity = 1, UnitPrice = 10
            ));
        }
        insert items;
        return o;
    }

    private static Order buildOrderWithItem(Boolean isLargeDeal) {
        return buildOrderWithItems(isLargeDeal, 1);
    }

    /** Seeds the Active Exclude-from-Billing treatment; returns its id. */
    private static Id seedExcludeTreatment() {
        BillingPolicy p = new BillingPolicy(
            Name = 'RLM Large Deal Policy', Status = 'Draft', BillingTreatmentSelection = 'Default'
        );
        insert p;
        BillingTreatment t = new BillingTreatment(
            Name = 'RLM Large Deal - Exclude from Billing',
            Status = 'Draft',
            BillingPolicyId = p.Id,
            ExcludeFromBilling = 'Yes',
            IsMilestoneBilling = false
        );
        insert t;
        t.Status = 'Active';
        update t;
        return t.Id;
    }
}
