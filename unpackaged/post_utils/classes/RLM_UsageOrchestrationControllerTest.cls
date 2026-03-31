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

    @IsTest
    static void testGetOrchestrationStatus_InvalidId_Throws() {
        // Use a syntactically-valid but nonexistent FlowInterview Id.
        String fakeInterviewId = '301000000000001AAA';

        Test.startTest();
        Boolean didThrow = false;
        try {
            RLM_UsageOrchestrationController.getOrchestrationStatus(fakeInterviewId);
            System.assert(false, 'Expected exception for nonexistent interview');
        } catch (AuraHandledException e) {
            didThrow = true;
        }
        Test.stopTest();
        System.assert(didThrow, 'Expected AuraHandledException for nonexistent interview');
    }

    @IsTest
    static void testGetLastRunInfo_NoInterview_ReturnsNullOrStatus() {
        Test.startTest();
        RLM_UsageOrchestrationController.OrchestrationStatus status =
            RLM_UsageOrchestrationController.getLastRunInfo();
        Test.stopTest();

        // In isolated test context this is typically null; keep assertion tolerant in case
        // org metadata/setup exposes interview rows.
        if (status != null) {
            System.assertNotEquals(null, status.interviewId, 'Status should include interviewId when present');
            System.assertNotEquals(null, status.status, 'Status should include interview status when present');
        } else {
            System.assertEquals(null, status, 'Expected null when no interview data is available');
        }
    }
}
