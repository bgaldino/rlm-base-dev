---
article_id: ind.qocal_coterminate_with_contract_end_date.htm
title: Coterminate Subscription Assets with Contract End Dates
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_coterminate_with_contract_end_date.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_manage_contract_pricing_in_revenue_lifecycle_management.htm
fetched_at: 2026-09-04
---

# Coterminate Subscription Assets with Contract End Dates

Synchronize subscription end dates with their corresponding contract end dates to improve accuracy and efficiency in sales and renewal processes. Cotermination reduces manual mistakes, simplifies renewals, and minimizes administrative tasks associated with managing subscription lifecycles.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To use contract cotermination:	Renew Assets user permission
Considerations for Contract Cotermination
Review the limitations and requirements for aligning subscription end dates with contract end dates to ensure successful sales and renewal processes. Reference these specifics when you build or troubleshoot transactions that use cotermination.
Prerequisites to Use Cotermination

Before you begin, configure Contract Cotermination.

In Setup, select Object Manager.
Search for and select Contract.
In the Contract Layout, add the Co-termination field to the Contract Detail section.

After you turn on cotermination, API validation prevents saving quote line items (QLIs) or order line items (OLIs) if their end dates don’t align with the contract end date. Sales reps typically operate at the contract level, so synchronized end dates for all subscriptions within a contract facilitate smooth renewal events.

Perform Contract Cotermination
From the App Launcher, search for and select Contracts.
Select a contract record
On the Details tab, select Contract Cotermination.
Create an initial sale, amendment, or renewal quote or order for that contract.
Add termed subscription products to the quote or order.
The quote line item (QLI) or order line item (OLI) end date automatically populates to match the contract end date. The system locks these end dates to prevent manual edits.
EXAMPLE
Consider contract A with a start date of 1/1/2025 and an end date of 12/31/2025 with cotermination enabled.
User created an initial sale order on 2/1/2025 and assigned the order to contract A.
User added a product to the order and noted that the OLI's start and end dates are automatically set to 2/1/2025–12/31/2025. With the end date locked, the subscription end date is set to coterminate with the contract end date.
After the Quote-to-Order process and assetization, the product is created with subscription dates of 2/1/2025–12/31/2025.

Add-on sale order:

User starts with the same contract A with a start date of 1/1/2025 and an end date of 12/31/2025.
User adds another product to this contract on 3/1/2025 by creating an initial sale order and linking it to contract A.
The QLI's start date and end date are automatically set to 3/1/2025–12/31/2025. The subscription end date is set to the contract end date.
After assetization, the product is created with subscription dates of 3/1/2025–12/31/2025.

Amendment order: A user extends contract A’s end date to 6/30/2026 and then amends a product. The product’s QLI end date automatically adjusts to 6/30/2026.

Renewal order: If you’re renewing a contract where the cotermination flag is set to True, subscription end dates automatically align with the contract renewal date.

Negative amendments with contract date changes: An initial sale of 100 product licenses with a start date 1/1/2025 and an end date 12/31/2025 are under a cotermed contract. Later, if the user extends the contract end date to 6/1/2026 with a negative amendment of 10 licenses, the end dates of the remaining 90 licenses update to 6/1/2026.

Cotermination Scenarios

Review these examples of how the feature automatically aligns subscription end dates.

Initial Order Sale
For a contract with a start date of 1/1/2025 and an end date of 12/31/2025, an initial sale order created on 2/1/2025 automatically sets the OLI start and end dates to 2/1/2025–12/31/2025. After assetization, the product carries these same subscription dates.
Add-on Sale Order
Adding another product to the same contract on 3/1/2025 via an initial sale order automatically sets the QLI dates to 3/1/2025–12/31/2025 to match the contract end date.
Amendment Order
When a user extends the contract end date to 6/30/2026 and amends a product, the QLI end date automatically adjusts to 6/30/2026.
Renewal Order
If you renew a contract with the cotermination flag set to True, subscription end dates automatically align with the contract renewal date.
Negative Amendments with Contract Date Changes
If a user extends a contract end date to 6/1/2026 while performing a negative amendment for 10 licenses of an original 100-license sale, the end dates for the remaining 90 licenses update to 6/1/2026.
