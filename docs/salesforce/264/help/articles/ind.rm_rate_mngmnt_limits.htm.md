---
article_id: ind.rm_rate_mngmnt_limits.htm
title: Rate Management Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_rate_mngmnt_limits.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rate_management.htm
fetched_at: 2026-11-23
---

# Rate Management Limits

Review the default limits for Rate Management components and their usage. To modify the set default values, ask your Salesforce admin to raise a support ticket.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
Rating Procedures
VALUE	DEFAULT	MINIMUM	MAXIMUM
The duration that a rating procedure can remain active	10000 milliseconds	1000 milliseconds	60000 milliseconds
The duration that a rating element can remain active	5000 milliseconds	4 milliseconds	10000 milliseconds
The number of rating elements in a rating procedure	70	2	100
The number of active decision tables in an org	50	0	1000
The maximum number of simultaneous lookup inputs allowed per HBPO-based decision table	1000	1	8000
Rating Discovery Procedures
VALUE	DEFAULT	MINIMUM	MAXIMUM
The duration that a rating discovery procedure can remain active	10000 milliseconds	1000 milliseconds	60000 milliseconds
The duration that a rating discovery element can remain active	5000 milliseconds	4 milliseconds	10000 milliseconds
The number of rating discovery elements in a rating discovery procedure	50	1	100
The number of active decision tables in an org	40	0	1000
The maximum number of simultaneous lookup inputs allowed for an org’s HBPO-based decision tables of the usage type Rating Discovery	2000	1	8000
Rate Card Entries
VALUE	LIMIT
The number of rate card entries	1200
The number of adjustment records associated with tier rate card entries	3000
Other Limitations
Rate Management isn’t supported on mobile devices.
Rate Management objects don't support the creation of records in Data Cloud.
Rate Management doesn't support CSV-based decision tables and decision matrices.
Attribute-based rate cards aren't supported in Usage Selling and Consumption Management. Avoid creating attribute-based rate cards or related customizations.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.rm_rate_mngmnt_limits.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
