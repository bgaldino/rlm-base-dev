---
page_id: connect_requests_resource_input.htm
title: Resource Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_resource_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Resource Input

Input representation of the expression set resource (variable or
      constant).

         

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

**JSON example**

: 

```
{
   "variables":{
      "details":[ {
         "apiName":"condition_output__1",
         "dataType":"Boolean",
         "defaultValue":"False",
         "id":"0kJxx00000000KzEAI",
         "isEditable":false,
         "isUserDefined":false,
         "name":"condition_output__1"
      } ]
   }
}
"constants":{
   "details":[ {
      "apiName":"SENIOR_CITIZEN_AGE",
      "dataType":"Number",
      "defaultValue":"60",
      "isEditable":true,
      "isUserDefined":true,
      "name":"SENIOR_CITIZEN_AGE",
      "precision":2
   }.]
}
```

**Properties**

: 

- 
- 
- 
- 
- 
- 

#### 

#### 

#### 

#### 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `apiName` | String | The API name of the variable or constant. | Required | 53.0 |
| `calculationMatrixName` | String | The name of the decision matrix used in the variable or constant. | Optional | 53.0 |
| `dataType` | String | The date type of the variable or constant.Possible values are: `Boolean` `Currency` `Date` `Number` `Percent` `Text` | Required | 53.0 |
| `defaultValue` | String | The default value of the variable or constant. | Optional | 53.0 |
| `displayName` | String | The display name of the variable or constant that appears in the user interface. | Optional | 53.0 |
| `id` | String | The ID of the variable or constant. | Required Note This field is required for the update request. | 53.0 |
| `isEditable` | Boolean | Indicates whether the variable or constant is editable. Note This field is for user-interface use only. | Optional | 53.0 |
| `isUserDefined` | Boolean | Indicates whether the variable or constant is user-defined. | Optional | 53.0 |
| `name` | String | The name of the variable or constant. | Required | 53.0 |
| `precision` | Integer | The floating-point precision of the variable or constant. | Required Note This field is required when the data type is `number`, `currency`, or `percentage`. | 53.0 |
| `uiDisplayOrder` | Integer | The display order of the variable or constant in the UI. Note Reserved for future use. | Optional | 53.0 |
