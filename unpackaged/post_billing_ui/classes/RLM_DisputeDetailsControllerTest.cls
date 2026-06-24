@isTest
private class RLM_DisputeDetailsControllerTest {

    private static Id fakeId(Schema.SObjectType sot) {
        String prefix = sot.getDescribe().getKeyPrefix();
        // Defensive: a type with no key prefix would otherwise build 'null000...' and throw an
        // unhelpful StringException. Fall back to the Account prefix for such (unused) types.
        if (String.isBlank(prefix)) {
            prefix = Account.SObjectType.getDescribe().getKeyPrefix();
        }
        return Id.valueOf(prefix + '000000000000');
    }

    @isTest
    static void getRelatedNames_nullLists_returnsEmptyMaps() {
        Test.startTest();
        Map<String, Object> result = RLM_DisputeDetailsController.getRelatedNames(null, null);
        Test.stopTest();
        System.assertNotEquals(null, result, 'A non-null result map should always be returned.');
        System.assert(result.containsKey('invoiceNames'), 'invoiceNames key expected.');
        System.assert(result.containsKey('lineNames'), 'lineNames key expected.');
        System.assert(result.containsKey('lineBalances'), 'lineBalances key expected.');
        System.assertEquals(0, ((Map<String, String>) result.get('invoiceNames')).size(),
            'Null invoice ids yield an empty name map.');
    }

    @isTest
    static void getRelatedNames_unknownIds_returnsEmptyMaps() {
        List<Id> invoiceIds = new List<Id>{ fakeId(Invoice.SObjectType) };
        List<Id> invoiceLineIds = new List<Id>{ fakeId(InvoiceLine.SObjectType) };
        Test.startTest();
        Map<String, Object> result = RLM_DisputeDetailsController.getRelatedNames(invoiceIds, invoiceLineIds);
        Test.stopTest();
        System.assertNotEquals(null, result, 'A non-null result map should always be returned.');
        System.assertEquals(0, ((Map<String, String>) result.get('lineNames')).size(),
            'Non-existent line ids yield an empty name map.');
    }

    @isTest
    static void saveApprovedAmounts_nullAndEmpty_noOp() {
        Test.startTest();
        RLM_DisputeDetailsController.saveApprovedAmounts(null);
        RLM_DisputeDetailsController.saveApprovedAmounts(new List<Map<String, Object>>());
        Test.stopTest();
        System.assert(true, 'Null/empty input short-circuits without error.');
    }

    // Exercises the DisputeItem field-discovery + query path with a non-existent item id. Whatever
    // the org's DisputeItem gating (object/field present or absent), the contract is the same: a
    // fake id matches no record, so the method must never persist an update. Asserting zero DML
    // rows is deterministic across both the clean-no-op and graceful-AuraHandledException outcomes.
    @isTest
    static void saveApprovedAmounts_unknownItem_persistsNothing() {
        List<Map<String, Object>> items = new List<Map<String, Object>>{
            new Map<String, Object>{ 'id' => disputeItemFakeId(), 'approvedAmount' => 10 }
        };

        Test.startTest();
        Integer rowsBefore = Limits.getDmlRows();
        try {
            RLM_DisputeDetailsController.saveApprovedAmounts(items);
        } catch (AuraHandledException e) {
            // Acceptable: DisputeItem object or its Approved Amount field is gated/absent here.
        }
        Integer rowsAfter = Limits.getDmlRows();
        Test.stopTest();

        System.assertEquals(rowsBefore, rowsAfter,
            'A non-existent DisputeItem id must never cause a record to be updated.');
    }

    private static Id disputeItemFakeId() {
        if (Schema.getGlobalDescribe().containsKey('DisputeItem')) {
            String prefix = Schema.getGlobalDescribe().get('DisputeItem').getDescribe().getKeyPrefix();
            if (String.isNotBlank(prefix)) {
                return Id.valueOf(prefix + '000000000000');
            }
        }
        // DisputeItem absent or prefix-less: any well-formed id drives the object-not-found path.
        return fakeId(Account.SObjectType);
    }
}
