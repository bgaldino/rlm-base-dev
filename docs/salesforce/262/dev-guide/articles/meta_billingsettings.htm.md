---
page_id: meta_billingsettings.htm
title: BillingSettings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_billingsettings.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# BillingSettings

Represents the settings for Salesforce
Billing.

## Parent Type and Manifest Access

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

In the package manifest, all the settings metadata types for the org are accessed using the
“Settings” name. See [Settings](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)") for more details.

## File Suffix and Directory Location

The BillingSettings values are stored in the
BillingSettings.settings file in the
settings folder. The .settings files
are different from other named components, because there’s only one settings file
for each settings component.

## Version

BillingSettings components are available in API version 62.0 and later.

## Special Access Rules

These settings are available when Billing is enabled.

## Fields

| Field Name | Description |
| --- | --- |
| acctRecGlAccount | Field Type  string  Description  General ledger account to record the credit amount for unrealized or realized losses and the debit amount for unrealized or realized gains in transaction journals. Available in API version 64.0 and later. |
| billingContextDefinition | Field Type  string  Description  Name of the context definition that the [Create Billing Schedules for Orders API](https://developer.salesforce.com/docs/./connect_resources_create_billing_schedules.htm.md "HTML (New Window)") uses to understand your order data. Available in API version 64.0 and later. |
| billingContextSourceMapping | Field Type  string  Description  Name of the context mapping that links Order fields to billing transaction context nodes. Available in API version 64.0 and later. |
| billingIntraCtxtSrcMapping | Field Type  string  Description  Name of the custom context mapping that maps your custom or standard Order fields to billing transaction context nodes. Available in API version 64.0 and later. |
| defaultAPClosureDPEDefnName | Field Type  string  Description  Org-wide default value to specify the Data Processing Engine (DPE) definition to close legal entity accounting periods. Available in API version 64.0 and later. |
| defaultApplyCreditMemoFlow | Field Type  string  Description  Default flow that’s used to apply the credit memo to invoices. Available in API version 64.0 and later. |
| defaultBillingTreatment | Field Type  string  Description  Org-wide default value to specify the name of the billing treatment. Available in API version 64.0 and later. |
| defaultEmailTemplate | Field Type  string  Description  Default email template to send the generated invoice PDFs. Available in API version 64.0 and later. |
| defaultInvPreviewTemplate | Field Type  string  Description  Default template to generate PDFs of invoice previews. Available in API version 64.0 and later. |
| defaultInvoiceDocTemplate | Field Type  string  Description  Default template to generate PDFs of invoices. Available in API version 64.0 and later. |
| defaultLegalEntity | Field Type  string  Description  Org-wide default value to specify the name of the legal entity. Available in API version 64.0 and later. |
| defaultTaxTreatment | Field Type  string  Description  Org-wide default value to specify the name of the tax treatment. Available in API version 64.0 and later. |
| enableBillingDisputeManagement | Field Type  boolean  Description  Indicates whether to enable Dispute Management (`true`) or not (`false`). The default value is `false`. Available in API version 66.0 and later. |
| enableBillingSetup | Field Type  boolean  Description  Indicates whether to enable Billing setting (`true`) or not (`false`). The default value is `false`. |
| enableCreditMemoSequenceService | Field Type  boolean  Description  Indicates whether to mandate the application of sequence policy for credit memos (`true`) or not (`false`). The default value is `false`. Available in API version 66.0 and later with Revenue Cloud Billing. |
| enableCrMemoApplicationToPostedInvoices | Field Type  boolean  Description  Indicates whether to enable Apply Credits to Posted Invoices setting (`true`) or not (`false`). The default value is `false`.  This setting automates settlement of invoices through application of credits to posted invoices. The credit application level determines whether credits are automatically applied to invoices or invoice lines. |
| enableFailedPaymentsRetry | Field Type  boolean  Description  Indicates whether to retry failed payment schedule items automatically based on the defined payment retry rules (`true`) or not (`false`). The default value is `false`. Available in API version 66.0 and later. |
| enableForeignExchangeTrxnJrnlCreation | Field Type  boolean  Description  Indicates whether to create Transaction Journal records for invoices that hold balance amounts (partially settled and not fully settled posted invoices) to record foreign exchange unrealized gains or losses during the closure activity of a legal entity accounting period. The default value is `false`. Available in API version 65.0 and later with Revenue Cloud Billing. |
| enableInvoiceEmailDelivery | Field Type  boolean  Description  Indicates whether to enable Configure Email Delivery Settings (`true`) or not (`false`). The default value is `false`. Available in API version 63.0 and later with Revenue Cloud Billing. |
| enableInvoicePdfGeneration | Field Type  boolean  Description  Indicates whether to enable Document Generation setting (`true`) or not (`false`). The default value is `false`. Available in API version 63.0 and later with Revenue Cloud Billing. |
| enableInvoiceSequenceService | Field Type  boolean  Description  Indicates whether to mandate the application of sequence policy for posted invoices (`true`) or not (`false`). The default value is `false`.  If enabled, each posted invoice is assigned an invoice number. Available in API version 65.0 and later with Revenue Cloud Billing. |
| enableNegInvoiceLnConversionToCrMemoLn | Field Type  boolean  Description  Indicates whether to enable Convert Negative Invoice Lines to Credit Memo Lines setting (`true`) or not (`false`). The default value is `false`. |
| enablePaymentSchedulesAndItemsCreation | Field Type  boolean  Description  Indicates whether to create a default payment schedule policy and payment schedule treatment (`true`) or not (`false`). The default value is `false`.  If enabled, payment schedules and payment schedule items are created during financial transactions such as posting of invoices. Available in API version 64.0 and later with Revenue Cloud Billing. |
| enableRefundIssuingAndBalanceSettlement | Field Type  boolean  Description  Indicates whether to issue refunds and settle balances (`true`) or not (`false`). The default value is `false`.  If enabled, refunds are issued and credit memos are applied to any remaining invoice balance when customers amend or cancel an order. Available in API version 67.0 and later. |
| enableTransactionJournalCreation | Field Type  boolean  Description  Indicates whether to create Transaction Journal records based on the defined general ledger account assignment rules for the billing entities when billing transaction records are created or updated (`true`) or not (`false`). The default value is `false`. Available in API version 63.0 and later with Revenue Cloud Billing.  Billing transaction records include these transaction types.   - Invoice - Invoice Line - Invoice Line Tax - Credit Memo - Credit Memo Line - Credit Memo Line Tax - Payment - Refund - Payment Line Invoice - Payment Line Invoice Line - Credit Memo Inv Application - Credit Memo Line Invoice Line |
| enableTransactionsApplicationToInvoices | Field Type  boolean  Description  Indicates whether to enable Credit Application Level setting (`true`) or not (`false`). The default value is `false`.  Revenue Cloud Advanced  This setting applies balances of credit memos to invoices or balances of credit memo lines to invoice lines. For the latter, amounts and balances on the invoices are rolled-up from the related invoice lines.  Revenue Cloud Billing  This setting applies balances of credit memos and payments to invoices or balances of credit memo lines and payments lines to invoice lines. For the latter, amounts and balances on the invoices are rolled-up from the related invoice lines. |
| enableTrxnAmountsStorageInCorpCurrency | Field Type  boolean  Description  Indicates whether to allow conversion of amounts of the Invoice, Invoice Line, Credit Memo, and Credit Memo Line records to your corporate currency (`true`) or not (`false`). The default value is `false`. Available in API version 63.0 and later.  Store the converted amounts in corporate currency-specific amount fields. |
| realisedGainGlAccount | Field Type  string  Description  Name of the general ledger account to record realized gains in transaction journals. Available in API version 64.0 and later. |
| realisedLossGlAccount | Field Type  string  Description  Name of the general ledger account to record realized losses in transaction journals. Available in API version 64.0 and later. |
| ruleBasedCrAndPymtAppln | Field Type  string  Description  Automates the settlement of the posted invoices by applying payments and credits that meet the specified application rules. The rules application level determines whether payments or credits are applied first to the invoices. The ruleset displays a list of selectable rules. Available in API version 66.0 and later. |
| unrealisedGainGlAccount | Field Type  string  Description  Name of the general ledger account to record unrealized gains in transaction journals. Available in API version 64.0 and later. |
| unrealisedLossGlAccount | Field Type  string  Description  Name of the general ledger account to record unrealized losses in transaction journals. Available in API version 64.0 and later. |

## Declarative Metadata Sample Definition

The following is an example of a BillingSettings component.

```
<BillingSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <enableBillingSetup>true</enableBillingSetup>
    <enableForeignExchangeTrxnJrnlCreation>true</enableForeignExchangeTrxnJrnlCreation>
    <enableInvoicePdfGeneration>true</enableInvoicePdfGeneration>
    <enableTransactionsApplicationToInvoices>true</enableTransactionsApplicationToInvoices>
    <enableCrMemoApplicationToPostedInvoices>true</enableCrMemoApplicationToPostedInvoices>
    <enableInvoiceEmailDelivery>true</enableInvoiceEmailDelivery>
    <enableInvoiceSequenceService>true</enableInvoiceSequenceService>
    <enableTransactionJournalCreation>true</enableTransactionJournalCreation>
    <enableTrxnAmountsStorageInCorpCurrency>true</enableTrxnAmountsStorageInCorpCurrency>
    <enablePaymentSchedulesAndItemsCreation>true</enablePaymentSchedulesAndItemsCreation>
</BillingSettings>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>Billing</members>
        <name>Settings</name>
    </types>
    <version>67.0</version>
</Package>
```

## Wildcard Support in the Manifest File

The wildcard character `*` (asterisk) in the
package.xml manifest file doesn’t apply to metadata types
for feature settings. The wildcard applies only when retrieving all settings, not
for an individual setting. For details, see [Settings](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)"). For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
