---
article_id: ind.pricing_pricing_adjustment_batch_jobs.htm
title: Pricing Adjustment Batch Jobs
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_pricing_adjustment_batch_jobs.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_price_adjustment_schedules_salesforce_pricing.htm
fetched_at: 2026-09-07
---

# Pricing Adjustment Batch Jobs

Utilizing pricing adjustment batch jobs is key for efficient, accurate bulk pricing updates. You can initiate these operations directly from the Related List and List View components of Price Book Entry, Attribute Based Adjustment, Bundle Based Adjustment, and Price Adjustment Tier objects.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

For failed requests, a detailed report with error messages is available via the related list of the batch job record. This allows you to quickly identify issues, make necessary edits, and re-execute the job to ensure all adjustments are applied successfully.

Let’s explore the primary tasks you can perform using the Pricing Adjustment Batch Jobs feature.

Perform a Pricing Adjustment Batch Job
Before you begin a pricing adjustment batch job, remember the following.
View Pricing Adjustment Batch Job Logs
After your pricing adjustment batch job record is created, you can check the status and details of the job. If your batch job has failed or partially failed, you can review the generated logs to find out the reason for the failure.
Fix and Execute Failed Pricing Adjustment Batch Jobs
You can resolve issues with your failed records by making the necessary edits and running the pricing batch job again. For example, a pricing adjustment batch job may fail when an adjustment relies on a product attribute that is missing or invalid.
