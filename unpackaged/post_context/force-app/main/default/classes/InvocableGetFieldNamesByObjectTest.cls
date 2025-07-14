@isTest
private class InvocableGetFieldNamesByObjectTest {

    @isTest
    static void testValidObjectName() {
        // Prepare test input with a valid standard object
        InvocableGetFieldNamesByObject.ApiRequest req = new InvocableGetFieldNamesByObject.ApiRequest();
        req.objectName = 'Account';

        List<InvocableGetFieldNamesByObject.ApiRequest> reqList = new List<InvocableGetFieldNamesByObject.ApiRequest>{ req };

        // Call the method
        Test.startTest();
        List<InvocableGetFieldNamesByObject.ApiResponse> responses = InvocableGetFieldNamesByObject.createHeadlessBody(reqList);
        Test.stopTest();

        // Assertions
        System.assertEquals(1, responses.size(), 'Should return one response');
        InvocableGetFieldNamesByObject.ApiResponse response = responses[0];
        System.assertEquals(200, response.status, 'Status should be 200');
        System.assert(response.fieldNames != null && !response.fieldNames.isEmpty(), 'Field names should not be empty');

        // Check that each entry has name and description (field name and type)
        for (Account acc : response.fieldNames) {
            System.assertNotEquals(null, acc.Name, 'Field name should not be null');
            System.assertNotEquals(null, acc.Description, 'Field type should not be null');
        }
    }

    @isTest
    static void testInvalidObjectName() {
        // Prepare test input with an invalid object
        InvocableGetFieldNamesByObject.ApiRequest req = new InvocableGetFieldNamesByObject.ApiRequest();
        req.objectName = 'InvalidObjectName';

        List<InvocableGetFieldNamesByObject.ApiRequest> reqList = new List<InvocableGetFieldNamesByObject.ApiRequest>{ req };

        // Expect an exception to be thrown
        Test.startTest();
        try {
            InvocableGetFieldNamesByObject.createHeadlessBody(reqList);
            System.assert(false, 'Expected exception for invalid object name');
        } catch (IllegalArgumentException ex) {
            System.assert(ex.getMessage().contains('Invalid object name'), 'Should catch invalid object name exception');
        }
        Test.stopTest();
    }
}
