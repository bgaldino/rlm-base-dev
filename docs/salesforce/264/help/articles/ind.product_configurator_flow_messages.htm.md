---
article_id: ind.product_configurator_flow_messages.htm
title: Messages
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_messages.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_flow_screen_components.htm
fetched_at: 2026-11-23
---

# Messages

Messages is a UI display component that renders validation messages to Product Configurator users. The component shows messages in an expandable accordion and filters messages by severity, either Error, Warning, or Info. Messages has no output properties, and doesn’t listen to or fire any events.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Messages Responsibilities
Display validation messages as Error, Warning, or Info, in an expandable accordion interface
Sort messages by severity
Show count badges for each message type
Allow users to filter messages by severity
Dynamically track accordion height
Support fixed or relative positioning for messages in the user interface
API Name

S01_Messages

Input Properties

Messages accepts data from these parent and flow component properties, set by users.

PROPERTY	TYPE	REQUIRED	DESCRIPTION
messages	Array	Yes	Array of message objects from DataManager
areMessagesFixed	Boolean	No	

Whether messages have fixed position (scroll with UI) or relative position

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_messages.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
