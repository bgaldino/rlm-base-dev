---
article_id: ind.billing_billing_arrangements.htm
title: Manage Billing Arrangements
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_billing_arrangements.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-05-11
---

# Manage Billing Arrangements

Billing arrangements facilitate precise invoicing for business scenarios such as parent account billed for subsidiary accounts, cross-departmental charge allocations, or services or assets shared among multiple parties. Use billing arrangements to configure the allocation of billing amounts to a specific billing account or distribute costs among several billing accounts based on fixed percentages.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Key Terms

Here are a few key terms used when configuring billing arrangements.

Owning Account
The account that uses or owns the service or asset
Billing Account
The account that receives the bill
Billing Arrangement
The configuration for invoicing a transaction’s billing amount to one or more accounts. The billing arrangement specifies whether the total amount is invoiced to the owning account or a different billing account, or whether the invoice is split among multiple billing accounts. For each assigned account, users can select a corresponding billing profile to fetch its billing preferences.
Billing Arrangement Line
The billing account, billing profile, and the percentage of the billing amount to be invoiced. Each billing arrangement line results in a separate invoice addressed to the selected billing account.
Split Billing
The process of splitting the bills for services or assets to generate multiple invoices addressed to different billing accounts. The split billing amounts in each invoice are calculated based on predefined percentages in the billing arrangement that’s associated with the billing schedule group.
How Billing Arrangements Work

You can create billing arrangements and apply them to billing schedule groups. When the invoice batch run processes billing schedule groups with related billing arrangements, Billing generates invoices simultaneously for each of the billing accounts that are part of the billing arrangement on the next billing date of the billing schedule group. Based on the configuration specified in the billing arrangement, Billing generates one or more invoices for the total bill amount. If the billing arrangement indicates a 100% allocation to an account, then Billing generates one invoice for the corresponding billing account. If the billing arrangement has multiple billing arrangement lines with various specified percentages, then Billing splits the total amount into multiple split invoices, and generates invoices for each billing account accordingly.

The billing profile selected for a billing account in the billing arrangement line indicates the preferred payment terms, bill-to contact, billing address, and invoice template for that account. These preferences take precedence over the default values provided on the billing schedule group. Billing preferences such as suspension dates, and document and email delivery settings, are based on the default billing profiles of the corresponding billing accounts. All other billing details such as the billing day of month and next billing date are based on the billing schedule group and apply to the split invoices as well.

The invoices can be viewed on the Invoices related list of the corresponding billing accounts. The invoices are also available in the All Invoices related list of the corresponding Order records.

How Billing Operations Impact Billing Arrangements

Let’s understand the impact of billing operations on billing arrangements.

BILLING OPERATION	IMPACT ON THE BILLING ARRANGEMENT
Post, void, or delete invoices	

If any invoice generated from a billing schedule group with a related billing arrangement is voided, deleted, or posted, then the same action applies to all the split invoices generated from that billing schedule group. This is because the invoice lines originate from the same billing schedule group and billing arrangement. For instance, if you post one invoice, then all the other split invoices are also posted.


Amend, renew, cancel transactions	Billing preserves the billing arrangement configuration when a billing schedule group with associated billing arrangements undergoes amend, renew, or cancel transactions. The actions create new amend, renew, or cancellation billing schedules in the same billing schedule group. The percentage allocations and billing account assignments remain intact across the transaction lifecycle.
Write-off invoices	If any of the split invoices created from the same set of billing schedule group and billing arrangement is written off,then the other split invoices can’t be voided.
Suspend billing	If the billing schedule group or any of the billing accounts in its associated billing arrangement are suspended for billing, then none of the billing accounts are invoiced during the suspension period.
Billing Arrangements on Orders and Other External Transactions

To view an order or account’s related billing arrangement as a field on the Order or Account record, add the Billing Arrangement field as a custom field of type Lookup Relationship to the Order or Account object.

To view the Billing Arrangements as a separate tab on the Order or Account record, edit the page layout of the Order or Account object and add a new tab for the Billing Arrangements component.

To configure billing arrangements for an order or any other external transaction, extend the out-of-the-box BillingContext or StandaloneBillingContext context definitions and map the billing arrangement to its billing schedule groups. Make sure to add the Billing Arrangement field on the Order object, and then view all related billing arrangements for the order on the Billing Arrangement tab of the Order record.

Track Billing Arrangement Relationships on Account and Invoice Records

Use the related lists on Account and Invoice records to track billing arrangement activity.

On the Account record, two related lists give you visibility into billing schedule groups. The Billing Schedule Groups Owned related list shows all billing schedule groups owned by the account, The Billing Schedule Groups with Billing Arrangement related list shows the groups tagged with an active billing arrangement where the account is a billing account. A billing schedule group appears in this list for all billing accounts in the billing arrangement, regardless of which account owns the billing schedule group.

On the Invoice record, the Related Invoices with Same Billing Arrangement related list shows all other invoices generated from the same billing arrangement version as the current invoice.

Create Billing Arrangements and Billing Arrangement Lines
Billing arrangements define how a transaction’s billable amount is invoiced to the relevant billing accounts.
Configure Billing Arrangements for Billing Schedule Groups
Route invoices with the appropriate allocated charges to the correct billing accounts by configuring billing arrangements on billing schedule groups.
Examples: Flexible Invoicing for Complex Business Models
Billing arrangements can help you manage complex financial relationships by automating the allocation of invoice charges across billing accounts. You can configure billing arrangements for invoicing a billing account that’s different from a service or owning account. You can also split bills for products or services shared by multiple accounts to streamline invoicing with prorated charge allocation. Here are several business scenarios where billing arrangements help businesses by invoicing and billing the right parties.
