---
article_id: ind.qocal_limits.htm
title: Transaction Management Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_limits.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_quote_and_order_capture.htm
fetched_at: 2026-11-23
---

# Transaction Management Limits

Review the record, attribute, and bundle limits for Transaction Management to make sure that your quotes and orders remain within supported thresholds. Understanding these technical specifics helps you optimize performance and avoid process timeouts during asset lifecycle operations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Record and Attribute Limits

Transaction Management enforces limits on the number of line items and related records to maintain system stability.

OBJECT	LIMIT
Quote Line Items	Up to 1,000 per quote
 	Up to 10-MB limit when importing quote lines by using a CSV import. If you receive a RESPONSE_SIZE_LIMIT_EXCEEDED error, the file is too large. Create smaller files and try again
Order Products	Up to 1,000 per order
Total Quote Records	Up to 5,000 total records per quote, including related records like relationships, attributes, related objects, tax items, and price adjustments
Quote Line Item Attributes	Up to 3,000 per quote
Order Line Item Attributes	Up to 3,000 per order
Asset Lifecycle Flow Limits

Standard flow timeouts impact the creation of amendment, renewal, and cancellation (ARC) quotes when they use the UI.

The UI supports creating ARC quotes with up to 300 lines.
Update quotes to 1,000 lines by using Asset Lifecycle Standard Invocable Actions or the Add Assets button in the Quote Viewer.
Bundle and Apex Performance Recommendations
Bundle Size: A bundle includes up to 200 lines, including the root product. This size means a single quote line item or order line item for a bundle supports up to 199 associated child items.
Apex Optimization: Synchronous custom Apex code consumes significant resources and triggers governor limits. Use Asynchronous Apex to optimize performance.
IMPORTANT To raise these limits when possible, contact Salesforce Customer Support.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_limits.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
