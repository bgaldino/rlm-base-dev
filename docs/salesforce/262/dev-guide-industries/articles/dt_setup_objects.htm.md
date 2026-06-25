---
page_id: dt_setup_objects.htm
title: Decision Table Tooling API Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/dt_setup_objects.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_parent.htm
fetched_at: 2026-06-25
---

# Decision Table Tooling API Objects

Use Tooling API objects to create, update, and activate decision tables. Dataset links
can also be created and associated with decision tables using Tooling API objects.

|  |
| --- |
| Available in: Lightning Experience |
| Available in: Decision Table is available with Enterprise, Unlimited, and Performance Editions with Loyalty Management or Rebate Management |

- **[Decision Table Data Model](./decision_table_data_model.htm.md)**  
  Before you start using the Decision Table Tooling API objects, here's a representation of the data model.
- **[DecisionTable](./tooling_api_objects_decisiontable.htm.md)**  
  Represents the information about a decision table. This object is available in API version 51.0 and later.
- **[DecisionTableDatasetLink](./tooling_api_objects_decisiontabledatasetlink.htm.md)**  
  Represents a dataset link associated with a decision table. Use dataset links in a decision table to select an object whose records the decision table must evaluate and provide outcomes for. This object is available in API version 51.0 and later.
- **[DecisionTableParameter](./tooling_api_objects_decisiontableparameter.htm.md)**  
  Represents an input or output field in a decision table. An input field is a field in the business rule object or custom metadata type that contains values used by the decision table to evaluate records and values. An output field is a field in the business rule object or custom metadata type that contains the values provided as outcomes for a rule. This object is available in API version 51.0 and later.
- **[DecisionTblDatasetParameter](./tooling_api_objects_decisiontbldatasetparameter.htm.md)**  
  Represents the mapping between a decision table parameter and a field of the object selected in the dataset link. This mapping allows the decision table to know which object fields from the dataset link must be evaluated by the input fields of the decision table. This object is available in API version 51.0 and later.
- **[DecisionTableSourceCriteria](./tooling_api_objects_decisiontablesourcecriteria.htm.md)**  
  Represents the fields and values from a data source that are used to define the condition logic of the data that's used in a decision table. This object is available in API version 59.0 and later.
