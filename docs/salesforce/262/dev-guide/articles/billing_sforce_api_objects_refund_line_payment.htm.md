---
page_id: billing_sforce_api_objects_refund_line_payment.htm
title: Billing Fields on RefundLinePayment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_refund_line_payment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-06-09
---

# Billing Fields on RefundLinePayment

Standard fields extend the Refund Line Payment object for use in
Billing to represent information about accounting periods for legal entities. This
object is available in API version 64.0 and later.

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the
Payment Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity accounting period related to the refund.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntityAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity related to the refund.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
