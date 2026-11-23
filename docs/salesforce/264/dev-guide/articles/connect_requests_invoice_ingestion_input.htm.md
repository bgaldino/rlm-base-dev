---
page_id: connect_requests_invoice_ingestion_input.htm
title: Invoice Ingestion Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_invoice_ingestion_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Invoice Ingestion Input

Input representation of the details of the invoice to be processed. The details include the tax processing status, user preferences for tax callouts, and associated object graph representation.

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Splunk correlation ID to track the messages that are related to the request and are logged in Splunk by the different services involved in the request. If the ID isn’t specified, the service creates a random Universally Unique Identifier (UUID). | Optional | 63.0 |
| `graph` | [Object Graph Input](./connect_requests_object_graph_input.htm.md) | Graph that represents the invoice structure for invoice ingestion or generation. The supported Graph attribute types for invoice ingestion are Account, Contact, Invoice, InvoiceLine, InvoiceLineTax, and InvoiceAddressGroup. See [Graph Record for Invoice Ingestion](./connect_requests_graph_record_input.htm.md "A Graph record is an object that’s a part of the graph structure, representing both the fields and relationships among different objects. Each record in the graph can contain attributes, which are fields of the object, and references to other related records."). | Required | 63.0 |
| `should​CalculateTax` | Boolean | Indicates whether the estimated tax must be calculated for the ingested invoice (`true`) or not (`false`). The default value is `false`. | Optional | 63.0 |
| `taxCalculation​Status` | String | Status of the tax calculation, which is saved on the invoice line. Valid values are `Estimated`, `Pending`, or `Posted`. The default value is `Pending`. | Optional | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_invoice_ingestion_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
