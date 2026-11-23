---
page_id: product_discovery_flow_metadata_api.htm
title: Flow for Product Discovery
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_discovery_flow_metadata_api.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_metadata_api_parent.htm
fetched_at: 2026-11-23
---

# Flow for Product Discovery

Represents the metadata associated with a flow. With Flow, you can create an application that takes users through a series of pages to query and update the records in the database. You can also run logic and provide branching capability based on user input to build dynamic applications.

## FlowActionCall

Product Discovery exposes additional actionType values for the FlowActionCall metadata type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values for Product Discovery are `findProducts`—Search for the products from a catalog, category, or subcategory by using the specified search term, `GetProducts`—Get products from the specified catalog, category, or subcategory, including product qualification and pricing details, `GetProductDetails`—Get details such as attributes, hierarchy, and cardinality for the specified product, `executeQualificationProcedure`—Execute a qualification procedure, which returns the qualification status for the specified products, `getCatalogDetails`—Get details of a catalog record, `getCatalogs`—Get a list of catalog records, `getCategories`—Get the list of categories associated with a catalog record, `getCategoryDetails`—Get details of a category record, `getMultipleProductDetails`—Get product details for a list of products, `searchPrdctWithGuidedSelection`—Use guided product selection to search for products, or `getRecommendedProducts`—Retrieve a list of recommended products for a quote or order by using the Constraint Rule Engine. |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_discovery_flow_metadata_api.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
