---
page_id: connect-responses-os-element-property-set-output
title: Omniscript Element Property Set Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-os-element-property-set-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-responses
legacy_page_id: connect_responses_os_element_property_set_output.htm
fetched_at: 2026-11-25
---

# Omniscript Element Property Set Output

Output representation of the property set configuration of the Omniscript elements.

## JSON Example

```
     "PropertySetConfig": {
            "label": "Can you provide more details about the transaction",
            "defaultValue": null,
            "help": false,
            "helpText": "",
            "show": null,
            "conditionType": "Hide if False"
          }
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `checkLabel` | String | Label of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `conditionType` | String | Condition type of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `dataType` | String | Data type of the formula for the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `dateFormat` | String | Date format of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `expression` | String | Formula expression of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `help` | String | Help details of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `helpText` | String | Help text of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `label` | String | Label of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `options` | List<Map<String, Object>> | Options of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `radioLabels` | List<Map<String, Object>> | Radio labels of the Omniscript element from the property set configuration for the radio group child questions. | Small, 60.0 | 60.0 |
| `required` | String | Specifies whether the Omniscript element is required to submit the form. | Small, 60.0 | 60.0 |
| `show` | Map<String, Object> | Display field details for the conditional rendering of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `text` | String | Text of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |
| `type` | String | Type of the Omniscript element from the property set configuration. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-os-element-property-set-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
