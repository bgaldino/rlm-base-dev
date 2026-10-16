---
page_id: deployment_global_UID_setup.htm
title: Global Unique ID Setup
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_global_UID_setup.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Global Unique ID Setup

The establishment of a Global Unique ID (GUID) column on all objects during day-one
    initialization is a recommended practice for Salesforce DevOps.

    

Salesforce uses its own internal ID for records, but this ID isn't portable. The same record
      in a testing, sandbox, or production org has different Salesforce IDs. This makes tracking a
      single piece of data across environments nearly impossible. By introducing your own custom,
      externally set GUID, you have a single, immutable, and universally consistent identifier.

    

#### Note

You can also choose your preferred method to maintain the mapping of records IDs across
      orgs.

    

Before performing any deployment work, establish your GUID across all database objects, and
      across all Salesforce orgs involved in your deployment plan.

    

#### Note

Add a GUID field to all objects used during your deployment. Since you can't add fields to
      metadata types (such as a Flow), use the API name for each metadata type as the unique
      identifier.

  

- 
**[Create a GUID Field](./deployment_create_guid_field.htm.md)**  

Add a GUID field to all objects used during your deployment to ensure unique   identification of records across environments.

- 
**[GUID Design and Usage](./deployment_guid_design_concept.htm.md)**  

The format and values of the Global Unique ID (GUID) are up to you. Here's some     guidance on what makes a good versus poor GUID for deployment tracking.
