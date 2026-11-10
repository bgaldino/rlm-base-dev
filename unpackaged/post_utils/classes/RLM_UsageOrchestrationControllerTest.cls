/**
 * Tests for RLM_UsageOrchestrationController.startOrchestration: a named flow is started and
 * returns the started token (when that flow is active in the org), and a flow name that
 * cannot be resolved into an interview reaches the LWC as an AuraHandledException.
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
     *
     * Flows deploy INACTIVE to production and TSO orgs unless "Deploy processes and flows as
     * active" is on, which this repo does not enable. The named-flow test therefore checks
     * FlowDefinitionView first and skips visibly (a WARN debug line) when the flow is inactive,
     * rather than failing that org's deploy. Scratch org builds activate it.
     */
    private static final String NO_OP_FLOW = 'RLM_RenewalCoveredAssets';

    @IsTest
    static void testStartOrchestration_NamedFlow_Starts_whenTheFlowIsActive() {
        // The assertions assume the repo's version of the flow, so require that the latest
        // version is the active one, not just that some version is active.
        List<FlowDefinitionView> flows = [
            SELECT ActiveVersionId, LatestVersionId FROM FlowDefinitionView WHERE ApiName = :NO_OP_FLOW LIMIT 1
        ];
        Boolean latestIsActive = !flows.isEmpty()
            && flows[0].ActiveVersionId != null
            && flows[0].ActiveVersionId == flows[0].LatestVersionId;
        if (!latestIsActive) {
            System.debug(
                LoggingLevel.WARN,
                'SKIPPED: ' + NO_OP_FLOW + ' is not active (flows deploy inactive in production unless Deploy-as-active is on)'
            );
            return;
        }

        Test.startTest();
        String token = RLM_UsageOrchestrationController.startOrchestration(NO_OP_FLOW);
        Integer queries = Limits.getQueries();
        Integer dmlStatements = Limits.getDmlStatements();
        Test.stopTest();

        Assert.areEqual(
            0,
            queries,
            'DEPENDENCY: ' + NO_OP_FLOW + ' must end without reading anything when started with no inputs'
        );
        Assert.areEqual(
            0,
            dmlStatements,
            'DEPENDENCY: ' + NO_OP_FLOW + ' must end without writing anything when started with no inputs'
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
