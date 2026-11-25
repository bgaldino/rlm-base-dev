---
page_id: connect-requests-batch-invoice-scheduler-input
title: Batch Invoice Scheduler Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-batch-invoice-scheduler-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_batch_invoice_scheduler_input.htm
fetched_at: 2026-11-25
---

# Batch Invoice Scheduler Input

Input representation of the details of the request to create an invoice scheduler.

## JSON Example

This example shows a sample request to create an invoice scheduler that generates invoices once.

```
{
  "schedulerName": "InvoiceScheduler",
  "startDate": "2024-05-06",
  "invoiceStatus": "POSTED",
  "preferredTime": "00:45",
  "targetDate": "2024-05-22",
  "invoiceDate": "2024-05-22",
  "frequencyCadence": "Once",
  "frequencyCadenceOptions": {},
  "timezone": "Asia/Kolkata",
  "status": "Active",
  "filterCriteria": [
    {
      "operation": "InList",
      "value": "Batch 2,Batch 3,Batch 4",
      "criteriaSequence": 1,
      "objectName": "BillingSchedule",
      "fieldName": "InvoiceRunMatchingValue"
    },
    {
      "operation": "Equals",
      "value": "001xx000003GZG5AAO",
      "criteriaSequence": 2,
      "objectName": "BillingSchedule",
      "fieldName": "BillingAccount"
    },
    {
      "operation": "Equals",
      "value": "0fwxx0000000001AAA",
      "criteriaSequence": 3,
      "objectName": "BillingScheduleGroup",
      "fieldName": "LegalEntity"
    },
    {
      "operation": "InList",
      "value": "OneTime,Recurring",
      "criteriaSequence": 4,
      "objectName": "BillingSchedule",
      "fieldName": "BillingTermUnit"
    },
    {
      "operation": "Equals",
      "value": "USD",
      "criteriaSequence": 5,
      "objectName": "BillingSchedule",
      "fieldName": "Currency_Iso_code"
    }
  ]
}
```

This example shows a sample request to create an invoice scheduler that generates invoices daily.

```
{
  "schedulerName": "InvoiceScheduler",
  "startDate": "2024-05-06",
  "endDate": "2026-05-06",
  "invoiceStatus": "POSTED",
  "preferredTime": "00:45",
  "targetDateOffset": 0,
  "invoiceDateOffset": 0,
  "isInvoiceDateFromRunDate": true,
  "frequencyCadence": "Daily",
  "frequencyCadenceOptions": {},
  "timezone": "Asia/Kolkata",
  "status": "Active",
  "filterCriteria": [
    {
      "operation": "InList",
      "value": "Batch 2,Batch 3,Batch 4",
      "criteriaSequence": 1,
      "objectName": "BillingSchedule",
      "fieldName": "InvoiceRunMatchingValue"
    },
    {
      "operation": "Equals",
      "value": "001xx000003GZG5AAO",
      "criteriaSequence": 2,
      "objectName": "BillingSchedule",
      "fieldName": "BillingAccount"
    },
    {
      "operation": "Equals",
      "value": "0fwxx0000000001AAA",
      "criteriaSequence": 3,
      "objectName": "BillingScheduleGroup",
      "fieldName": "LegalEntity"
    },
    {
      "operation": "InList",
      "value": "OneTime,Recurring",
      "criteriaSequence": 4,
      "objectName": "BillingSchedule",
      "fieldName": "BillingTermUnit"
    },
    {
      "operation": "InList",
      "value": "USD",
      "criteriaSequence": 5,
      "objectName": "BillingSchedule",
      "fieldName": "Currency_Iso_code"
    }
  ]
}
```

This example shows a sample request to create an invoice scheduler that generates invoices weekly.

