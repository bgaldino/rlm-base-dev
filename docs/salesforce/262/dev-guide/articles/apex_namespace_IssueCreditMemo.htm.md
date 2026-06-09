---
page_id: apex_namespace_IssueCreditMemo.htm
title: IssueCreditMemo Namespace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_IssueCreditMemo.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_reference.htm
fetched_at: 2026-06-09
---

# IssueCreditMemo Namespace

Issue credit memos from disputed invoices. Use this namespace to create and apply credit
memos against invoices or invoice lines based on dispute adjustments.

You can access this namespace if Dispute Management is enabled in Billing.

The
`IssueCreditMemo` namespace includes these
classes.

- **[CreditLineRequestInputRepresentations Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm)**  
  Represents a single line-level credit request. Specifies the invoice line to credit, the amount to apply, and an optional description.
- **[CreditRequestInputRepresentations Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm)**  
  Represents a credit request for an invoice. Contains invoice and dispute identifiers, total credit amount, category, and line-level credit details for issuing a credit memo.
- **[CreditResponseOutputRepresentations Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm)**  
  Represents the result of a credit memo operation. Indicates success or failure and any additional information or message.
