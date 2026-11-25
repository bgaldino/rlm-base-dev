---
page_id: billing-std-objects-parent
title: Billing Standard Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-std-objects-parent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-overview
legacy_page_id: billing_std_objects_parent.htm
fetched_at: 2026-11-25
---

# Billing Standard Objects

The Billing data model provides objects and fields to manage billing and tax configurations, credit memos, and invoices, and accounting periods for legal entities.

- 

**[AccountingPeriod](./sforce-api-objects-accountingperiod.md)**

Represents information about a time period for which businesses prepare reports and analyze performance. Each billing transaction is associated with an accounting period. This object is available in API version 62.0 and later.

- 

**[BillingArrangement](./sforce-api-objects-billingarrangement.md)**

Represents the arrangement for invoicing a transaction’s billing amount to one or more accounts. The arrangement specifies whether the total amount must be invoiced to the owning account or a different billing account, or whether the invoices must be split among multiple billing accounts. This object is available in API version 66.0 and later.

- 

**[BillingArrangementLine](./sforce-api-objects-billingarrangementline.md)**

Represents the billing account, billing profile, and the percentage of billing amount to be invoiced. Each billing arrangement line results in a separate invoice addressed to the selected billing account. This object is available in API version 66.0 and later.

- 

**[BillingBatchScheduler](./sforce-api-objects-billingbatchscheduler.md)**

Represents a scheduled processing job that triggers recurring invoice batch runs. This object is available in API version 62.0 and later.

- 

**[BillingBatchFilterCriteria](./sforce-api-objects-billingbatchfiltercriteria.md)**

Represents the filter that all eligible billing schedules must satisfy in order to be picked up by an invoice run. This object is available in API version 62.0 and later.

- 

**[BillingForecast](./sforce-api-objects-billingforecast.md)**

Represents forecasted invoice lines generated from billing schedules before actual invoicing occurs. This object is available in API version 68.0 and later.

- 

**[BillingMilestonePlan](./sforce-api-objects-billingmilestoneplan.md)**

Represents a structured approach to invoicing where invoices are scheduled based on predefined milestones. This object is available in API version 63.0 and later.

- 

**[BillingMilestonePlanItem](./sforce-api-objects-billingmilestoneplanitem.md)**

Represents a specific billing milestone within the billing milestone plan that’s used to manage and track billing based on the completion of certain deliverables or stages. This object is available in API version 63.0 and later.

- 

**[BillingPeriodItem](./sforce-api-objects-billingperioditem.md)**

Represents a payment period for an invoice. The billing period item is used to pass billing information to an invoice line. This object is available in API version 62.0 and later.

- 

**[BillingPolicy](./sforce-api-objects-billingpolicy.md)**

Represents information about a set of billing treatments that define the rules to invoice a customer for an order item. This object is available in API version 62.0 and later.

- 

**[BillingSchedule](./sforce-api-objects-billingschedule.md)**

Represents information about the order item that’s used in the invoicing process. This object is available in API version 62.0 and later.

- 

**[BillingScheduleGroup](./sforce-api-objects-billingschedulegroup.md)**

Represents a consolidated view of all the billing schedules related to the order items generated from one asset, including new orders and amendment orders. This object is available in API version 62.0 and later.

- 

**[BillingTreatment](./sforce-api-objects-billingtreatment.md)**

Represents information about the billing of an order item. This object is available in API version 62.0 and later.

- 

**[BillingTreatmentItem](./sforce-api-objects-billingtreatmentitem.md)**

Represents information about allocation of the total amount of an order item to billing schedules throughout the order item’s lifecycle. This object is available in API version 62.0 and later.

- 

**[BsgRelationship](./sforce-api-objects-bsgrelationship.md)**

Represents a relationship between billing schedule groups to support bundles where one parent billing schedule group has multiple child billing schedule groups. This object is available in API version 62.0 and later.

- 

**[CaseServiceProcessExtension](./sforce-api-objects-caseserviceprocessextension.md)**

Represents additional information for a case record based on the type of service process for which the case was raised. This object is available in API version 67.0 and later.

- 

**[CreditMemo](./sforce-api-objects-creditmemo.md)**

Represents a document that’s used to reduce the amount that a buyer owes a seller under the terms of an earlier invoice. This object is available in API version 62.0 and later.

