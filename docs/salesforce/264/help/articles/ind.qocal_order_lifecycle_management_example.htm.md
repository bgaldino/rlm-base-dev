---
article_id: ind.qocal_order_lifecycle_management_example.htm
title: Order Lifecycle States and Transitions
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_order_lifecycle_management_example.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_order_lifecycle_management_using_object_state_definitions.htm
fetched_at: 2026-11-23
---

# Order Lifecycle States and Transitions

Familiarize yourself with the specific states and transitions used to manage an order through its lifecycle. Use this example and the accompanying object state definitions to configure valid status changes and establish clear fulfillment milestones in your Salesforce org.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Order Lifecycle Diagram

Review these specific transition rules from the diagram.

The status changes from Submitted to Processing.
The status changes from Processing to either Fulfilled or Rejected.
The status doesn’t change from Rejected or Fulfilled.

To implement this example order lifecycle, create an object state definition and then add these object state values and object state transitions.

Object State Values

To implement this lifecycle, create an object state definition and add these values.

ORDER STATUS AND OBJECT STATE VALUE	DESCRIPTION
Draft	The order is being created.
Ready to Submit	The order is ready for submission or approval.
Submitted	The order is submitted and is ready for processing.
Processing	The order is being processed.
Rejected	The order is rejected, or there’s an error during processing.
Fulfilled	The order is fulfilled.
Object State Transitions

Define these transitions to control the movement between states.

OBJECT STATE TRANSITION NAME	FROM STATE	TO STATE
Draft_to_ReadytoSubmit	Draft	Ready to Submit
ReadytoSubmit_to_Draft	Ready to Submit	Draft
ReadytoSubmit_to_Submitted	Ready to Submit	Submitted
Submitted_to_Processing	Submitted	Processing
Processing_to_Rejected	Processing	Rejected
Processing_to_Fulfilled	Processing	Fulfilled

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_order_lifecycle_management_example.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
