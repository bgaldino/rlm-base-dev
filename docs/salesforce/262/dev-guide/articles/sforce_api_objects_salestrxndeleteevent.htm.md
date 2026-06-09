---
page_id: sforce_api_objects_salestrxndeleteevent.htm
title: SalesTrxnDeleteEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_salestrxndeleteevent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# SalesTrxnDeleteEvent

Represents the platform event that triggers the deletion of sales transaction
fulfillment request records when the corresponding reference records are deleted. This
object is available in API version 64.0 and later.

## Supported Calls

`create()`,
`describeSObjects()`

## Fields

| Field | Details |
| --- | --- |
| ReferenceObjectIdentifier | Type  string  Properties  Create, Nillable  Description  Object identifier for the sales transaction fulfillment request to be deleted. |
