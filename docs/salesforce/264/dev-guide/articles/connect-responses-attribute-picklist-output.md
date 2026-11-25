---
page_id: connect-responses-attribute-picklist-output
title: Attribute Picklist
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-attribute-picklist-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_attribute_picklist_output.htm
fetched_at: 2026-11-25
---

# Attribute Picklist

Output representation of the attribute picklist.

## JSON Example

```
"picklist": {
     "dataType": "Text",
     "description": "Fabric Module options",
     "id": "0v51Q000000TNDkQAO",
     "name": "Fabric Module options",
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
      },
      {
        "abbreviation": "IFM2"
        "code": "PV0052",
        "displayValue": "100G Intelligent Fabric Module with 8x 100G QSFP28 ports",
        "id": "0v61Q0000008OMZQA2",
        "name": "100G Intelligent Fabric Module with 8x 100G QSFP28 ports",
        "sequence": "2",
        "value": "100G Intelligent Fabric Module with 8x 100G QSFP28 ports",
        "status" : "Active"
      }
     ]
  }
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataType` | String | Data type of the values in the picklist. Valid values are `Boolean`, `Date`, `Datetime`, `Number`, `Text`, `Currency`, or `Percent`. | Small, 60.0 | 60.0 |
| `description` | String | Description of the picklist, such as the picklist purpose or the associated product. | Small, 60.0 | 60.0 |
| `id` | String | ID associated with the attribute picklist record. | Small, 60.0 | 60.0 |
| `name` | String | Name of the picklist value. | Small, 60.0 | 60.0 |
| `values` | [Attribute Picklist Value](./connect-responses-attribute-picklist-value-output.md)[] | List of values associated with the picklist. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-attribute-picklist-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
