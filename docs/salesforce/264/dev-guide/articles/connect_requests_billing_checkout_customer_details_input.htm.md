---
page_id: connect_requests_billing_checkout_customer_details_input.htm
title: Billing Checkout Customer Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_checkout_customer_details_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_billing_checkout_input.htm
fetched_at: 2026-11-23
---

# Billing Checkout Customer Details Input

Input representation of customer details used to create a customer when accountId isn't provided.

## JSON Example

```
{
  "companyName": "Acme Corporation",
  "currencyIsoCode": "USD",
  "email": "billing@acme.example.com",
  "website": "https://www.acme.example.com"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `company​Name` | String | Name of the customer's company. | Optional | 68.0 |
| `currency​Iso​Code` | String | ISO currency code for the customer. | Optional | 68.0 |
| `email` | String | Email address of the customer. | Optional | 68.0 |
| `website` | String | Website of the customer. | Optional | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_checkout_customer_details_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
