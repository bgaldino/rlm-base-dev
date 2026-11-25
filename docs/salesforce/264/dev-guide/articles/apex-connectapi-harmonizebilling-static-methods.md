---
page_id: apex-connectapi-harmonizebilling-static-methods
title: HarmonizeBilling Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-harmonizebilling-static-methods.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-connect-api-namespace
legacy_page_id: apex_ConnectAPI_HarmonizeBilling_static_methods.htm
fetched_at: 2026-11-25
---

# HarmonizeBilling Class

Update the status of the invoice from Draft to Posted by using the HarmonizeBilling class.

## Namespace

[ConnectApi](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_classes_connect_api.htm)

## HarmonizeBilling Methods

These methods are for `HarmonizeBilling`. All methods are static.

- 

**[postDraftInvoices(inputRequest)](#postdraftinvoicesinputrequest)**

Update the status of the invoice from Draft to Posted.

### postDraftInvoices(inputRequest)

Update the status of the invoice from Draft to Posted.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RevenueAsyncRepresentation postDraftInvoices(ConnectApi.InvoiceDraftToPostedInputRequest inputRequest)`

#### Parameters

***inputRequest***

Type: [`ConnectApi.InvoiceDraftToPostedInputRequest`](./apex-connectapi-input-invoice-draft-to-posted.md)

Input representation of the details of the draft invoice that’s posted.

#### Return Value

Type: [`ConnectApi.RevenueAsyncRepresentation`](./apex-connectapi-output-revenue-async.md)

#### Usage

You need the Billing Operations User permission set to use this method.

This method calls an external tax engine to calculate taxes for the draft invoice, posts the invoice, and updates the related billing schedules and billing periods.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-harmonizebilling-static-methods.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