```
{
  "schedulerName": "InvoiceScheduler",
  "startDate": "2024-05-06",
  "endDate": "2026-05-06",
  "invoiceStatus": "POSTED",
  "preferredTime": "00:45",
  "targetDateOffset": 0,
  "invoiceDateOffset": 0,
  "isInvoiceDateFromRunDate": false,
  "frequencyCadence": "Weekly",
  "frequencyCadenceOptions": {
    "recursOnDay": "Sunday"
  },
  "timezone": "Asia/Kolkata",
  "status": "Active",
  "filterCriteria": [
    {
      "operation": "InList",
      "value": "Batch 2,Batch 3,Batch 4",
      "criteriaSequence": 1,
      "objectName": "BillingSchedule",
      "fieldName": "InvoiceRunMatchingValue"
    },
    {
      "operation": "Equals",
      "value": "001xx000003GZG5AAO",
      "criteriaSequence": 2,
      "objectName": "BillingSchedule",
      "fieldName": "BillingAccount"
    },
    {
      "operation": "Equals",
      "value": "0fwxx0000000001AAA",
      "criteriaSequence": 3,
      "objectName": "BillingScheduleGroup",
      "fieldName": "LegalEntity"
    },
    {
      "operation": "InList",
      "value": "OneTime,Recurring",
      "criteriaSequence": 4,
      "objectName": "BillingSchedule",
      "fieldName": "BillingTermUnit"
    },
    {
      "operation": "Equals",
      "value": "USD",
      "criteriaSequence": 5,
      "objectName": "BillingSchedule",
      "fieldName": "Currency_Iso_code"
    }
  ]
}
```

This example shows a sample request to create an invoice scheduler that generates invoices monthly on a specific date.

```
{
  "schedulerName": "InvoiceScheduler",
  "startDate": "2024-05-06",
  "endDate": "2026-05-06",
  "invoiceStatus": "POSTED",
  "preferredTime": "00:45",
  "targetDateOffset": 0,
  "invoiceDateOffset": 0,
  "isInvoiceDateFromRunDate": false,
  "frequencyCadence": "Monthly",
  "frequencyCadenceOptions": {
    "recurringSubType": "SpecificDate",
    "recursOnDate": "L-1",
    "shouldExcludeWkendAndHldy": true
  },
  "timezone": "Asia/Kolkata",
  "status": "Active",
  "filterCriteria": [
    {
      "operation": "InList",
      "value": "Batch 2,Batch 3,Batch 4",
      "criteriaSequence": 1,
      "objectName": "BillingSchedule",
      "fieldName": "InvoiceRunMatchingValue"
    },
    {
      "operation": "Equals",
      "value": "001xx000003GZG5AAO",
      "criteriaSequence": 2,
      "objectName": "BillingSchedule",
      "fieldName": "BillingAccount"
    },
    {
      "operation": "Equals",
      "value": "0fwxx0000000001AAA",
      "criteriaSequence": 3,
      "objectName": "BillingScheduleGroup",
      "fieldName": "LegalEntity"
    },
    {
      "operation": "InList",
      "value": "OneTime,Recurring",
      "criteriaSequence": 4,
      "objectName": "BillingSchedule",
      "fieldName": "BillingTermUnit"
    },
    {
      "operation": "Equals",
      "value": "USD",
      "criteriaSequence": 5,
      "objectName": "BillingSchedule",
      "fieldName": "Currency_Iso_code"
    }
  ]
}
```

This example shows a sample request to create an invoice scheduler that runs immediately.

```
{
    "schedulerName": "InvoiceScheduler",
    "status": "Draft",
    "invoiceStatus": "Posted",
    "frequencyCadenceOptions": {
        "shouldStartRunImmediately": true
    },
    "frequencyCadence": "Once",
    "targetDate": "2024-08-28",
    "invoiceDate": "2024-08-28",
    "filterCriteria": [
        {
            "operation": "InList",
            "value": "Batch 2,Batch 3,Batch 4",
            "criteriaSequence": 1,
            "objectName": "BillingSchedule",
            "fieldName": "InvoiceRunMatchingValue"
        },
        {
            "operation": "Equals",
            "value": "001xx000003GZG5AAO",
            "criteriaSequence": 2,
            "objectName": "BillingSchedule",
            "fieldName": "BillingAccount"
        },
        {
            "operation": "Equals",
            "value": "0fwxx0000000001AAA",
            "criteriaSequence": 3,
            "objectName": "BillingScheduleGroup",
            "fieldName": "LegalEntity"
        },
        {
            "operation": "InList",
            "value": "OneTime,Recurring",
            "criteriaSequence": 4,
            "objectName": "BillingSchedule",
            "fieldName": "BillingTermUnit"
        },
        {
            "operation": "Equals",
            "value": "USD",
            "criteriaSequence": 5,
            "objectName": "BillingSchedule",
            "fieldName": "Currency_Iso_code"
        }
    ]
}
```

