---
page_id: apex-namespace-issuecreditmemo
title: IssueCreditMemo Namespace
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-issuecreditmemo.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-reference
legacy_page_id: apex_namespace_IssueCreditMemo.htm
fetched_at: 2026-11-25
---

# IssueCreditMemo Namespace

Issue credit memos from disputed invoices. Use this namespace to create and apply credit memos against invoices or invoice lines based on dispute adjustments.

You can access this namespace if Dispute Management is enabled in Billing.

The `IssueCreditMemo` namespace includes these classes.

- 

**[CreditLineRequestInputRepresentations Class](./apex-class-issuecreditmemo-creditlinerequestinputrepresentations.md#creditlinerequestinputrepresentations-class)**

Represents a single line-level credit request. Specifies the invoice line to credit, the amount to apply, and an optional description.

- 

**[CreditRequestInputRepresentations Class](./apex-class-issuecreditmemo-creditrequestinputrepresentations.md#creditrequestinputrepresentations-class)**

Represents a credit request for an invoice. Contains invoice and dispute identifiers, total credit amount, category, and line-level credit details for issuing a credit memo.

- 

**[CreditResponseOutputRepresentations Class](./apex-class-issuecreditmemo-creditresponseoutputrepresentations.md#creditresponseoutputrepresentations-class)**

Represents the result of a credit memo operation. Indicates success or failure and any additional information or message.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-issuecreditmemo.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
