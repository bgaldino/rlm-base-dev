---
article_id: ind.um_configure_usage_product_with_guided_workflow.htm
title: Configure a Usage-Based Product with Guided Workflow
source_url: https://help.salesforce.com/s/articleView?id=ind.um_configure_usage_product_with_guided_workflow.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Configure a Usage-Based Product with Guided Workflow

Follow the guided workflow to create the related records required for your usage-based product. These records complete the product setup so that you can start selling quickly.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Advanced license and the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To use guided workflow with Agentforce Revenue Management Advanced license:	

Product Catalog Management Designer

Rate Management Design Time User

Usage Design User


To use guided workflow with Agentforce Revenue Management Advanced and Agentforce Revenue Management Billing license:	

Product Catalog Management Designer

Rate Management Design Time User

Usage Management Designer

Before you use the workflow, configure organization-wide defaults for these objects. See Configure Record Sharing.

OBJECT	ORGANIZATION-WIDE DEFAULTS
Unit of Measure	Public Read/Write
Unit of Measure Class	Public Read/Write
Usage Resource	Public Read/Write
Usage Aggregation Policy	Public Read/Write
Usage Overage Policy	Public Read/Write
Rating Frequency Policy	Public Read/Write
Usage Commitment Policy	Public Read/Write
Usage Grant Refresh Policy	Public Read/Write
Usage Grant Rollover Policy	Public Read/Write
SEE ALSO
Rate Cards and Rate Card Entries
Manage Product Selling Model in Revenue Cloud
Define Prices in Price Books
Decision Tables for Rate Cards
Initiate the Guided Workflow
From the App Launcher, find and select Products.
Go to an anchor or pack product page, and then click Configure Usage Properties.
The Configure Usage Properties page appears with sections to add usage product related records, such as product usage resources and product usage grants.
Add or Create Product Usage Resources

To create product usage resources, you can either add existing usage resources or create new resources.

To add existing usage resources, in the Product Usage Resources pane, click Add.
In Add Usage Resources, select the resources, and then click Add.
If there are no resources available, click New.
Enter a name for the resource, and select a unit of measure class and a default unit of measure.
To ease setup, out-of-the-box policies, such as a Usage Aggregation Policy and Usage Overage Policy, are autopopulated. If the autopopulated policies don't meet your requirements, you can create or select different policies.
Click Add.
The product usage resource record is created and added to the Product Usage Resources list.
NOTE When you associate usage resources with a product, the related product usage resource record is created by default at 12:00 AM in your locale. For example, if your user in Germany selects a usage resource with a product on March 25, 2026, the product usage resource is created with an Effective Start Date of 25.03.2026 12:00 AM.
View and Define Usage Resource Details and Policies

While the product usage resource records are in the draft state, you can update their properties.

In the Product Usage Resource pane, select a record.
The right panel shows details of the selected record.
In the Product Usage Resource section, configure the effective start date and end date.
Review the autopopulated policies related to the product usage resource.
The policies are autopopulated with default lookups based on the selected usage resource. If the autopopulated policies don't meet your requirements, you can create or select different policies. The policies section isn't shown for pack products.
To save product usage resource and product usage resource policy record changes, under the Product Usage Resource section, click Save.
The action also creates the product usage resource policy record.
Configure Product Usage Grants

Define the grants provided with the product usage resource and the policies governing them.

In the Usage Grant section, enter the grant quantity, validity period term and unit, and effective period.
Review the autopopulated grant policies that are provided out of the box.
If the autopopulated policies don't meet your requirements, you can create or select different policies.
To save the product usage grant record, under the Product Usage Grant Details section, click Save.
The product usage grant record is saved and added to the Product Usage Grants list in the right panel.
To edit an existing product usage grant:
In the Product Usage Grants list, from the quick actions menu for a record, click Edit.
In the Product Usage Grant Details section, update the required fields.
Save your changes.
Validate and Activate Usage Product and Related Records

When you activate the usage records, the system runs cross-object validations to evaluate if all records work together. If the system detects issues, such as overlapping effective dates between product usage resource and product usage grant records, the errors are shown with error icons.

IMPORTANT Before you can successfully activate your product, you must create and associate an active Product Selling Model (PSM), price book (PB), and Rate Card Entry (RCE) records.
Click Activate.
If there are validation errors, resolve them by updating draft records.
Click Activate again.

These usage records get activated.

Usage Product
Usage Resource
Product Usage Resource
Product Usage Resource Policy
Product Usage Grant

If you've created new records for units of measure, unit of measure class, rate card entry, or any policy for product usage resource or product usage grant, they also get activated.

Manually refresh the decision tables used for the rate card and rate card entries.
