---
article_id: ind.product_configurator_visual_builder_dynamic_message_rule.htm
title: Dynamic Message Rule in the Visual Builder
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_visual_builder_dynamic_message_rule.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_visual_builder_constraint_and_rule_types.htm
fetched_at: 2026-11-23
---

# Dynamic Message Rule in the Visual Builder

The dynamic message rule shows a message to users if the specified condition is true. Include a message to provide the user with information about an item, such as a promotional offer on a selected product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

In the dynamic message rule window, add one or more expressions to define a condition or conditions that, if true, show a message to the user. Then, enter the message in the Run-time Message field. You can also apply a message severity type to change the message's appearance and convey the level of urgency to the user.

The informational message type has a gray banner. An informational message doesn't require the user to take any action.
The warning type has a yellow banner. A warning message allows the user to continue working on the current task, but blocks them from taking the next step on the configuration page until they take action to address the issue described in the message.
The error type has a red banner. An error message blocks the user from continuing with the current task on the configuration page until they fix the error described in the message.
NOTE An error message doesn't block a user working in the Transaction Line Editor (Transaction Line Table, or TLT). In that component, the user can still make changes and save the quote, even when the quote contains conditions that trigger an error message.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_configurator_visual_builder_dynamic_message_rule.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
