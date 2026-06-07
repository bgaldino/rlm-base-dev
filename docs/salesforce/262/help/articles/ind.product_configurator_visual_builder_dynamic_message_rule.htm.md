---
article_id: ind.product_configurator_visual_builder_dynamic_message_rule.htm
title: Dynamic Message Rule in the Visual Builder
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_visual_builder_dynamic_message_rule.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Dynamic Message Rule in the Visual Builder

The dynamic message rule shows a message to users if the specified condition is true. Include a message to provide the user with information about an item, such as a promotional offer on a selected product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

In the dynamic message rule window, add one or more expressions to define a condition or conditions that, if true, show a message to the user. Then, enter the message in the Run-time Message field. You can also apply a message severity type to change the message's appearance and convey the level of urgency to the user.

The informational message type has a gray banner. An informational message doesn't require the user to take any action.
The warning type has a yellow banner. A warning message allows the user to continue working on the current task, but blocks them from taking the next step on the configuration page until they take action to address the issue described in the message.
The error type has a red banner. An error message blocks the user from continuing with the current task on the configuration page until they fix the error described in the message.
NOTE An error message doesn't block a user working in the Transaction Line Editor (Transaction Line Table, or TLT). In that component, the user can still make changes and save the quote, even when the quote contains conditions that trigger an error message.
