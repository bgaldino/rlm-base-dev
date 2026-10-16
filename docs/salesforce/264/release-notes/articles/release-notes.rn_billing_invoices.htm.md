---
article_id: release-notes.rn_billing_invoices.htm
title: Invoice Management
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_invoices.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing.htm
fetched_at: 2026-09-30
---

# Invoice Management

Invoice each account for every billing schedule group that the account owns or is billed for. Resume billing on migrated schedules without reissuing past invoices, produce invoice documents during batch runs, and embed record fields into invoice and credit memo numbering. Set invoice target dates by calendar day or number of billing periods, track each schedule's periods and milestones on a timeline, review linked split invoices before you act, and forecast upcoming charges before invoices are created.

Generate Invoices Across Accounts for Owned and Billed Charges
At the account level, run Generate Invoices, Preview Invoices, and Invoice Scheduler for all billing schedule groups that list the account as a billing account in a billing arrangement. Billing includes both owned and billed groups by default. Accounts are invoiced for every billing schedule group they owe, including split invoices for charges owned by other accounts. This change eliminates manual reconciliation across split billing scenarios. Previously, account-level operations processed only billing schedule groups the account owned.
Advance Migrated Billing Schedules Without Rebilling by Using Catch-Up Bill Runs
Migrate billing transactions from an external system to Salesforce and resume billing from the appropriate point. Use catch-up bill runs to advance billing schedules to a target date without generating invoices for previously billed periods. Preserve billing continuity without reprocessing historical invoices or triggering unnecessary tax processing.
Generate Invoice Documents Automatically During Invoice Batch Runs
Create invoice documents automatically as invoices are streamed during a batch run, eliminating the need for a separate document generation step.
Generate Context-Rich Sequence Patterns with Dynamic Fields
Embed standard or custom fields from target objects, such as invoice and credit memo, into sequence patterns to encode business context into sequence numbers. Combine dynamic fields with static text to create numbering formats that support compliance and operational requirements.
Set Invoice Target Dates by Calendar Day or Billing Period Count
Adapt invoice processing for complex billing scenarios with dynamic target dates in invoice batch runs and Invoice API. Set target dates based on a specific calendar day of the month or a fixed number of billing periods instead of static day offsets.
Preview Future Invoice Charges with Billing Forecast
Get full transparency into projected billing charges before invoices are created. Run scheduled forecasts for one-time and subscription charge types and categories. Use forecast data to align with customers on upcoming charges and report on projected billing.
