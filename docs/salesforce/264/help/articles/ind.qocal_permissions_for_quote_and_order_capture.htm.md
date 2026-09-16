---
article_id: ind.qocal_permissions_for_quote_and_order_capture.htm
title: Personas and Permissions Sets for Transaction Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_permissions_for_quote_and_order_capture.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_quote_and_order_capture.htm
fetched_at: 2026-09-04
---

# Personas and Permissions Sets for Transaction Management

Transaction Management offers specific permission sets for different users involved in creating and managing sales transactions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
IMPORTANT Assign permission sets to users before they create quotes or orders. If a user creates a quote without the required permissions, the system permanently assigns a non-Revenue Management pricing type to the quote. Adding the correct permissions after creating the quote doesn't change the pricing type. The user must create a new quote after receiving the correct permissions.
Create Users and Profiles

To begin, create users for Transaction Management. Then assign users the appropriate permission sets. To help you plan, refer to the Transaction Management Personas table.

When you create a user, you must also assign a profile. Profiles define default settings for users. Some organizations create their own profiles, while others choose to use profiles included with Salesforce.

Remember, users can have only one profile, but can have many permission sets assigned to them.

Transaction Management Personas

Multiple users who work in various capacities within an organization can use and manage Transaction Management.

PERSONA	DESCRIPTION
Transaction Management Admin	

The admins perform these tasks.

Enable Quote and Order Capture.
Customize page layouts.
Customize components in Lightning App Builder.
Enable features.

Sales Rep	Sales reps browse catalogs, create quotes, and place orders.
Sales Operations Rep	Sales operations reps assetize orders and amend, renew, and cancel orders using Asset Lifecycle Management.
NOTE Non-admin users may encounter a FieldUndefined error (RelatedRevenueTransactionErrorLogs) when accessing quote line items. For troubleshooting steps, see Non-Admin Users Error Accessing Quote Line Items.
Transaction Management Permission Sets and Licenses

Manage sales transactions easily and securely by using permission sets that use the Revenue Cloud User permission set license. Permissions are added so that specific user personas can complete the work for their role.

The Revenue Cloud User permission set license provides access to product configuration, quotes, orders, and asset lifecycle management.

PERMISSION SET	QUOTE AND ORDER CAPTURE ADMIN	SALES REP	SALESFORCE OPERATIONS REP
Assetize Order	—	—	Yes
CalculatePrices API	Yes	Yes	Yes
CalculateTaxes API	—	Yes	Yes
Create Orders from Quotes	—	Yes	Yes
CreateContract API	—	Yes	Yes
InitiateAmendment API	—	—	Yes
InitiateCancellation API	—	—	Yes
InitiateRenewal API	—	—	Yes
PlaceOrder API	—	Yes	Yes
Price and Tax Calculation for Quoting	—	Yes	—
ProductAndPriceConfiguration API	Yes	Yes	Yes
ProductImport API	Yes	Yes	Yes
Document Builder User	Yes	Yes	Yes