- 

**[CreditMemoAddressGroup](./sforce-api-objects-creditmemoaddressgroup.md)**

Represents the storage of the buyer’s address information, which is used to determine the tax credit amount for a buyer when a credit memo is issued. This object is available in API version 62.0 and later.

- 

**[CreditMemoInvApplication](./sforce-api-objects-creditmemoinvapplication.md)**

Represents information about the application of a credit memo to an invoice. This object is available in API version 62.0 and later.

- 

**[CreditMemoLine](./sforce-api-objects-creditmemoline.md)**

Represents the product, service, adjustment, or tax line items included in a credit memo. This object is available in API version 62.0 and later.

- 

**[CreditMemoLineInvoiceLine](./sforce-api-objects-creditmemolineinvoiceline.md)**

Represents a junction between a credit memo line and an invoice line. This object is available in API version 62.0 and later.

- 

**[CreditMemoLineTax](./sforce-api-objects-creditmemolinetax.md)**

Represents tax information of a credit memo line of type `Tax`. This object is available in API version 62.0 and later.

- 

**[DebitMemo](./sforce-api-objects-debitmemo.md)**

Represents the document used to charge an additional amount to a buyer by a seller. An invoice is generated for the debit memo in the next invoice run. This object is available in API version 65.0 and later.

- 

**[DebitMemoAddress](./sforce-api-objects-debitmemoaddress.md)**

Represents the buyer’s address information, which is used to determine the tax amount for a buyer when a debit memo is issued. This object is available in API version 65.0 and later.

- 

**[DebitMemoLine](./sforce-api-objects-debitmemoline.md)**

Represents the additional charge amount that the buyer must pay for the product, service, or debit memo line tax that’s related to the debit memo. This object is available in API version 65.0 and later.

- 

**[DebitMemoLineTax](./sforce-api-objects-debitmemolinetax.md)**

Represents the tax information for a debit memo line. This object is available in API version 66.0 and later.

- 

**[GeneralLedgerAccount](./sforce-api-objects-generalledgeraccount.md)**

Represents information about the accounting codes, types, and names that are used to store and organize financial transactions. This object is available in API version 63.0 and later.

- 

**[GeneralLedgerAcctAsgntRule](./sforce-api-objects-generalledgeracctasgntrule.md)**

Represents information about the rule based on which general ledger accounts are assigned to transaction journals that are created for billing transactions. This object is available in API version 63.0 and later.

- 

**[GeneralLdgrAcctPrdSummary](./sforce-api-objects-generalldgracctprdsummary.md)**

Represents a junction between a general ledger account and a legal entity accounting period. Stores information about the total credit amount, total debit amount, opening balance, and closing balance of a general ledger account for a specific legal entity accounting period. This object is available in API version 65.0 and later.

- 

**[GeneralLedgerJrnlEntryRule](./sforce-api-objects-generalledgerjrnlentryrule.md)**

Represents information about the transaction journal entry rule, based on which transaction journals are created for the selected credit and debit general ledger accounts, transaction amount field, and percentage. This object is available in API version 65.0 and later.

- 

**[InvBatchDraftToPostedRun](./sforce-api-objects-invbatchdrafttopostedrun.md)**

Represents information about the batch job that posts all invoices with the status as `Draft` that are generated by the invoice batch run associated with the billing schedule. This object is available in API version 62.0 and later.

- 

**[Invoice](./sforce-api-objects-invoice.md)**

Represents information about a financial document describing the total amount a buyer must pay for provided products or services. This object is available in API version 62.0 and later.

- 

**[InvoiceAddressGroup](./sforce-api-objects-invoiceaddressgroup.md)**

Represents the storage of the buyer’s address information. This object is available in API version 62.0 and later.

- 

**[InvoiceBatchRun](./sforce-api-objects-invoicebatchrun.md)**

Represents a batch processing job in Billing. During an invoice batch run, all billing schedules that meet the specified criteria are processed, resulting in the generation of invoices. This object is available in API version 62.0 and later.

- 

**[InvoiceBatchRunCriteria](./sforce-api-objects-invoicebatchruncriteria.md)**

Represents a batch processing job and its required criteria in Billing. During an invoice batch run, all billing schedules that meet the specified criteria are processed, resulting in the generation of invoices. This object is available in API version 62.0 and later.

