---
article_id: ind.um_usage_orchestration_flow_stages.htm
title: Orchestrate Usage Management Flow Stages
source_url: https://help.salesforce.com/s/articleView?id=ind.um_usage_orchestration_flow_stages.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Orchestrate Usage Management Flow Stages

The Orchestrate Usage Management flow with its subflows processes consumption data in various stages.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license
Generate Zero-Value Summary Records
Generates advanced zero-value records for Usage Summary, Usage Ratable Summary, and Liable Summary (Usage Billing Period Item). This stage streamlines downstream operations that let the subsequent batch management jobs update existing summaries. For products that are assetized on the current date but were purchased on an earlier date, this stage creates summaries with records aggregated until today.
Aggregate Transaction Journal Records
Summarizes raw usage records from transaction journal entries by using the batch job and determines the overall consumption within a specified period. This aggregation is governed by the usage accumulation method and the usage accumulation period specified in the usage aggregation policy. The aggregated consumption is then stored in a Usage Summary record.
Transaction journal entries are aggregated into usage summaries throughout the billing period. For late data ingestion, the process adds a waiting period (x) after the ratable period's end date and time (T). The default value for this waiting period (or rating delay duration) is 3 days, however, you can customize the flows and update it as per your requirements.
After the waiting period is complete, the status of the usage summary is updated to UsageSummaryComplete.
On the T+x+1 day, the process executes the drawdown process, aggregates any overages to update the ratable summary, and calculates the net unit rate.
If you add consumption logs via transaction journal entries after the T+x waiting period is complete and the usage summary status is updated to UsageSummaryComplete or DrawdownComplete, the Data Processing Engine filters out and ignore the newly added logs for that period.
Process Drawdowns
Processes the aggregated usage summary records. The batch management job in this stage calls the entitlement service that processes the drawdowns for the grants allocated with the asset. The drawdowns happen after the deterministic order logic is applied to the usage summaries. Here’s the priority sequence that the deterministic logic applies.
Usage Summary with the earliest start date is prioritized. For example, a usage summary starting on January 1, 2024 is prioritized over a usage summary starting on January 2, 2024.
If start times are identical, the summary related to the asset that was created earliest with the earliest transaction usage entitlement start date is prioritized. For example, if two usage summaries have the same start date, the summary related to an asset that started on January 1 (Asset 1) is prioritized over the usage summary associated with the other asset that started on September 1 (Asset 2).
If the first two scenarios are tied, the summary related to the transaction usage entitlement with the lowest numerical name is processed first. For example, two usage summaries and their related assets started on the same date, but one is related to a transaction usage entitlement record with the TUE-0000000034 record name, and the other is related to the TUE-0000000045 record name. So, the usage summary related to TUE-0000000034 is prioritized.
After the drawdowns are processed, the corresponding wallet for each asset or binded object is also updated.
Retrieve Net Unit Rates
Retrieves the applicable net unit rate by using the rating procedure specified in the Generate Ratable Summary flow. Usage Management executes rating daily. The batch job first determines the rating schedule and processes summaries provisionally. By using the selected rating procedure, the process identifies the relevant context definition ID and mapping ID required by the rating service to determine the final net unit rate. This rate, along with the identified IDs, is then stamped on the ratable summary records. Customers can gain immediate insight into provisional balances and overages visible on their summaries before the end of the billing period. After the billing period is complete, a cumulative ratable summary is created with the rates applied to the usage summaries based on consumption from the start of the billing period.
Generate Liable Summary Records
Generates the invoice-ready records on a periodic schedule. The process filters the usage summary records that were successfully rated, determines the billing period, calculates the overages and the overage amount, identifies the related liable summary records, and updates these records with the overage amount and quantity.
