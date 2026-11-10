/**
 * Tests for RLM_UsageOrchestrationController.startOrchestration: a named flow is started and
 * returns the started token, and a flow name that cannot be resolved into an interview reaches
 * the LWC as an AuraHandledException.
 *
 * Not covered:
 *  - the blank-name fallback to RLM_OrchestrateUsageManagement. Starting that flow inside a
 *    test runs the managed usage orchestration subflows, and the test job then ends Failed
 *    with no coverage recorded even though the method itself passes.
 *  - a failure raised by interview.start() after the interview was created; no flow in this
 *    repo fails on start without inputs.
 */
@IsTest
private with sharing class RLM_UsageOrchestrationControllerTest {

    /**
     * TEST DEPENDENCY on unpackaged/post_utils/flows/RLM_RenewalCoveredAssets.flow-meta.xml.
     * It must stay an active, untriggered autolaunched flow with no required input, whose first
     * decision (Has_Candidate_Assets) has no default path, so that started with no inputs it
     * ends at once without reading or writing anything. That lets this test prove the
     * named-flow path without running usage orchestration. If that flow is renamed, gains a
     * required input, or gains a default path from Has_Candidate_Assets, change this constant
     * to another flow that ends at once.
     */
    private static final String NO_OP_FLOW = 'RLM_RenewalCoveredAssets';

    @IsTest
    static void testStartOrchestration_NamedFlow_Starts() {
        Test.startTest();
        String token = RLM_UsageOrchestrationController.startOrchestration(NO_OP_FLOW);
        Integer queries = Limits.getQueries();
        Integer dmlStatements = Limits.getDmlStatements();
        Test.stopTest();

        Assert.areEqual(
            0,
            queries,
            'PRECONDITION: ' + NO_OP_FLOW + ' must end without reading anything when started with no inputs'
        );
        Assert.areEqual(
            0,
            dmlStatements,
            'PRECONDITION: ' + NO_OP_FLOW + ' must end without writing anything when started with no inputs'
        );
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
