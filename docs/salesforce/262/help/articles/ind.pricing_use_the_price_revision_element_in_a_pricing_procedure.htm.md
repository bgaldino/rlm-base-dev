---
article_id: ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm
title: Use the Price Revision Element in a Pricing Procedure
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Use the Price Revision Element in a Pricing Procedure

To maintain profitability on renewals, use the Price Revision element to automatically adjust for inflation and rising operational costs on quotes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create pricing procedures:	Salesforce Pricing Design Time
NOTE After your Salesforce org updates to Winter ’26, users who have Price Tracking enabled may be unable to use the Price Revision feature because the Index Rate decision table may be deactivated. To activate the Index Rate decision table, from Setup, search for and select Decision Tables. Select the Index Rate decision table and activate it.

Let’s consider a scenario where a business wants to adapt its pricing to frequent inflationary effects in a country that we’ll call ABC. To achieve this, it secures an agreement with its customers for an annual price increase equivalent to the Consumer Price Index (CPI) plus 5%, while ensuring the total adjustment is capped at 10%.

Calculating the revised price of a product involves a few key steps.

Add picklist values to the Region field on the Index Rate entity.
Create a price revision policy record.
Define the index rates.
Add the Price Revision element to a pricing procedure to calculate the adjusted prices due to inflation.
Modify the Index Rate Record Page

Before you create an index rate record, you’ll need to add Region picklist values to the Index Rate entity's Region field.

From Setup, in Object Manager, search for and select Index Rate.
Select Fields & Relationships, and then click Region.
In the Region Picklist Values section, click New.
Enter country names. For our use case, specify ABC.
Save your changes.
Create a Price Revision Policy Record

Configure an inflation policy for the country of ABC to enable sales reps to apply specific price uplifts to quotes and deals based on its defined inflation rate.

Before creating a price revision policy, you need to understand the two policy types:

Flat. This policy type uses a manually entered uplift value (a policy adjustment). The system doesn't reference a decision table to find the value.
Price Index. This policy type automatically retrieves the uplift value from the Index Rate decision table, ensuring the rate matches the input criteria.
From the App Launcher, find and select Price Revision Policies.
Click New.
Specify these details.
Name: ABC CPI
Type: Price Index
Effective From: 1/1/2025
Effective To: 12/31/2025
Region: ABC
Formula: MAX(10, PriceIndex + 5)
To define a formula, follow the steps below.
Select a function in the Search functions… field. Here, select MAX.
Highlight the value within the brackets and delete it.
Place your cursor in the brackets and then, enter 10,.
Select a resource from the Select a resource... field. Here, select PriceIndex.
Select an operator from the Enter an operator… field. Here, select +.
Enter 5. All numerical values as treated as a percentage.
Save your changes.
IMPORTANT Effective date ranges for the same region can’t overlap, unless you’re on a multi-currency organization.
Define Index Rates

The index rates entity stores inflation rates for various periods of time based on different time periods.

From the App Launcher, find and select Index Rates.
Click New.
Specify these details.
Name: ABC CPI 2025
Rate: 8
Valid Start Date: 1/1/2025
Valid End Date: 12/31/2025
Region: ABC
Usage Type: Pricing
Save your changes.
IMPORTANT Effective date ranges for the same region can’t overlap, unless you’re on a multi-currency organization.
Add the Price Revision Element
Create a pricing procedure. To create a pricing procedure, follow the first 5 steps in Configure Your Pricing Procedure.
Add the Pricing Setting element and map these variables.
Input Variables
Line Item: LineItem
Output Variables
Price Waterfall: price_water_fall
Net Unit Price: NetUnitPrice.
Subtotal: ItemNetTotalPrice
Add the List Price element to fetch the base price of the product.
Under Lookup Table Details, select the Price Book Entries V2 decision table and map these variables.
Input Rule Variables
Product: Product
Price Book: PriceBooks
Product Selling Model: ProductSellingModel
Input Variables
Quantity: LineItemQuantity
Output Variables
List Price: ListPrice
Subtotal: ItemNetTotalPrice
Resolution Variables
Resolution Strategy: ResolutionStrategyMinPrice
Use As List: Price Book
Add the Price Revision element to adjust prices for a product.
Under Lookup Table Details, select the Index Rate decision table and map these variables.
Input Rule Variables
Valid Start Date: ItemConsumerPriceIndexDate_std. This is the date for your price revision that must fall within the effective date range specified in the index rate record.
Region: ItemPriceRevisionPolicyRegion_std. This is the region where you’re verifying the inflation rate.
Input Variables
Quantity: LineItemQuantity
Price Revision Policy: ItemPriceRevisionPolicyName_std. This is the name of the price revision policy record.
Input Unit Price: ListPrice
Policy Type: ItemPriceRevisionPolicyType_std. This is the policy type you’ve selected in the price revision policy record, which can be either Flat or Price Index.
Price Revision Formula: ItemPriceRevisionPolicyFormula_std. This is the formula you’ve provided in the price revision policy record.
Click and select Include in Output.
Save your procedure.
Click Simulate
Specify the input values for subscriptions to Slack along with the additional uplift of 5% that must be added to maintain gross margins. Click Simulate again.
The price waterfall shows the Price Revision updates, confirming that your procedure is working as expected.

When you simulate a pricing procedure, you can enter the formula manually to verify if the adjusted prices are reflected for a given product. However, when a sales rep creates a quote, they'll see this information on the quote itself, along with the option to enter additional uplift data.

IMPORTANT If your waterfall doesn’t reflect the right values, we recommend refreshing your Index Rate decision table.
