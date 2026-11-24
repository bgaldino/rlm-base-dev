/**
 * Starts the named approval flow once per request.
 *
 * Limits: each request starts its own flow interview, so a batch is bounded by the per-transaction
 * limits (for example the 150 DML statements and 100 SOQL queries any interview's elements use).
 * Pass the smallest batches the caller can; the invocable does not chunk or bulkify the flow.
 *
 * A failure stops the whole batch: the interviews run in the caller's transaction and nothing here
 * catches their exceptions, so when one request fails (an unknown flow name, or a fault in its flow)
 * the later requests are not started, and unless the caller handles the fault the transaction rolls
 * back the submissions the earlier requests made.
 */
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