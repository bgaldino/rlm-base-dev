---
article_id: ind.product_configurator_flow_transaction_header.htm
title: Transaction Header
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_transaction_header.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_flow_screen_components.htm
fetched_at: 2026-11-23
---

# Transaction Header

Transaction Header is a navigation and control component that displays a header with a dynamic Back or Cancel button at the top of Product Configurator. The component allows users to exit the configurator and navigate back to the parent transaction record. Transaction Header has no output properties and doesn’t listen to any events.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Transaction Header Responsibilities
Show the Back/Cancel button with dynamic label
Navigate back to parent transaction record
Show confirmation dialog before canceling, when the user isn’t in preview mode
Handle preview mode without confirmation
Fire CustomEvent to close Product Configurator
Transaction Header API Name

S01_TransactionHeader

Input Properties

Transaction Header accepts data from this property, set by users.

PROPERTY	TYPE	REQUIRED	DESCRIPTION
transactionRecord	Object	Yes	Transaction record data (parentId, parentName, origin)
Events Transaction Header Fires

Transaction Header fires this custom event to close Product Configurator.

EVENT NAME	BUBBLES	COMPOSED	WHEN IS IT FIRED	PURPOSE
proceed	Yes	Yes	User confirms cancel (non-preview mode)	Close configurator without saving

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_transaction_header.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
