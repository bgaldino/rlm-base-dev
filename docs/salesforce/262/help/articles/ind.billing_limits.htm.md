---
article_id: ind.billing_limits.htm
title: Limits in Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_limits.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Limits in Billing

Review the default limits for Billing features.

Billing Business API Limits

See Billing Business API Limits to learn about the default limits on the usage of the Billing business APIs.

Total Heap Size Limit for Custom Tax Engine Apex Adapter

From Summer ’25, Billing supports up to 2000 invoice lines for a single invoice. To avoid limit-related issues, test your TaxEngineAdapter Apex interface’s implementation to make sure that it adheres to the Apex limit for total heap size.

See Tax Setup Prerequisites.

Invoice Lines Limit for Invoice Batch Runs

Invoice batch runs can generate a maximum of 2000 invoice lines for an invoice. Since invoice runs use Data Processing Engine, it is crucial to also understand the default limits for Data Processing Engine and Data Pipelines. These underlying limits can impact the overall invoice generation by batch runs.

You can have a maximum of 30 active billing batch schedulers.

See Automated Invoice Generation with Invoice Batch Runs.

Document Generation Request Limits

Before generating invoice PDF documents, review the default limits for document generation requests and the process for increasing the maximum number of content versions that are published per day.

See Generate a Batch of Invoice PDF Documents.

Email Limits

A maximum of 5000 emails can be sent to the email address on Bill to Contact records daily. To send emails beyond the daily limit, enable customer user for the Bill to Contact record. Emails sent to customer community users are not counted against the 5000 daily email limit. The system first checks for a customer community user before considering the email address on the Bill to Contact record.

See Send Invoices Through Email.
