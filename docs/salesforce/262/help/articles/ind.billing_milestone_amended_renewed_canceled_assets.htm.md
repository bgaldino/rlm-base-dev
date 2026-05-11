---
article_id: ind.billing_milestone_amended_renewed_canceled_assets.htm
title: Milestone Billing for Amended, Renewed, and Canceled Assets
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_milestone_amended_renewed_canceled_assets.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Milestone Billing for Amended, Renewed, and Canceled Assets

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Milestone Billing for Amended, Renewed, and Canceled Assets

Handle milestone plans during amendments, renewals, and cancellations to ensure accurate billing. By default, milestone-based billing doesn’t create new milestone plans or plan items for amend or renew orders. When the Support Milestone Plans for Amended Billing Schedules setting is enabled, Billing creates or links a milestone plan to the amendment schedule and recalculates milestone dates and amounts from the amendment start date.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Amendment Scenarios

When you amend an asset with a milestone billing plan:

Amendments with a milestone-enabled billing treatment create a new billing milestone plan based on the amendment and link it to the amendment billing schedule. Milestone dates and amounts are recalculated from the amendment start date.
Amendments with a non-milestone billing treatment are processed as one-time billing schedules, and no billing milestone plan is created.
Amendments that include a preconfigured or negotiated billing milestone plan link the provided milestone plan directly to the amendment billing schedule.
Amendments without a billing treatment use the billing treatment from the original billing schedule group to create a new billing milestone plan based on the amendment details. They don’t reuse the original milestone plan.
Cancellation Behavior

When you cancel an asset with a milestone billing plan:

A cancellation billing schedule is created within the same billing schedule group, reflecting a negative amount equal to the cancellation order.
Invoiced milestones from the original billing milestone plan remain unchanged.
Date-based billing milestone plan items with milestone accomplishment dates on or after the cancellation date move to Canceled status.
Date-based billing milestone plan items with milestone accomplishment dates before the cancellation date remain active and are invoiced after the completion.
All uninvoiced event-based billing milestone plan items are marked as Canceled after the event-based milestone plan item on the original order is invoiced and posted. Until then, event-based milestone plan items can still be marked as Accomplished, but they remain uninvoiced.

Billing issues a credit memo for the difference between the original sale amount and the total invoiced billing milestone plan items, providing a partial credit for incomplete milestones.

The generated invoice lines reflect the net amount of the original sale and the canceled amount, similar to standard one-time or subscription cancellations.
