---
page_id: connect_responses_omniscript_elements_list.htm
title: Omniscript Elements List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_omniscript_elements_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_responses.htm
fetched_at: 2026-06-25
---

# Omniscript Elements List

Output representation of the details of the Omniscript elements.

JSON example
:   ```
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

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `custom​Type​Details` | [Custom Type Details](./connect_responses_custom_type_details.htm.md "Output representation of the custom type details of the Omniscript elements.")[] | Custom type details for the Omniscript element. | Small, 60.0 | 60.0 |
| `description` | String | Description of the Omniscript element. | Small, 60.0 | 60.0 |
| `designer​Customization​Type` | String | The customization type of the Omniscript element. | Small, 60.0 | 60.0 |
| `discovery​Framework​UsageType` | String | Discovery framework usage type of the Omniscript element. | Small, 60.0 | 60.0 |
| `elements` | [Omniscript Elements List](# "Output representation of the details of the Omniscript elements.")[] | Elements within the Omniscript element. | Small, 60.0 | 60.0 |
| `level` | String | Level of the Omniscript element. | Small, 60.0 | 60.0 |
| `name` | String | Name of the Omniscript element. | Small, 60.0 | 60.0 |
| `omniProcess​Version​Number` | String | OmniProcess version number of the Omniscript element. | Small, 60.0 | 60.0 |
| `parent​Element​Name` | String | Parent element name of the Omniscript element. | Small, 60.0 | 60.0 |
| `parent​Element​Type` | String | Parent element type of the Omniscript element. | Small, 60.0 | 60.0 |
| `property​Set​Config` | [OS Element Property Set](./connect_responses_os_element_property_set_output.htm.md "Output representation of the property set configuration of the Omniscript elements.")[] | Property set configuration of the Omniscript element. | Small, 60.0 | 60.0 |
| `sequence​Number` | String | Sequence number of the Omniscript element. | Small, 60.0 | 60.0 |
| `type` | String | Type of the Omniscript element. | Small, 60.0 | 60.0 |
