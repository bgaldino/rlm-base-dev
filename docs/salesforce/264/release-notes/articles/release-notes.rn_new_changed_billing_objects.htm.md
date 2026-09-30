---
article_id: release-notes.rn_new_changed_billing_objects.htm
title: New and Changed Objects for Billing
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_new_changed_billing_objects.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing.htm
fetched_at: 2026-09-30
---

# New and Changed Objects for Billing

Store and access more data with these new and changed Billing objects.

New Objects
Invoice Management
Get information about forecasted invoice lines generated from billing schedules before actual invoicing occurs
Use the new BillingForecast object.
Payments and Refunds
Get information about the match between a payment advice line and an open invoice
Use the new PaymentAdviceInvoiceRecile object.
Get information about the reconciliation of a payment advice with a bank transaction and a resolved account, including match confidence and the reviewer’s decision
Use the new PaymentAdviceReconciliation object.
Get information about a refund that’s applied to a credit memo
Use the new RefundLineCreditMemo object.
Get information about a refund that’s applied to a credit memo line
Use the new RefundLineCreditMemoLine object.
Changed Objects
Billing Schedules
Stores the number of billing frequency units to combine into a billing period item
Use the new BillingTerm field on the existing AssetActionSource, OrderItem, and QuoteLineItem objects.
Indicates that the billing period item was processed by a catch-up bill run
Use the new supported value Catch-Up Processed in the existing Status field on the BillingPeriodItem object.
Specifies the lifecycle of the billing schedule in a forecast run
Use the new ForecastStatus field on the existing BillingSchedule object.
Stores the invoice batch run associated with the billing schedule that’s used for forecasting
Use the new InvoiceBatchRun field on the existing BillingSchedule object.
Stores the target date used by the most recent forecast batch run that processed the billing schedule
Use the new LastForecastRunTargetDate field on the existing BillingSchedule object.
Stores the ID of the ramp deal that groups billing schedules belonging to the same ramped product
Use the new RampIdentifier field on the existing BillingSchedule object.
Stores the ID of the ramp segment in which the billing schedule is grouped
Use the new SegmentIdentifier field on the existing BillingSchedule object.
Stores the name of the ramp segment
Use the new SegmentName field on the existing BillingSchedule object.
Stores the type of the ramp segment
Use the new SegmentType field on the existing BillingSchedule object.
Invoice Management
Specify whether the invoice scheduler must generate invoice documents
Use the new ShouldGenerateInvoiceDocuments field on the existing BillingBatchScheduler object.
Stores the ID of the document generation batch process that’s used to generate documents for the invoice batch run
Use the new DocGenerationBatchProcess field on the existing InvoiceBatchRun object.
Stores the end date of the forecast invoice batch run
Use the new ForecastEndDate field on the existing InvoiceBatchRun object.
Stores the start date of the forecast invoice batch run
Use the new ForecastStartDate field on the existing InvoiceBatchRun object.
Specify the job type for the batch run
Use the new JobType field on the existing InvoiceBatchRun object.
Indicates that the invoice batch run has started creating catch-up billing schedules
Use the new supported value Catch-Up Billing Schedules Started in the existing StatusSubtype field on the InvoiceBatchRun object.
Indicates that the invoice batch run is creating catch-up billing schedules
Use the new supported value Catch-Up Billing Schedules In Progress in the existing StatusSubtype field on the InvoiceBatchRun object.
Indicates that the invoice batch run has completed creating catch-up billing schedules
Use the new supported value Catch-Up Billing Schedules Completed in the existing StatusSubtype field on the InvoiceBatchRun object.
Indicates that the invoice batch run is summarizing catch-up billing schedules
Use the new supported value Catch-Up Billing Schedules Summarization In Progress in the existing StatusSubtype field on the InvoiceBatchRun object.
Stores the total charge amount of all billing forecast lines generated during the batch run
Use the new TotalForecastedAmount field on the existing InvoiceBatchRun object.
Stores the number of billing forecast lines generated for the forecast invoice batch run
Use the new TotalForecastLines field on the existing InvoiceBatchRun object.
Stores the number of billing periods to process per billing schedule
Use the new BillingPeriodCount field on the existing InvoiceBatchRunCriteria object.
Specify whether the invoice batch run must advance billing schedules to a target date without generating invoices for prior billing periods
Use the new ShouldCatchUpBillRun field on the existing InvoiceBatchRunCriteria object.
Specify whether to include all billing schedules in the billing forecast run
Use the new ShouldRecalculateAllForecastLn field on the existing InvoiceBatchRunCriteria object.
Specify the day of the month to use as the target date
Use the new TargetDayOfMonth field on the existing InvoiceBatchRunCriteria object.
Specify the number of months offset to apply to the scheduled run date to calculate the target date
Use the new TargetMonthOffset field on the existing InvoiceBatchRunCriteria object.
Stores the total credit memo line amount that’s applied to the invoice line tax
Use the new NetCreditsApplied field on the existing InvoiceLineTax object.
Stores the total payment amount that’s applied to the invoice line tax
Use the new NetPaymentsApplied field on the existing InvoiceLineTax object.
Tax Management
Stores the API name of the custom metadata type that defines field mappings for tax callout requests and responses
Use the new CustomMetadataTypeApiName field on the existing TaxEngine object.
Stores the decision table that’s used by the revenue standard tax engine to calculate taxes
Use the new DecisionTable field on the existing TaxEngine object.
Payments and Refunds
Stores the date and time when the credit memo was locked
Use the new CreditMemoLockedDateTime field on the existing CreditMemo object.
Specify whether the credit memo is locked for editing
Use the new IsCreditMemoLocked field on the existing CreditMemo object.
Stores the saved payment method that’s used for the credit memo
Use the new SavedPaymentMethod field on the existing CreditMemo object.
Stores the refund amount that’s applied to the credit memo line
Use the new TotalAppliedRefundAmount field on the existing CreditMemoLine object.
Stores the refund amount that’s unapplied from the credit memo line
Use the new TotalUnappliedRefundAmount field on the existing CreditMemoLine object.
Stores the invoice line tax to which the credit memo line was applied or unapplied
Use the new InvoiceLineTax field on the existing CreditMemoLineInvoiceLine object.
Specifies the type of amount settled by the credit memo line that’s applied to the invoice line
Use the new SettlementType field on the existing CreditMemoLineInvoiceLine object.
Stores the invoice line tax to which the payment line was applied or unapplied
Use the new InvoiceLineTax field on the existing PaymentLineInvoiceLine object.
Specifies the type of amount settled by the payment line that’s applied to the invoice line
Use the new SettlementType field on the existing PaymentLineInvoiceLine object.
Specifies a unique code that identifies the primary reason for a refund
Use the new ReasonCode field on the existing Refund object.
Stores the record that the refund was issued against, such as an invoice, credit memo, or payment
Use the new ReferenceRecord field on the existing Refund object.
Collections
Stores the balance amount of the related invoice at the time the collection plan item is created
Use the new InitialInvoiceBalance field on the existing CollectionPlanItem object.
