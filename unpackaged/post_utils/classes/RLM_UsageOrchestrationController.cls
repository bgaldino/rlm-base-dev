/**
 * RLM_UsageOrchestrationController
 *
 * Apex controller for the rlmUsageOrchestration Lightning Web Component.
 * Provides methods to trigger usage processing by invoking
 * the RLM_Orchestrate_Usage_Management flow.
 */
public with sharing class RLM_UsageOrchestrationController {

    private static final String ORCHESTRATION_FLOW_API_NAME = 'RLM_Orchestrate_Usage_Management';

    /**
     * Starts the usage orchestration flow asynchronously.
     *
     * The flowApiName parameter is intentionally open (no allowlist). This component
     * is designed for demos and post-deployment customization — admins configure the
     * flow API name via the Lightning App Builder property, allowing them to swap in
     * custom orchestration flows without code changes.
     *
     * @param flowApiName The API name of the autolaunched flow to invoke (optional, defaults to RLM_Orchestrate_Usage_Management)
     * @return Non-empty token indicating start was successful
     */
    @AuraEnabled
    public static String startOrchestration(String flowApiName) {
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
            return 'started';

        } catch (Exception e) {
            throw new AuraHandledException('Failed to start orchestration: ' + e.getMessage());
        }
    }
}
