/**
 * Tests for RLM_AA_Submit_Approval, the invocable that starts a named approval
 * flow with the record, approval level, submitter and comments.
 *
 * The tests that start a flow use RLM_AA_Set_Quote_Status, an autolaunched flow
 * in this module. Flows deploy inactive in production unless "Deploy processes
 * and flows as active" is on, so when it is not active those tests are skipped
 * visibly (a WARN debug line) instead of failing. Those tests are environment probes: in an org
 * where the flow is inactive they prove nothing, and the debug line is the only sign.
 *
 * Limits: each request starts its own flow interview, so a batch is bounded by the per-transaction
 * limits (for example the 150 DML statements and 100 SOQL queries any interview's elements use).
 * Pass the smallest batches the caller can; the invocable does not chunk or bulkify the flow.
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

    // Environment probe (skips when the flow is inactive, see the class comment). Every request in
    // the batch is started: a second request naming a flow that does not
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

    // An empty or null request list starts nothing: no exception, and no SOQL or DML (a started
    // flow interview would run elements that use them).
    @IsTest
    static void callFlowStartsNothingForAnEmptyOrNullRequestList() {
        Test.startTest();
        // Limits are read inside the start/stop block: they reset on entry and are restored on exit.
        Integer queriesBefore = Limits.getQueries();
        Integer dmlBefore = Limits.getDmlStatements();
        RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>());
        RLM_AA_Submit_Approval.callFlow(null);
        Assert.areEqual(queriesBefore, Limits.getQueries(), 'No SOQL runs for an empty or null list');
        Assert.areEqual(dmlBefore, Limits.getDmlStatements(), 'No DML runs for an empty or null list');
        Test.stopTest();
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
