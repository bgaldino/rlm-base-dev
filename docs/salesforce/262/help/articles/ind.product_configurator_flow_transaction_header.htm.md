---
article_id: ind.product_configurator_flow_transaction_header.htm
title: Transaction Header
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_transaction_header.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Transaction Header

Transaction Header is a navigation and control component that displays a header with a dynamic Back or Cancel button at the top of Product Configurator. The component allows users to exit the configurator and navigate back to the parent transaction record. Transaction Header has no output properties and doesn’t listen to any events.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
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
