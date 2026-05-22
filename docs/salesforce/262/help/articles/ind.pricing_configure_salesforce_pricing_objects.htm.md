---
article_id: ind.pricing_configure_salesforce_pricing_objects.htm
title: Configure Salesforce Pricing Objects
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_configure_salesforce_pricing_objects.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Configure Salesforce Pricing Objects

To optimize Salesforce Pricing, configure the page layouts for Product, Price Book Entry, and Price Adjustment Schedule objects to ensure the proper display and functionality of pricing-related fields and related lists, thereby guaranteeing accurate product and service pricing and streamlining sales processes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To update object layouts:	

Salesforce Pricing Design Time


To customize an Experience Cloud site:	

Be a member of the site AND Create and Set Up Experiences

OR

Be a member of the site AND an experience admin, publisher, or builder in that site

NOTE The standard product lookup function (used on objects such as Opportunities and Work Orders) relies heavily on the record's context to find linked price book entries. If you customize these standard page layouts or use URL-based custom buttons, the product lookup can fail because it can't retrieve the necessary object or correlation IDs. If you build a custom page layout, include the parent object (such as the Opportunity or Work Order) as a field on the layout. Additionally, use custom actions rather than URL-based buttons so that the pricing engine successfully passes the required context IDs to the product lookup plug-in.
Update the Product Page Layout
From Object manager, search for and select the Product object.
Select Page Layouts, and then click Product Layout.
In the palette, click Related Lists.
Drag and drop these related lists to the Product’s page layout:
Price Adjustment Tier
Attribute Based Adjustment
Bundle Based Adjustment
Parent Products
Derived Products
Source Products
Save your changes.
Configure Price Book Entry
From Object manager, search for and select the Price Book Entry object.
Select Page Layouts, and then click Price Book Entry Layout.
In the palette, click Fields.
Drag and drop Product Selling Model field to the Price Book Entry’s page layout.
Save your changes.
Configure Price Adjustment Schedule
From Object manager, search for and select the Price Adjustment Schedule object.
Select Page Layouts, and then click Price Adjustment Schedule Layout.
In the palette, click Related Lists.
Drag and drop the Attribute Based Adjustment related list to the Price Adjustment Schedule’s page layout
Save your changes.
