---
article_id: ind.um_consumption_management_standard_flow_templates.htm
title: Consumption Management Flows
source_url: https://help.salesforce.com/s/articleView?id=ind.um_consumption_management_standard_flow_templates.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Consumption Management Flows

To process consumption data and generate invoice-ready summaries, the consumption management process uses schedule-triggered flows.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license
IMPORTANT Before you schedule the flows, change the default context in which the flows run to System Context without Sharing. See Change the Flow Run Context.

To process consumption data, save each flow as a new flow and schedule it based on your organization’s needs. Schedule the Entitlement Refresh flow to run before the Orchestrate Usage Management flow. See Schedule-Triggered Flows.

Schedule Entitlement Refresh flow—runs the entitlement refresh batch job at the scheduled date and time.
Call Entitlement Refresh Service—calls the Refresh Usage Entitlement Bucket invocable action to refresh usage entitlements.
Orchestrate Usage Management flow—processes consumption data and creates invoice-ready summaries by using these subflows.
Generate Usage Summary flow—creates zero-value summaries and updates usage summaries by aggregating transaction journal records.
Generate Usage Ratable Summary flow—processes drawdowns, applies the net unit rate retrieved by using the rating request, and updates the usage ratable summary and the asset-related wallets.
Generate Liable Summary—summarizes the consumption overages in the usage summary and usage ratable summary.
