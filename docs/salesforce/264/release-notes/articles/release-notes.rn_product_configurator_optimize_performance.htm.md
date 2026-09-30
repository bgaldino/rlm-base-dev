---
article_id: release-notes.rn_product_configurator_optimize_performance.htm
title: Optimize Performance for Revenue Management (Release Update)
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_product_configurator_optimize_performance.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_product_configurator.htm
fetched_at: 2026-09-30
---

# Optimize Performance for Revenue Management (Release Update)

This update optimizes the Configuration API to speed up processing times in Product Configurator. Enable the test run in a sandbox environment to confirm that the optimizations work with your setup. This update is available starting in Winter ’27.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

When: Salesforce enforces this update in Summer ’27. The update is opt-in until the enforcement date. To get the major release upgrade date for your instance, go to Trust Status, search for your instance, and click the maintenance tab.

Why: Product Configurator delivers faster response times for key flows, such as launching the configurator, updating attributes or quantities on configured products, and adding or removing options during bundle configurations. The inputs, outputs, and behavior of the configuration flows are unchanged. Only the performance is improved, particularly in high-volume transaction scenarios.

How: To review this update, from Setup, in the Quick Find box, enter Release Updates, and then select Release Updates. For Optimize Performance for Revenue Management, follow the testing and activation steps.

The change is an opt-in release update with Test Run support, so you can validate against your existing workflows in a sandbox org and enable the update in production when you're ready. If you encounter issues, disable the test run to revert to the previous implementation. Report any issues to Salesforce Customer Support before the enforcement date.
