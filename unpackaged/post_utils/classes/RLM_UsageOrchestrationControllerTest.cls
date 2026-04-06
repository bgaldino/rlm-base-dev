@IsTest
private class RLM_UsageOrchestrationControllerTest {

    @IsTest
    static void testStartOrchestration_InvalidFlow_Throws() {
        Test.startTest();
        Boolean didThrow = false;
        try {
            RLM_UsageOrchestrationController.startOrchestration('Definitely_Not_A_Real_Flow_API_Name');
            System.assert(false, 'Expected exception for invalid flow API name');
        } catch (AuraHandledException e) {
            didThrow = true;
        }
        Test.stopTest();
        System.assert(didThrow, 'Expected AuraHandledException for invalid flow API name');
    }

}
