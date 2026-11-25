---
page_id: connect-responses-attribute-picklist-value-output
title: Attribute Picklist Value
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-attribute-picklist-value-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_attribute_picklist_value_output.htm
fetched_at: 2026-11-25
---

# Attribute Picklist Value

Output representation of the attribute picklist value.

## JSON Example

```
"values": [
      {
        "abbreviation": "IFM1"
        "code": "PV0051",
        "displayValue": "25G Intelligent Fabric Module with 8x 25G SFP28 ports",
        "id": "0v61Q0000008OMYQA2",
        "name": "25G Intelligent Fabric Module with 8x 25G SFP28 ports",
        "sequence": "1",
        "value": "25G Intelligent Fabric Module with 8x 25G SFP28 ports",
        "status" : "Active"
      }
     ]
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `abbreviation` | String | Name of the picklist value that appears at run time. | Small, 60.0 | 60.0 |
| `code` | String | Unique code of the picklist value within the picklist. | Small, 60.0 | 60.0 |
| `display​Value` | String | Picklist value that appears at run time in the order capture page. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `id` | String | ID associated with the attribute picklist value. | Small, 60.0 | 60.0 |
| `name` | String | Name of the picklist value. | Small, 60.0 | 60.0 |
| `sequence` | String | Order in which the picklist value appears in the picklist. | Small, 60.0 | 60.0 |
| `status` | String | Status of the attribute picklist value. | Small, 62.0 | 62.0 |
| `value` | String | Value of the picklist item. Value must be unique within the picklist. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-attribute-picklist-value-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
