---
article_id: ind.collections_configure_max_ptp.htm
title: Configure Maximum Promise to Pay Count
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_configure_max_ptp.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections_setup_ptp.htm
fetched_at: 2026-11-23
---

# Configure Maximum Promise to Pay Count

Set a limit on the number of promises to pay for a collection plan.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To set a limit on the number of promises to pay:	

Collections and Recovery Admin permission set

In Setup, find and select Collections and Recovery Settings.
Click Maximum Promise to Pay Count.
Enter a value, and save the changes.

The MaximumPromisetoPayCount field on the Collection Plan object is updated with the value you enter. This value applies to the collection plan records created after the update but it doesn't apply to existing records. If a borrower requests a promise-to-pay agreement after the limit is set, the Create Promise to Pay action checks if the borrower has reached the limit. If the limit was reached, the flow doesn’t create a promise-to-pay agreement.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_configure_max_ptp.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
