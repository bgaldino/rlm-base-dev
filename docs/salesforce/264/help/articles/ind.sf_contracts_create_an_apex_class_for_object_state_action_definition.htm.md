---
article_id: ind.sf_contracts_create_an_apex_class_for_object_state_action_definition.htm
title: Create an Apex Class for Object State Action Definition
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_an_apex_class_for_object_state_action_definition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_state_models_transitions_and_actions.htm
fetched_at: 2026-10-13
---

# Create an Apex Class for Object State Action Definition

Create an Apex Class for Object State Action Definition

Create an invocable Apex class in the Developer Console for each of the object state action definitions (custom actions).

Click the quick access menu (), then click Developer Console.
Select File | NewApex Class.
Enter a name and click OK.
Paste the sample code into the dialog box.
See Sample Apex Invocation Class for Object State Action Definition.
Save your changes.

See Also

Apex Developer Guide

Sample Apex Invocation Class for Object State Action Definition

Here are some sample apex classes for creating object state action definitions. Modify the sample code to suit your requirements

Method Signature includes these mandatory parameters:

PARAMETER	DESCRIPTION
Map < String, Object > inputMap	

Contains two keys:

contractId: The SObjectId

objectStateActionDefinition: A record for the called action.

actionData: An action-specific data that contains additional details from API or default actions of type Map <String, String>.


Map < String, Object > outMap	

outMap.put('isSuccess', true): The Apex actions fail if the isSuccess parameter wasn't returned, or the isSuccess parameter is returned as false.

outMap.put('finalStatusValue', '<abc>'): If multiple object state transitions with the same “From” state and a different “To” states are possible for the called action, the Apex class won’t change the “To” state of the contract. You must define the finalStatusValue.

Sample RestartContract Apex Class

Restart a terminated contract by using a custom action.

global class RestartContract implements industries_clm.OpenInterface { 
    public Boolean invokeMethod(String methodName, Map<String, Object> request, Map<String, Object> outMap) {
        Boolean success = true;
        if (methodName == 'executeAction') {
            makeCallout(request, outMap);
        }
        return success;
    }
    public static void makeCallout(Map < String, Object > inputMap, Map < String, Object > outMap) {
        String ContractId = (String) inputMap.get('contractId');
        List<Contract> contract = [SELECT Id, Name, Status FROM Contract WHERE Id =:contractId];
        contract[0].Status = 'Draft';
        update(contract); 
            outMap.put('isSuccess', true);
        }
    }
}

Sample ApprovalAction Apex Class

Implement additional logic that runs concurrently with the standard Salesforce approval process.

global class ApprovalAction implements industries_clm.OpenInterface { 
    public Boolean invokeMethod(String methodName, Map<String, Object> request, Map<String, Object> outMap) {
        Boolean success = true;
        if (methodName == 'executeAction') {
            executeAction(request, outMap);
        }
        return success;
    }
    private void executeAction(Map < String, Object > inputMap, Map < String, Object > outMap) {
		Approval.ProcessSubmitRequest req1 = 
            new Approval.ProcessSubmitRequest();
        req1.setComments('Submitting request for approval.');
        String contractId = (String) inputMap.get('contractId');
        req1.setObjectId(contractId);
        
        // Submit the record to specific process and skip the criteria evaluation
        req1.setProcessDefinitionNameOrId('ContractApprovalProcessName');
        req1.setSkipEntryCriteria(true);
        
        // Submit the approval request for the account
        Approval.ProcessResult result = Approval.process(req1);
        
              outMap.put('isSuccess', true);
    }
}

Sample EndContract Apex Class

For a called action, if multiple object state transitions are possible for a From state because multiple To states are available, Apex won’t change the state of the contract. For example, on an activated contract, there is a custom action called Endcontract that is configured to move the contract to two states: canceled and terminated. For the Apex call to succeed, the finalStatusValue parameter is required.

global class EndContract implements industries_clm.OpenInterface { 

    public Boolean invokeMethod(String methodName, Map<String, Object> request, Map<String, Object> outMap) {
        Boolean success = true;
        if (methodName == 'executeAction') {
            executeAction(request, outMap);
        }
        return success;
    }
    private void executeAction(Map < String, Object > inputMap, Map < String, Object > outMap) {   
		String contractId = (String) inputMap.get('contractId');
        
        outMap.put('isSuccess', true);
		outMap.put('finalStatusValue', 'Canceled');
    }
}
