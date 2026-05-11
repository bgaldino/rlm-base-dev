---
article_id: ind.billing_suspend_and_resume.htm
title: Suspend and Resume Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_suspend_and_resume.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Suspend and Resume Billing

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Suspend and Resume Billing

When temporary challenges such as billing errors, disputes, or payment disruptions occur, you can suspend billing for customer accounts or billing schedule groups for a specific period. You can resume billing after the suspension period, without restarting the entire billing cycle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To suspend and resume billing:	

You must have one of these permission sets:

Billing Admin permission set
Billing Operations User permission set
Billing Customer Service User permission set
Suspend Billing

You can suspend billing directly from an Account record or a Billing Schedule Group record.

From the App Launcher, find and select Accounts or Billing Schedule Groups.
Open the Account record or Billing Schedule Group record that you want to suspend billing for.
From the quick actions menu, click Suspend Billing.
Specify the suspension date.
The suspension date can be the current date or a future date.
Specify the resumption date.
The resumption date can be any date after the suspension date.
Click Suspend.

After you suspend billing, no invoices are generated for the account or billing schedule group between the suspension date and the day before the resumption date.

EXAMPLE A customer's payment method is unexpectedly failing from 10 April and is expected to resolve in 10 days. Specify the suspension date as April 10 and the resumption date as April 20 for that customer’s account. As a result, invoices aren't generated from April 10 to April 19, and billing resumes from April 20.
Resume Billing or Cancel Suspension

When an account or a billing schedule group is currently suspended for billing or is scheduled to be suspended for billing in the future, the Resume Billing button appears on the Account record or the Billing Schedule Group record.

To update the resumption date of billing during this period, click Resume Billing, update the resumption date, and click Resume.
To cancel the suspension, click Resume Billing, select Cancel suspension, and click Resume.

After billing resumes, charges during the suspension period are also be billed. If you don't want to include these charges, issue a credit memo.

You can also suspend and resume billing by using the Suspend Billing API and the Resume Billing API.
