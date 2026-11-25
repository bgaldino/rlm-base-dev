---
page_id: connect-responses-omniscript-elements-list
title: Omniscript Elements List
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-omniscript-elements-list.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: dfdt-apis-responses
legacy_page_id: connect_responses_omniscript_elements_list.htm
fetched_at: 2026-11-25
---

# Omniscript Elements List

Output representation of the details of the Omniscript elements.

## JSON Example

```
  "elements": [
    {
      "DiscoveryFrameworkUsageType": "Default",
      "DesignerCustomizationType": "Discovery Framework",
      "Type": "Step",
      "PropertySetConfig": {
        "label": "Card Details",
        "show": null,
        "conditionType": "Hide if False"
      },
      "ParentElementType": null,
      "ParentElementName": null,
      "SequenceNumber": 0,
      "OmniProcessVersionNumber": 1,
      "Level": 0,
      "Description": null,
      "Name": "Step1",
      "elements": [
        {
          "DiscoveryFrameworkUsageType": "Default",
          "DesignerCustomizationType": "Discovery Framework",
          "Type": "Radio",
          "PropertySetConfig": {
            "label": "Was the card in your possession at the time of the disputed transactions?",
            "defaultValue": null,
            "help": false,
            "helpText": "",
            "options": [
              {
                "name": "Yes",
                "developerName": "Yes",
                "value": "Yes",
                "setAll": false
              },
              {
                "name": "No",
                "developerName": "No",
                "value": "No",
                "setAll": false
              }
            ],
            "show": null,
            "conditionType": "Hide if False"
          },
          "ParentElementType": "Step",
          "ParentElementName": "Step1",
          "SequenceNumber": 0,
          "OmniProcessVersionNumber": 1,
          "Level": 1,
          "Description": null,
          "Name": "FSC_DM_v1_CardRelatedQ1",
          "elements": [],
          "customTypeDetails" : {
            "discoveryFramework": {
                "questionText": "Was the card in your possession at the time of the disputed transactions?"
            }
          }
        },
        {
          "DiscoveryFrameworkUsageType": "Default",
          "DesignerCustomizationType": "Discovery Framework",
          "Type": "Radio",
          "PropertySetConfig": {
            "label": "Was the card lost or stolen at the time of the disputed transactions?",
            "defaultValue": null,
            "help": false,
            "helpText": "",
            "options": [
              {
                "name": "Yes",
                "developerName": "Yes",
                "value": "Yes",
                "setAll": false
              },
              {
                "name": "No",
                "developerName": "No",
                "value": "No",
                "setAll": false
              }
            ],
            "show": {
              "group": {
                "operator": "AND",
                "rules": [
                  {
                    "data": "Yes",
                    "condition": "=",
                    "field": "FSC_DM_v1_CardRelatedQ1"
                  }
                ]
              }
            },
            "conditionType": "Hide if False"
          },
          "ParentElementType": "Step",
          "ParentElementName": "Step1",
          "SequenceNumber": 1,
          "OmniProcessVersionNumber": 1,
          "Level": 1,
          "Description": null,
          "Name": "FSC_DM_v1_CardRelatedQ2",
          "elements": [],
          "customTypeDetails" : {
            "discoveryFramework": {
                "questionText": "Was the card lost or stolen at the time of the disputed transactions?"
            }
          }
        },
        {
          "DiscoveryFrameworkUsageType": "Default",
          "DesignerCustomizationType": "Discovery Framework",
          "Type": "Radio",
          "PropertySetConfig": {
            "label": "Did you provide your card details on any unfamiliar or suspicious websites?",
            "defaultValue": null,
            "help": false,
            "helpText": "",
            "options": [
              {
                "name": "Yes",
                "developerName": "Yes",
                "value": "Yes",
                "setAll": false
              },
              {
                "name": "No",
                "developerName": "No",
                "value": "No",
                "setAll": false
              }
            ],
            "show": null,
            "conditionType": "Hide if False"
          },
          "ParentElementType": "Step",
          "ParentElementName": "Step1",
          "SequenceNumber": 2,
          "OmniProcessVersionNumber": 1,
          "Level": 1,
          "Description": null,
          "Name": "FSC_DM_v1_FraudRelatedQ4",
          "elements": [],
          "customTypeDetails" : {
            "discoveryFramework": {
                "questionText": "Did you provide your card details on any unfamiliar or suspicious websites?"
            }
          }
        }
      ]
    },
    {
      "DiscoveryFrameworkUsageType": "Default",
      "DesignerCustomizationType": "Discovery Framework",
      "Type": "Step",
      "PropertySetConfig": {
        "label": "Additional Details",
        "show": null,
        "conditionType": "Hide if False"
      },
      "ParentElementType": null,
      "ParentElementName": null,
      "SequenceNumber": 2,
      "OmniProcessVersionNumber": 1,
      "Level": 0,
      "Description": null,
      "Name": "Step2",
      "elements": [
        {
          "DiscoveryFrameworkUsageType": "Default",
          "DesignerCustomizationType": "Discovery Framework",
          "Type": "Text Area",
          "PropertySetConfig": {
            "label": "Can you provide more details about the transaction",
            "defaultValue": null,
            "help": false,
            "helpText": "",
            "show": null,
            "conditionType": "Hide if False"
          },
          "ParentElementType": "Step",
          "ParentElementName": "Step2",
          "SequenceNumber": 2,
          "OmniProcessVersionNumber": 1,
          "Level": 1,
          "Description": null,
          "Name": "FSC_DM_v1_AdditionalQ2",
          "elements": [],
          "customTypeDetails" : {
            "discoveryFramework": {
                "questionText": "Can you provide more details about the transaction"
            }
          }
        }
      ]
    }
  ]
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `custom​Type​Details` | [Custom Type Details](./connect-responses-custom-type-details.md)[] | Custom type details for the Omniscript element. | Small, 60.0 | 60.0 |
| `description` | String | Description of the Omniscript element. | Small, 60.0 | 60.0 |
| `designer​Customization​Type` | String | The customization type of the Omniscript element. | Small, 60.0 | 60.0 |
| `discovery​Framework​UsageType` | String | Discovery framework usage type of the Omniscript element. | Small, 60.0 | 60.0 |
| `elements` | [Omniscript Elements List](./connect-responses-omniscript-elements-list.md)[] | Elements within the Omniscript element. | Small, 60.0 | 60.0 |
| `level` | String | Level of the Omniscript element. | Small, 60.0 | 60.0 |
| `name` | String | Name of the Omniscript element. | Small, 60.0 | 60.0 |
| `omniProcess​Version​Number` | String | OmniProcess version number of the Omniscript element. | Small, 60.0 | 60.0 |
| `parent​Element​Name` | String | Parent element name of the Omniscript element. | Small, 60.0 | 60.0 |
| `parent​Element​Type` | String | Parent element type of the Omniscript element. | Small, 60.0 | 60.0 |
| `property​Set​Config` | [OS Element Property Set](./connect-responses-os-element-property-set-output.md)[] | Property set configuration of the Omniscript element. | Small, 60.0 | 60.0 |
| `sequence​Number` | String | Sequence number of the Omniscript element. | Small, 60.0 | 60.0 |
| `type` | String | Type of the Omniscript element. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-omniscript-elements-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
