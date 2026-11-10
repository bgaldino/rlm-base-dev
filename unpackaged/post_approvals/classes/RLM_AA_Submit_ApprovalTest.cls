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

    // Known gap: the invocable reads only svcParameters[0]. A batch whose second
    // request names a flow that does not exist succeeds today, because the
    // second request is never tried. The pin detects a fix that starts every
    // request and lets a failure propagate: the missing flow's TypeException
    // then trips the assertion below. A fix that loops but swallows each
    // request's failure would not trip it.
    @IsTest
    static void knownGap_callFlowIgnoresRequestsAfterTheFirst_whenTheFlowIsActive() {
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

        // Any exception naming the missing flow, whatever its type, means the
        // second request was tried: the fix. Matches only the flow API name the
        // platform passes through, never its translated wording.
        if (thrown != null && thrown.getMessage() != null && thrown.getMessage().contains(MISSING_FLOW)) {
            Assert.fail('Known gap: only the first request was started; it now started the second request ('
                + thrown.getTypeName() + '). Update this test.');
        }
        Assert.isNull(thrown, 'Unexpected exception starting the batch (not the known gap): '
            + (thrown == null ? '' : thrown.getTypeName() + ': ' + thrown.getMessage()));
    }

    // Known gap: with no guard on the list, an empty request list fails reading
    // request 0. No flow is started.
    @IsTest
    static void knownGap_callFlowThrowsOnAnEmptyRequestList() {
        Exception thrown = null;
        Test.startTest();
        try {
            RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>());
        } catch (Exception caught) {
            thrown = caught;
        }
        Test.stopTest();

        // Any outcome other than a raw ListException counts as the fix (for
        // example an IllegalArgumentException, as the docgen invocables throw).
        // Type only: platform exception text is translated into the running
        // user's language, so it is not checked.
        if (!(thrown instanceof ListException)) {
            Assert.fail('Known gap: an empty request list throws a raw ListException; it now '
                + (thrown == null ? 'returns' : 'throws ' + thrown.getTypeName()) + '. Update this test.');
        }
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
