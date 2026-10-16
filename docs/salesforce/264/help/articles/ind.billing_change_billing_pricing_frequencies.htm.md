---
article_id: ind.billing_change_billing_pricing_frequencies.htm
title: Change Billing Frequency on New and Existing Subscriptions
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_change_billing_pricing_frequencies.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_frequency_change_flow_impact.htm
fetched_at: 2026-09-04
---

# Change Billing Frequency on New and Existing Subscriptions

You can update the billing frequency of a subscription at any time, such as by switching from monthly to annual or from annual to monthly. On active subscriptions, you can update the billing frequency from any cadence to any other, such as monthly to annual billing or vice versa, without canceling or recreating the subscription. To achieve this, sales reps make a zero-quantity, field amendment for the asset, to update the billing frequency, Billing automatically prorates the charges and applies the new billing cadence from the effective date.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To change billing frequency on new and existing subscriptions:	

Billing Admin permission set

OR

Billing Operations User permission set

NOTE For orgs created in or upgraded to Spring ’26, perform a one-time task of adding the Change Billing Frequency checkbox to the Billing Treatment page layout.
Examples: Impact of Billing Frequency Change
When you change billing frequency on a transaction as different from the pricing frequency, Billing prorates the total amount from the transaction over whole and partial billing periods. For any partial periods, Billing prorates the amount based on the billing frequency. Let’s understand the calculation process with a few examples.
Change the Billing Frequency

Make sure that the product has a valid, active billing treatment, and the Change Billing Frequency checkbox is selected on that billing treatment.

Open the quote line record or open the Billing Information section of the order product.
For new sale orders, select the billing frequency or cadence, such as Weekly, Monthly, Quarterly, Semi-Annual, or Annual. For existing orders, initiate the billing frequency change as a zero-quantity, field amend action.
Save your changes, and then activate the order.

On existing orders, Billing automatically prorates the charges and applies the new billing frequency from the effective date. Billing cancels existing billing schedules and generates updated billing schedules for the new billing frequency, which are picked up during invoice generation.

Change the Billing Frequency by Using Create Standalone Billing Schedules API

Starting Summer ’26, you can use the Create Standalone Billing Schedules API to change billing frequencies of order products during a subscription period. Use the API to update multiple billing schedules from lower pricing frequency to higher billing frequencies and vice versa, directly from the Billing Schedule Group record.

In the request body of the API, specify these values in the transactionDetails property value of the amended transaction.
Specify the billing schedule group ID for which you want to update the billing frequency in BillingScheduleGroupId__std.
Specify the billing frequency for the specific billing schedule group ID in BillingTermUnit__std.
Specify the date from when the update to the billing frequency is applicable in StartDate__std.
If the billing term unit is quarterly, semi-annual, or annual, then specify the month from when the billing frequency change is applicable in BillingStartMonth__std.
Specify Amend as the action type in BillingActionType__std.
Specify BillingFrequencyChange as the action subtype in BillingSubActionType.

Billing automatically handles complex proration and calculates the correct billing period amounts for the varied pricing and billing frequencies.

IMPORTANT When a billing schedule group is linked to an asset, initiate any new sale, amend, renew, or cancel actions directly from the order or asset. In such cases, use the Order to Billing Schedule flow or Create Billing Schedules for Orders API, and not the Create Standalone Billing Schedules API.
