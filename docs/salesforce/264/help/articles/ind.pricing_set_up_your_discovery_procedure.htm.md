---
article_id: ind.pricing_set_up_your_discovery_procedure.htm
title: Configure a Discovery Procedure
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_set_up_your_discovery_procedure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_discovery_procedure_for_pricing.htm
fetched_at: 2026-09-07
---

# Configure a Discovery Procedure

To calculate a product's derived price, configure a discovery procedure with the elements required to gather all contributing factors.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To create discovery procedures:	

Salesforce Pricing Design Time User


To run discovery procedures:	Salesforce Pricing Run Time
From the App Launcher, find and select Discovery Procedures.
Click New.
Specify these details.
Enter a name and then press Tab to autopopulate the API name.
Select Pricing Discovery as the usage type.
Associate the discovery procedure with a context definition.
In all our examples, we’ll use the SalesTransactionContext context definition. We also recommend using the predefined Default Discovery Procedure, or you can modify it with a context definition of your choice.
Save your changes.
On the Details tab, in the Discovery Procedure Versions section, click the discovery procedure version that you want to work on.
The Discovery Procedure Builder opens in a new tab.
To add your discovery elements, click .
If you want to map commonly used input variables, such as line items or net unit price, add the Discovery Settings element, followed by the Map Line Item element. These are optional.
Add the Fetch Pricing Rules element and enter your values.
Ensure that the Fetch Pricing Rules element is the first element in your pricing procedure.
Add the Map Products element.
The Map Products element uses the fixed input variables in the Fetch Pricing Rules element.
For example, to derive the price of a contributing product within a single bundle in the quote line, use the Map Product element. Validate that the contributing product's parent bundle has the same ID by checking if the RootItem matches. If the contributing products share the same root product, then the derived price for the product is calculated.
If your derived price record has set the pricing scope as Non-Transactional or Both, add the Asset Discovery element and map your variables.
Non-transactional scope indicates that you can derive a product's derived from assets.
Click , and enter 1 as the rank number.
NOTE When more than one enabled version matches a discovery procedure, choose the version with the highest rank. For example, if two enabled versions have rank values set to 1 and 2, choose the version with rank 2.
Click , select Include in Output, and save your pricing procedure.
Save your changes.
Simulate your procedure to verify the queried data.
On the Input tab, enter your values and click Simulate again.
Activate your discovery procedure.
