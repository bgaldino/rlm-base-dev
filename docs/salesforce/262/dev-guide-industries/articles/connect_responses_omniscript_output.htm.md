---
page_id: connect_responses_omniscript_output.htm
title: Omniscript Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_omniscript_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_responses.htm
fetched_at: 2026-06-25
---

# Omniscript Output

Output representation of the details of the Omniscript.

JSON example
:   ```
    {
      "DiscoveryFrameworkUsageType": "Default",
      "DesignerCustomizationType": "Discovery Framework",
      "VersionNumber": 1,
      "Type": "DiscoveryFramework",
      "Language": "English",
      "IsActive": false,
      "Description": null,
      "Name": "Dispute",
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
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `additionalAttributes` | [additionalAttributes Output](./connect_responses_additional_attributes.htm.md "Output representation of the Additional Attributes.")[] | Additional attributes of the Omniscript. | Small, 63.0 | 63.0 |
| `description` | String | Description of the Omniscript. | Small, 60.0 | 60.0 |
| `designer​Customization​Type` | String | Custom type of the Omniscript. | Small, 60.0 | 60.0 |
| `discovery​FrameworkUsage​Type` | String | Usage type of the Omniscript. | Small, 60.0 | 60.0 |
| `elements` | [Omniscript Elements List](./connect_responses_omniscript_elements_list.htm.md "Output representation of the details of the Omniscript elements.")[] | Element node of the Omniscript. | Small, 60.0 | 60.0 |
| `isActive` | Boolean | Indicates if the Omniscript assessment is active `(true)` or not `(false)`. | Small, 60.0 | 60.0 |
| `language` | String | Language of the Omniscript. | Small, 60.0 | 60.0 |
| `lastModifiedDate` | String | Date when the Omniscript was modified. | Small, 60.0 | 60.0 |
| `name` | String | Name of the Omniscript. | Small, 60.0 | 60.0 |
| `omniprocessId` | String | ID of the Omniscript associated with the assessment record. | Small, 60.0 | 60.0 |
| `subType` | String | Subtype of the Omniscript. | Small, 60.0 | 60.0 |
| `type` | String | Type of the Omniscript. | Small, 60.0 | 60.0 |
| `version​Number` | String | Version of the Omniscript. | Small, 60.0 | 60.0 |
| `uniqueName` | String | Unique name for the Omniscript. | Small, 60.0 | 60.0 |
