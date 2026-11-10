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
    @IsTest
    static void callFlowStartsAnExistingFlowWithoutError() {
        Quote quote = createQuote('Approval Test Quote');

        RLM_AA_Submit_Approval.svcParameter params = new RLM_AA_Submit_Approval.svcParameter();
        params.flowName = 'RLM_AA_Set_Quote_Status';
        params.recordId = quote.Id;
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

    private static Quote createQuote(String name) {
        Account account = new Account(Name = name + ' Account');
        insert account;
        Opportunity opportunity = new Opportunity(
            Name = name + ' Opportunity',
            AccountId = account.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opportunity;
        Quote quote = new Quote(
            Name = name,
            OpportunityId = opportunity.Id,
            Pricebook2Id = Test.getStandardPricebookId(),
            Status = 'Draft'
        );
        insert quote;
        return quote;
    }
}
