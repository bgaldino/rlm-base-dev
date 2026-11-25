---
page_id: connect-requests-billing-checkout-billing-contact-input
title: Billing Contact Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-billing-checkout-billing-contact-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: connect-requests-billing-checkout-input
legacy_page_id: connect_requests_billing_checkout_billing_contact_input.htm
fetched_at: 2026-11-25
---

# Billing Contact Input

Input representation of billing contact details used when billingProfileId isn’t provided. Creates the contact if it doesn’t exist.

## JSON Example

```
{
  "firstName": "Jane",
  "lastName": "Doe",
  "email": "jane.doe@example.com",
  "phone": "4155550100"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `email` | String | Email address of the billing contact. | Optional | 68.0 |
| `first​Name` | String | First name of the billing contact. | Optional | 68.0 |
| `last​Name` | String | Last name of the billing contact. | Optional | 68.0 |
| `phone` | String | Phone number of the billing contact. | Optional | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-billing-checkout-billing-contact-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
