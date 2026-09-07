---
article_id: ind.pricing_perform_pricing_adjustment_batch_job.htm
title: Perform a Pricing Adjustment Batch Job
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_perform_pricing_adjustment_batch_job.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_adjustment_batch_jobs.htm
fetched_at: 2026-09-07
---

# Perform a Pricing Adjustment Batch Job

Before you begin a pricing adjustment batch job, remember the following.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To view pricing adjustment batch job logs:	Salesforce Pricing Design Time
All bulk updates are made to a product's price. So, you can make a bulk update to any price adjustment schedule or price book.
You can update up to 200 pricing records in a batch.
Don’t run multiple batch jobs simultaneously. Wait for each job to complete before starting the next one.

Let’s consider a scenario where we need to make a bulk update of increasing the price by $10 of all products whose product selling model is set to Evergreen.

From App Launcher, find and select Price Management.
From the app navigation menu, select Price Books.
Select Standard Price Book.
On the Related tab, under the Price Book Entries section, click View All.
A list of all the price book entries associated with the Standard Price Book are displayed.
Based on our example, select all the entries whose product selling model is Evergreen.
Select Pricing Adjustment Batch Job.
In the Update Price Book Entries window, specify these details.
Update Type: Amount
Update Value: $10
NOTE
The update value depends on the update type selected. There are three types of updates - Amount, Percentage, and Override.
To increase the value of your record, add a whole number. To decrease the value of a record, add a negative value. If the update type is Amount, and you want to increase the dollar value of your records, enter 10, and to decrease the adjustment value, enter -10.
If you’re making changes to a price adjustment schedule, then you’ll need to provide effective dates.
Price book entries only store the price of a product and don’t have effective dates associated with their records.
Save your changes.
