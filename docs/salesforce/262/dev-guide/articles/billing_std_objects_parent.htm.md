---
page_id: billing_std_objects_parent.htm
title: Billing Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_std_objects_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_overview.htm
fetched_at: 2026-06-09
---

# Billing Standard Objects

The Billing data model provides objects and fields to manage billing and tax
configurations, credit memos, and invoices, and accounting periods for legal entities.

- **[AccountingPeriod](./sforce_api_objects_accountingperiod.htm.md)**  
  Represents information about a time period for which businesses prepare reports and analyze performance. Each billing transaction is associated with an accounting period. This object is available in API version 62.0 and later.
- **[BillingArrangement](./sforce_api_objects_billingarrangement.htm.md)**  
  Represents the arrangement for invoicing a transaction’s billing amount to one or more accounts. The arrangement specifies whether the total amount must be invoiced to the owning account or a different billing account, or whether the invoices must be split among multiple billing accounts. This object is available in API version 66.0 and later.
- **[BillingArrangementLine](./sforce_api_objects_billingarrangementline.htm.md)**  
  Represents the billing account, billing profile, and the percentage of billing amount to be invoiced. Each billing arrangement line results in a separate invoice addressed to the selected billing account. This object is available in API version 66.0 and later.
- **[BillingBatchScheduler](./sforce_api_objects_billingbatchscheduler.htm.md)**  
  Represents a scheduled processing job that triggers recurring invoice batch runs. This object is available in API version 62.0 and later.
- **[BillingBatchFilterCriteria](./sforce_api_objects_billingbatchfiltercriteria.htm.md)**  
  Represents the filter that all eligible billing schedules must satisfy in order to be picked up by an invoice run. This object is available in API version 62.0 and later.
- **[BillingMilestonePlan](./sforce_api_objects_billingmilestoneplan.htm.md)**  
  Represents a structured approach to invoicing where invoices are scheduled based on predefined milestones. This object is available in API version 63.0 and later.
- **[BillingMilestonePlanItem](./sforce_api_objects_billingmilestoneplanitem.htm.md)**  
  Represents a specific billing milestone within the billing milestone plan that’s used to manage and track billing based on the completion of certain deliverables or stages. This object is available in API version 63.0 and later.
- **[BillingPeriodItem](./sforce_api_objects_billingperioditem.htm.md)**  
  Represents a payment period for an invoice. The billing period item is used to pass billing information to an invoice line. This object is available in API version 62.0 and later.
- **[BillingPolicy](./sforce_api_objects_billingpolicy.htm.md)**  
  Represents information about a set of billing treatments that define the rules to invoice a customer for an order item. This object is available in API version 62.0 and later.
- **[BillingSchedule](./sforce_api_objects_billingschedule.htm.md)**  
  Represents information about the order item that's used in the invoicing process. This object is available in API version 62.0 and later.
- **[BillingScheduleGroup](./sforce_api_objects_billingschedulegroup.htm.md)**  
  Represents a consolidated view of all the billing schedules related to the order items generated from one asset, including new orders and amendment orders. This object is available in API version 62.0 and later.
- **[BillingTreatment](./sforce_api_objects_billingtreatment.htm.md)**  
  Represents information about the billing of an order item. This object is available in API version 62.0 and later.
- **[BillingTreatmentItem](./sforce_api_objects_billingtreatmentitem.htm.md)**  
  Represents information about allocation of the total amount of an order item to billing schedules throughout the order item's lifecycle. This object is available in API version 62.0 and later.
- **[BsgRelationship](./sforce_api_objects_bsgrelationship.htm.md)**  
  Represents a relationship between billing schedule groups to support bundles where one parent billing schedule group has multiple child billing schedule groups. This object is available in API version 62.0 and later.
- **[CaseServiceProcessExtension](./sforce_api_objects_caseserviceprocessextension.htm.md)**  
  Represents additional information for a case record based on the type of service process for which the case was raised. This object is available in API version 67.0 and later.
- **[CreditMemo](./sforce_api_objects_creditmemo.htm.md)**  
  Represents a document that’s used to reduce the amount that a buyer owes a seller under the terms of an earlier invoice. This object is available in API version 62.0 and later.
