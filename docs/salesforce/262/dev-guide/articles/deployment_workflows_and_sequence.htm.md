---
page_id: deployment_workflows_and_sequence.htm
title: Deployment Workflows and Sequence
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_workflows_and_sequence.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_overview.htm
fetched_at: 2026-06-09
---

# Deployment Workflows and Sequence

A typical dev ops cycle involves managing test orgs, sandboxes, and a production org.
Your deployment workflow can be a simple deployment of all setup and data from a development org
to production. Or, it can be much more complex, involving multiple staging and testing orgs
before any changes are sent to production.

Here's a diagram illustrating several potential deployment plans.

![Illustration for potential deployment plans](/docs/resources/img/en-us/262.0?doc_id=dev_guides%2Frev_lifecycle_mgmt%2Fdeployment_guide%2Fimages%2Fdeployment_workflows.png&folder=revenue_lifecycle_management_dev_guide)

## Full vs. Incremental Deployment

Deployments take two primary forms: full and incremental.

A full deployment involves migrating the entire set of relevant metadata such as objects,
fields, classes, triggers, and potentially a significant volume of data from a source org.
This ensures that the target org is a complete, synchronized replica of the source at that
point in time.

Full deployments are best suited for initial setup, major releases, or when deploying to a
completely new, or non-synced environment, such as the first deployment to a sandbox or
staging org.

Incremental deployments are used for ongoing DevOps activities. They focus only on the
specific metadata components and associated data records that have been created, modified,
or deleted since the last successful deployment.

This incremental approach is faster, reduces deployment risk by minimizing the scope of
changes, and is essential for maintaining business continuity in a live production
environment. Critical to this process is a version control system to track and compare
differences between environments, ensuring only the necessary "delta" is packaged and
deployed.

Planning for incremental deployments requires change tracking, dependency analysis, and
careful sequencing of data and metadata components to ensure that all prerequisites are met
in the target environment.

## Deployment Sequence and Dependencies

The deployment process must navigate intricate dependencies involving both metadata and the data
records themselves. For instance, before deploying the data records for an object, the
necessary metadata must be in place first to ensure that the destination org is structurally
prepared to receive the data.

Also, there are dependencies based on the record relationships. For example, if you're deploying
a custom object with a lookup to the standard Account object, the Account records must be
created first to satisfy the lookup relationship when the custom object's child records are
subsequently inserted. You must also account for parent-child or master-detail
relationships, requiring the parent record to be deployed before the child, to preserve
referential integrity. Proper assessment and sequencing of these interdependent data and
metadata components is vital to avoid validation errors and data corruption.

Sometimes, there are loops in the inter-relationships. For example, an object A depends on object
B being deployed earlier, and object B depends on object A being deployed earlier. Let’s say
object A goes first, then object B goes next. Because of circular dependencies, one has to
redeploy object A a second time to ensure all the references are properly populated.

Here are a few deployment dependency examples.

- The Product Specification Record Type must be deployed before you can insert any Product
  records.
- The Attribute Based Adjustment Rule must be deployed before you can insert any Attribute
  Based Adjustment records.
- Decision Tables (metadata records) must be deployed before deploying Pricing Recipes
  (metadata records).

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

For complete information on the required deployment sequence, see [Object Deployment Sequence](./deployment_appendix_A.htm.md "Get to know the object deployment sequence and associated properties.") and [Metadata Deployment Reference](./deployment_appendix_B.htm.md "Get to know the metadata deployment sequence and associated details.").
