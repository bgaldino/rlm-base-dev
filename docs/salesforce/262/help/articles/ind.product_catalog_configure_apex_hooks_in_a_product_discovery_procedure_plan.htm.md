---
article_id: ind.product_catalog_configure_apex_hooks_in_a_product_discovery_procedure_plan.htm
title: Configure Apex Hooks in a Product Discovery Procedure Plan
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_configure_apex_hooks_in_a_product_discovery_procedure_plan.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Configure Apex Hooks in a Product Discovery Procedure Plan

Use Apex sections in a Product Discovery procedure plan to run custom pricing logic, such as fetching prices from an external system. The order of Apex and Pricing sections determines how prices are applied. You can include multiple Pricing and Apex sections, but only one Qualification section.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User or Procedure Plan Access
To use pricing procedures:	Salesforce Pricing Run Time User
To define, edit, delete, set security, and set version settings for Apex classes:	Author Apex
Make sure the Apex class implements RevSignaling.SignalingApexProcessor.
Confirm that the class is packaged and available in your org namespace.
Make sure the External ID field is populated for your Product2 records if used in pricing.
Only one Qualification section is supported. You can include multiple Pricing and Apex sections.
To create a procedure plan and add base sections, see Creating Procedure Plan Definitions Using Templates.
From Setup, in the Quick Find box, enter Apex, then select Apex Classes.
Select New to create a new Apex class.
In the class editor, enter the class definition and save the definition. When you activate a procedure plan, Salesforce checks the order of Qualification, Pricing, and Apex sections. Activation fails if the order doesn’t follow the supported sequence.
EXAMPLE

Examples of supported and unsupported section orders:

Supported: Apex , Pricing , Apex
Supported: Apex , Apex , Pricing
Supported: Apex , Apex , Pricing , Apex , Apex
Supported: Apex , Apex , Pricing , Pricing , Apex , Apex
Unsupported: Apex , Pricing , Apex , Pricing , Apex
Unsupported: Apex , Pricing , Apex , Apex , Pricing , Apex
