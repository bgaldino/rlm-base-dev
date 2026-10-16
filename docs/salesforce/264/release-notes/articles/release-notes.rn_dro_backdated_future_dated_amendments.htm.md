---
article_id: release-notes.rn_dro_backdated_future_dated_amendments.htm
title: Orchestrate Backdated and Future-Dated Contract Changes Automatically
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_dro_backdated_future_dated_amendments.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_dynamic_revenue_orchestrator.htm
fetched_at: 2026-09-30
---

# Orchestrate Backdated and Future-Dated Contract Changes Automatically

Fulfill amendments, renewals, and cancellations with past or future effective dates, and roll back future-dated changes in assets before they take effect. During decomposition, Dynamic Revenue Orchestrator evaluates the future state of each fulfillment asset to make sure that fulfillment actions, quantities, and dates reflect the correct time period, even for complex subscriptions and multiyear deals. Time-aware fulfillment assets capture quantities and attributes for each time period to guarantee correct provisioning based on the effective date rather than the submission date.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Advanced license.

How: On an amendment, renewal, or cancellation order, specify an effective date. To reverse a future change, submit a rollback order. Dynamic Revenue Orchestrator handles time-aware line item generation upon submission.

SEE ALSO
Salesforce Help: Considerations for Backdated Changes in Dynamic Revenue Orchestrator
