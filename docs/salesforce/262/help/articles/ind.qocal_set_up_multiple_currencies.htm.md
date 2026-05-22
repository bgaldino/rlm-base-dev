---
article_id: ind.qocal_set_up_multiple_currencies.htm
title: Multiple Currencies for Transactions
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_multiple_currencies.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Multiple Currencies for Transactions

Turn on multiple currencies to help your users to transact in different global units. The system uses the currency code in the Quote or Order Currency fields to determine the transaction's currency.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To edit pricing procedures:	Salesforce Pricing Design Time User
Turn on and activate other currencies in Setup.
Enable multiple currencies
Activate and Deactivate Currencies
Create a price book for the new currencies and add your products. Create a price book for the currencies. See .
See Define Prices in Price Books
Open your Pricing Procedure and deactivate the version.
Map the CurrencyIsoCode input variable to PricingCurrencyCode in the Pricing Setting element.
See Map Context Tags in Pricing Procedures.
Activate the procedure.
NOTE Only the Place Sales Transaction API supports multi-currency transactions.
