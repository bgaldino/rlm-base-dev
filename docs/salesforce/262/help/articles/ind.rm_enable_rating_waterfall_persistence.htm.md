---
article_id: ind.rm_enable_rating_waterfall_persistence.htm
title: Enable Rating Waterfall Persistence
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_enable_rating_waterfall_persistence.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Enable Rating Waterfall Persistence

Waterfall persistence stores the rating logs in a structured manner within the Salesforce database. Rating waterfall logs capture the sequence of rating decisions applied during execution for efficient tracking and retrieval of rating information.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
USER PERMISSIONS
NEEDED
To turn on rating waterfall persistence:	Rate Management Admin

If you turn on the rating waterfall without enabling waterfall persistence, keep these things in mind:

The active session or API responses shows the rating logic. However, after the transaction is finalized, the steps behind rating disappear. If your user disputes a charge three months later, you can only see the final price because the step-by-step logs aren’t available.

Rating waterfall persistence stores detailed rating execution logs for every transaction. Over time, this increasing data storage usage can have a minor impact on overall system performance, especially in high-volume environments. If you process numerous transactions and don’t require historical step-level traceability for audits or dispute resolution, keep persistence turned off to avoid unnecessary storage pile up.
From Setup, in the Quick Find box, enter Usage Management, and then select Rate Management Setup.
Turn on Rating Waterfall Persistence.
SEE ALSO
Revenue Cloud Developer Guide: Line Item Waterfall Response
