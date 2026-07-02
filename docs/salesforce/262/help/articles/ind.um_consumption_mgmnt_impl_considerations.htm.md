---
article_id: ind.um_consumption_mgmnt_impl_considerations.htm
title: Consumption Management Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.um_consumption_mgmnt_impl_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Consumption Management Considerations

Here are the key things to consider when you use Consumption Management for your organization.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license
Usage management creates empty usage, ratable, and liable summary records in advance, but only up to the active billing period. For example, if an asset's effective period is from July 1, 2025, to June 30, 2026, and you trigger the Orchestrate Usage flow on April 9, 2026, the system generates zero-value summaries only through the April 2026 billing period. It doesn't create summaries for May or June until you run the flow again in those respective months. 
Usage Summary records are created only when the liable summary period term is longer than the ratable summary period term and the ratable summary period term is longer than the usage summary period term.
The timestamp on the transaction journal records is in the Coordinated Universal Time (UTC) time zone.
To view transaction journal entries, the Standard User profile must have Read access to the Quantity, Quantity Unit, Transaction Amount, Start Date, and End Date fields on the Transaction Journal object.
To maintain the accuracy of transaction journal data, set the scale to 6 for the Quantity field of the Transaction Journal object.
Consumption Management uses these Data Processing Engine definitions:
Generate Usage Summary
Generate Ratable Summary
Generate Liable Summary
NOTE To use the Create Usage Summary definition, set field-level security for all the fields on the Transaction Journal object. See Field Permissions.
When a usage entitlement account record isn't processed after it's created, the billing period start date and end date fields default to December 31, 1969, 4 PM PST. The system uses January 1, 1970, 12 AM GMT as a placeholder to indicate that the record is unprocessed. The fields update with the correct values after the Create Summary flow is triggered.
If an order is assetized with a start date earlier than the date the order was created, you must run the Call Entitlement Refresh Service standard flow to refresh the active transaction usage entitlements. You must also call the flow for the back-dated products that are part of group segments. Usage entitlement buckets aren’t refreshed for expired segments.
Consumption Management considers only the date of an asset, regardless of the time the product is ordered. For example, if a customer buys a mobile plan at 3 PM on October 10, 2025, the order start date and time is October 10, 2025, at 3:00 PM. However, Consumption Management considers the start date for that asset to be October 10, 2025, at 12:00 AM.
If you encounter issues with the usage liable summary, such as the overage amount shown is zero, ask your Salesforce admin to enable Null Measure Handling. See Enable Null Measure Handling.
SEE ALSO
Orchestrate Usage Management Flow Stages
