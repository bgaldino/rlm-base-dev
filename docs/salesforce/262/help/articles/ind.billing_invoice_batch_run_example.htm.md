---
article_id: ind.billing_invoice_batch_run_example.htm
title: "Examples: Invoice Batch Run Frequencies"
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_batch_run_example.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Examples: Invoice Batch Run Frequencies

Explore examples to understand how to schedule invoice batch runs based on your requirements.

Weekly Invoice Schedule

Cumulus Cloud Corporation operates in an industry that requires frequent billing cycles to maintain cash flow and minimize outstanding payments. Weekly invoicing ensures timely processing, reduces the risk of delays, and enhances financial tracking. Invoices are initially set to draft status for internal review before finalization, ensuring accuracy. The company generates invoices every Monday to cover the previous week's charges. The company configures invoice runs by using these values.

Invoice Status: Draft (for internal review to ensure accuracy)
Frequency: Weekly every Monday
End Date: Dec 31, 2025
Target Date Offset: —7 (to include the previous week's invoices)
Monthly Invoice Schedule

Ursa Major Solar, a renewable energy company, follows a subscription-based model, billing customers for recurring and usage-based charges. A monthly invoicing cycle aligns with standard subscription practices, making invoice management easier for customers. The company generates invoices on the 1st of each month for applicable charges. If this date falls on a public holiday, invoicing is postponed to the next business day. Automatically posting invoices streamlines billing, reduces manual effort, and improves revenue recognition. The company configures invoice runs by using these values.

Invoice Status: Post invoices (to generate invoice documents)
Frequency: 1st day of every month
Special Requirement: If the 1st day of the month is a public holiday, shift to the next business day and generate invoices only for recurring and usage-based charges.
On-Demand Invoice Schedule

Northern Trail Outfitters needs on-demand invoicing to handle urgent client requests and one-time services across various regions. The run now option allows invoices to be created immediately, instead of waiting for a set schedule. This improves cash flow, reduces delays in billing, and makes it easier to manage invoices. The company configures invoice runs by using these values.

Invoice Status: Post invoices (to generate invoice documents)
Frequency: Generate invoices on-demand
Special Requirement: Include the billing schedules for all currencies.

Each company's invoicing schedule is strategically designed to align with its business model, optimize cash flow, and enhance customer experience.
