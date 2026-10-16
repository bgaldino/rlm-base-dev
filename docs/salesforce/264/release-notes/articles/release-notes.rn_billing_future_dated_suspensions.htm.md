---
article_id: release-notes.rn_billing_future_dated_suspensions.htm
title: Honor Future-Dated Billing Suspensions During Invoicing
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_future_dated_suspensions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing_schedules_arrangements.htm
fetched_at: 2026-09-30
---

# Honor Future-Dated Billing Suspensions During Invoicing

Process future-dated invoices while honoring billing suspensions as of the target date rather than the run date. If the target date falls in the suspension time frame, billing period items aren't created for the suspended period, eliminating the need to backdate suspensions to prevent charges during suspension.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Advanced or Revenue Cloud Billing license.

Who: To suspend and resume billing, you need the Billing Admin permission set, or the Billing Operations User permission set, or the Billing Customer Service User permission set.

How: From the quick actions menu of the Account record or the Billing Schedule Group record that you want to suspend, click Suspend Billing. You can also use the Suspend and Resume Billing APIs.

SEE ALSO
Salesforce Help: Understand Billing Suspensions and Target Date
