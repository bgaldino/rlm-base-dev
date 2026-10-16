---
article_id: ind.billing_suspend_and_resume.htm
title: Manage Suspend and Resume Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_suspend_and_resume.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_suspend_and_resume_overview.htm
fetched_at: 2026-09-04
---

# Manage Suspend and Resume Billing

Suspend billing from an account or billing schedule group, then update the resumption date or cancel the suspension.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
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
The resumption date can be any date after the suspension date. If you don’t know when billing should resume, specify your best estimate. You can update the resumption date later from Resume Billing.
Click Suspend.

After you suspend billing, no invoices are generated for the account or billing schedule group between the suspension date and the day before the resumption date.

Suspending billing defers charges for that period—it doesn’t waive them. For how Billing evaluates suspensions with a target date, billing period count, and multiple suspensions, see Understand Billing Suspensions and Target Date.

NOTE Starting Winter ’27, Billing evaluates billing suspensions as of the target date, not the run date of the invoice batch run. If you already have suspension periods, invoice runs that use a target date can generate different invoices than before.
EXAMPLE A customer’s payment method fails on April 10 and is expected to recover in 10 days. Specify the suspension date as April 10 and the resumption date as April 20 for that customer’s account. As a result, invoices aren’t generated from April 10 to April 19, and billing resumes from April 20.
Resume Billing or Cancel Suspension

When an account or a billing schedule group is currently suspended for billing or is scheduled to be suspended for billing in the future, the Resume Billing button appears on the Account record or the Billing Schedule Group record.

To update the resumption date of billing during this period, click Resume Billing, update the resumption date, and click Resume.
To cancel the suspension, click Resume Billing, select Cancel suspension, and click Resume.

After billing resumes, charges from the suspension period are also billed. Those deferred charges can also be included when an invoice run uses a target date on or after the resumption date. If you don’t want to include these charges, issue a credit memo. See Understand Billing Suspensions and Target Date.

You can also suspend and resume billing by using the Suspend Billing API and the Resume Billing API.
