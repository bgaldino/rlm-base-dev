---
page_id: runtime_context_intance_management.htm
title: Context Service Runtime
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/runtime_context_intance_management.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_resources.htm
fetched_at: 2026-11-23
---

# Context Service Runtime

Create new runtime context instances, query data from context instances, and delete
context instances.

- **[Context Service (POST)](./connect_resources_create_context.htm.md)**  
  Create new context records by submitting metadata and associated JSON data. After validating the data, the system generates a new context ID. Context objects created using this API apply only to a single request. They cannot be used to pass data across multiple requests.
- **[Context Service (DELETE, GET)](./connect_resources_context_service_runtime.htm.md)**  
  Retrieve the context details using a context ID. Delete a context record using a context ID.
- **[Context Attribute (PATCH)](./connect_resources_update_context_attribute.htm.md)**  
  Update attributes of a context record.
- **[Context Runtime Schema (DELETE)](./connect_resources_context_runtime_schema.htm.md)**  
  Clear runtime schema cache for context definitions and their associated mappings.
- **[Query Context Definition Interfaces (GET)](./connect_resources_query_context_interfaces.htm.md)**  
  Get the lists of metadata associated with context definition interfaces.
- **[Query Context Definition Interface By Name (GET)](./connect_resources_query_context_interface_by_name.htm.md)**  
  Get the details of a context definition interface by using the context definition interface name.
- **[Query Context Records and Children (POST)](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_query_context_records.htm)**  
  Query context records and their child records by data path.
- **[Query Record Status (PATCH, POST)](./connect_resources_create_update_query_data_record_status.htm.md)**  
  Update the processing status and related error messages of query data records. Create the processing status and related error messages of query data records
- **[Query Tags (POST)](./connect_resources_create_query_tag.htm.md)**  
  Create query tags within a defined context
- **[Write Through Tags (PATCH)](./connect_resources_write_through_tags.htm.md)**  
  Update Context Attributes through tags.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/runtime_context_intance_management.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
