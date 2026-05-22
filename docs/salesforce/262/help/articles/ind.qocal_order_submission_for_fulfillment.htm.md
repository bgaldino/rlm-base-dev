---
article_id: ind.qocal_order_submission_for_fulfillment.htm
title: Order Submission to Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_order_submission_for_fulfillment.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Order Submission to Dynamic Revenue Orchestrator

Submit sales transactions to Dynamic Revenue Orchestrator (DRO) for fulfillment by using the Submit Sales Transaction invocable action in flows or Apex classes. Automating this process via record-triggered flows makes sure that all eligible records enter the fulfillment pipeline immediately upon meeting specified criteria. Customizing order page layouts to include Orchestration Plan and Orchestration Submission Status fields provides users with real-time visibility into the fulfillment progress.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Assetization Rules for Dynamic Revenue Orchestrator
Use Asset Lifecycle Management to create and activate multiple asset-based orders (ABOs) for the same asset across different sales transactions or orders. Maintaining precise assetization rules makes sure that the system applies changes sequentially and prevents data conflicts during the fulfillment process.
Example: Automate Order Submission for Fulfillment
Create a record-triggered flow to submit Agentforce Revenue Management orders to Dynamic Revenue Orchestrator automatically when users activate the orders. Automation makes sure that all eligible records enter the fulfillment pipeline immediately upon meeting specified status criteria.
SEE ALSO
Customize Page Layouts with the Enhanced Page Layout Editor
Initiate Fulfillment Process of any Sales Transaction
