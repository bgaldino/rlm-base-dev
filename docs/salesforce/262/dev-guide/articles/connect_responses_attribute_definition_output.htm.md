---
page_id: connect_responses_attribute_definition_output.htm
title: Attribute Definition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_attribute_definition_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Attribute Definition

Output representation of the attribute definition.

JSON example
:   ```
    "attributes": [
         {
          "additionalFields": {
          "scope": "Order"
           },
          "attributeNameOverride": "AD Text",
          "code": "AD02",
          "dataType": "Text",
          "defaultValue": "AD Text DV",
          "description": "AD Text Desc",
          "displayType": "Text",
          "helpText": "AD Text DHT",
          "id": "0tjT1000000002bIAA",
          "isHidden": false,
          "isPriceImpacting": true,
          "isReadOnly": true,
          "isRequired": true,
          "label": "AD Text Label",
          "maximumCharacterCount": 20,
          "maximumValue": "100",
          "minimumCharacterCount": 1,
          "minimumValue": "50",
          "name": "AD Text",
          "sequence": 1,
          "status": "Active",
          "valueDescription": "AD Text VD"
         }
       ],
        "code": "AC001",
        "id": "0v3T1000000000BIAQ",
        "name": "build and make"
    }]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `additional​Fields` | Map<String, [Additional Fields Input](./connect_requests_product_catalog_additional_fields_input.htm.md "Input representation of the additional standard or custom fields to be included in the response.")> | Key-value pair of additional standard or custom fields to include in the response. | Small, 61.0 | 61.0 |
| `attribute​Name​Override` | String | Name to display for the attribute, which overrides the name on the attribute. For example, the Color attribute is overridden to display as Laptop Color. | Small, 60.0 | 60.0 |
| `code` | String | Unique code of the attribute definition. | Small, 60.0 | 60.0 |
| `dataType` | String | Data type of the attribute definition value. | Small, 60.0 | 60.0 |
| `default​Value` | String | Default value of the attribute. | Small, 60.0 | 60.0 |
| `description` | String | Description of the attribute. | Small, 60.0 | 60.0 |
| `display​Type` | String | Display types of the attribute. Valid values are:   - `Radio Button` - `Checkbox` - `Toggle` - `Input Date` - `DateTime` - `Currency Symbol` - `Currency Code` - `Currency Name` - `Percentage` - `Text` - `Combobox` - `Radio Button` - `MultiSelect` - `MultiSelectCheckboxes` | Small, 60.0 | 60.0 |
| `help​Text` | String | Help text that appears at run time for the attribute. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `id` | String | ID of the attribute definition. | Small, 60.0 | 60.0 |
| `is​Configurable` | Boolean | Reserved for future use. | Small, 60.0 | 60.0 |
| `is​Hidden` | Boolean | Indicates whether to hide the attribute from the users in the order capture interface (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isPrice​Impacting` | Boolean | Indicates whether the attribute impacts the product price (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isRead​Only` | Boolean | Indicates whether the product attribute is read-only for the end users in the order capture page (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `is​Required` | Boolean | Indicates whether a value for the attribute is required for the assigned parent object (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `is​Value​Cloneable` | Boolean | Reserved for future use. | Small, 60.0 | 60.0 |
| `label` | String | Label of the attribute. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `maximum​Character​Count` | Integer | Maximum number of alphanumeric characters that can be entered for attributes of type number and text in run time. | Small, 60.0 | 60.0 |
| `maximum​Value` | String | Maximum value that can be entered for attributes of type number, currency, and percent in run time. | Small, 60.0 | 60.0 |
| `minimum​Character​Count` | Integer | Minimum number of alphanumeric characters that can be entered for attributes of type number and text in run time. The minimum character count must be less than or equal to the maximum character count. | Small, 60.0 | 60.0 |
| `minimum​Value` | String | Minimum value that can be entered for attributes of type number, currency, and percent in run time. The minimum value must be less than or equal to the maximum value. | Small, 60.0 | 60.0 |
| `name` | String | Name of the attribute. | Small, 60.0 | 60.0 |
| `picklist` | [Attribute Picklist](./connect_responses_attribute_picklist_output.htm.md "Output representation of the attribute picklist.") | ID of the attribute picklist that provides the valid values for the attribute. | Small, 60.0 | 60.0 |
| `sequence` | Integer | Order in which the attribute values appear in the attribute definition when the product is configured at run time. | Small, 60.0 | 60.0 |
| `status` | String | Lifecycle state of the attribute picklist. Valid values are:   - `Active` - `Draft` - `Inactive` | Small, 60.0 | 60.0 |
| `step​Value` | String | Reserved for future use. | Small, 60.0 | 60.0 |
| `value​Decoder` | String | Reserved for future use. | Small, 60.0 | 60.0 |
| `value​Description` | String | Description of the value assigned to the attribute. | Small, 60.0 | 60.0 |
