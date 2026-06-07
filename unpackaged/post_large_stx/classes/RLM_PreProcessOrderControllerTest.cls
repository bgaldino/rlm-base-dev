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
    static void testStartPreprocess_UnknownId_ReturnsError() {
        // An unknown / inaccessible order must fail fast (consistent with getOrderInfo /
        // getPricingStatus / enqueuePreprocess) rather than reporting a misleading
        // ready_to_enqueue success the UI would act on.
        String resp = RLM_PreProcessOrderController.startPreprocess('801000000000000AAA');
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertEquals(false, m.get('success'), 'Unknown order id should not succeed');
        System.assertNotEquals(null, m.get('errorMessage'), 'An error message is returned for a missing order');
    }

    @isTest
    static void testStartPreprocess_StandardOrder_ReadyToEnqueue() {
        Order o = buildOrderWithItem(false);
        Test.startTest();
        String resp = RLM_PreProcessOrderController.startPreprocess(o.Id);
        Test.stopTest();
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertEquals(true, m.get('success'), 'Standard order phase 1 succeeds (reprice/stamp no-op)');
        System.assertEquals('ready_to_enqueue', m.get('phase'), 'Standard order is ready to enqueue');
        System.assertEquals(false, m.get('isLargeDeal'), 'Standard order flagged not-large');
    }

    @isTest
    static void testGetPricingStatus_BlankId() {
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(
            RLM_PreProcessOrderController.getPricingStatus('')
        );
        System.assertEquals(false, m.get('success'), 'Blank id fails gracefully');
    }

    @isTest
    static void testGetPricingStatus_InvalidId() {
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(
            RLM_PreProcessOrderController.getPricingStatus('801000000000000AAA')
        );
        System.assertEquals(false, m.get('success'), 'No matching order returns structured error');
    }

    @isTest
    static void testGetPricingStatus_RealOrder() {
        Order o = buildLargeDealOrder();
        Test.startTest();
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(
            RLM_PreProcessOrderController.getPricingStatus(o.Id)
        );
        Test.stopTest();
        System.assertEquals(true, m.get('success'), 'Real order pricing status resolves');
        System.assertNotEquals(null, m.get('phase'), 'phase key present');
        System.assert(m.containsKey('calculationStatus'), 'calculationStatus key present');
        System.assert(m.containsKey('validationResult'), 'validationResult key present');
        System.assert(m.containsKey('pendingAsyncCount'), 'pendingAsyncCount key present');
    }

    @isTest
    static void testEnqueuePreprocess_BlankId() {
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(
            RLM_PreProcessOrderController.enqueuePreprocess('')
        );
        System.assertEquals(false, m.get('success'), 'Blank id fails gracefully');
    }

    @isTest
    static void testEnqueuePreprocess_LargeDeal_NotCommitted() {
        // A fresh large-deal order has no committed pricing, so enqueue must refuse
        // and report the pricing_not_committed phase (never enqueues against unpriced lines).
        Order o = buildLargeDealOrder();
        Test.startTest();
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(
            RLM_PreProcessOrderController.enqueuePreprocess(o.Id)
        );
        Test.stopTest();
        System.assertEquals(false, m.get('success'), 'Uncommitted pricing blocks enqueue');
        System.assertEquals('pricing_not_committed', m.get('phase'), 'Reports pricing_not_committed');
    }

    @isTest
    static void testClassifyPricingPhase_Cases() {
        System.assertEquals('pricing_committed',
            RLM_PreProcessOrderController.classifyPricingPhase('CompletedWithPricing', null, 0),
            'Cleared ValidationResult + terminal success + no pending = committed');
        System.assertEquals('pricing_in_progress',
            RLM_PreProcessOrderController.classifyPricingPhase('CompletedWithPricing', 'TransactionIncomplete', 0),
            'Dirty ValidationResult is not committed even with terminal status');
        System.assertEquals('pricing_in_progress',
            RLM_PreProcessOrderController.classifyPricingPhase('CompletedWithPricing', null, 2),
            'Pending async work is not committed');
        System.assertEquals('pricing_in_progress',
            RLM_PreProcessOrderController.classifyPricingPhase('PriceCalculationInProgress', null, 0),
            'In-progress status waits');
        System.assertEquals('pricing_in_progress',
            RLM_PreProcessOrderController.classifyPricingPhase(null, null, 0),
            'Null status waits');
        System.assertEquals('pricing_failed',
            RLM_PreProcessOrderController.classifyPricingPhase('PstBaseStepFailed', null, 0),
            'PstBaseStepFailed = failed (retry)');
        System.assertEquals('pricing_failed',
            RLM_PreProcessOrderController.classifyPricingPhase('PriceCalculationFailed', null, 9),
            'Failure status overrides pending/validation');
        System.assertEquals('pricing_investigate',
            RLM_PreProcessOrderController.classifyPricingPhase('PartialSaveSuccess', null, 0),
            'Partial-save = investigate (no auto-retry)');
    }

    @isTest
    static void testClassifyPricingPhase_AllStatusesBucketed() {
        // Exhaustiveness guard over the full core OrderCalculationStatus picklist
        // (24 values). Fails loudly if a value drifts into the wrong bucket.
        Map<String, String> expected = new Map<String, String>{
            'NotStarted' => 'pricing_in_progress',
            'ContextHydrationInProgress' => 'pricing_in_progress',
            'QueuedForConfiguration' => 'pricing_in_progress',
            'ConfigurationInProgress' => 'pricing_in_progress',
            'QueuedForPricing' => 'pricing_in_progress',
            'QueuedForPricingAndSaving' => 'pricing_in_progress',
            'PriceCalculationInProgress' => 'pricing_in_progress',
            'TaxCalculationWaiting' => 'pricing_in_progress',
            'QueuedForSaving' => 'pricing_in_progress',
            'Saving' => 'pricing_in_progress',
            'ReconciliationInProgress' => 'pricing_in_progress',
            'PstBaseStepFailed' => 'pricing_failed',
            'ConfigurationFailed' => 'pricing_failed',
            'GroupRampConfigurationFailed' => 'pricing_failed',
            'PriceCalculationFailed' => 'pricing_failed',
            'TaxCalculationFailed' => 'pricing_failed',
            'SaveFailedOrIncomplete' => 'pricing_failed',
            'ReconciliationFailed' => 'pricing_failed',
            'OrderRequestFailed' => 'pricing_failed',
            'OrderRequestPartiallySaved' => 'pricing_investigate',
            'PartialSaveSuccess' => 'pricing_investigate',
            'CompletedWithPricing' => 'pricing_committed',
            'CompletedWithTax' => 'pricing_committed',
            'CompletedWithoutPricing' => 'pricing_committed'
        };
        System.assertEquals(24, expected.size(), 'All 24 CalculationStatus values covered');
        for (String status : expected.keySet()) {
            // committed inputs (ValidationResult cleared, no pending) so terminal-success
            // values resolve to committed and the in-progress/failed buckets are isolated.
            System.assertEquals(
                expected.get(status),
                RLM_PreProcessOrderController.classifyPricingPhase(status, null, 0),
                'Status ' + status + ' classified into the wrong bucket'
            );
        }
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
    static void testGetStatus_RealOrder_NoTracker_FreshFlags() {
        // Success path for a freshly built large-deal order with no PreprocessOrder
        // AsyncOperationTracker and an unstamped (null) PreprocessingStatus. Every flag is
        // deterministic: requestId=null skips the scoped tracker query and the fallback finds
        // no rows, so trackerStatus stays null (=> failed/trackerDone false); PreprocessingStatus
        // is null so isValidationComplete is false (=> ready and done false); Status is 'Draft'
        // so activated is false.
        Order o = buildLargeDealOrder();
        Test.startTest();
        String resp = RLM_PreProcessOrderController.getStatus(o.Id, null);
        Test.stopTest();
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertEquals(true, m.get('success'), 'Real order status resolves');
        System.assertEquals(null, m.get('trackerStatus'), 'No tracker for a fresh order (scoping falls through to none)');
        System.assertEquals(null, m.get('preprocessingStatus'), 'PreprocessingStatus unstamped on a fresh order');
        System.assertEquals('Draft', m.get('orderStatus'), 'Order status reflected from the order record');
        System.assertEquals(false, m.get('done'), 'No tracker-done and no validation-complete => not done');
        System.assertEquals(false, m.get('failed'), 'No tracker status => not failed');
        System.assertEquals(false, m.get('ready'), 'Null PreprocessingStatus => validation not complete => not ready');
        System.assertEquals(false, m.get('activated'), 'Draft order is not activated');
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
        Order o = buildOrderWithItems(true, 200);
        Test.startTest();
        RLM_PreProcessOrderController.stampLargeDealExcludeTreatment(o.Id);
        Test.stopTest();
        List<OrderItem> ois = [SELECT BillingTreatmentId FROM OrderItem WHERE OrderId = :o.Id];
        System.assertEquals(200, ois.size(), 'All 200 items present');
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
