---
article_id: ind.um_sum_statuses_through_cnsmptn_mngmnt_lifecycle.htm
title: Consumption Management Lifecycle Statuses
source_url: https://help.salesforce.com/s/articleView?id=ind.um_sum_statuses_through_cnsmptn_mngmnt_lifecycle.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Consumption Management Lifecycle Statuses

The successful processing of consumption data involves status changes across the interlinked summaries—Usage Summary, Usage Ratable Summary, and Liable Summary. The entire flow, from raw usage data in the transaction journal to the calculation of net unit rates and the creation of invoice-ready data, is managed through these coordinated summaries.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license
Usage Summary

The usage summary stores the aggregated transaction journal entries and drawdown results for a specified period.

STATUS	WHAT DOES IT MEAN?	PROCESSING JOB
New	Zero-value usage summary record is created.	Create Empty Summaries batch job
Usage Summary In Progress	Usage summary is being updated with consumption data provisionally.	Create Usage Summary Data Processing Engine job
Usage Summary Complete	The time period to rate the consumption data along with the waiting period is achieved for the linked usage summary. The usage summary is frozen and sent for drawdown. After the Usage Summary reaches this state, no transaction journal entries are considered for the specified period.	Create Usage Summary Data Processing Engine job
Drawdown Complete	Consumption drawdowns are processed, and the overages are added to the usage summary. The usage summary is sent to generate the ratable summary.	Process Consumption Overages batch job
Ratable Summary Complete	Ratable summary is generated for the usage summary.	Create Ratable Summary batch job
Liable Summary Complete	Liable summary is generated for the usage summary.	Usage Liable Summary DPE Job
Usage Ratable Summary

The usage ratable summary stores the aggregated usage summaries and the calculated rates at which the overages are charged.

STATUS	WHAT DOES IT MEAN?	PROCESSING JOB
New	Zero-value usage ratable summary record is created.	Create Empty Summaries batch job
Rating In Progress	The provisional rating of the usage ratable summary is complete. During the provisional rating run, the rating process rates the usage summary cumulatively, and the calculated rate is reevaluated as new usage is recorded throughout the billing cycle.	Create Ratable Summary batch job
Summary Created	Usage ratable summary is updated with the aggregated usage summaries after the billing period is complete.	Create Ratable Summary batch job
Rating Complete	Usage ratable summary is updated with the net unit rate applicable for the overages.	Retrieve Net Unit Rates for Ratable Summary batch job
Rating Failed	Usage ratable summary failed to record the net unit rates and couldn’t be updated.	Net Unit Rate batch job
Liable Summary

The liable summary stores the calculated overages for the services and the amount that’s charged for these overages.

STATUS	WHAT DOES IT MEAN?	PROCESSING JOB
New	Zero-value usage summary record is created.	Create Empty Summaries batch job
Liable Summary In Progress	Liable summary is updated with provisional data, including the current running overage amount and the total unbilled usage quantity for the billing period to date.	Create Liable Summary DPE Job
Liable Summary Complete	Liable summary is updated with the details of overages and the applicable net unit rate.	Create Liable Summary DPE job
Ready for Invoicing	The billing cycle is completed for the liable summary, and the liable summary is ready for invoicing.	Create Liable Summary DPE job
