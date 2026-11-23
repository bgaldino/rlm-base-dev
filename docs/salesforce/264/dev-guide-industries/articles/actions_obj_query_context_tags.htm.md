---
page_id: actions_obj_query_context_tags.htm
title: Query Context Tags Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_query_context_tags.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Query Context Tags Action

Query the tag values from an instance that are associated with a context
definition.

This action is available in API version 63.0 and later.

## Special Access Rules

Available in Developer, Enterprise, Professional, and Unlimited editions for
Industries clouds where Context Service is enabled.

## Supported REST HTTP Methods

**URI:**
`/services/data/vXX.X/actions/standard/queryContextTags`

Where `XX.X` is the latest API version.

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:**
`Authorization: Bearer TOKEN`

Where `TOKEN` is a variable.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| contextId | string | Required. The ID of the context instance. |
| tagsList | string | Required. A collection of tags to be queried. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| queryResult | string | The output of the queried context instance. |

## Example

POST
:   This sample request is for the Query Context Tags action.

    ```
    {
      "inputs": [
        {
          "contextId": "0000000a07da09100251752497651022c35b6150a4d04cd6a84bf1a0439cc609",
          "tagList": [
            "Account_Name",
            "Contact_LastName"
          ]
        }
      ]
    }
    ```
:   This sample response is for the Query Context Tags action.

    ```
    {
      "actionName": "queryContextTags",
      "errors": null,
      "invocationId": null,
      "isSuccess": true,
      "outputValues": {
        "queryResult": {
          "Contact_LastName": [
            {
              "tagValue": "Miller",
              "dataPath": [
                "0000000a07da09100251752497651022c35b6150a4d04cd6a84bf1a0439cc609",
                "account1",
                "contact1"
              ],
              "eTag": "fba12e2955bf4a46354fee73ee8b238c",
              "weakEtag": 0
            }
          ],
          "Account_Name": [
            {
              "tagValue": "AcmeFlow",
              "dataPath": [
                "0000000a07da09100251752497651022c35b6150a4d04cd6a84bf1a0439cc609",
                "account1"
              ],
              "eTag": "fa0867f98939f191957687c1456715f7",
              "weakEtag": 0
            }
          ]
        }
      },
      "sortOrder": -1,
      "version": 1
    }
    ```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_query_context_tags.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
