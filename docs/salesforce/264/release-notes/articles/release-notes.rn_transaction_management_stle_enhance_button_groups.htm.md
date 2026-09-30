---
article_id: release-notes.rn_transaction_management_stle_enhance_button_groups.htm
title: Organize Sales Transaction Line Editor Actions into Button Groups for Efficient Editing
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_transaction_management_stle_enhance_button_groups.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_transaction_management.htm
fetched_at: 2026-09-30
---

# Organize Sales Transaction Line Editor Actions into Button Groups for Efficient Editing

Configure Sales Transaction Line Editor (STLE) header actions with a new, visual admin UI instead of a text box. Organize actions into button groups, set how many actions show in each group, and add as many groups as your business needs. Ten action groups are visible, with the remaining groups placed in an overflow menu. Existing text box configurations carry over automatically, keeping your sales reps' experience the same until you're ready to reorganize.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

Why: The previous text box experience to configure action buttons offered no visual layout and required entering API names for each action. Now, your admin can design the STLE header visually and organize actions around how your sales teams work on quotes and orders. Sales reps also get a more responsive STLE header. The STLE header’s size changes based on the actions that fit in the header, and automatically collapses the other actions into an overflow menu.

If a configured action isn't available to a sales rep because of their access level or the state of the quote or order, the STLE header automatically adjusts to show available actions. The next action in that group becomes available, so sales reps get a full set of usable actions to keep moving quotes and orders forward.

How: From Setup, select Object Manager. Search for and select the quote or order object. Click Lightning Record Pages, then the quote or order record page. Click Edit to open Lightning App Builder. Select the STLE component to update the action button groups section.

SEE ALSO
Configure Action Buttons in Transaction Line Editor
