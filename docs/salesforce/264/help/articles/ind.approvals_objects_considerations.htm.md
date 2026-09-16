---
article_id: ind.approvals_objects_considerations.htm
title: Considerations for Approval Objects
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_objects_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_advanced_approvals_considerations.htm
fetched_at: 2026-09-07
---

# Considerations for Approval Objects

This section covers considerations and limitations for approval objects and related records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
An approval request can be triggered only from supported objects. To check or request support for your object, contact your Salesforce admin.
If a related record’s access is set to Public Read Only, all users automatically get access to its approval submissions. However, if it's set to Private, you can share temporary access to the related record using Apex triggers. See Share Temporary Access to Records in Advanced Approvals.
