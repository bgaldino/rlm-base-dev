---
article_id: ind.sf_contracts_datatrueup_enable.htm
title: Enable Data True-Up
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_datatrueup_enable.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_datatrueup_overview.htm
fetched_at: 2026-10-13
---

# Enable Data True-Up

Turn on the Data True-Up feature in Setup to allow document and record sync, and provide Field-Level Security (FLS) access to specific fields.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To enable Data True-Up setting:	CLM Admin
IMPORTANT Users in your org must have FLS access to specific fields in the ContentLink and ContentSource objects. Without this access, the Data True-up feature won’t work and check-in process will fail.
From Setup, in the Quick Find box, enter Document Generation, and then select General Settings.
Turn on Data True-up.
Add FLS access as Visible and Read-only to these fields in the ContentLink and ContentSource objects.
Update these ContentLink fields: UpdatedContent, LastCntntUpdateDateTime, and Status.
Update these ContentSource fields: RelatedObjectApiName, RelatedFieldApiName, ExtractDataMapperName, TransformDataMapperName, ExtractDataMapperInput, and RelatedRecordIdentifier.
Assign standard object permissions for ContentLink and ContentSource objects at the profile level.
SEE ALSO
Set Field-Level Security for a Field on All Profiles
Edit Object Permissions in Profiles
