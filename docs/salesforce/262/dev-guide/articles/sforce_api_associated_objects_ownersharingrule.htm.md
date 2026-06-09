---
page_id: sforce_api_associated_objects_ownersharingrule.htm
title: StandardObjectNameOwnerSharingRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_associated_objects_ownersharingrule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Associated Objects
parent_page: sforce_api_associated_objects_list.htm
fetched_at: 2026-06-09
---

# StandardObjectNameOwnerSharingRule

StandardObjectNameOwnerSharingRule is the model
for all owner sharing rule objects associated with standard objects. These objects
represent a rule for sharing a standard object with users other than the
owner.

The object name is variable and uses StandardObjectNameOwnerSharingRule syntax. For example, ChannelProgramOwnerSharingRule is a rule for sharing a channel program
with users other than the channel program owner. The available associated owner sharing rule objects are listed at the end of this topic. For specific version information, see the
standard object documentation.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

To enable access to this object, contact Salesforce customer support. But we recommend that you use Metadata API to programmatically update owner sharing rules instead because it
triggers automatic sharing rule recalculation. The [SharingRules](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_sharingrules.htm) Metadata API type is enabled for all orgs.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

For specific special access rules, if any, see the documentation for the standard object. For example, for ChannelProgramOwnerSharingRule, see the
special access rules for ChannelProgram.

## Fields

| Field Name | Details |
| --- | --- |
| AccessLevel | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Determines the level of access users have to records. Values are:  - `Read` (read only) - `Edit` (read/write) |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  Description of the sharing rule. Maximum length is 1,000 characters. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The unique name of the object in the API. This name can contain only underscores and alphanumeric characters and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. In managed packages, this field prevents naming conflicts on package installations. With this field, a developer can change the object’s name in a managed package, and the changes are reflected in a subscriber’s organization. When creating large sets of data, always specify a unique DeveloperName for each record. If no DeveloperName is specified, performance can slow while Salesforce generates one for each record. |
| GroupId | Type  reference  Properties  Create, Filter, Group, Sort  Description  ID of the source group. Records that are owned by users in the source group trigger the rule to give access. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Label of the sharing rule as it appears in the UI. Maximum length is 80 characters. |
| UserOrGroupId | Type  reference  Properties  Create, Filter, Group, Sort  Description  ID of the user or group that you're granting access to. |
