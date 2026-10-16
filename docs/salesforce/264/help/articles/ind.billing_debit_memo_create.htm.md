---
article_id: ind.billing_debit_memo_create.htm
title: Create Debit Memos and Related Records
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_debit_memo_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_debit_memo.htm
fetched_at: 2026-09-04
---

# Create Debit Memos and Related Records

After you identify the additional charges to be paid by your buyer, create debit memos and their related records to make the required adjustments.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create debit memos:	

You must have one of these permission sets:

Billing Admin permission set
Billing Operations User permission set
Payment Admin permission set
Payment Operations User permission set
Credit Memo Operations User permission set
NOTE

For Salesforce orgs that are created in Winter ’26, the Debit Memos and Debit Memo Lines tabs are available by default. For Salesforce orgs that are created before Winter ’26, change the tab settings for these objects to Default On.

Create Debit Memos

Create a Debit Memo record for an account that's undercharged.

Before you create debit memos, go to the Object Manager and add all the required values to the Reason Code picklist field on the Debit Memo object. Add values such as LP for late payment charges.

From the App Launcher, find and select Debit Memo.
Click New.
Select the account that you are creating the debit memo for.
Select Draft as the status.
A Debit Memo record can be created only in the Draft status.
Select the reason code for the debit memo.
If necessary, enter a description.
Select the legal entity.
Select the next billing date.
On the target date of the invoice batch run, the invoice batch run picks up all the debit memos that have the next billing date on or before the target date.
Enter an invoice matching reference key or invoice matching reference name.
The specified value along with the default matching group of the debit memo is used to identify an invoice with the same details. The default matching group includes the account, currency, and legal entity of the debit memo.
	
Matching invoice reference key is specified	The specified matching invoice reference key is considered along with the default matching group.
Matching invoice reference name is specified	The specified matching invoice reference name is considered along with the default matching group.
Both fields are specified	The specified matching invoice reference key is considered along with the default matching group.
Neither of the fields is specified	The default matching group is considered.
Save your work.

Create the required debit memo lines for the debit memo.

Create Debit Memo Addresses

Create a debit memo address to specify the billing address and shipping address for the debit memo lines.

Open the debit memo that you want to create the debit memo address for.
Go to the debit memo address related list, and click New.
Enter the address.
Save your work.
Create Debit Memo Lines

Create Debit Memo Line records for an asset, contract, invoice line, or refund. Create the debit memo line from the related list of the Debit Memo record or from the Debit Memo tab.

Open the debit memo.
Go to the debit memo lines related list, and click New.
Enter a name.
Enter the product that you're creating the debit memo line for.
If necessary, enter a description.
Select the start date and end date.
When you don't select a date in these fields, the date when the record is created is used as the default date for the fields.
Enter the charge amount.
This amount appears as the charge amount of the invoice lines, when the debit memo line gets converted into an invoice line.
Select a tax treatment.
If no tax treatment is selected, then the tax treatment of the related product is considered. If the tax treatment isn't found on the product, then the default tax treatment of your Salesforce org is used.
Select the legal entity.
If you don't select a legal entity, then the legal entity of the related debit memo or the default legal entity of your Salesforce org is used.
Select the legal entity accounting period.
Select the reference record.
You can manually enter the ID of an asset, contract, invoice line, or refund that the debit memo line is created for.
Select the debit memo address as the shipping address and billing address.
Save your work.

Go back to the parent debit memo and change the status to Posted. The invoice generation status then automatically changes to Ready for Invoice Generation.

If you manually convert debit memo lines to invoice lines, then post the related invoice and select the Manually Processed check box on the related Debit Memo record. You can also use Invoice Ingestion API to convert them manually.

When you click the Generate Invoices button or schedule an invoice batch run, after all valid billing schedule groups are converted to invoice lines, all valid debit memo lines are converted to invoice lines.
