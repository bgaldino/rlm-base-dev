public class RLM_QuoteApprovalController {
private Id quoteId;
    private String userId ;
    public String submitterComments { get; set; }
    private Decimal approvalLevel;
    
    public RLM_QuoteApprovalController(ApexPages.StandardController controller) {
        Quote quote = (Quote) controller.getRecord(); // orig
        approvalLevel = [SELECT Id, RLM_Approval_Level__c FROM Quote WHERE Id =: quote.Id].get(0).RLM_Approval_Level__c; 
        quoteId = quote.Id; // orig
        
        userId = UserInfo.getUserId();
    }
    
    public void submitQuoteForApproval() {
        String flowApiName = 'RLM_AA_Quote_Approval';
        Map<String, Object> inputs = new Map<String, Object>();
        inputs.put('recordId', quoteId);
        inputs.put('ApprovalLevel', approvalLevel);
        inputs.put('submitter', userId);
        inputs.put('submissionComments', submitterComments);
        Flow.Interview myFlow = Flow.Interview.createInterview(flowApiName, inputs);
        myFlow.start();
    }
}