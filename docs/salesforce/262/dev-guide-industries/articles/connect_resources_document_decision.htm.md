---
page_id: connect_resources_document_decision.htm
title: Document Decision
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_document_decision.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_resources.htm
fetched_at: 2026-06-25
---

# Document Decision

Invoke a Decision Table, accept key-value pairs that match the Decision Table keys, and
return either Document Types or Document Categories and the Document Types associated with
them.

For example, one use case is applying for a driver's license. Based on questions about where the
applicant lives, a Decision Table can list the documents to be uploaded for proof of
identity.

The Decision Table must be active and have DocumentDecisionRequirement, a platform object, as its
Source Object. This platform object stores the Decision Table's inputs, outputs, and
business rules.

One of the Decision Table outputs must be DocumentReferenceObjectId, which references a
Document Type or Document Category object. An optional output is isUploadRequired, which
sets the default for the Document Categories property isRequired. These two outputs don’t
appear in the connect API’s outputs.

Resource
:   ```
    /connect/document-matrix/document-decision/decisionTableId
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "inputs": [
            {
              "Country": "USA",
              "State": "CA"
            }
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `inputs` | List<Map<String, Object>> | List of inputs passed to Decision Table. Each key is a Decision Table field name, and each value is valid for that field. | Required | 59.0 |

Response body for POST
:   [Document Decision Response](./connect_responses_document_decision_response.htm.md "Output representation of the Document Decision response, including Decision Table output.")