- 

**[InvoiceBatchRunRecovery](./sforce-api-objects-invoicebatchrunrecovery.md)**

Represents information about the recovery procedure of an invoice batch run. This object is available in API version 62.0 and later.

- 

**[InvoiceDocument](./sforce-api-objects-invoicedocument.md)**

Represents the PDF document generated for an invoice. This object is available in API version 63.0 and later.

- 

**[InvoiceLine](./sforce-api-objects-invoiceline.md)**

Represents the amount that a buyer must pay for a product, service, or fee. Invoice lines are created based on the amount of an order line. This object is available in API version 62.0 and later.

- 

**[InvoiceLineRelationship](./sforce-api-objects-invoicelinerelationship.md)**

Represents a relationship between invoice line items to support bundles where one parent invoice line has multiple child invoice lines. This object is available in API version 62.0 and later.

- 

**[InvoiceLineTax](./sforce-api-objects-invoicelinetax.md)**

Represents tax information of an invoice line of type `Tax`. This object is available in API version 62.0 and later.

- 

**[LegalEntity](./sforce-api-objects-legalentity.md)**

Represents the way an organization is structured. An organization can be a single legal entity or it can comprise more than one legal entity. This object is available in API version 62.0 and later.

- 

**[LegalEntyAccountingPeriod](./sforce-api-objects-legalentyaccountingperiod.md)**

Represents a junction between a legal entity and an accounting period. This object is available in API version 62.0 and later.

- 

**[PaymentAdviceInvoiceRecile](./sforce-api-objects-paymentadviceinvoicerecile.md)**

Represents an invoice match with a payment advice line, linking a payment advice line to an open invoice. This object is available in API version 68.0 and later.

- 

**[PaymentAdviceReconciliation](./sforce-api-objects-paymentadvicereconciliation.md)**

Represents the reconciliation of a payment advice with a bank transaction and a resolved account, including match confidence and the reviewer’s decision. This object is available in API version 68.0 and later.

- 

**[PaymentBatchRun](./sforce-api-objects-paymentbatchrun.md)**

Represents a batch processing job that processes payments in Billing. During a payment batch run, all the payment schedules that meet the specified criteria are processed and the corresponding Payment records are created. These payments are then applied to invoices or invoice lines. This object is available in API version 64.0 and later.

- 

**[PaymentLineInvoiceLine](./sforce-api-objects-paymentlineinvoiceline.md)**

Represents information about a payment line that’s applied to or unapplied from an invoice line. This object is available in API version 64.0 and later.

- 

**[PaymentRetryRule](./sforce-api-objects-paymentretryrule.md)**

Represents the specific payment retry rule for a failed payment schedule item. Each rule defines actionable parameters such as the maximum number of retries for the failed records and time intervals between subsequent retry attempts. This object is available in API version 66.0 and later.

- 

**[PaymentRetryRuleSet](./sforce-api-objects-paymentretryruleset.md)**

Represents the payment retry rule definition that defines how failed payments are retried based on the error codes across various retry categories. This object is available in API version 66.0 and later.

- 

**[PaymentSchedule](./sforce-api-objects-paymentschedule.md)**

Represents information about a set of payments that a customer wants to collect at different times for a certain record. A schedule contains one or more payment schedule items, where each item represents one payment to be processed. Each of a schedule’s items can have different payment configuration fields, such as payment methods, payment dates, and payment accounts. When a payment scheduler launches a payment run, the run evaluates active payment schedule items, and picks them up for payment processing if they match the scheduler’s payment criteria. This object is available in API version 64.0 and later.

- 

**[PaymentSchedulePolicy](./sforce-api-objects-paymentschedulepolicy.md)**

Represents information about the configuration for the payment schedule. This object is available in API version 64.0 and later.

- 

**[PaymentScheduleTreatment](./sforce-api-objects-paymentscheduletreatment.md)**

Represents information about the processing of payment schedules including the payment method and the payment amount for the payment schedule. This object is available in API version 64.0 and later.

- 

**[PaymentScheduleTreatmentDtl](./sforce-api-objects-paymentscheduletreatmentdtl.md)**

Represents information about the processing of payment schedules after the corresponding invoices are posted. This object is available in API version 64.0 and later.

