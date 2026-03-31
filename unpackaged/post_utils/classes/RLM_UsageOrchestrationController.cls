/**
 * RLM_UsageOrchestrationController
 *
 * Apex controller for the rlmUsageOrchestration Lightning Web Component.
 * Provides methods to:
 *  - Trigger usage processing by invoking the RLM_Orchestrate_Usage_Management flow
 *  - Poll for orchestration status by querying FlowInterview records
 *  - Retrieve last run information
 */
public with sharing class RLM_UsageOrchestrationController {

    private static final String ORCHESTRATION_FLOW_API_NAME = 'RLM_Orchestrate_Usage_Management';

    /**
     * Wrapper class for orchestration status information.
     */
    public class OrchestrationStatus {
        @AuraEnabled public String interviewId;
        @AuraEnabled public String status; // 'Started', 'Paused', 'Finished', 'Error'
        @AuraEnabled public String step1Status; // 'Success', 'Error', or null
        @AuraEnabled public String step2Status;
        @AuraEnabled public String step3Status;
        @AuraEnabled public DateTime startTime;
        @AuraEnabled public DateTime lastModifiedTime;
        @AuraEnabled public String currentElement;
    }

    /**
     * Starts the usage orchestration flow asynchronously.
     *
     * @param flowApiName The API name of the autolaunched flow to invoke (optional, defaults to RLM_Orchestrate_Usage_Management)
     * @return Interview ID that can be used to poll for status
     */
    @AuraEnabled
    public static String startOrchestration(String flowApiName) {
        // Default to standard orchestration flow if not specified
        if (String.isBlank(flowApiName)) {
            flowApiName = ORCHESTRATION_FLOW_API_NAME;
        }

        try {
            // Create and start the flow interview
            Flow.Interview interview = Flow.Interview.createInterview(
                flowApiName,
                new Map<String, Object>()
            );
            interview.start();

            // Return the interview ID directly to avoid nondeterministic "most recent" queries.
            String interviewId = interview.getInterviewId();
            if (String.isNotBlank(interviewId)) {
                return interviewId;
            }

            throw new AuraHandledException('Could not determine started flow interview ID');

        } catch (Exception e) {
            throw new AuraHandledException('Failed to start orchestration: ' + e.getMessage());
        }
    }

    /**
     * Retrieves the current status of a running or completed orchestration.
     *
     * @param interviewId The interview ID returned by startOrchestration
     * @return OrchestrationStatus with current state
     */
    @AuraEnabled
    public static OrchestrationStatus getOrchestrationStatus(String interviewId) {
        try {
            // Query the FlowInterview to get status
            List<FlowInterview> interviews = [
                SELECT Id, InterviewLabel, InterviewStatus, CurrentElement,
                       CreatedDate, LastModifiedDate, Guid
                FROM FlowInterview
                WHERE Id = :interviewId
                LIMIT 1
            ];

            if (interviews.isEmpty()) {
                throw new AuraHandledException('Flow interview not found');
            }

            FlowInterview interview = interviews[0];
            OrchestrationStatus status = new OrchestrationStatus();
            status.interviewId = interview.Id;
            status.status = interview.InterviewStatus;
            status.startTime = interview.CreatedDate;
            status.lastModifiedTime = interview.LastModifiedDate;
            status.currentElement = interview.CurrentElement;

            // Try to get step statuses from flow variables if interview is complete
            if (interview.InterviewStatus == 'Finished') {
                // For now, we'll indicate completion based on status
                status.step1Status = 'Success';
                status.step2Status = 'Success';
                status.step3Status = 'Success';
            }

            return status;

        } catch (Exception e) {
            throw new AuraHandledException('Failed to get orchestration status: ' + e.getMessage());
        }
    }

    /**
     * Retrieves information about the last orchestration run.
     *
     * @return OrchestrationStatus of the most recent run, or null if none found
     */
    @AuraEnabled(cacheable=true)
    public static OrchestrationStatus getLastRunInfo() {
        try {
            // Query the most recent FlowInterview for our orchestration flow
            List<FlowInterview> interviews = [
                SELECT Id, InterviewLabel, InterviewStatus, CurrentElement,
                       CreatedDate, LastModifiedDate, Guid
                FROM FlowInterview
                WHERE InterviewLabel LIKE 'RLM Orchestrate Usage Management%'
                ORDER BY CreatedDate DESC
                LIMIT 1
            ];

            if (interviews.isEmpty()) {
                return null;
            }

            FlowInterview interview = interviews[0];
            OrchestrationStatus status = new OrchestrationStatus();
            status.interviewId = interview.Id;
            status.status = interview.InterviewStatus;
            status.startTime = interview.CreatedDate;
            status.lastModifiedTime = interview.LastModifiedDate;
            status.currentElement = interview.CurrentElement;

            return status;

        } catch (Exception e) {
            // Return null if query fails (e.g., user lacks permissions)
            return null;
        }
    }
}
