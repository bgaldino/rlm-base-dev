---
article_id: ind.billing_understand_billing_suspensions_and_target_date.htm
title: Understand Billing Suspensions and Target Date
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_understand_billing_suspensions_and_target_date.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_suspend_and_resume_overview.htm
fetched_at: 2026-09-04
---

# Understand Billing Suspensions and Target Date

Learn how Billing evaluates suspensions when invoice runs and the Invoice Creation API use a target date or billing period count.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Deferred Charges

Suspending billing defers charges for the suspension period—it doesn’t waive them. Charges for the suspended period are billed when billing resumes or when a later invoice run uses a target date on or after the resumption date.

Target Date and Suspensions

When a run uses a target date, Billing evaluates billing suspensions as of that date, not the run date. Backdating suspensions isn’t required to prevent charges during that suspension period. Depending on where the target date falls relative to the suspension window:

Target date before the suspension starts: Invoicing proceeds as normal—the suspension has no effect yet.
Target date falls within the suspension window: Billing doesn’t create billing period items or generate an invoice for the suspended billing periods, even if the run date is before the suspension starts. If a billing schedule falls partially in the suspension window, Billing creates billing period items and invoices for the periods before the suspension start date. Invoice run responses can report that the account or billing schedule group is suspended, if there are no billing periods falling before the suspension window.
Target date falls on or after the resumption date: The invoice run bills all periods up through the target date, including the previously deferred charges from the suspension period, in the same run. The suspension has no effect on those invoices, because the target date is on or after the resumption date.
EXAMPLE You suspend billing for a monthly billing schedule group. The group’s next billing date is July 15, and Billing Day of Month is 15. You set the suspension date to September 10 and the resumption date to September 30. On July 15, you send a request to the Invoice Creation API with a target date of September 15.

Because the target date falls in the suspension window, Billing creates billing period items only for periods that end before the suspension starts—through August 15—and generates an invoice for those charges. The billing period item for the period that ends September 15 isn’t created, because that period overlaps the suspension window.

September charges are billed when a later invoice run uses a target date on or after September 30, or when you cancel the suspension and run invoicing again.

Billing Period Count and Suspensions

When an invoice run uses billing period count instead of a target date, Billing still evaluates suspension for each schedule separately. A suspended schedule isn’t invoiced for any period that falls in its suspension window.

What changes is which periods the run retrieves. A target date selects schedules up to a calendar date. Billing period count selects a fixed number of periods per schedule, so the period range can differ for schedules with different next billing dates.

Multiple Suspensions

If more than one suspension applies to the same account or billing schedule group, Billing uses the earliest suspension start date.

EXAMPLE Account Acme has a suspension from June 1 through June 15, and the related billing schedule group has a suspension from June 10 through June 30. Billing uses June 1 as the suspension start. An invoice run with a target date of June 12 doesn’t create billing period items for the suspended schedules.
