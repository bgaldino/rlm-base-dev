/**
 * Tests for RLM_AA_Submit_Approval, the invocable that starts a named approval
 * flow with the record, approval level, submitter and comments.
 */
@IsTest
private class RLM_AA_Submit_ApprovalTest {

    // Covers only that the invocable creates and starts an existing flow without
    // error. Whether start() ran the interview is not observable here. It uses
    // RLM_AA_Set_Quote_Status, an autolaunched flow in this module, which does
    // not declare the invocable's inputs (recordId, ApprovalLevel, submitter,
    // submissionComments): a live run showed Flow.Interview.createInterview
    // ignores undeclared input names rather than failing.
    // Smoke test: asserts only that starting the flow does not throw. The
    // try/catch turns an exception into a named assertion failure.
    // Flows deploy inactive in production unless "Deploy processes and flows as
    // active" is on, so on a first production deploy the flow is not active and
    // this test is skipped visibly (a WARN debug line) instead of failing.
    @IsTest
    static void callFlowStartsAnExistingFlowWithoutError_whenTheFlowIsActive() {
        if ([SELECT COUNT() FROM FlowDefinitionView WHERE ApiName = 'RLM_AA_Set_Quote_Status' AND IsActive = true] == 0) {
            System.debug(
                LoggingLevel.WARN,
                'SKIPPED: RLM_AA_Set_Quote_Status is not active (flows deploy inactive in production unless Deploy-as-active is on)'
            );
            return;
        }
        RLM_AA_Submit_Approval.svcParameter params = new RLM_AA_Submit_Approval.svcParameter();
        params.flowName = 'RLM_AA_Set_Quote_Status';
        params.recordId = '0Q0000000000001';
        params.approvalLevel = '1';
        params.comments = 'Please review the discount.';

        Test.startTest();
        try {
            RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>{ params });
        } catch (Exception unexpected) {
            Assert.fail('Starting an existing flow must not fail: ' + unexpected.getMessage());
        }
        Test.stopTest();
    }

    // Known gap: the invocable reads only svcParameters[0], with no guard, so an
    // empty request list fails with a ListException instead of doing nothing,
    // and any requests after the first are ignored. No flow is started.
    @IsTest
    static void callFlowFailsOnAnEmptyRequestList() {
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
        RLM_AA_Submit_Approval.svcParameter params = new RLM_AA_Submit_Approval.svcParameter();
        params.flowName = 'RLM_No_Such_Approval_Flow';
        params.recordId = '0Q0000000000001';

        Boolean threw = false;
        Test.startTest();
        try {
            RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>{ params });
        } catch (TypeException caught) {
            threw = true;
            Assert.isTrue(caught.getMessage().contains('RLM_No_Such_Approval_Flow'), caught.getMessage());
        }
        Test.stopTest();

        Assert.isTrue(threw, 'Starting a flow that does not exist must fail.');
    }
}