- **[CreditMemoAddressGroup](./sforce_api_objects_creditmemoaddressgroup.htm.md)**  
  Represents the storage of the buyer's address information, which is used to determine the tax credit amount for a buyer when a credit memo is issued. This object is available in API version 62.0 and later.
- **[CreditMemoInvApplication](./sforce_api_objects_creditmemoinvapplication.htm.md)**  
  Represents information about the application of a credit memo to an invoice. This object is available in API version 62.0 and later.
- **[CreditMemoLine](./sforce_api_objects_creditmemoline.htm.md)**  
  Represents the product, service, adjustment, or tax line items included in a credit memo. This object is available in API version 62.0 and later.
- **[CreditMemoLineInvoiceLine](./sforce_api_objects_creditmemolineinvoiceline.htm.md)**  
  Represents a junction between a credit memo line and an invoice line. This object is available in API version 62.0 and later.
- **[CreditMemoLineTax](./sforce_api_objects_creditmemolinetax.htm.md)**  
  Represents tax information of a credit memo line of type `Tax`. This object is available in API version 62.0 and later.
- **[DebitMemo](./sforce_api_objects_debitmemo.htm.md)**  
  Represents the document used to charge an additional amount to a buyer by a seller. An invoice is generated for the debit memo in the next invoice run. This object is available in API version 65.0 and later.
- **[DebitMemoAddress](./sforce_api_objects_debitmemoaddress.htm.md)**  
  Represents the buyer's address information, which is used to determine the tax amount for a buyer when a debit memo is issued. This object is available in API version 65.0 and later.
- **[DebitMemoLine](./sforce_api_objects_debitmemoline.htm.md)**  
  Represents the additional charge amount that the buyer must pay for the product, service, or debit memo line tax that’s related to the debit memo. This object is available in API version 65.0 and later.
- **[DebitMemoLineTax](./sforce_api_objects_debitmemolinetax.htm.md)**  
  Represents the tax information for a debit memo line. This object is available in API version 66.0 and later.
- **[GeneralLedgerAccount](./sforce_api_objects_generalledgeraccount.htm.md)**  
  Represents information about the accounting codes, types, and names that are used to store and organize financial transactions. This object is available in API version 63.0 and later.
- **[GeneralLedgerAcctAsgntRule](./sforce_api_objects_generalledgeracctasgntrule.htm.md)**  
  Represents information about the rule based on which general ledger accounts are assigned to transaction journals that are created for billing transactions. This object is available in API version 63.0 and later.
- **[GeneralLdgrAcctPrdSummary](./sforce_api_objects_generalldgracctprdsummary.htm.md)**  
  Represents a junction between a general ledger account and a legal entity accounting period. Stores information about the total credit amount, total debit amount, opening balance, and closing balance of a general ledger account for a specific legal entity accounting period. This object is available in API version 65.0 and later.
- **[GeneralLedgerJrnlEntryRule](./sforce_api_objects_generalledgerjrnlentryrule.htm.md)**  
  Represents information about the transaction journal entry rule, based on which transaction journals are created for the selected credit and debit general ledger accounts, transaction amount field, and percentage. This object is available in API version 65.0 and later.
- **[InvBatchDraftToPostedRun](./sforce_api_objects_invbatchdrafttopostedrun.htm.md)**  
  Represents information about the batch job that posts all invoices with the status as `Draft` that are generated by the invoice batch run associated with the billing schedule. This object is available in API version 62.0 and later.
- **[Invoice](./sforce_api_objects_invoice.htm.md)**  
  Represents information about a financial document describing the total amount a buyer must pay for provided products or services. This object is available in API version 62.0 and later.
- **[InvoiceAddressGroup](./sforce_api_objects_invoiceaddressgroup.htm.md)**  
  Represents the storage of the buyer's address information. This object is available in API version 62.0 and later.
- **[InvoiceBatchRun](./sforce_api_objects_invoicebatchrun.htm.md)**  
  Represents a batch processing job in Billing. During an invoice batch run, all billing schedules that meet the specified criteria are processed, resulting in the generation of invoices. This object is available in API version 62.0 and later.
