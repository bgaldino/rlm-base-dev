---
page_id: deployment_considerations.htm
title: Deployment Considerations
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_considerations.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_overview.htm
fetched_at: 2026-06-09
---

# Deployment Considerations

In any deployment scenario, you must understand all dependencies and prerequisites
related to your planned changes.

Here's a list of things to consider and plan for.

Key considerations include:

- What’s the sequence followed for object deployment? What dependencies exist on related
  objects?
- Do your objects have Draft, Active, or Inactive states?
- Does activation occur through an API or by simply setting a boolean field (active
  flag)?
- Are there special fields to consider, such as text fields with embedded IDs, JSON, or
  fields populated via triggers?
- Are there fields or objects that represent unique or sequential data that must be
  preserved in the target org?
- How would you handle system settings between the orgs? For example, making sure that a
  feature toggle is turned off in the target org so that automation doesn't start executing
  when you insert data from your source org.
- What's the impact of versioning on your deployment? For example, schema, app, or API
  versions.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

For detailed information about these deployment considerations, see [Additional Deployment Information](./deployment_appendix_C.htm.md "Get to know additional deployment information for each Revenue Cloud feature domain, ensuring successful deployments and migrations.").
