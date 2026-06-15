---
article_id: ind.um_key_objects_in_consumption_management.htm
title: Consumption Management Records
source_url: https://help.salesforce.com/s/articleView?id=ind.um_key_objects_in_consumption_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Consumption Management Records

Usage Management creates certain object records that the Consumption Management process uses to track and manage the grant consumption. You can use these records to view and understand how the process manages the provided grants.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license
OBJECT	DESCRIPTION
Usage Entitlement Account	A usage entitlement account is a customer instance of the purchased product. Usage Management creates this record after an order is assetized. The object record includes the billing cycle details for the product, such as billing frequency, billing day of the month, start and end date of billing period and the service. A usage entitlement account has individual usage entitlement buckets for each usage resource.
Usage Entitlement Bucket	A usage entitlement bucket represents a wallet that records the credits and debits of a usage resource. If grants are rolled over or renewed, units are added to the bucket balance. When the customer consumes the usage resource, units are debited from the bucket balance.
Usage Entitlement Entry	A usage entitlement entry represents a transaction entry that records each credit and debit entry for the usage entitlement bucket.
Transaction Usage Entitlement	A transaction usage entitlement stores information about how grants are tracked and managed. The object record includes the associated usage grant rollover policy, usage grant refresh policy, drawdown order in which the grant consumption is debited, and other details.