- **[InvoiceBatchRunCriteria](./sforce_api_objects_invoicebatchruncriteria.htm.md)**  
  Represents a batch processing job and its required criteria in Billing. During an invoice batch run, all billing schedules that meet the specified criteria are processed, resulting in the generation of invoices. This object is available in API version 62.0 and later.
- **[InvoiceBatchRunRecovery](./sforce_api_objects_invoicebatchrunrecovery.htm.md)**  
  Represents information about the recovery procedure of an invoice batch run. This object is available in API version 62.0 and later.
- **[InvoiceDocument](./sforce_api_objects_invoicedocument.htm.md)**  
  Represents the PDF document generated for an invoice. This object is available in API version 63.0 and later.
- **[InvoiceLine](./sforce_api_objects_invoiceline.htm.md)**  
  Represents the amount that a buyer must pay for a product, service, or fee. Invoice lines are created based on the amount of an order line. This object is available in API version 62.0 and later.
- **[InvoiceLineRelationship](./sforce_api_objects_invoicelinerelationship.htm.md)**  
  Represents a relationship between invoice line items to support bundles where one parent invoice line has multiple child invoice lines. This object is available in API version 62.0 and later.
- **[InvoiceLineTax](./sforce_api_objects_invoicelinetax.htm.md)**  
  Represents tax information of an invoice line of type `Tax`. This object is available in API version 62.0 and later.
- **[LegalEntity](./sforce_api_objects_legalentity.htm.md)**  
  Represents the way an organization is structured. An organization can be a single legal entity or it can comprise more than one legal entity. This object is available in API version 62.0 and later.
- **[LegalEntyAccountingPeriod](./sforce_api_objects_legalentyaccountingperiod.htm.md)**  
  Represents a junction between a legal entity and an accounting period. This object is available in API version 62.0 and later.
- **[PaymentBatchRun](./sforce_api_objects_paymentbatchrun.htm.md)**  
  Represents a batch processing job that processes payments in Billing. During a payment batch run, all the payment schedules that meet the specified criteria are processed and the corresponding Payment records are created. These payments are then applied to invoices or invoice lines. This object is available in API version 64.0 and later.
- **[PaymentLineInvoiceLine](./sforce_api_objects_paymentlineinvoiceline.htm.md)**  
  Represents information about a payment line that's applied to or unapplied from an invoice line. This object is available in API version 64.0 and later.
- **[PaymentRetryRule](./sforce_api_objects_paymentretryrule.htm.md)**  
  Represents the specific payment retry rule for a failed payment schedule item. Each rule defines actionable parameters such as the maximum number of retries for the failed records and time intervals between subsequent retry attempts. This object is available in API version 66.0 and later.
- **[PaymentRetryRuleSet](./sforce_api_objects_paymentretryruleset.htm.md)**  
  Represents the payment retry rule definition that defines how failed payments are retried based on the error codes across various retry categories. This object is available in API version 66.0 and later.
- **[PaymentSchedule](./sforce_api_objects_paymentschedule.htm.md)**  
  Represents information about a set of payments that a customer wants to collect at different times for a certain record. A schedule contains one or more payment schedule items, where each item represents one payment to be processed. Each of a schedule’s items can have different payment configuration fields, such as payment methods, payment dates, and payment accounts. When a payment scheduler launches a payment run, the run evaluates active payment schedule items, and picks them up for payment processing if they match the scheduler’s payment criteria. This object is available in API version 64.0 and later.
- **[PaymentSchedulePolicy](./sforce_api_objects_paymentschedulepolicy.htm.md)**  
  Represents information about the configuration for the payment schedule. This object is available in API version 64.0 and later.
- **[PaymentScheduleTreatment](./sforce_api_objects_paymentscheduletreatment.htm.md)**  
  Represents information about the processing of payment schedules including the payment method and the payment amount for the payment schedule. This object is available in API version 64.0 and later.
- **[PaymentScheduleTreatmentDtl](./sforce_api_objects_paymentscheduletreatmentdtl.htm.md)**  
  Represents information about the processing of payment schedules after the corresponding invoices are posted. This object is available in API version 64.0 and later.
