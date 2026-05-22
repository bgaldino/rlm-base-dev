---
article_id: ind.product_catalog_create_a_qual_rule_for_product.htm
title: Create Qualification Rule Criteria
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_create_a_qual_rule_for_product.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create Qualification Rule Criteria

Create criteria using field data on your chosen Salesforce object that you want to use for qualification rules. The object can be one that you create, or one of the included qualification or disqualification objects.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To create a qualification rule:	Manage Product Catalog

To help illustrate how qualification rule criteria works, let's use an example. Imagine that we need to restrict sales of a certain chemical called PEST-1X to customers in California. We can use the Billing State field on the Account object as the qualification rule.

Therefore, we need a field for Billing State on our evaluation object. We can use the Product Disqualification object that's already included in our org.

Create the Product Disqualification Field

To create the custom field for Billing State on the Product Disqualification object:

Go to the Object Manager in Setup.
Find the Product Disqualification object.
Create a new text field called BillingState.
Set field visibility for your profiles and select a page layout to display the field.
Save your changes.

Now that you have a field to record your criteria, you must create Product Disqualification records for each product that you want to include in the rule evaluation.

Create a Product Disqualification Record

To create a Product Disqualification record to use in the rule evaluation:

Open the App Launcher and find Product Disqualifications.
Click New, and enter this field data:
Enter a product you wish to use in the Product field.
In our example scenario, you would enter PEST-1X.
For Effective Date, enter the current date.
For Effective To, eneter a date in the future.
Enter CA for the BillingState.
Save the record.

You now have a product disqualification record ready to use in your qualification rule. This record is referenced by the qualification rule decision table.
