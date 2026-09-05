---
article_id: ind.qocal_considerations_for_group_ramps_for_usage_products.htm
title: Set Up Ramp Deals for Groups
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_considerations_for_group_ramps_for_usage_products.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.setting_up_ramp_deals.htm
fetched_at: 2026-09-04
---

# Set Up Ramp Deals for Groups

After prerequisites are complete, here's the end-to-end setup flow.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
Step 1: Complete the Prerequisites

Complete all steps in Prerequisites: Ramp Deals for Groups. Turn on Enable Groups in Quotes and Orders, Clone Quotes and Orders, and Ramp Deals for Groups in Quotes and Orders. Optionally turn on Multiple Ramp Schedules Per Transaction and Trial Segments for Group Ramp Schedules.

Step 2: Configure the Product Discovery Flow

Use the Discover Products flow to select a catalog and then add products from the catalog to their associated record pages. The Discover Products flow is readily available with Product Discovery, and you can customize the flow beyond the available capabilities to meet your business needs. For more information, follow steps 5 to 7 in Prerequisites: Ramp Deals for Groups.

Step 3: Configure the Transaction Line Editor

In Setup, add the Sales Transaction Line Editor component to quote and order page layouts and configure it to show the required segment and group fields as described in the prerequisites.

Step 4: Create Ramp Schedules

In Setup, find and select Revenue Settings. In Set Up Flow for Creating Ramp Schedules, provide the API name of the flow to use when creating a ramp schedule. This setting unlocks segment selection, letting sales reps add products to the current segment only or to current and subsequent segments.

Step 5: Test

Create a quote or order with ramp deals for groups to verify the setup works as expected.
