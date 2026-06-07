---
article_id: ind.approvals_objects_considerations.htm
title: Considerations for Approval Objects
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_objects_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Considerations for Approval Objects

This section covers considerations and limitations for approval objects and related records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions where Advanced Approvals is enabled
An approval request can be triggered only from supported objects. To check or request support for your object, contact your Salesforce admin.
The Approval Submission object controls the access to other approval objects. For example, if a user is given access to the Approval Submission object, they get access to a submission’s child records, such as submission details and work items.
By default, all approval records are set to Private to restrict their visibility to relevant users.
If a related record’s access is set to Public Read Only, all users automatically get access to its approval submissions and work items. However, if it's set to Private, you can share temporary access to the related record using Apex triggers. See Share Temporary Access to Records in Advanced Approvals.
You can't manually share access to approval submission records.