This example shows a sample request to create an invoice scheduler where generating invoice documents is enabled and the invoice date offset is defined.

```
{
  "schedulerName": "InvoiceScheduler",
  "status": "Draft",
  "invoiceStatus": "Draft",
  "startDate": "2023-09-01",
  "endDate": "2026-09-17",
  "preferredTime": "00:15",
  "frequencyCadence": "Daily",
  "frequencyCadenceOptions": {
    "shouldExcludeWkendAndHldy": true,
    "shouldStartRunImmediately": false
  },
  "timezone": "America/Los_Angeles",
  "targetDateOffset": "2",
  "invoiceDateOffset": "4",
  "isInvoiceDateFromRunDate": false,
  "shouldRunDpeOnCore": false,
  "shouldGenerateInvoiceDocuments": true,
  "billingCycleCount": "4",
  "filterCriteria": [
    {
      "criteriaSequence": 1,
      "operation": "InList",
      "objectName": "BillingSchedule",
      "fieldName": "InvoiceRunMatchingValue",
      "value": "Batch 1"
    },
    {
      "criteriaSequence": 2,
      "operation": "InList",
      "objectName": "BillingSchedule",
      "fieldName": "BillingTermUnit",
      "value": "Usage"
    },
    {
      "criteriaSequence": 3,
      "operation": "InList",
      "objectName": "BillingSchedule",
      "fieldName": "Currency_Iso_code",
      "value": "JPY"
    }
  ]
}
```

This example shows a sample request to create an invoice scheduler that has the `jobType` property set to `Catchup`.

```
{
  "schedulerName": "InvoiceScheduler",
  "status": "Draft",
  "startDate": "2023-09-01",
  "preferredTime": "00:15",
  "frequencyCadence": "Once",
  "frequencyCadenceOptions": {
    "shouldExcludeWkendAndHldy": false,
    "shouldStartRunImmediately": false
  },
  "timezone": "America/Los_Angeles",
  "targetDate": "2026-09-25",
  "billingCycleCount": "4",
  "shouldCatchUpBillRun": true,
  "filterCriteria": [
    {
      "criteriaSequence": 1,
      "operation": "InList",
      "objectName": "BillingSchedule",
      "fieldName": "InvoiceRunMatchingValue",
      "value": "Batch 1"
    },
    {
      "criteriaSequence": 2,
      "operation": "InList",
      "objectName": "BillingSchedule",
      "fieldName": "BillingTermUnit",
      "value": "Usage"
    },
    {
      "criteriaSequence": 3,
      "operation": "InList",
      "objectName": "BillingSchedule",
      "fieldName": "Currency_Iso_code",
      "value": "JPY"
    }
  ],
  "jobType": "Catchup"
}
```

This example shows a sample request to create an invoice scheduler where the `targetDayOfMonth` and `targetMonthOffset` properties are defined.

```
{
  "schedulerName": "InvoiceScheduler",
  "status": "Active",
  "invoiceStatus": "Draft",
  "startDate": "2020-09-01",
  "endDate": "2026-09-10",
  "preferredTime": "00:00",
  "frequencyCadence": "Monthly",
  "frequencyCadenceOptions": {
    "recurringSubType": "Every",
    "recursOn": "First",
    "recursOnDay": "Monday",
    "shouldExcludeWkendAndHldy": true,
    "shouldStartRunImmediately": false
  },
  "timezone": "America/Los_Angeles",
  "invoiceDateOffset": "5",
  "isInvoiceDateFromRunDate": true,
  "shouldRunDpeOnCore": false,
  "shouldGenerateInvoiceDocuments": false,
  "billingCycleCount": 1,
  "filterCriteria": [
    {
      "criteriaSequence": 1,
      "operation": "InList",
      "objectName": "BillingSchedule",
      "fieldName": "InvoiceRunMatchingValue",
      "value": "Batch 1"
    },
    {
      "criteriaSequence": 2,
      "operation": "InList",
      "objectName": "BillingSchedule",
      "fieldName": "BillingTermUnit",
      "value": "Usage"
    },
    {
      "criteriaSequence": 3,
      "operation": "InList",
      "objectName": "BillingSchedule",
      "fieldName": "Currency_Iso_code",
      "value": "INR"
    }
  ],
  "targetDayOfMonth": 3,
  "targetMonthOffset": 4
}
```

