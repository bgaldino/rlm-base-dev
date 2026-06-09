---
page_id: sforce_api_objects_assetownersharingrule.htm
title: AssetOwnerSharingRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetownersharingrule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# AssetOwnerSharingRule

Represents the rules for sharing an Asset with users other than the
owner. This object is available in API version 33.0 and later.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

To enable access to this object for your org, contact Salesforce customer support.
However, we recommend that you instead use Metadata API to programmatically update owner
sharing rules because it triggers automatic sharing rule recalculation. The [SharingRules](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_sharingrules.htm) Metadata API type is enabled for
all orgs.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

Customer Portal users can’t access this object.

## Fields

| Field | Details |
| --- | --- |
| AssetAccessLevel | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  A value that represents the type of sharing being allowed. The possible values are:  - Read - Edit |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  A description of the sharing rule. Maximum size is 1000 characters. |
| DeveloperName | Type  string  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The unique name of the object in the API. This name can contain only underscores and alphanumeric characters, and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. In managed packages, this field prevents naming conflicts on package installations. With this field, a developer can change the object’s name in a managed package and the changes are reflected in a subscriber’s organization. Corresponds to **Rule Name** in the user interface. Note Note When creating large sets of data, always specify a unique DeveloperName for each record. If no DeveloperName is specified, performance may slow while Salesforce generates one for each record. |
| GroupId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID representing the source group. Cases owned by users in the source group trigger the rule to give access. |
| Name | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Label of the sharing rule as it appears in the user interface. Limited to 80 characters. Corresponds to **Label** on the user interface. |
| UserOrGroupId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID representing the target user or group. Target users or groups are given access. |

## Usage

Use this object to manage the sharing rules for assets. General sharing uses this
object.
