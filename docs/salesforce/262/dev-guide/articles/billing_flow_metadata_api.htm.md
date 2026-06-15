---
page_id: billing_flow_metadata_api.htm
title: Flow for Billing
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_flow_metadata_api.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# Flow for Billing

Represents the metadata associated with a flow. With Flow, you can create an
application that navigates users through a series of screens to query and update records in the
database. You can also execute logic and provide branching capability based on user input to
build dynamic applications.

## FlowActionCall

Billing exposes additional actionType values for the FlowActionCall Metadata type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required.  The action type. Additional valid values only for Billing include:   - `applyCredit`—Apply a credit memo or credit memo line to an invoice or invoice   line, respectively. - `unapplyCredit`—Unapply a credit memo or credit memo line from an invoice or invoice   line, respectively. - `postDraftInvoice`—Update the status of an invoice from `Draft` to `Posted` for a credit memo   application. - `postDraftInvoiceBatchRun`—Update the status of a batch of invoices from `Draft` to `Posted`   for a credit memo application. - `createBillingSchedulesFromBillingTransaction`—Create one or more billing schedules for a specified billing   transaction ID. - `recoverBillingSchedules`—Recover one or more billing schedules in the `Error` or `Processing` status. - `generateInvoiceDocuments`—Asynchronously generate PDF documents for the invoices associated with   an invoice batch run record that are in the `Draft`   or `Posted` status. - `createBillingSchedulesFromTrxn`—Creates billing schedules for internal or external transaction   records by calling the Create Standalone Billing Schedules API. - `unapplyPayment`—Unapplies a payment that's already been applied to an invoice or   invoice line by crediting the amount back to the payment and the invoice or invoice   line. - `writeOffInvoices`—Write off partially paid or unpaid invoices to manage pending debts   and to maintain accurate financial records. This action calls the Posted Invoice List   Write-Off (POST) API. - `assignSequences`—Assigns sequence pattern values to target invoice records based on   the specified sequence policy. - `postDraftCreditMemo`—Post a draft credit memo to a credit memo record for review and   approval. - `generateAccountStatement`—Generates a comprehensive account statement for a specified account   with transaction history and balance information. - `blngDsptIssueCreditMemo`—Issue credit memos for disputed invoices to resolve billing   disputes. - `blngSvcExtendInvoiceDueDate`—Update the due date on an invoice to accommodate payment extensions   or resolve billing disputes. - `blngSvcSuspendBilling`—Suspend or resume the billing of an account to handle billing   disputes. - `blngSvcUpdateBillToContact`—Update the Bill to Contact detail on an invoice to ensure accurate   billing communication and routing. - `blngSendDunningEmail`—Run an orchestration that sends dunning   process emails for collection plans to recover overdue revenue and notify customers   about amounts still due. - `automateRefund`—Initiate refund orchestration for a credit memo   generated from a subscription cancellation or negative amendment. |
