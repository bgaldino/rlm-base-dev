---
article_id: ind.qocal_backdate_asset_transactions.htm
title: Backdate Asset Transactions
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_backdate_asset_transactions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_specialized_asset_considerations.htm
fetched_at: 2026-09-04
---

# Backdate Asset Transactions

Apply an amendment, renewal, or cancellation to an asset with a past effective date so that the asset reflects the change from the date it took effect.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
USER PERMISSIONS NEEDED
To amend, transfer, or swap assets:	

Initiate Amend user permission

OR

initiateAmendment API access


To renew and cancel assets:	

Initiate Renew and Initiate Cancel user permissions

OR

initiateRenew API and initiateCancel API access

Before you backdate a change, review Considerations for Assets with Backdated Changes.

IMPORTANT Backdated changes require the standard flow for managing assets. In Revenue Settings, under Set Up Flow for Managing Assets, confirm that the flow API name is runtime_revenue_arcflows__arcFlow. If your org uses a custom or earlier flow, such as RLM_ARC_Assets, enter the new API name and save.

A backdated change is a transaction with an effective date in the past. It records an update that already took effect for the customer so the asset reflects the correct pricing, quantities, or status from the backdated effective date. You can backdate amendment, renewal, and cancellation transactions for standard and ramped assets. You can also backdate transfer and swap transactions for standard assets.

Backdated transactions can have a revenue recognition impact for your business. Consider adding a confirmation dialog to the user experience when they create a backdated amendment. The Salesforce Flow drives the amendment, renewal, and cancellation user experience. Add a confirmation dialog box to the flow specifically for backdated transactions.

If your org uses Revenue Cloud Billing, billing schedules and invoices align with the backdated effective date. The system prorates amounts for the affected period and generates credit memos for previously invoiced periods.

For the account that you want to change, go to the Assets tab and open the Managed Asset viewer.
Select the assets, and then select Amend, Renew, or Cancel.
Enter the effective date for the change.

Enter a date in the past and on or after the asset's start date.

Select Create Order, and then select Create Single Order.
Select the new order and activate it.

The asset state periods update so the asset reflects the change as of the backdated effective date.

EXAMPLE

Today is November 12, 2025. A customer canceled a product effective November 1, 2025, so that they aren't billed for access after that date. You select the asset in the Managed Asset viewer, select Cancel, and enter a cancellation date of November 1, 2025. Then, you create the cancellation order and activate it. The asset reflects the cancellation as of November 1, 2025, even though you entered the change on November 12, 2025.

To make a change that takes effect today or later, see Future-Dated Changes.
