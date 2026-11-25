---
page_id: connect-responses-update-nodes-configurator-output
title: Configurator Update Nodes
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-update-nodes-configurator-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-responses
legacy_page_id: connect_responses_update_nodes_configurator_output.htm
fetched_at: 2026-11-25
---

# Configurator Update Nodes

Output representation of the configuration request details to update nodes.

## JSON Example

```
{
  "configuratorMessages": {},
  "configuratorUITreatments": [
    {
      "details": {
        "attributeId": "0tjxx0000000007AAA",
        "prcId": "0dSxx0000000007EAA",
        "stiId": "0QLxx0000004CU0GAM",
        "attributePicklistValueId": "0v6xx0000000005AAA"
      },
      "uiTreatmentScope": "Bundle",
      "uiTreatmentTarget": "Attribute_Picklist_Value",
      "uiTreatmentType": "Hide"
    },
    {
      "details": {
        "stiId": "ref_f0f2da7b_c431_482d_bf4b_599052f3a2e1"
      },
      "uiTreatmentScope": "Product",
      "uiTreatmentTarget": "Component",
      "uiTreatmentType": "Disable"
    }
  ],
  "errors": [],
  "productQualifications": {
    "01tDU000000EOTCYA4": {
      "isQualified": true
    }
  },
  "success": true
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `configurator​Messages` | Map<String, [Configurator Message](./connect-responses-configurator-message-output.md)> | Map of the product IDs to the list of configurator messages. Configurator messages are results from any validations, Business Rules Engines (BRE) calls, or Salesforce Pricing calls. | Small, 60.0 | 60.0 |
| `configurator​UITreatments` | [Configurator UI Treatment](./connect-responses-configurator-u-i-treatment-output.md)[] | Details of the UI treatments that specify the product configuration rule actions to override the disable or hide behavior in the UI for product options, product attributes, and attribute picklist values. | Small, 62.0 | 62.0 |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | List of errors, which contains an error code and a message. | Small, 60.0 | 60.0 |
| `product​Qualifications` | Map<String, [Configurator Qualification Context](./connect-responses-configurator-qualification-context-output.md)> | Map of the product IDs to the qualification rule execution results. | Small, 60.0 | 60.0 |
| `success` | Boolean | Indicates whether the call was successful (`true`) not (`false`). | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-update-nodes-configurator-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
