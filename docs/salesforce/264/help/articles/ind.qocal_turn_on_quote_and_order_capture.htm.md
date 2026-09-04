---
article_id: ind.qocal_turn_on_quote_and_order_capture.htm
title: Enabling Revenue Settings
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_turn_on_quote_and_order_capture.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_quote_and_order_capture.htm
fetched_at: 2026-09-04
---

# Enabling Revenue Settings

Give your users access to Transaction Management. Also, enable optional features to enhance the sales experience for your reps.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To turn on quote and order capture:	

Customize Application

AND

Manage Revenue Cloud

IMPORTANT The order for enabling features and assigning permissions can vary, so if you encounter an error during enablement, check that you have the required permission sets. Skip these steps if the feature is already active in your scratch org definition file.
Turn On Revenue Management

If you haven’t done it yet, enable Revenue Management Features to give your users access to Transaction Management’s object and features.

From Setup, in the Quick Find box, find and select Revenue Settings.
Verify that Enable Revenue Cloud Features is turned on.
Set Up Application Usage Type

Set up proper application tagging to support Revenue Lifecycle Management

From Setup, in the Quick Find box, find and select Revenue Settings.
Turn on Create Application Usage Type for Revenue Cloud.
Set Up Quote

Set up quotes and quote line items across your Salesforce org.

From Setup, in the Quick Find box, find and select Quote Settings.
Select the option for enabling quotes.
Then, select Create Quotes Without a Related Opportunity.
Save your changes.
Add quotes to the Opportunity page.
From Object Manager, select the Opportunity object.
On the Page Layout Selection page, select Opportunity Layout to include Quotes related list.
Set Up Order

Use the Order Settings page to control whether users in your organization have the ability to create and manage orders.

From Setup, in the Quick Find box find and select Order Settings.
Select these settings.
Enable Orders
Enable Negative Quantity
Enable Enhanced Commerce Orders
Enable Zero Quantity
Save your changes.

When you enable the Enhance Commerce Orders option, it makes the Total Line Amount field available and the Unit Price optional on order items.

The total price is calculated based on the fields that you provide.

If both Unit Price and Total Line Amount are specified, then the Total Line Amount is used as the final price.
If only Unit Price is specified, then the total price is the Unit Price multiplied by the quantity.

All final prices are automatically rounded to the currency's smallest denomination (for example, to the nearest cent for USD) based on the ISO 4217 standard, not your Salesforce org's currency settings.

Set Up Flows

Build flows for managing assets and creating contracts and orders from quotes.

From Setup, in the Quick Find box, find and select Revenue Settings.
Scroll and search for Set Up Flow for Managing Assets.
Provide the API name of the screen flow that will be used when amending, renewing, and canceling assets. To use the predefined flow, keep the default value, runtime_revenue_arcflows__arcFlow. To use a custom flow, enter the API name of the flow that you created.
Save your changes.
Scroll and search for Set Up Flow for Creating Contracts from Quotes.
Provide the API name of the screen flow that will be used when converting a quote to a contract. To use the predefined flow, keep the default value, rev_contracts__CreateCntrFromQuote. To use a custom flow, enter the API name of the flow that you created.
Save your changes.
Scroll and search for Set Up Flow for Creating Orders from Quotes.
Provide the API name of the screen flow that will be used when creating orders from a quote using the Create Order button. To use the predefined flow, keep the default value, revenue_adv_q2o__CreateOrdersFromQuote. To use a custom flow, enter the API name of the flow that you created.
Save your changes.
To assetize orders using Assetize Order flow, asset managers should follow these steps:
From Setup, in the Quick Find box, find and select Flows.
From the Flow Label column, select Assetize Order.
Click Save As New Flow and enter a new name to override the original flow.
Edit the new flow.
Users can edit the flow as needed by selecting a node and then clicking Edit.
Save and activate your flow.
Set Up Product Configurator

Simplify product configuration for your quotes and orders with these settings.

From Setup, in the Quick Find box, find and select Revenue Settings.
Turn on Configure Products at Runtime.
Set Up Salesforce Pricing

