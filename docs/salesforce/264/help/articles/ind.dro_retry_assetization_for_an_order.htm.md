---
article_id: ind.dro_retry_assetization_for_an_order.htm
title: Retry Assetization for a Dynamic Revenue Orchestrator Order
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_retry_assetization_for_an_order.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_run_time_administration.htm
fetched_at: 2026-11-23
---

# Retry Assetization for a Dynamic Revenue Orchestrator Order

If assetization doesn't complete after fulfillment, fix the cause of the failure and invoke the Create or Update Asset from Order action. The action retries commercial assetization for the order and starts technical assetization to create or update its fulfillment assets.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS
NEEDED
To create or update assets from an order:	

The Assetize Order permission set from the Revenue Lifecycle Management permission sets.

The user who submits an order needs this permission set so products are assetized automatically upon fulfillment. See Permission Sets in Dynamic Revenue Orchestrator. This requirement also applies to users, integration users included, who invokes this action directly for recovery. The same permission set apply to direct API calls.

During commercial assetization, Salesforce creates or updates assets from the order line items. During technical assetization, Dynamic Revenue Orchestrator (DRO) creates or updates fulfillment assets from the fulfillment order line items.

Use this procedure when the fulfillment plan has completed but the order's Orchestration Submission Status is Assetization Failed. Also use it when Salesforce or DRO didn't create the expected assets or fulfillment assets. For the meaning of other order statuses, see Order Submission to Dynamic Revenue Orchestrator. Before you retry assetization, correct the configuration, data, permission, or status issue that caused the failure.

IMPORTANT Don't invoke Submit Sales Transaction to retry assetization for an order already submitted for orchestration. The action validates the order's Orchestration Submission Status before doing any work and always rejects the resubmission with the DRO_ORDER_ORCH_SUBM_STATUS_INCOMPATIBLE_ERROR error to prevent creating a duplicate fulfillment plan. This rejection applies whether the status is Completed, Assetization Failed, or Submitted.
NOTE The Retry action for a failed fulfillment step doesn't retry assetization after the fulfillment plan is complete. See Retry or Complete Multiple Failed Fulfillment Steps.
On the order record, confirm that Orchestration Submission Status is Assetization Failed.
If the field isn't on the record page, add it to the Order page layout.
Identify the failed phase and correct the cause of the failure.
Assets created from order line items appear on the Assets tab of the related account. Fulfillment assets created from fulfillment order line items appear in the Related Tab's Fulfillment Asset section.
Send a POST request from an authenticated REST client to the Create or Update Asset from Order standard action.
/services/data/vXX.X/actions/standard/createOrUpdateAssetFromOrder

In the request body, replace ORDER_ID with the ID of the order to assetize. The order must be in the Activated state. The action rejects the request for an order in any other state.

{
  "inputs": [
    {
      "orderId": "ORDER_ID"
    }
  ]
}
Review the action response to confirm that DRO accepted the request.
Commercial assetization runs before technical assetization. Technical assetization can continue asynchronously after the Create or Update Asset from Order action returns.
Wait until Orchestration Submission Status is Completed and verify that DRO created or updated the expected assets and fulfillment assets.
DRO sets the status to Completed after commercial and technical assetization complete successfully.

If commercial assetization already completed successfully for the order, invoking the Create or Update Asset from Order action again doesn't rerun technical assetization.

After the retry, check the existing Fulfillment Asset for these problems.

It's inactive.
Its quantity is zero.
It's missing its expected relationship to the Asset.

If you see any of these problems, contact Salesforce Support before retrying again.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_retry_assetization_for_an_order.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
