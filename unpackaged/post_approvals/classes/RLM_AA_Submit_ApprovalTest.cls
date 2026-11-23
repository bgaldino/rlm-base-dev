/**
 * Tests for RLM_AA_Submit_Approval, the invocable that starts a named approval
 * flow with the record, approval level, submitter and comments.
 *
 * The tests that start a flow use RLM_AA_Set_Quote_Status, an autolaunched flow
 * in this module. Flows deploy inactive in production unless "Deploy processes
 * and flows as active" is on, so when it is not active those tests are skipped
 * visibly (a WARN debug line) instead of failing.
 */
@IsTest
private class RLM_AA_Submit_ApprovalTest {

    private static final String ACTIVE_FLOW = 'RLM_AA_Set_Quote_Status';
    private static final String MISSING_FLOW = 'RLM_No_Such_Approval_Flow';

    private static Boolean activeFlowAvailable() {
        if ([SELECT COUNT() FROM FlowDefinitionView WHERE ApiName = :ACTIVE_FLOW AND IsActive = true] == 0) {
            System.debug(
                LoggingLevel.WARN,
                'SKIPPED: ' + ACTIVE_FLOW + ' is not active (flows deploy inactive in production '
                + 'unless Deploy-as-active is on)'
            );
            return false;
        }
        return true;
    }

    private static RLM_AA_Submit_Approval.svcParameter request(String flowName) {
        RLM_AA_Submit_Approval.svcParameter params = new RLM_AA_Submit_Approval.svcParameter();
        params.flowName = flowName;
        params.recordId = '0Q0000000000001';
        params.approvalLevel = '1';
        params.comments = 'Please review the discount.';
        return params;
    }

    // Smoke test: asserts only that starting the flow does not throw. The flow
    // does not declare the invocable's inputs; a live run showed
    // Flow.Interview.createInterview ignores undeclared input names.
    @IsTest
    static void callFlowStartsAnExistingFlowWithoutError_whenTheFlowIsActive() {
        if (!activeFlowAvailable()) {
            return;
        }
        Test.startTest();
        try {
            RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>{ request(ACTIVE_FLOW) });
        } catch (Exception unexpected) {
            Assert.fail('Starting an existing flow threw ' + unexpected.getTypeName() + ': '
                + unexpected.getMessage() + '\n' + unexpected.getStackTraceString());
        }
        Test.stopTest();
    }

    // Every request in the batch is started: a second request naming a flow that does not
    // exist fails the batch with the platform's TypeException naming that flow, proving the
    // second request was tried (the first request's flow is active, so it started).
    @IsTest
    static void callFlowStartsEveryRequestInTheBatch_whenTheFlowIsActive() {
        if (!activeFlowAvailable()) {
            return;
        }
        Exception thrown = null;
        Test.startTest();
        try {
            RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>{
                request(ACTIVE_FLOW),
                request(MISSING_FLOW)
            });
        } catch (Exception caught) {
            thrown = caught;
        }
        Test.stopTest();

        // Matches only the flow API name the platform passes through, never its
        // translated wording.
        Assert.isNotNull(thrown, 'The second request must be tried, so the missing flow fails the batch.');
        Assert.isTrue(thrown.getMessage() != null && thrown.getMessage().contains(MISSING_FLOW),
            'The failure names the second request\'s flow: ' + thrown.getTypeName() + ': ' + thrown.getMessage());
    }

    // Proves only that an empty request list does not throw; it does not assert that no flow starts.
    @IsTest
    static void callFlowDoesNotThrowForAnEmptyRequestList() {
        Test.startTest();
        RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>());
        Test.stopTest();
        // Reaching this line is the check: an uncaught exception above would fail the test.
    }

    // An unknown flow name cannot be started: the platform's TypeException
    // reaches the caller instead of being swallowed.
    @IsTest
    static void callFlowFailsForAnUnknownFlow() {
        Boolean threw = false;
        Test.startTest();
        try {
            RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>{ request(MISSING_FLOW) });
        } catch (TypeException caught) {
            threw = true;
            // Matches only the flow API name the platform passes through, never its
            // translated wording.
            Assert.isTrue(caught.getMessage().contains(MISSING_FLOW), caught.getMessage());
        }
        Test.stopTest();

        Assert.isTrue(threw, 'Starting a flow that does not exist must fail.');
    }
}
