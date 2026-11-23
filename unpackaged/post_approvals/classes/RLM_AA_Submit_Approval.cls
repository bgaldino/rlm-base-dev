global class RLM_AA_Submit_Approval {
@InvocableMethod(label='Submit for Approval' description='Calls a Flow Orchestration Approval.' category='Approvals')
    public static void callFlow(List<svcParameter> svcParameters) {
    if (svcParameters == null || svcParameters.isEmpty()) {
        return;
    }
    // Start the approval flow for every request in the batch (one interview each).
    for (svcParameter param : svcParameters) {
        // Prepare the Flow variables
        Map<String, Object> inputs = new Map<String, Object>();
        inputs.put('recordId', param.recordId);
        inputs.put('ApprovalLevel', param.approvalLevel);
        inputs.put('submitter', UserInfo.getUserId());
        inputs.put('submissionComments', param.comments);
        // Instantiate and start the Flow
        Flow.Interview myFlow = Flow.Interview.createInterview(param.flowName, inputs);
        myFlow.start();
    }
    }
    global class svcParameter {
            @InvocableVariable(required=true)
            global String flowName;
            @InvocableVariable(required=true)
            global String recordId;
            @InvocableVariable(required=false)
            global String approvalLevel;
            @InvocableVariable(required=false)
            global String comments;
            }
}