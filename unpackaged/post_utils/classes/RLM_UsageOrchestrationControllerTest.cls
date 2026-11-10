/**
 * Tests for RLM_UsageOrchestrationController.startOrchestration: a named flow is started,
 * and any failure to create or start the interview reaches the LWC as an AuraHandledException.
 *
 * Not covered: the blank-name fallback to RLM_OrchestrateUsageManagement. Starting that flow
 * inside a test runs the managed usage orchestration subflows, and the test job then ends
 * Failed with no coverage recorded even though the method itself passes.
 */
@IsTest
private with sharing class RLM_UsageOrchestrationControllerTest {

    /**
     * An active, untriggered autolaunched flow from this module that does nothing when it gets
     * no inputs (its first decision has no default path). Starting it proves the named-flow
     * path without running usage orchestration.
     */
    private static final String NO_OP_FLOW = 'RLM_RenewalCoveredAssets';

    @IsTest
    static void testStartOrchestration_NamedFlow_Starts() {
        Test.startTest();
        String token = RLM_UsageOrchestrationController.startOrchestration(NO_OP_FLOW);
        Test.stopTest();

        Assert.areEqual('started', token, 'Starting a valid flow returns the started token');
    }

    @IsTest
    static void testStartOrchestration_InvalidFlow_Throws() {
        Test.startTest();
        Boolean didThrow = false;
        try {
            RLM_UsageOrchestrationController.startOrchestration('Definitely_Not_A_Real_Flow_API_Name');
            Assert.fail('Expected exception for invalid flow API name');
        } catch (AuraHandledException e) {
            didThrow = true;
        }
        Test.stopTest();
        Assert.isTrue(didThrow, 'Expected AuraHandledException for invalid flow API name');
    }

}
