---
article_id: ind.approvals_define_custom_logic_auto_approvals.htm
title: Define Rules and Conditions for Auto-Approval Resubmissions
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_define_custom_logic_auto_approvals.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Define Rules and Conditions for Auto-Approval Resubmissions

Set your own rules and conditions on specific fields for auto-approving resubmissions. Compare the current submission’s record details against the previously submitted record so that only significant changes require manual review.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions where Advanced Approvals is enabled
USER PERMISSIONS NEEDED
To configure the properties of an approval step in a workflow:	

Approval Designer

OR

Manage Flow

Before you begin, make sure that you have an approval workflow with at least one stage and an approval step.

To determine whether an approval step can skip manual review during resubmission, use a custom autolaunched flow. You can invoke the flow from a background step that precedes the target approval step in your workflow.

In your custom flow, use an Apex action to retrieve the previously submitted record’s data and compare it with the current submission. This data serves as reference to help you create your own evaluation logic for auto-approvals. The evaluation must provide a boolean outcome that the target approval step uses to execute the auto-approval decision.

Create an Apex Class for the Apex Action to Retrieve and Evaluate Data
From Setup, find and select Apex Classes.
Click New.
In the class editor, enter the sample Apex code, and customize it per your requirements.
// This is wrapper class to get getPreviousRelaRecDetails results
public class ApprovalPreviousRelatedRecordDetails {
    
    static final String ACTION_NAME = 'getPreviousRelaRecDetails';
    static final String ACTION_INPUT_PARAM_FOI_ID = 'flowOrchestrationInstanceId';
    static final String ACTION_INPUT_PARAM_STEP_API_NAMES = 'stepApiNamesList';
    static final String ACTION_OUTPUT_PARAM_PREVIOUS_RECORD_DETAILS = 'previousRelatedRecordDetails';
        
    @InvocableMethod(label='Get Previous Related Record Details' description='Gets the related record details submitted for approval prior to the current approval submission, which is required for approval steps that use custom logic for auto-approvals.')
    // This method gets the previous related record details for the passed flow orchestration instance ID and the step api names.
    public static List<List<SObject>> getPreviousRelaRecDetails(List<FlowInputs> flowInputs) {
        List<List<SObject>> response = new List<List<SObject>>();
        List<SObject> allPreviousRelatedRecordDetails = new List<SObject>();

        // Set the action as the getPreviousRelaRecDetails which fetches related record details from the previous submission. 
        Invocable.Action action = Invocable.Action.createStandardAction(ACTION_NAME);
        action.setInvocationParameter(ACTION_INPUT_PARAM_FOI_ID, flowInputs[0].flowOrchestrationInstanceId);
        action.setInvocationParameter(ACTION_INPUT_PARAM_STEP_API_NAMES, flowInputs[0].stepApiNamesList);

        // Run the invocable action.
        List<Invocable.Action.Result> results = action.invoke();

        // Get all the previous related record details. They are retrieved in the same order as the order of the input step API names.
        if (results.size() > 0 && results[0].isSuccess()) {
            allPreviousRelatedRecordDetails = (List<SObject>) results[0].getOutputParameters().get(ACTION_OUTPUT_PARAM_PREVIOUS_RECORD_DETAILS);
            response.add(allPreviousRelatedRecordDetails);
        } else if (!results[0].isSuccess()){
            // If there are no results returned, consider it as a failure.
            // Based upon the use case, this can also be success with 0 records.
            for(Invocable.Action.Error error : results[0].getErrors()) {
                // throw new InvocableActionException(error.getMessage());
            }
        }
        return response;
    }
    
    // This inner class sets invocable action input variables
    public class FlowInputs {
        @InvocableVariable
        public String flowOrchestrationInstanceId;

        @InvocableVariable(required=false)
        public List<String> stepApiNamesList;
        
    }
    
    // This inner class is to handle any invocable action related exceptions
    public class InvocableActionException extends Exception {
   // Add your custom logic here.
    }
}

Create an autolaunched flow that uses the Apex action to retrieve the previous submitted record details for your custom evaluations. You can configure your evaluation conditions either in this flow or in the approval workflow by using variables.

Configure Your Approval Workflow

Invoke your custom flow from a background step that precedes the target approval step in your approval workflow.

From Setup, find and select Flows.
Open the flow that you use for managing approvals.
In the stage with the target approval step, click + Add Step.
Select Background Step and specify these details.
Enter a name, an API name, and a description.
Select a condition.
Under the Select an Action to Run section, select the custom flow that you created.
For Select Who to Run the Action as, select Automated Process User as the user type.
Go to the target approval and specify these details.
If your background step precedes the target approval step within the same stage, select When another step is marked Complete, the step starts as the condition.
For Step API Name, enter the name of the background step that runs your custom flow.
Select Set custom logic for auto-approvals.
For Auto-Approve Step, specify the boolean output from your custom evaluations.
Save and activate your flow.
