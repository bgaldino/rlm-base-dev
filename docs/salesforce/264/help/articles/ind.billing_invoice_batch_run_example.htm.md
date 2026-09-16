---
article_id: ind.billing_invoice_batch_run_example.htm
title: "Examples: Invoice Batch Run Frequencies"
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_batch_run_example.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_automate_invoice_generation.htm
fetched_at: 2026-09-04
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
Invoice Schedule with Billing Period Count

Cloud Kicks sells memberships billed monthly and quarterly. Those billing schedules don’t share the same next billing date. A later target date that includes all of them invoices extra periods on the monthly memberships. To invoice one period for each selected schedule, the company configures invoice runs by using these values.

Invoice Status: Post invoices
Frequency: Monthly
Select billing schedules based on: Billing Period Count
Billing Period Count: 1
Monthly Invoice Schedule Using Day of Month

Edge Communications invoices customers through the last day of the previous month. The invoice batch run runs on the 5th of each month. Billing calculates the target date as the last day of the previous month and stamps that date on each invoice for tax. The company configures invoice runs by using these values.

Invoice Status: Post invoices
Frequency: Monthly
On: Specific Date
Date: 5
Select billing schedules based on: Target Date
Base Target Date On: Day Of Month
Target Day Of Month: last
Target Month Offset: −1
Base Invoice Date On: Offset from Target Date
Invoice Date Offset: 0

Each company's invoicing schedule is strategically designed to align with its business model, optimize cash flow, and enhance customer experience.
