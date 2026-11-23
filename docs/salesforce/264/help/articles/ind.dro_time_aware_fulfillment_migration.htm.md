---
article_id: ind.dro_time_aware_fulfillment_migration.htm
title: Migrate Fulfillment Assets from Time-Agnostic to Time-Aware
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_time_aware_fulfillment_migration.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_time_aware_fulfillment.htm
fetched_at: 2026-11-23
---

# Migrate Fulfillment Assets from Time-Agnostic to Time-Aware

Attribute values of Fulfillment Asset (FA) records created before time-awareness reflect only the most recent assetization state and not the values that were in effect during each asset state period in the past. When you submit an Amend, Renew, or Cancel order on these assets, decomposition can derive the wrong fulfillment order line item action for the affected period. Also, the resulting fulfillment asset state period (FASP) values can be incorrect.

To fix this issue, manually create the missing state period data for each affected fulfillment asset before turning on time-awareness:

Identify the FA records created before time-awareness was enabled. Look for records whose quantity or attribute values change over time.
For each FA record, create an FASP record with the configuration for every state change, with the correct start date, end date, and quantity for that period.
For each FASP record, create the corresponding FASP attribute records that capture the attribute key-value pairs in effect during that period.
SEE ALSO
Turn On Time-Awareness

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_time_aware_fulfillment_migration.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