- **[PymtSchdDistributionMethod](./sforce_api_objects_pymtschddistributionmethod.htm.md)**  
  Represents information about the partial payments that the total payment is divided into. This object is available in API version 64.0 and later.
- **[PaymentScheduleItem](./sforce_api_objects_paymentscheduleitem.htm.md)**  
  Represents information about a payment to be processed. Each schedule item can have different payment configuration fields, such as payment methods, payment dates, and payment accounts. When a payment scheduler launches a payment run, the run evaluates active payment schedule items, and picks them up for payment processing if they match the scheduler’s payment criteria. This object is available in API version 64.0 and later.
- **[PaymentTerm](./sforce_api_objects_paymentterm.htm.md)**  
  Represents an agreement between a buyer and a seller about when payment is due for an invoice. This object is available in API version 62.0 and later.
- **[PaymentTermItem](./sforce_api_objects_paymenttermitem.htm.md)**  
  Represents configuration of a payment term. This object is available in API version 62.0 and later.
- **[RevenueTransactionErrorLog](./sforce_api_objects_revenuetransactionerrorlog.htm.md)**  
  Represents the details of errors that occurred during the processing of a request. The error record persists until a new error with the same category, primary record, and, if necessary, related record occurs. This object is available in API version 62.0 and later.
- **[SeqPolicySelectionCondition](./sforce_api_objects_seqpolicyselectioncondition.htm.md)**  
  Represents the condition used to determine which sequence policy is applied to a record. This object is available in API version 65.0 and later.
- **[SequenceGapReconciliation](./sforce_api_objects_sequencegapreconciliation.htm.md)**  
  Represents a missing sequence value identified during reconciliation, which can be used later to ensure there are no gaps in the sequence policy numbers. This object is available in API version 65.0 and later.
- **[SequencePolicy](./sforce_api_objects_sequencepolicy.htm.md)**  
  Represents the configuration of rules and parameters for generating unique, sequential numbers for records. Stores settings such as numbering patterns, prefixes, suffixes, sequence start numbers, increment values, and filter criteria to ensure accurate and compliant numbering. This object is available in API version 65.0 and later.
- **[TaxEngine](./sforce_api_objects_taxengine.htm.md)**  
  Represents information about an instance of a tax engine provider as well as the merchant credentials for that specific instance. This object is available in API version 62.0 and later.
- **[TaxEngineInteractionLog](./sforce_api_objects_taxengineinteractionlog.htm.md)**  
  Represents a record of a communication with an external tax engine following a tax calculation request. This object is available in API version 62.0 and later.
- **[TaxEngineProvider](./sforce_api_objects_taxengineprovider.htm.md)**  
  Represents general information about a service that manages a tax engine. Tax engine providers have a one-to-many relationship with tax engines, where the tax engine record represents a specific configuration of a tax engine that can be assigned to multiple order items. This object is available in API version 62.0 and later.
- **[TaxPolicy](./sforce_api_objects_taxpolicy.htm.md)**  
  Represents information about a group of tax treatments, where each treatment represents parameters to determine how a particular product is taxed for a transaction line item. Tax policies are related to products, which pass the policy on to the resulting order items and in turn the billing schedules. This object is available in API version 62.0 and later.
- **[TaxTreatment](./sforce_api_objects_taxtreatment.htm.md)**  
  Represents information about tax calculation by external engines. Each product requires a tax policy to determine whether to apply tax. Each tax policy requires at least one tax treatment. The tax treatments determine how taxable products are taxed. This object is available in API version 62.0 and later.
- **[Tax Treatment Item](./sforce_api_objects_taxtreatmentitem.htm.md)**  
  Represents tax code information that’s used to calculate tax for a product by a specific tax engine. This object is available in API version 66.0 and later.

#### See Also

- [*Object Reference for the Salesforce Platform*: Overview of Salesforce Objects
  and Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm "Object Reference for the Salesforce Platform: Overview of Salesforce Objects
         and Fields - HTML (New Window)")
- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/sforce_api_quickstart_intro.htm "SOAP API Developer Guide: Introduction to SOAP API - HTML (New Window)")
