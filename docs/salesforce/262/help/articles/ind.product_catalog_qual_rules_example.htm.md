---
article_id: ind.product_catalog_qual_rules_example.htm
title: Explore a Qualification Rule Example
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_qual_rules_example.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Explore a Qualification Rule Example

Qualification rules can be a complex topic to understand. Let's look at an example to see how the components come together to create a fully functional qualification rule.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To create and test all qualification rule components:	

Manage Product Catalog

Context Service Admin

Rules Engine Designer

Rules Engine Runtime

NOTE Your Salesforce org may be customized or configured differently from what is described here. If these instructions become difficult to follow, create a promo developer org to use for this example exercise.
Example Overview

Qualification rules come in two types: qualification and disqualification. In this example, we'll explore a disqualification rule.

Consider a company in the United States that sells landscaping and lawn care materials such as tools, grass seed, mulch, fertilizer, and pesticide. In the agricultural industry, many states regulate the use and sale of certain chemicals. One particular product, a pesticide sold as PEST-1X, is not allowed for sale in California due to local environmental laws.

We'll use the Billing State field as the primary criteria for our qualification rule. If a sales rep creates a quote or order for a customer in California, PEST-1X does not appear as a choice in the Landscaping product catalog.

Let's explore how to build a qualification rule that satisfies these requirements.

Summary of Components

Qualification rules require several technical components. To make keeping track of them easier, refer to this table. Note that the exact component names used here may be different from what's in your org.

COMPONENT NAME	COMPONENT TYPE
PEST-1X	Product
Disqualification Record	Product Disqualification Object
BrowseProductsCtxDefinition	Product Discovery Context Definition
ProductDisqualificationDT	Product Disqualification Decision Table
Product Qualification	Qualification Rule Procedure
Create the PEST-1X Product

Before implementing the qualification rule, let's add a product we can test with the catalog.

Create a Catalog called Landscaping.
Create a Category called Pesticides, and assign it to the Landscaping Catalog.
Create a simple Product called PEST-1X. Make sure to activate it.
Create a One Time Product Selling Model Option for the product.
Create a price book entry for PEST-1X. Choose any price you want.
Select One Time as the Selling Model, then save the price book entry.

You now have a product that is ready to add to quotes and orders.

Add Custom Field to the Product Disqualification Object

To begin building the qualification rule, add a custom field for Billing State to the Product Disqualification object. Fields on this object are used as evaluation criteria by qualification rules.

To create the custom field:

Go to the Object Manager in Setup.
Find the Product Disqualification object.
Create a new text field called BillingState.
Set the field visibility for all profiles and select the page layout to display the field.
Save your work.
Create a Product Disqualification Record

Now that you have the custom Billing State field, create a Product Disqualification record with the criteria for our example scenario.

To create the Product Disqualification record:

Open the App Launcher and find Product Disqualifications.
Click New and enter this field data:
Product: PEST-1X.
Effective From: today's date.
Effective To: a date in the future.
BillingState: CA.
Save the record.
Modify the Product Discovery Context Definition

To add Billing State to the active product discovery context definition, modify the BrowseProductsCtxDefinition context definition.

To modify the BrowseProductsCtxDefinition context definition:

Go to Setup and find Context Definitions using Quick Find.
Click Custom Definitions.
Click BrowseProductsCtxDefinition.
Click Edit.
Click Next.
You don't need to add any nodes, so click Next.
Click Account Inherited, then click Add Attributes and enter these field values:
Name: BillingState.
Type: Input.
Data Type: String.
Click CategoryProduct Inherited. Add another BillingState attribute with the same values as before.
Click Next.
In the Account Node, enter BillingState as the Context Tag for BillingState.
Save your work.
Map Billing State in the Context Definition

To complete the context definition modifications, map Billing State from the context definition input node to the account object node.

Go to Setup and find Context Definitions using Quick Find.
Click Custom Definitions.
Click BrowseProductsCtxDefinition.
Click Map Data.
Open the action menu for the mapping and click Edit.
Click Map.
Map BillingState from the input Account Node to BillingState on the account object node.
Save your work.
Modify the Product Disqualification Decision Table

Modify the disqualification decision table to include the criteria for our example qualification rule. The decision table is used by the Qualification Rule Procedure to evaluate the criteria for both qualification and disqualification.

To add the Billing State criteria to the product disqualification decision table:

Open the App Launcher and select Product Catalog Management. Navigate to the Home tab.
Scroll down the page and click Qualification Rules.
Open the Product Disqualification rule and click Deactivate.
Click Save & Next.
Click Add Condition.
In Source Object Field, enter BillingState__c for the Source.
In Operator, select Equals.
Click Save & Next.
Click Save & Next.
Click Finish.
Click Activate.
Modify the Qualification Rule Procedure

We're almost there! Now that we have configured all the qualification rule components we need, let's bring them all together in the qualification rule procedure.

To modify the qualification rule procedure:

Open the App Launcher and select Product Catalog Management.
On the Home tab, scroll down and click Qualification Rules Procedures.
Select the All Qualification Procedures list view.
Click Product Qualification.
In Qualification Procedure Versions click the most recent, active version.
Deactivate the Rule Procedure.
Open the Evaluate Disqualification component.
Map the Billing State input parameter by selecting BillingState.
Save and Activate the procedure.
Confirm Product Discovery Settings

All the pieces are now in place. As a best practice, let's check the Product Discovery Settings to ensure that we have the correct Context Definition and Qualification Procedure selected there.

In Setup, find Product Discovery Settings using Quick Find.
Confirm that Context Definition is set to BrowseProductsCtxDefinition.
Confirm that Qualification Procedure is set to ProductQualification.
Test the Qualification Rule

Now let's ensure that the qualification rule performs as expected.

Create a quote for an Account where Billing State = CA. Confirm that PEST-1X is not available in the catalog.
Create a quote for an Account where Billing State is not CA. Confirm that PEST-1X is available in the catalog.
NOTE If the qualification rule doesn't appear to be working, Sync Pricing Data and try again.
