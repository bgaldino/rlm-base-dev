---
page_id: billing_sforce_api_objects_refund_line_payment.htm
title: Billing Fields on RefundLinePayment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_refund_line_payment.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-11-23
---

# Billing Fields on RefundLinePayment

Standard fields extend the Refund Line Payment object for use in Billing to represent information about accounting periods for legal entities. This object is available in API version 64.0 and later.

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the Payment Operations User permission set to access this object.

## Fields

### LegalEntityAccountingPeriodId

**Type:** reference

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The legal entity accounting period related to the refund.

This field is a relationship field.

**Relationship Name:** LegalEntityAccountingPeriod

**Refers To:** LegalEntityAccountingPeriod

### LegalEntityId

**Type:** reference

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The legal entity related to the refund.

This field is a relationship field.

**Relationship Name:** LegalEntity

**Refers To:** LegalEntity

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[RefundLinePaymentHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object."):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_refund_line_payment.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
