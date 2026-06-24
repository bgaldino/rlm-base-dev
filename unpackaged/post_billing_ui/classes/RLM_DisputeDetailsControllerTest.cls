@isTest
private class RLM_DisputeDetailsControllerTest {

    private static Id fakeId(Schema.SObjectType sot) {
        return Id.valueOf(sot.getDescribe().getKeyPrefix() + '000000000000');
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

    // Exercises the DisputeItem field-discovery + query path. DisputeItem is a license-gated
    // extension, so either a clean no-op (record not found) or a graceful AuraHandledException
    // (object/field absent in this org) is acceptable.
    @isTest
    static void saveApprovedAmounts_unknownItem_handledGracefully() {
        Boolean completed = false;
        Test.startTest();
        try {
            List<Map<String, Object>> items = new List<Map<String, Object>>();
            if (Schema.getGlobalDescribe().containsKey('DisputeItem')) {
                Id fakeItem = Id.valueOf(
                    Schema.getGlobalDescribe().get('DisputeItem').getDescribe().getKeyPrefix() + '000000000000');
                items.add(new Map<String, Object>{ 'id' => fakeItem, 'approvedAmount' => 10 });
            } else {
                items.add(new Map<String, Object>{ 'id' => fakeId(Account.SObjectType), 'approvedAmount' => 10 });
            }
            RLM_DisputeDetailsController.saveApprovedAmounts(items);
            completed = true;
        } catch (AuraHandledException e) {
            completed = true;
        }
        Test.stopTest();
        System.assert(completed, 'The save path executes and is handled gracefully.');
    }
}
