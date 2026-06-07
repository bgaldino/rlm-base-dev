---
article_id: ind.rm_implementation_considerations.htm
title: Implementation Considerations for Rate Management
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_implementation_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Implementation Considerations for Rate Management

Learn about the limitations in Rate Management and the points to keep in mind when you plan your implementation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
To create Unit of Measure records for Rate Management, you must add picklist values for the Type field on the Unit Of Measure object.
Rate card entry uses the same default unit of measure that’s defined in the related usage resource record.
Only Salesforce admins can create and run batch jobs for Rate Management.
Starting in Summer ’25, admins can choose between decision tables and real-time data for rating procedures. The real-time data option ensures accuracy but impacts performance. Conversely, not using real-time data can enhance performance but requires manual updates of decision tables when base rates, tiers, or adjustments change, or during the quote capture and order lifecycle. To avoid the overhead of manual refreshes and to ensure precise data retrieval, we recommend that you select the data retrieval method that most closely meets your unique needs and performance criteria.
Real-time data doesn't support the "not matches" or "contains" operators. If you’re using customized decision tables that include these operators, we recommend manually syncing the decision tables.
Rate Management provides real-time data support for these elements available in the respective procedures.
Rating Discovery Procedure
Get Binding Object Rate Adjustment
Get Binding Object Rate Card Entries
Negotiable Rating Procedure
Negotiated Rate Card Entries
Negotiated Base Rate
Negotiated Volume-Based Rate Adjustment
Commitment Rate Adjustment
For optimized data retrieval while running rating procedures, make sure that the number of decision tables in your org is within the specified limits. To know the maximum number of decision tables supported in an org, see Business Rules Engine Default Limits.
