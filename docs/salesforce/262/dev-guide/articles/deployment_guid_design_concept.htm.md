---
page_id: deployment_guid_design_concept.htm
title: GUID Design and Usage
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_guid_design_concept.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_global_UID_setup.htm
fetched_at: 2026-06-09
---

# GUID Design and Usage

The format and values of the Global Unique ID (GUID) are up to you. Here's some
guidance on what makes a good versus poor GUID for deployment tracking.

The format and values of the GUID itself are up to you. Here's some guidance on what makes a
good versus poor GUID.

A good GUID design includes these characteristics.

- Immutable
- Unique globally
- Non-translatable
- A single key
- Generated programmatically, and not manually

Poor GUID design includes these characteristics.

- Record Name field (mutable)
- Combination of mutable attributes such as Name + Version + Sequence
- Concatenated keys
- Conditional keys (Pricebook + Product OR Pricebook + Product + ISO Code)

## Populate a GUID

Once you have created the GUID field on all the Salesforce objects related to your
deployment plan, you're ready to populate the field with data.

Add the GUID column to your import spreadsheets or import file definitions. Populate the
field with the GUID format you've chosen. Now, you're ready to use the GUID in your
deployment process.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

You must populate the GUID field not only at the beginning of your
deployment process, but you must also populate it for any new records you generate along the
way.

## Usage of GUID in the Deployment Cycle

The GUID is the cornerstone of your deployment and data migration strategy. During the deployment
process, leverage the GUID for accurate upserts and data mapping. When migrating data
records from one org to another, your deployment method must use the GUID as the external ID
field for lookup and matching. This practice ensures that updates are applied precisely to
the correct record, preventing data duplication or corruption.

In the event of a deployment
failure or a post-deployment data issue, administrators can use the GUID to quickly and
confidently locate the problematic records in all orgs for precise auditing and
troubleshooting.

![Usage of GUID in the Deployment Cycle](/docs/resources/img/en-us/262.0?doc_id=dev_guides%2Frev_lifecycle_mgmt%2Fdeployment_guide%2Fimages%2Fdeployment_GUID_Usage.png&folder=revenue_lifecycle_management_dev_guide)

## Non-Extensible Objects

A few Revenue Cloud objects are protected, and therefore non-extensible. You can't add a
GUID field to these objects. Instead, create an external reference table to store your GUID.
Use this reference table to track the non-extensible object throughout your deployment
process.