- 

**[PymtSchdDistributionMethod](./sforce-api-objects-pymtschddistributionmethod.md)**

Represents information about the partial payments that the total payment is divided into. This object is available in API version 64.0 and later.

- 

**[PaymentScheduleItem](./sforce-api-objects-paymentscheduleitem.md)**

Represents information about a payment to be processed. Each schedule item can have different payment configuration fields, such as payment methods, payment dates, and payment accounts. When a payment scheduler launches a payment run, the run evaluates active payment schedule items, and picks them up for payment processing if they match the scheduler’s payment criteria. This object is available in API version 64.0 and later.

- 

**[PaymentTerm](./sforce-api-objects-paymentterm.md)**

Represents an agreement between a buyer and a seller about when payment is due for an invoice. This object is available in API version 62.0 and later.

- 

**[PaymentTermItem](./sforce-api-objects-paymenttermitem.md)**

Represents configuration of a payment term. This object is available in API version 62.0 and later.

- 

**[RefundLineCreditMemo](./sforce-api-objects-refundlinecreditmemo.md)**

Represents a junction between a refund and a credit memo. This object is available in API version 68.0 and later.

- 

**[RefundLineCreditMemoLine](./sforce-api-objects-refundlinecreditmemoline.md)**

Represents a junction between a refund and a credit memo line. This object is available in API version 68.0 and later.

- 

**[RevenueTransactionErrorLog](./sforce-api-objects-revenuetransactionerrorlog.md)**

Represents the details of errors that occurred during the processing of a request. The error record persists until a new error with the same category, primary record, and, if necessary, related record occurs. This object is available in API version 62.0 and later.

- 

**[SeqPolicySelectionCondition](./sforce-api-objects-seqpolicyselectioncondition.md)**

Represents the condition used to determine which sequence policy is applied to a record. This object is available in API version 65.0 and later.

- 

**[SequenceGapReconciliation](./sforce-api-objects-sequencegapreconciliation.md)**

Represents a missing sequence value identified during reconciliation, which can be used later to ensure there are no gaps in the sequence policy numbers. This object is available in API version 65.0 and later.

- 

**[SequencePolicy](./sforce-api-objects-sequencepolicy.md)**

Represents the configuration of rules and parameters for generating unique, sequential numbers for records. Stores settings such as numbering patterns, prefixes, suffixes, sequence start numbers, increment values, and filter criteria to ensure accurate and compliant numbering. This object is available in API version 65.0 and later.

- 

**[TaxEngine](./sforce-api-objects-taxengine.md)**

Represents information about an instance of a tax engine provider as well as the merchant credentials for that specific instance. This object is available in API version 62.0 and later.

- 

**[TaxEngineInteractionLog](./sforce-api-objects-taxengineinteractionlog.md)**

Represents a record of a communication with an external tax engine following a tax calculation request.  This object is available in API version 62.0 and later.

- 

**[TaxEngineProvider](./sforce-api-objects-taxengineprovider.md)**

Represents general information about a service that manages a tax engine. Tax engine providers have a one-to-many relationship with tax engines, where the tax engine record represents a specific configuration of a tax engine that can be assigned to multiple order items. This object is available in API version 62.0 and later.

- 

**[TaxPolicy](./sforce-api-objects-taxpolicy.md)**

Represents information about a group of tax treatments, where each treatment represents parameters to determine how a particular product is taxed for a transaction line item. Tax policies are related to products, which pass the policy on to the resulting order items and in turn the billing schedules. This object is available in API version 62.0 and later.

- 

**[TaxTreatment](./sforce-api-objects-taxtreatment.md)**

Represents information about tax calculation by external engines. Each product requires a tax policy to determine whether to apply tax. Each tax policy requires at least one tax treatment. The tax treatments determine how taxable products are taxed. This object is available in API version 62.0 and later.

- 

**[Tax Treatment Item](./sforce-api-objects-taxtreatmentitem.md)**

Represents tax code information that’s used to calculate tax for a product by a specific tax engine. This object is available in API version 66.0 and later.

**See Also**

- [*Object Reference for the platform*: Overview of Salesforce Objects and Fields](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_concepts.htm)

- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_quickstart_intro.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-std-objects-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
