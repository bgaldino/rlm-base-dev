---
article_id: ind.billing_retry_failed_payments.htm
title: Retry Failed Payments
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_retry_failed_payments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Retry Failed Payments

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Retry Failed Payments

Billing supports automated retries of failed payments, helping you capture more revenue and reduce manual collections work. When you enable the automatic retry of failed payments in your org, you can define and apply a payment retry strategy for all failed payments. You can define payment retry rules based on error categories such as insufficient funds or payment processing issues. For greater control and flexibility, you can define retry rules based on specific payment gateways and gateway-specific error codes. For each error category, you can configure the retry intervals that determine how frequently Billing can attempt to reprocess the failed payment. Additionally, you can set the maximum number of retry attempts, after which Billing either tries an alternate payment method or marks the payment request as failed.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Key Terms

Here are a few key terms used when configuring payment retry rules and rule sets for failed payments.

Payment Retry Rule Set
The retry rule set that contains the default retry settings to be applied when no specific rule matches. It also contains default org preferences for retry behavior.
Payment Retry Rule
One or more rules that define specific retry behavior for various failure scenarios. The payment retry rule defines the retry category, the payment gateway, and the payment gateway raw error code. It also includes information on specific retry intervals and maximum attempts on failed payment records.
Retry Interval Type
The regular or varied intervals of time when the payment batch run retries the failed payment records.
Maximum Retry Count
The maximum number of retries attempted by the payment batch run on failed payment records
Interval Unit
The unit of time such as hours, days, or minutes based on which a payment batch run tries again the failed payment records
Interval Value
The single or comma-separated values that determine the fixed or staggered intervals at which the payment batch run tries failed payment records again
Initial Setup
Define the Retry Rule Set: Create a payment retry rule set that defines your organization’s overall retry strategy. Define the rule set with relevant details such as the maximum retry count, interval value, interval unit, and a retry mode such as fixed or staggered. You can opt to use an alternate payment method in the last payment attempt when all previous attempts fail. A payment retry rule set acts as a parent record for a set of payment retry rules.
Define Retry Rules: Define one or more payment retry rules in the payment retry rule set. Create specific payment retry rules based on:
Payment gateway
Payment gateway error category
Payment gateway error code

The settings such as maximum retry count, retry interval type, interval value, and interval unit that are defined in the payment retry rule set are automatically inherited by all payment retry rules in the rule set. But, you can override these values in the payment retry rules that are part of the rule set.

Set a default payment retry rule set: Mark at least one rule set as active, and set it as the org default.
Turn On Retry Failed Payments setting: Enable the Retry Failed Payments feature for your org on the Billing Settings page.
Failed Payments Retry Process

When a payment fails, Billing retries the failed payment based on the retry behavior defined in the payment retry rule set and rules. Based on the next scheduled retry attempt defined in the retry rules, Billing continues to pick up failed payment schedule items until the retry attempts are exhausted or the payment succeeds, whichever is earlier.

If you opted to use an alternate payment method in the payment retry rule set, Billing uses the alternate payment method in the last attempt. For example, if the maximum retry count is 5, then the alternate payment method is used on the fifth retry.

For each payment schedule item, you can view the maximum retry count, payment retry value, and the next payment retry time in the payment schedule item record.

How Payment Retry Rules Are Resolved

Billing searches for the most specific matching payment retry rule, and then gradually broadens the search if no match is found.

Billing looks for payment retry rules that match all three criteria–retry category, payment gateway, and raw error code.
If no match is found, Billing searches for payment retry rules matching the retry category with the payment gateway, and then the retry category with raw error code.
If no match is found, Billing searches for payment retry rules based only on the retry category.

If none of these searches find a match, Billing applies the default values from the payment retry rule set.

How Payment Methods Are Applied

Based on the maximum retry count, Billing automatically retries failed payments by using the payment method specified on the payment schedule item. However, if you opted to use an alternate payment method in the payment retry rule set, then Billing attempts the last retry by using the alternate payment method. Billing automatically selects the appropriate payment method based on recency and availability.

If the failed payment method isn’t the account’s default payment method, then Billing uses the account default payment method.
If the failed payment method is already the account’s default payment method, then Billing uses the most recently created payment method that’s different from the existing one.
Payment Gateway Error Categories

A payment transaction sent across a payment gateway can fail due to multiple reasons such as insufficient funds, incorrect card information, or a connectivity issue. When you set up Billing for retrying failed payments, you can define payment retry rules for specific types of errors based on the failure reasons. For each payment retry rule, you can select from these predefined error categories.

ERROR CATEGORY	DESCRIPTION
Card Limit Decline	Insufficient funds, exceeded spending limits, or other restrictions on the card.
Payment Processing Error	Payment account is invalid, closed, restricted, or the transaction was declined for reasons other than insufficient funds.
Invalid Payment Details	Missing or incorrect data such as incorrect card numbers, addresses, or currencies.
Security Failure	Security violations or issues such as fraud, risk, authentication, verification, and authorization.
Gateway Connection Error	Connectivity or communication errors between systems, including upstream gateway errors.
Internal Validation Error	An internal error occurred due to a validation failure even before the request was sent to the gateway.
Unknown Error	Payment gateway error code isn't recognized or isn't mapped to a specific category.
Set Up Payment Retry Rules
Define payment retry rule sets and payment retry rules and configure Billing to automatically retry failed payments for specific error categories at various time intervals.
Examples: Configure Payment Retry Rule Sets and Retry Rules
Let’s explore a few examples for creating and configuring payment retry rule sets and rules.
