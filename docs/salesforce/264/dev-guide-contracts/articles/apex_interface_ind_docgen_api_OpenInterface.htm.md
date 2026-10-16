---
page_id: apex_interface_ind_docgen_api_OpenInterface.htm
title: OpenInterface Interface
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/apex_interface_ind_docgen_api_OpenInterface.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: apex_namespace_ind_docgen_api.htm
fetched_at: 2026-10-13
---

# OpenInterface Interface

  
The `OpenInterface` provides user the capability
    to provide custom logic for task permitted by Salesforce.

## Namespace

[ind_docgen_api](./apex_namespace_ind_docgen_api.htm.md)

- 
**[OpenInterface Methods](./apex_interface_ind_docgen_api_OpenInterface.htm.md#apex_ind_docgen_api_OpenInterface_methods)**  

- 
**[OpenInterface Example Implementation](./apex_interface_ind_docgen_api_OpenInterface.htm.md#apex_interface_ind_docgen_api_OpenInterface_Example)**  

## OpenInterface Methods

The following are methods for `OpenInterface`.

- 
**[invokeMethod(var1, var2, var3)](./apex_interface_ind_docgen_api_OpenInterface.htm.md#apex_ind_docgen_api_OpenInterface_invokeMethod)**  

Invokes method based on the use-case.

  

### invokeMethod(var1, var2, var3)

  
  
  
Invokes method based on the use-case.

    

#### Signature

      
      

`public Boolean invokeMethod(String var1, Map<String,ANY> var2, Map<String,ANY> var3)`

      
    

    

#### Parameters

      
      

**var1**

      

Type: String

      

Contains the name of the method that is supposed to be implemented from invoke method.

      

**var2**

      

Type: Map<String,ANY>

      

Contains the inputs as per the use-case.

      

**var3**

      

Type: Map<String,ANY>

      

Returns the output as per the use-case.

    

    

#### Return Value

      
      

Type: Boolean

      

true or false

    

  

## OpenInterface Example Implementation

    
      

This is an example implementation of the `ind_docgen_api.OpenInterface` interface.

      

```
global class TestTF implements ind_docgen_api.OpenInterface {
public Boolean invokeMethod(String methodName, Map<String, Object> request, Map<String, Object> outMap) {
Boolean success = true;
if (methodName == 'getDocumentTemplateList') {
getTemplateList(request, outMap);
}
return success;
} 
 
private void getTemplateList(Map < String, Object > inputMap, Map < String, Object > outMap) {
String contractId = (String) inputMap.get('contractId');
String usageType = (String) inputMap.get('usageType');
String billingCountry;
List<Contract> contractList = [SELECT BillingCountry, Id FROM Contract where Id = :contractId];
if(!contractList.isEmpty()) {
Contract contract = contractList.get(0);
billingCountry = contract.BillingCountry != null ? contract.BillingCountry : '';
}
List<DocumentTemplate> templist;
String objName = 'DocumentTemplate';
try {
if(billingCountry.equalsIgnoreCase('India')) {
templist = [select id, isActive, name, type, versionNumber from DocumentTemplate where IsActive=true and Type = 'MicrosoftWord' and Name like '%APAC%'
order by Name];
} else {
templist = [select id, isActive, name, type, versionNumber from DocumentTemplate where IsActive=true and Type = 'MicrosoftWord' order by Name];
}
} catch (Exception e) {
throw e;
}
if (tempList != null && tempList.size() > 0) {
outMap.put('documentTemplateList', tempList);
}
}
}
```
