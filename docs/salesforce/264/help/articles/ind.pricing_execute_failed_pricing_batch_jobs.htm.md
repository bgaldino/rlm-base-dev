---
article_id: ind.pricing_execute_failed_pricing_batch_jobs.htm
title: Fix and Execute Failed Pricing Adjustment Batch Jobs
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_execute_failed_pricing_batch_jobs.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_adjustment_batch_jobs.htm
fetched_at: 2026-09-07
---

# Fix and Execute Failed Pricing Adjustment Batch Jobs

You can resolve issues with your failed records by making the necessary edits and running the pricing batch job again. For example, a pricing adjustment batch job may fail when an adjustment relies on a product attribute that is missing or invalid.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To view pricing adjustment batch job logs:	Salesforce Pricing Design Time
From App Laucher, search and select Price Adjustment Batch Jobs.
Open a failed or partially completed pricing adjustment batch job.
In the Related tab, see the list of failed records under Pricing Adjustment Batch Job Log.
TIP To see the entire list of failed or partially completed jobs, select View All under Pricing Adjustment Batch Log. The entire list appears in a new tab, making it easier to filter through the records.
Select  against each record and make your edits.
To execute the pricing adjustment batch job again, select Rerun.
