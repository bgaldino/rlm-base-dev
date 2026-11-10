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
    static void knownGap_callFlowStartsOnlyTheFirstRequest_whenTheFlowIsActive() {
        if (!activeFlowAvailable()) {
            return;
        }
        Boolean laterRequestStarted = false;
        Test.startTest();
        try {
            RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>{
                request(ACTIVE_FLOW),
                request(MISSING_FLOW)
            });
        } catch (TypeException caught) {
            if (!caught.getMessage().contains(MISSING_FLOW)) {
                throw caught;
            }
            laterRequestStarted = true;
        }
        Test.stopTest();

        Assert.isFalse(laterRequestStarted,
            'Known gap: only the first request is started; requests after it are ignored. '
            + 'Update this test when it is fixed.');
    }

    // Known gap: with no guard on the list, an empty request list fails reading
    // request 0. No flow is started.
    @IsTest
    static void knownGap_callFlowThrowsOnAnEmptyRequestList() {
        Test.startTest();
        try {
            RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>());
            Assert.fail('Known gap: an empty request list throws a raw ListException (only the first '
                + 'request is read); update this test when it is fixed.');
        } catch (ListException caught) {
            Assert.isTrue(caught.getMessage().contains('out of bounds'),
                'the failure is the read of request 0: ' + caught.getMessage());
        }
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
            Assert.isTrue(caught.getMessage().contains(MISSING_FLOW), caught.getMessage());
        }
        Test.stopTest();

        Assert.isTrue(threw, 'Starting a flow that does not exist must fail.');
    }
}
