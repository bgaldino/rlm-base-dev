---
article_id: ind.billing_setup_payment_retry_rules.htm
title: Set Up Payment Retry Rules
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_payment_retry_rules.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Set Up Payment Retry Rules

Define payment retry rule sets and payment retry rules and configure Billing to automatically retry failed payments for specific error categories at various time intervals.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To retry failed payments:	Billing Admin permission set
Create Payment Retry Rule Sets

Payment retry rule sets specify how the failed payments must be retried based on the error codes across various retry categories. A payment retry rule set contains one or more payment retry rules. All payment rules in a payment retry rule set inherit the values of retry interval type, interval unit, and interval values, by default. You can, however, override the default values by specifying the same in the payment retry rule.

Make sure to add the Default Rule Set and Use Alternate Payment Method checkbox fields to the Payment Retry Rule Set page layout.

From the App Launcher, find and select Payment Retry Rule Sets.
Click New.
Enter a name for the payment retry rule set.
Select a retry interval type.
	
Fixed	Sets a consistent time period between retry attempts. To retry at regular intervals of a few hours, minutes, or days, set the retry interval type as Fixed. For example, to retry every five days, set the retry interval type to Fixed and retry interval to 5.
Staggered	Sets different intervals for each retry attempt. To retry at varied intervals of time, set the retry interval type as Staggered and provide. For example, to retry every second, fourth, and sixth hour, set the retry interval type to Staggered and retry interval to 2,4,6.
Select an interval unit—Hours, Minutes, or Days.
If you selected the fixed interval type, enter a positive number less than or equal to 10 for the maximum number of retry attempts.
Enter one or more positive numbers for the interval value to indicate the time intervals after which the payment batch run must retry the failed payments.
If you selected the fixed interval type, enter a positive number less than or equal to 60. If you selected a staggered retry interval type, enter one or more positive numbers less than or equal to 60, separated by commas. Make sure that there are no whitespaces before or after the comma.
Select Draft or Active as the status.
If necessary, enter a description.
To set the payment retry rule set as default for your Salesforce org, select Default Rule Set.
You can add only one active default payment retry rule set at a time. If you set any other payment retry rule set as default, the earlier one is automatically removed as the default rule set.
To use an alternate payment method on the last retry of the failed payment, select Use Alternate Payment Method.
Save your changes.
EXAMPLE

To retry failed payments three times every six hours, select the interval type as Fixed and the interval unit as Hours. Then, enter the interval value as 6 and the retry count as 3.

To retry failed payments four times, every first, fifth, tenth, and fifteenth day, select the interval type as Staggered and the interval unit as Days. Then, enter the interval values as 1,5,10,15.

After you create a payment retry rule set, create one or more payment retry rules.

IMPORTANT To automatically retry failed payments, add at least one default payment retry rule set and then turn on Retry Failed Payments on the Billing Settings page.
Create Payment Retry Rules

Payment retry rules define actionable parameters such as the maximum number of retries for the failed records and time intervals between subsequent retry attempts. Create payment retry rules specific to payment gateways and payment gateway error categories. All payment retry rules in a payment retry rule set inherit the default values for interval type, interval time, interval unit, and maximum retry count provided in the rule set. You can, however, override the default values of the payment retry rule set by specifying the values in the payment retry rule.

From the App Launcher, find and select Payment Retry Rules.
Click New.
Enter a name for the payment retry rule set.
Select a payment retry rule set.
Optionally, select a payment gateway.
Select a payment gateway error category.
For information about available error categories, see Payment Gateway Error Categories.
Optionally, enter a payment gateway error code.
Select a retry interval type.
	
Fixed	Sets a consistent time period between retry attempts. To retry at regular intervals of a few hours, minutes, or days, set the retry interval type as Fixed.
Staggered	Sets different intervals for each retry attempt. To retry at varied intervals of time, set the retry interval type as Staggered.
Select an interval unit—Hours, Minutes, or Days.
If you selected the fixed interval type, enter a positive number less than or equal to 10 for the maximum number of retry attempts.
Enter one or more positive numbers for the interval value to indicate the time intervals after which the payment batch run must retry the failed payments.
If you selected the fixed interval type, enter a positive number less than or equal to 60. If you selected a staggered retry interval type, enter one or more positive numbers less than or equal to 60, separated by commas. Make sure that there are no whitespaces before or after the comma.
Save your changes.

Alternatively, if you already have an existing payment retry rule set, create a new payment retry rule by clicking New on the Related tab of the payment retry rule set. The configuration steps are the same.
