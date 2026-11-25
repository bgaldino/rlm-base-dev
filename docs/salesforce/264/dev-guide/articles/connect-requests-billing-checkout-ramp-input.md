---
page_id: connect-requests-billing-checkout-ramp-input
title: Billing Checkout Ramp Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-billing-checkout-ramp-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: connect-requests-billing-checkout-line-item-input
legacy_page_id: connect_requests_billing_checkout_ramp_input.htm
fetched_at: 2026-11-25
---

# Billing Checkout Ramp Input

Input representation of a ramp period describing a change in quantity or price for a line item over time.

## JSON Example

```
{
  "productId": "01txx0000004C91",
  "transactionId": "TXN-RAMP-001",
  "startDate": "2026-01-01",
  "endDate": "2026-06-30",
  "quantity": 5,
  "unitPrice": 90.00,
  "netUnitPrice": 81.00,
  "lineTotal": 450.00,
  "sellingModelType": "TermDefined",
  "periodBoundary": "DayOfPeriod",
  "billingDayOfMonth": 1,
  "billingTermUnit": "Month",
  "billingTerm": 6,
  "taxTreatmentId": "0cXxx0000004C93",
  "billingTreatmentId": "0cYxx0000004C94"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Day​Of​Month` | Integer | The day of the month a recurring billing process is scheduled to occur for the transaction. Required when `periodBoundary` is `DayOfPeriod`. | Optional | 68.0 |
| `billing​Term` | Integer | Number of billing term units. Must be `1` for `OneTime` selling models. | Optional | 68.0 |
| `billing​Term​Unit` | String | Unit of measurement for the billing term. Required when `sellingModelType` is `TermDefined` or `Evergreen`. Valid values are `OneTime`, `Day`, `Week`, `Month`, `Quarter`, `SemiAnnual`, `Year`, or `BillingMilestonePlan`. | Optional | 68.0 |
| `billing​Treatment​Id` | String | ID of the billing treatment used to create the billing schedule for the transaction. If you don’t specify a `billingTreatmentId`, the org-default `billingTreatmentId` is considered. | Optional | 68.0 |
| `end​Date` | String | End date for this ramp period (YYYY-MM-DD). | Optional | 68.0 |
| `line​Total` | Double | Total price for this ramp period. | Required | 68.0 |
| `net​Unit​Price` | Double | Net unit price after discount calculation. Auto-calculated. | Optional | 68.0 |
| `period​Boundary` | String | Period boundary for the billing schedule. Required when `sellingModelType` is `TermDefined` or `Evergreen`. Valid values are `AlignToCalendar`, `Anniversary`, `DayOfPeriod`, or `LastDayOfPeriod`. | Optional | 68.0 |
| `product​Id` | String | ID of the ramped product. | Optional | 68.0 |
| `quantity` | Integer | Quantity for this specific period. | Optional | 68.0 |
| `selling​Model​Type` | String | Selling model of the ramp segment. Defaults to `OneTime`. A `TermDefined` or `Evergreen` value requires `billingTermUnit`. Valid values are `OneTime`, `TermDefined`, or `Evergreen`. | Optional | 68.0 |
| `start​Date` | String | Start date for this ramp period (YYYY-MM-DD). | Optional | 68.0 |
| `tax​Treatment​Id` | String | ID of the tax treatment used to calculate tax for the transaction. If you don’t specify a `taxTreatmentId`, the org-default `taxTreatmentId` is considered. | Optional | 68.0 |
| `transaction​Id` | String | Client-supplied transaction identifier for this line item. Used as the transaction ID on the generated billing transaction and as the grouping key for its ramp segments. Defaults to the product name or product ID when omitted. | Optional | 68.0 |
| `unit​Price` | Double | Price per unit before any discounts are applied. | Optional | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-billing-checkout-ramp-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
