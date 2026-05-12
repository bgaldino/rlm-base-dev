---
article_id: ind.rm_prereqs_to_build_rating_procedures.htm
title: Prerequisites for Building Rating Procedures
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_prereqs_to_build_rating_procedures.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Prerequisites for Building Rating Procedures

Before you create rating procedures and add elements to them, complete these prerequisites.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

Users must have the Rate Management Design Time user permission to:

Create context definitions.
Create, edit, and activate a decision table in Rate Management.
Create, update, and delete rating procedures.
NOTE Rate Management doesn't support CSV based decision tables and decision matrices.

Create custom lookup tables or use the predefined tables in the Rate Management solution. See Lookup Tables. By default, Salesforce provides these lookup tables.

To create, update, and delete rating procedures when rates are non negotiable, use these lookup tables:

Rate Card Entries 2
Rate Adjustment by Volume Entries 2
Rate Adjustment by Tier Entries 2
Rate Adjustment by Attribute Entries 2

To create, update, and delete rating procedures when rates are negotiable, use these lookup tables:

Rate Card Entries 2
Rate Adjustment by Volume Entries 2
Rate Adjustment by Tier Entries 2
Asset Rate Card Entry 2
Asset Rate 2
Asset Volume-based Rate Adjustment 2
Asset Tier-based Rate Adjustment 2
Tier-based Rate Adjustment by Rate Card Entry ID
Volume-based Rate Adjustment by Rate Card Entry ID
Binding Object Rate Card Entry 2
Binding Object Rate 2
Binding Object Volume-based Rate Adjustment 2
Binding Object Tier-based Rate Adjustment 2
Commitment-based Rate Adjustment
IMPORTANT Enable Transaction Management to view and invoke the asset-based lookup tables involved in the negotiable rating procedure. Alternatively, create your own lookup tables.
Enable the use of context definitions. The Rate Management solution includes its own predefined context definition called RateManagementContext for mapping the Usage Ratable Summary object. To customize parts of this context definition for reuse, extend or clone it, and make modifications. See Create Context Definitions.
To map the variables that don’t have context tags, create a constant resource. Constants are resource types that act as placeholders for fixed values in rating procedures for inputs, outputs, and other values passed from a rating element. SeeCreate a Constant Resource.
SEE ALSO
Enabling Revenue Settings
