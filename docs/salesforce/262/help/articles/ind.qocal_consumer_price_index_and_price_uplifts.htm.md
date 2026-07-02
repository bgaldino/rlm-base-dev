---
article_id: ind.qocal_consumer_price_index_and_price_uplifts.htm
title: Use Consumer Price Index for Automated Renewal Price Uplifts
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_consumer_price_index_and_price_uplifts.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Use Consumer Price Index for Automated Renewal Price Uplifts

Automate the calculation of renewal price increases by using the consumer price index (CPI) and additional negotiated price uplift. With this feature, your pricing keeps pace with market conditions and maximizes your high-margin annual contract value (ACV).

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To use CPI for renewal price uplifts:	Renew Assets user permission

Integrating CPI into your renewal price uplift strategy provides significant business benefits.

Price uplift provides instrumentation to monetize ongoing investments in products, platforms, and support.
Uplift minimizes the impact of dollars lost on an account, helping offset attrition.
Price uplift delivers a significant amount of high-margin ACV. All uplift dollars count toward the account executive quota.
Price uplift can be offset or combined with extended terms or additional products during negotiations.
Customers often raise their own prices based on market conditions, input costs, and other factors, requiring similar tools for monetization.
By tying the renewal uplift percentage to CPI, you can apply the new price at renewal time, based on CPI and any additional negotiated uplift amount.

Salesforce admins create price revision policies—for example, US CPI, that define the floating rate portion of the renewal price uplift. Over time, your admin creates index rate records to define the value for a price index for a time period. The US CPI for July 2025 was 2.7%.

Sales reps who are negotiating a deal at the quote line item or order item level select a price revision policy. They select a spread over the base rate in the Unit Price Uplift field—for example +5%, to get the CPI-based uplift, such as US CPI plus 5%.

At renewal time, the system automatically calculates the correct price based on the price revision policy, index rate, and unit price uplift. For example, CPI-adjusted uplift for a renewal in July 2025 is 7.7% because US CPI was 2.7% and the agreed-upon spread was +5%.

To implement CPI-based renewal uplift, configure data objects and fields within Agentforce Revenue Management to capture and apply relevant inflation data.

Configure a price revision policy.
With a price revision policy, a Pricing design-time user or Salesforce admin can define the CPI policy and the formula to be applied when calculating renewal uplift.
From the App Launcher, find and select Price Revision Policies.
Click New, and update the new price revision policy fields.
For example, set Policy Name to US CPI, Argentina Inflation Rate, or United Kingdom Inflation Rate; Type to Price Index; Effective From to 1/1/2025; Effective To to 12/31/2025; Region to US instead of Argentina or the United Kingdom; and Formula to PriceIndex, that is, the variable rate added to the fixed renewal uplift percentage.
Define and capture CPI data by creating index rate records, and save your changes.
Add the Price Revision Policy Name field and the Unit Price Uplift field to the Transaction Line Editor component on the quote and order pages.
In Setup, find and select Lightning App Builder.
Click Edit next to Quote Record Page.
On Quote Record Page, select the Transaction Line Editor (TLT 2.0) component.
On the component properties pane, under Display Columns, click Select....
In the Available section, select Unit Price Uplift and move it to the Selected section. Click OK.
Save your changes.
In Lightning App Builder, select Edit next to Order Record Page.
To add the Unit Price Uplift field to Transaction Line Editor, click the Details tab on Transaction Line Editor.
Click the Fields tab, and search for Unit Price Uplift.
Drag the Unit Price Uplift field to the Record Detail component.
Save your changes.
Add the Price Revision Policy field on quote line item (QLI), order product (OP), and asset state period (ASP) objects.
From Setup, in the Quick Find box, enter Object Manager, and then select Object Manager. Next, click Quote Line Item, and then click Page Layouts.
Click Quote Line Item Layout.
If the Pricing Revision Policy field isn't present in the Pricing Information section, in the Quick Find box, enter Price Revision Policy, and then drag the field to the Pricing Information section.
Save your changes.
Similarly, add the field to OP and ASP.
Add the Unit Price Uplift field to the QLI and OP objects.
From Setup, in the Quick Find box, enter Object Manager, and then select Object Manager. Next, click Quote Line Item, and then click Page Layouts.
If the Unit Price Uplift field isn't present in the Pricing Information section, in the Quick Find box, enter Unit Price Uplift, and then drag the field to the Pricing Information section.
Save your changes.
Similarly, add the field to OP.
Create a renewal quote or order.
If the asset’s pricing source is last transaction price (LTP) and uplift type is CPI/Variable, the net unit price is calculated as the latest asset action source (AAS) change in subtotal divided by the change in quantity * (1 + the renewal uplift percent).
The renewal process requires a matching CPI record for the effective date. If an effective date can't be found, an error occurs.
Sales reps can apply an additional discount on top of the calculated price uplift, overriding the net unit price.
EXAMPLE

Sales reps can use CPI in several scenarios to determine the final renewal price.

Standard CPI calculation: Agentforce Revenue Management calculates the renewal price by applying the CPI rate plus an additional defined uplift percentage to the LTP.

Last Transaction Price: $100
CPI Percentage: 3.5%
Additional uplift percentage: 2.0%
Calculation: LTP * (1 + CPI % + additional uplift %)
Result: $100 * (1 + 0.035 + 0.02) = $100 * 1.055 = $105.50

Asset renewal with a defined CPI type: The renewal flow checks the asset for specific CPI settings to determine the correct price.

Asset configuration: A Sales Cloud asset has an LTP of $150 per user per month, a CPI type of US CPI, and an additional 3% uplift with an uplift type of CPI/Variable.
CPI data match: The renewal process finds and uses a US CPI record for the effective renewal date with a 4.50% CPI value.
Net unit price calculation: Agentforce Revenue Management calculates the new net unit price as $150\times (1 + \text{CPI} + \text{Renewal Uplift}). Result: $150\times (1 + 0.045 + 0.03) = 150\times 1.075 =\mathbf($161.25).

Regional/international uplift: CPI uplift supports defining different inflation rates for localized sales.

A sales rep operating in China negotiates a renewal for Sales Cloud. The asset is set with an uplift percentage of 3%, an uplift enumeration of CPI uplift, and an uplift type of China Inflation Rate. The renewal process uses the correct CPI data for China, such as the 8% China Inflation Rate from January 2025.

Automated periodic price amendments: Sales reps can use CPI to automatically adjust prices periodically, not just at the primary renewal date.

For a three-year contract with a CPI anniversary clause, CPI automatically updates the prices for year two and year three at the first and second anniversary dates.
The system automatically sends a notification to the customer informing them of the price change.
