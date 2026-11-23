---
article_id: release-notes.rn_large_txn_clone_quotes_orders.htm
title: Clone Large Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_large_txn_clone_quotes_orders.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_large_txn.htm
fetched_at: 2026-11-23
---

# Clone Large Quotes and Orders

Sales reps no longer run into a line-item ceiling when cloning their biggest quotes and orders. The Clone API processes these large-scale clones asynchronously, returning a context ID and an async operation tracker ID so you can follow progress. When a clone finishes, reps see a completion alert, and any failures show a specific, actionable error message instead of a generic one.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Cloud, with the Revenue Cloud Advanced license.

How: From Setup, in the Quick Find box, search for and select Revenue Settings. Turn on Clone Quotes and Orders.

SEE ALSO
Salesforce Help: Clone Quotes and Orders
Salesforce Help: Clone Behavior for Large Transactions

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=release-notes.rn_large_txn_clone_quotes_orders.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
