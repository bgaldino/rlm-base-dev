---
page_id: runtime_context_intance_management.htm
title: Context Service Runtime
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/runtime_context_intance_management.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_resources.htm
fetched_at: 2026-06-25
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
- **[Query Context Record (POST)](./connect_resources_query_context_record.htm.md)**  
  Query a context record, with the option to retrieve child records.
- **[Query Record Status (PATCH, POST)](./connect_resources_create_update_query_data_record_status.htm.md)**  
  Update the processing status and related error messages of query data records. Create the processing status and related error messages of query data records
- **[Query Tags (POST)](./connect_resources_create_query_tag.htm.md)**  
  Create query tags within a defined context
- **[Write Through Tags (PATCH)](./connect_resources_write_through_tags.htm.md)**  
  Update Context Attributes through tags.
