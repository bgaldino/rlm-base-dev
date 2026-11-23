---
page_id: connect_requests_data_row_input.htm
title: Data Row Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_data_row_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-11-23
---

# Data Row Input

Input representation of the details of the input for a data rounding request.

**JSON Example**

```
JSON example
{
  "dataRowInputs": [
    {
      "key": "PRC1",
      "fieldDataInputs": [
        {
          "fieldApiName": "MaxQuantity",
          "originalValue": 1234.5678,
          "unitOfMeasureId": "0hExx0000000001EAA"
        },
        {
          "fieldApiName": "MinQuantity",
          "originalValue": "987462848934739347.32232590183756545",
          "unitOfMeasureId": "0hExx000000001dEAA"
        }
      ]
    },
    {
      "key": "PRC2",
      "fieldDataInputs": [
        {
          "fieldApiName": "MaxQuantity",
          "originalValue": 1234.5678,
          "unitOfMeasureId": "uomId1"
        },
        {
          "fieldApiName": "MinQuantity",
          "originalValue": 987.4628,
          "unitOfMeasureId": "Kgs Id"
        }
      ]
    },
    {
      "key": "PRC3",
      "fieldDataInputs": [
        {
          "fieldApiName": "MaxQuantity",
          "originalValue": 0.437584,
          "unitOfMeasureId": "uomId2"
        },
        {
          "fieldApiName": "MinQuantity",
          "originalValue": 7364.58923,
          "unitOfMeasureId": "uomId2"
        }
      ]
    }
  ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `fieldData​Inputs` | [Field Data Input](./connect_requests_field_data_input.htm.md "Input representation of the details of the field data input.")[] | List of field-level data inputs. | Required | 63.0 |
| `key` | String | Key that identifies a unique data row. | Required | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_data_row_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
