/**
 * Tests for RLM_AA_Submit_Approval, the invocable that starts a named approval
 * flow with the record, approval level, submitter and comments.
 */
@IsTest
private class RLM_AA_Submit_ApprovalTest {

    // RLM_AA_Set_Quote_Status is an autolaunched flow in this module that sets
    // Quote.RLM_Approval_Status__c on the quote named by its QuoteID input.
    // The invocable starts it without error, and passes only its own fixed
    // inputs (recordId, ApprovalLevel, submitter, submissionComments): QuoteID
    // is never set, so the quote is left unchanged.
    @IsTest
    static void callFlowStartsAnExistingFlowWithOnlyItsOwnInputs() {
        Quote premiseQuote = createQuote('Approval Premise Quote');
        Quote submitted = createQuote('Approval Submitted Quote');

        // PRECONDITION: the flow does write the status when QuoteID is supplied,
        // so an unchanged quote below is evidence, not a flow that never writes.
        Flow.Interview direct = Flow.Interview.createInterview(
            'RLM_AA_Set_Quote_Status',
            new Map<String, Object>{ 'QuoteID' => premiseQuote.Id, 'Status' => 'Pending' }
        );
        direct.start();
        Assert.areEqual('Pending',
            [SELECT RLM_Approval_Status__c FROM Quote WHERE Id = :premiseQuote.Id].RLM_Approval_Status__c,
            'PRECONDITION: the flow updates the quote named by QuoteID.');

        RLM_AA_Submit_Approval.svcParameter params = new RLM_AA_Submit_Approval.svcParameter();
        params.flowName = 'RLM_AA_Set_Quote_Status';
        params.recordId = submitted.Id;
        params.approvalLevel = '1';
        params.comments = 'Please review the discount.';

        Test.startTest();
        RLM_AA_Submit_Approval.callFlow(new List<RLM_AA_Submit_Approval.svcParameter>{ params });
        Test.stopTest();

        Assert.isNull(
            [SELECT RLM_Approval_Status__c FROM Quote WHERE Id = :submitted.Id].RLM_Approval_Status__c,
            'The invocable passes recordId, not QuoteID, so this flow leaves the quote unchanged.');
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
