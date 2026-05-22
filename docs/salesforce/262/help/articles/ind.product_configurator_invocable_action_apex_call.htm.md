---
article_id: ind.product_configurator_invocable_action_apex_call.htm
title: Use an Apex Call to Run the Run Config Rules Action
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_invocable_action_apex_call.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Use an Apex Call to Run the Run Config Rules Action

Use an Apex call to run the Run Config Rules invocable action with the Hide/Disable, Message, or Recommend rule.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To work with configuration rules	Manage Configurator with Constraint Rules Engine
To use the Run Config Rules invocable action	Product Configuration Rules User
To work with Apex	Apex Author

For information on the Run Config Rules invocable action, see Run Config Rules Action in the Agentforce Revenue Management Developers Guide.

Make an Apex call to create, debug, and execute the Run Config Rules invocable action, similar to this example.

EXAMPLE
public class RunConfigRulesDebugger {
    public static void debugRunConfigRules(String quoteId) {
        try {
            // Create the invocable action with namespace
            Invocable.Action action = Invocable.Action.createStandardAction('runConfigRules');
            
            System.debug('Setting transactionContextId parameter with value: ' + quoteId);
            
            action.setInvocationParameter('transactionId', quoteId);
            
            // Debug the action parameters
            System.debug('Action parameters: ' + action);
            
            // Execute the action
            System.debug('Invoking action...');
            List<Invocable.Action.Result> results = action.invoke();
            
            System.debug('Number of results: ' + results.size());
            
            // Process the results
            if (!results.isEmpty()) {
                Invocable.Action.Result result = results[0];
                System.debug('Is Success: ' + result.isSuccess());
                System.debug('Results are: ' + results);
                
            } 
         } catch (Exception e) {
            System.debug('=== EXCEPTION ===');
            System.debug('Exception occurred: ' + e.getMessage());
            System.debug('Stack trace: ' + e.getStackTraceString());
        }
       }
}
