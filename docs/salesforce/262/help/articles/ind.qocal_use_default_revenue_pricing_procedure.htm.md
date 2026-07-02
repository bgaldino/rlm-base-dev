---
article_id: ind.qocal_use_default_revenue_pricing_procedure.htm
title: Use the Default Revenue Management Pricing Procedure
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_use_default_revenue_pricing_procedure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Use the Default Revenue Management Pricing Procedure

While you can create custom pricing procedures, we strongly recommend using the predefined versions. These predefined procedures bring consistency to your org and deliver accurate calculations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User
To use pricing procedures:	Salesforce Pricing Run Time User

Predefined pricing procedures are associated with the PricingTransactionCD context definition and the Pricing usage type. If you want to change the context definition, you can clone and use the prebuilt pricing elements. However, remember that:

You can’t change the usage type.
Modifying the context definition can result in inaccurate context mappings.
From the App Launcher, find and select Expression Set Templates.
Change the list view to All Expression Set Templates.
Select the Revenue Management Default Pricing Procedure Procedure.
Clone and save the expression set template as a new pricing procedure.
Use the prebuilt pricing elements required for your scenarios. Add or delete elements based on your pricing needs.
After you modify your procedure, simulate and activate your procedure.
To use the modified pricing procedure when pricing line items in Agentforce Revenue Management, follow the steps below.
From Setup, in the Quick Find box, enter Revenue Settings, and then select Revenue Settings.
In the Set Up Salesforce Pricing section, select your custom pricing procedure.

To understand the functionality of each pricing element and relevant use cases, see Use Pricing Elements in Pricing Procedures.

SEE ALSO
Select a Pricing Procedure
Prerequisites to Build Pricing Procedures
Simple Pricing Procedure Example
Use Pricing Elements in Pricing Procedures
Unique Pricing Scenarios