This example shows a sample request to create a forecast scheduler that runs immediately with the `shouldRecalculateAllForecastLn` property set to `true`.

```
{
  "schedulerName": "ForecastScheduler",
  "jobType": "Forecast",
  "status": "Active",
  "frequencyCadence": "Once",
  "frequencyCadenceOptions": {
    "shouldStartRunImmediately": true
  },
  "targetDate": "2026-09-04",
  "filterCriteria": [],
  "shouldRecalculateAllForecastLn": true
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​CycleCount` | Integer | Number of billing cycles or billing periods to be invoiced. | Optional | 68.0 |
| `endDate` | String | End date of the invoice scheduler. | Optional | 63.0 |
| `filter​Criteria` | [Batch Invoice Filter Criteria Input](./connect-requests-batch-invoice-filter-criteria-input.md)[] | List of line items of the filter criteria. | Optional | 62.0 |
| `frequency​Cadence` | String | Frequency to run the invoice scheduler. | Required | 62.0 |
| `frequency​Cadence​Options` | [Frequency Cadence Options](./connect-requests-frequency-cadence-options.md) | Frequency cadence options for the invoice scheduler. | Required | 62.0 |
| `invoice​Date` | String | Date shown on the invoice. This date is also used for tax calculations. | Required if the `frequency​Cadence` property is set to `Once`. | 62.0 |
| `invoiceDate​Offset` | Integer | Offset applied to the target date, which is the number of days added to or subtracted from the invoice date, to calculate the updated invoice date. | Required if the `frequency​Cadence` property is set to `Daily`, `Weekly`, or `Monthly`. | 62.0 |
| `invoice​Status` | String | Status of the invoice that specifies the expected invoice status from an invoice batch run. Valid values are `Draft` or `Posted`. | Required | 62.0 |
| `isInvoice​DateFrom​RunDate` | Boolean | Indicates whether the invoice date is applicable from the date when the invoice scheduler is run (`true`) or not (`false`). | Optional | 63.0 |
| `jobType` | String | Type of job the scheduler runs. Valid values are `Catchup`, `Forecast`, `Invoice`, or `Payment`. | Optional | 68.0 |
| `preferred​Time` | String | Preferred time for the invoice batch run. | Required | 62.0 |
| `scheduler​Name` | String | Name of the invoice scheduler, which must be unique in your org. | Required | 62.0 |
| `should​CatchUp​BillRun` | Boolean | Indicates whether the invoice batch run advances billing schedules to a target date without generating invoices for prior billing periods (`true`) or not (`false`). | Optional | 68.0 |
| `should​Generate​Invoice​Documents` | Boolean | Indicates whether invoice documents are automatically generated during batch processing for runs triggered by the scheduler (`true`) or not (`false`). | Optional | 68.0 |
| `should​Recalculate​AllForecastLn` | Boolean | Indicates whether to recalculate all forecast lines for all billing schedules regardless of forecast status (`true`) or only eligible ones (`false`). Applies only to forecast job runs. | Optional | 68.0 |
| `startDate` | String | Start date of the invoice scheduler. | Required | 62.0 |
| `status` | String | Status of the invoice scheduler. Valid values are `Draft`, `Active`, or `Inactive`. | Required | 62.0 |
| `target​Date` | String | Target date of the invoice batch run. Billing schedules having the next billing date before this date are picked up for invoicing. The target date must be less than or equal to the maximum allowed target date for the org. | Required if the `frequency​Cadence` property is set to `Once`. | 62.0 |
| `target​DateOffset` | Integer | Target date offset applied to the next invoice run date to calculate the target date. The offset is the number of days added to or subtracted from the next billing date. | Required if the `frequency​Cadence` property is set to `Daily`, `Weekly`, or `Monthly`. | 62.0 |
| `target​Day​OfMonth` | Integer | Day of the month to use for calculating the target date. Values are 1 through 28, -3 (third-to-last day), -2 (second-to-last day), or -1 (last day). | Optional | 68.0 |
| `target​Month​Offset` | Integer | Number of months relative to each scheduled run for calculating the target date. For example, 0 is the current month, 1 is the next month, and -1 is the previous month. | Optional | 68.0 |
| `timezone` | String | Time zone that’s applicable for the invoice scheduler. | Optional | 62.0 |

Valid values are:

- `Once`

- `Daily`

- `Weekly`

- `Monthly`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-batch-invoice-scheduler-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
