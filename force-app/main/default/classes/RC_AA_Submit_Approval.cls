global class RC_AA_Submit_Approval {
@InvocableMethod(label='Submit for Approval' description='Calls a Flow Orchestration Approval.' category='Approvals')
    public static void callFlow(List<svcParameter> svcParameters) {
    // Prepare the Flow variables
    String flowApiName = svcParameters[0].flowName;
    Map<String, Object> inputs = new Map<String, Object>();
    inputs.put('recordId', svcParameters[0].recordId);
    inputs.put('ApprovalLevel', svcParameters[0].approvalLevel);
    inputs.put('submitter', UserInfo.getUserId());
    inputs.put('submissionComments', svcParameters[0].comments);
    // Instantiate and start the Flow
    Flow.Interview myFlow = Flow.Interview.createInterview(flowApiName, inputs);
    myFlow.start();
    return;
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