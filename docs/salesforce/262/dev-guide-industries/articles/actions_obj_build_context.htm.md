---
page_id: actions_obj_build_context.htm
title: Build Context Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_build_context.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_invocable_actions_parent.htm
fetched_at: 2026-06-25
---

# Build Context Action

Build and cache context data associated with a context definition.

This action is available in API version 59.0 and later.

## Special Access Rules

Available in Developer, Enterprise, Professional, and Unlimited editions for
Industries clouds where Context Service is enabled.

## Supported REST HTTP Methods

URI
:   `/services/data/v`59.0`/actions/standard/buildContext`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization:
    Bearertoken`

## Inputs

| Input | Details |
| --- | --- |
| contextData | Type  string  Description  Optional. JSON data that's used to build context data. |
| contextDefinitionId | Type  string  Description  Required. The ID or developer name of the context definition record that's used to build context data. |
| contextMappingId | Type  string  Description  Optional. The context mapping record ID or name that identifies which Salesforce object and mappings to use for building context data. |
| isTaggedData | Type  boolean  Description  Optional. Indicates whether the associated context node is tagged with a key (`true`) or not (`false`). |

## Outputs

| Output | Details |
| --- | --- |
| contextDefinitionId | Type  string  Description  The ID or Developer Name of the Context Definition record that was used to build context data. |
| contextId | Type  string  Description  ID of the cached context data. |
| contextMappingId | Type  string  Description  The Context Mapping record ID or Name that identifies which Salesforce object and mappings to use for building context data. |

## Usage

Build context invocable action is a wrapper over Build Context
business API. The API fetches the data passed in request and saves the data to the
cache. This is useful when the same data is required in multiple steps of the
process.

## Example

POST
:   This sample request is for the Build Context action. In this example, we
    are inserting new records to hydrate input values (input hydration). To
    use existing records instead, reference the IDs directly rather than
    providing full record data.

    ```
    {
      "inputs": [
        {
          "contextDefinitionId": "AccountContextDef",
          "ContextData": {
            "Account": [
              {
                "id": "account1",
                "businessObjectType": "Account",
                "Name": "AcmeFlow",
                "Contact": [
                  {
                    "id": "contact1",
                    "businessObjectType": "Contact",
                    "FirstName": "John",
                    "LastName": "Miller",
                    "ParentReference": "account1"
                  }
                ]
              }
            ]
          },
        "contextMappingId": "accountmap1",
        "isTaggedData": false
        }
      ]
    }
    ```
:   This sample response is for the Build Context action.

    ```
    {
      "actionName": "buildContext",
      "errors": null,
      "invocationId": null,
      "isSuccess": true,
      "outputValues": {
        "contextDefinitionId": "11Oxx0000006PXVEA2",
        "contextId": "0000000a07da091002517526756248297be68492e6b442e8ad80182d518e45aa",
        "contextMappingId": "11jxx0000004L59AAE"
      },
      "sortOrder": -1,
      "version": 1
    }
    ```