To ensure accurate pricing for your quotes and orders, enable Salesforce Pricing for your org.

From Setup, in the Quick Find box, find and select Salesforce Pricing Settings.
Turn on Salesforce Pricing.
Verify that your Salesforce org has a default pricing procedure. To learn how to select a pricing procedure, see Select a Pricing Procedure.
To give sales reps detailed insights into each step of the pricing calculation process, turn on Price Waterfall. To turn on price waterfall, see Set Up Price Waterfall.
Set Up Contract Pricing

Use custom fields beyond the default product and selling model rules.

From Setup, in the Quick Find box, find and select Revenue Settings.
Turn on Customize Contract Pricing.
Additional Quote and Order Capture Setup

Set up features that provide your sales reps, partners, and customers with the capabilities required to efficiently manage quotes and orders.

From Setup, in the Quick Find box, find and select Revenue Settings.
Turn on the following settings.
Ramp Deals for Groups in Quotes and Orders
Ramp deals for groups make it easier for sales reps to break down complex, long-term deals for multiple products into smaller, time-based segments. Ramp deals for groups are supported only in the Sales Transaction Line Editor and aren’t supported in the Transaction Line Editor.
Enable Groups in quotes and orders
Allow users to group their line items in both quotes and orders
For a better quote and order capture experience, consider enabling these optional settings.
Clone Quotes and Orders
Hide Price Refresh Notification
To process quotes and orders more efficiently by applying custom rules based on attributes like size and complexity, turn on Transaction processing for quotes and orders.
This feature can't be turned off once it's activated.
To generate quote PDFs or order forms from the UI directly, turn on Document Builder.
To provide users the ability to recalculate prices immediately when they edit a line, instead of only upon saving the transaction, turn on Instant Pricing.
Users see the Instant Pricing setting on quotes and orders. By default, the setting is turned off on quotes and orders.
To turn on the Instant Pricing setting on quotes and orders by default, turn on Instant Pricing Active by Default.
This setting is available only after you turn on the Instant Pricing setting on the Revenue Settings page. Instant Pricing Active by Default is supported only in the Sales Transaction Line Editor and isn’t supported in the Transaction Line Editor.
To make sure pricing procedures can access sensitive data, and prevent users from accessing that data, turn on Elevated Data Access for Pricing Quotes and Orders.
After you turn on this setting, set restrictive field and object permissions for users based on your business requirements.
NOTE
To hide the notification that appears when quote or order prices aren’t updated, turn on the Hide Price Refresh Notification setting. However, we recommend that you keep the notification on, because hiding it may affect saving quotes and creating orders because you could be using outdated prices. After a user modifies any price-impacting fields, to refresh the prices, they can click Reprice All. 
Set Up As-Is Renewal

Offer customers greater pricing transparency and flexibility during renewals by locking in the original price for a portion of their assets. This process makes sure that all other subscriptions are accurately repriced and extended, and correctly handles complex renewals with varying quantities and prices.

From Setup, in the Quick Find box, find and select Revenue Settings.
Turn on As-Is Renewals.
Set Up the Line Editor in Transaction Management

Set up the Transaction Line Editor or Sales Transaction Line Editor on the Quote or Order record page so sales reps can organize, edit, and review transactions efficiently.

You can add and customize the line editor to manage how quote and order line items appear in the grid. See Add and Customize the Transaction Line Editor or Sales Transaction Line Editor.

Turn On Tax Calculations for Quotes and Orders

Provide customers the estimated tax on their quotes and orders.

Set up a tax engine and create a tax policy before you enable tax configurations for Revenue Management. To learn more, see Tax Configurations in Transaction Management.

From Setup, in the Quick Find box, enter Revenue, and then select Revenue Settings.
Turn on Add Estimated Taxes to Quotes and Orders.
NOTE After you enable tax calculations, ensure accurate tax details by verifying that the tax attributes are mapped and synced to their data source in SalesTransactionContext or your extended context definition. See Upgrade Context Definition.

To proceed with the rest of the Revenue Management setup, see Set Up Revenue Management.
