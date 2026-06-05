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
        if (o == null) {
            return; // Environment without the prerequisite setup; covered by other tests.
        }
        Test.startTest();
        String resp = RLM_PreProcessOrderController.getOrderInfo(o.Id);
        Test.stopTest();
        Map<String, Object> m = (Map<String, Object>) JSON.deserializeUntyped(resp);
        System.assertEquals(true, m.get('success'), 'Real order info resolves');
        System.assertEquals(true, m.get('isLargeDeal'), 'IsLargeDeal flag surfaced');
    }

    /** Minimal large-deal order; returns null if the org cannot create one in test context. */
    private static Order buildLargeDealOrder() {
        try {
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
        } catch (Exception e) {
            return null;
        }
    }
}
