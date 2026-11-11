---
article_id: ind.sf_contracts_use_custom_document_template_filtering.htm
title: Use Custom Document Template Filtering for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_use_custom_document_template_filtering.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-10-13
---

# Use Custom Document Template Filtering for Salesforce Contracts

Use Custom Document Template Filtering for Salesforce Contracts

Using custom logic, you can filter the templates you want to display for a contract. You can configure a filtering class for each contract type. Only the set of templates that match the custom logic displays in the templates dropdown under the generate action in the Documents tab of a contract.

Create an apex class that implements an open interface.
From the Setup menu, choose Developer Console.
From the Developer Console, click File | New | Apex Class.
Enter a name and click OK.
Paste the sample code into the dialog box. For more information, see Sample Apex Code for Document Template Filtering .
You can modify the sample code (template select logic) to suit your requirements
Add Document Template Filter Class by mapping the custom apex class with a contract type.
All active templates display in the Template dropdown if a custom logic is not applied or can't be applied.
From Setup, enter Contract Type Config in the Quick Find box.
Click Contract Type Config.
Click New.
Enter these details:

Contract Type: Select an option.

NOTE You can only map one type of config value (custom class name) for each contract type.

Config Type - Document Template Filter Class

Usage Type - Document Settings

Config Value - Select the custom apex class name that you previously added to filter the document templates.

Click Create.
Sample Apex Code for Salesforce Contracts Document Template Filtering

Enables you to choose a template to attach to a contract document in run-time. The template list varies based on the interface implementation. The sample implementation includes all active document templates that are applicable to the contract for the user to select.

PARAMETER	DESCRIPTION
Interface to implement	

OpenInterface

Gets a list of templates including active document templates that are applicable to a contract.


Input	

Request map includes these keys:

• isActive - true

• usageType - Contract_Lifecycle_Management

• type - {document type}

• contractId - {Id of the contract}


Output	Output list that contains the document list must be added to outMap with key documentTemplateList.
Method Signature
global class DocumentTemplateFilter implements industries_clm.OpenInterface {
    public Boolean invokeMethod(String methodName, Map<String, Object> request, Map<String, Object> outMap) {
        system.debug(request);
        List<DocumentTemplate> dTList = [SELECT Id, IsActive, Name, Type, VersionNumber from DocumentTemplate WHERE IsActive = true AND UsageType = 'Contract_Lifecycle_Management' AND Type = 'MicrosoftWord' LIMIT 2];
        system.debug(dTList);
        outMap.put('documentTemplateList', dtList);
        return true;
    }
}
