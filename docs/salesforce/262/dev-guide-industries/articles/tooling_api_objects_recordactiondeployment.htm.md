---
page_id: tooling_api_objects_recordactiondeployment.htm
title: RecordActionDeployment
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_recordactiondeployment.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Action Launcher
parent_page: action_launcher_tooling_apis_parent.htm
fetched_at: 2026-06-25
---

# RecordActionDeployment

Represents configuration settings for the Actions &
Recommendations, Action Launcher, and Bulk Action Panel components. RecordActionDeployment
is available in API version 45.0 and later.

## Supported SOAP Calls

`create()`, `delete()`, `describeLayout()`,
`describeSObject()`, `query()`, `retrieve()`, `update()``upsert()`

## Supported REST HTTP Methods

`GET, HEAD, PATCH, POST, DELETE`

## Fields

| Field | Details |
| --- | --- |
| ChannelConfigurations | Type  mns:[RecordActionDeploymentChannel](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_recordactiondeployment.htm#recordactiondeployment/recordActionDeploymentChannel "HTML (New Window)")  Properties  Not applicable.  Description  Channel default settings for the deployment. This field is visible only in the metadata for a record. |
| ComponentName | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies the name of the component used in the deployment.  Possible values are:  - `ActionsAndRecommendations`—0 - `ActionLauncher`—1 - `BulkActionPanel`—2. This value is   available in API version 60.0 and later.  For example, a value of 1 indicates that 1 is stored in the database if Action Launcher is used to create a deployment. Available in API version 56.0 and later. Available in API version 56.0 and later. |
| DeploymentContexts | Type  mns:[RecordActionDeploymentContext](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_recordactiondeployment.htm#recordactiondeployment/recordActionDeploymentContext "HTML (New Window)")  Properties  Not applicable.  Description  Object context for the deployment. This field is visible only in the metadata for a record. Available in API version 46.0 and later. |
| DeveloperName | Type  string  Properties  Filter, Group, Sort  Description  A unique name for this record action deployment. This name can contain only underscores and alphanumeric characters, and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Provides a globally unique identifier for the record action deployment, which prevents conflicts with other record action deployments that have the same MasterLabel. Note Note Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field. |
| FullName | Type  string  Properties  Filter, Group, Sort  Description  The unique name used as the record action deployment identifier for API access. The fullName can contain only underscores and alphanumeric characters. It must be unique, begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores.  Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance. |
| HasGuidedActions | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  If `true`, indicates that the component shows standard actions; for example, flows and quick actions. Available in API version 46.0 and later. |
| HasComponents | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the record actions deployment includes components (`true`) or not (`false`). |
| HasOmniscripts | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the record actions deployment includes OmniScripts (`true`) or not (`false`). Available in API version 56.0 and later.  The default value is `false`. |
| HasRecommendations | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  If `true`, indicates that the component shows recommendations from a Next Best Action strategy. Available in API version 46.0 and later. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The language of the record action deployment. The following values are supported:  - Chinese (Simplified): `zh_CN` - Chinese (Traditional): `zh_TW` - Danish: `da` - Dutch: `nl_NL` - English: `en_US` - Finnish: `fi` - French: `fr` - German: `de` - Italian: `it` - Japanese: `ja` - Korean: `ko` - Norwegian: `no` - Portuguese (Brazil): `pt_BR` - Russian: `ru` - Spanish: `es` - Spanish (Mexico): `es_MX` Spanish (Mexico) defaults to   Spanish for customer-defined translations. - Swedish: `sv` - Thai: `th`   The Salesforce user interface is fully translated   to Thai, but Help is in English. |
| ManageableState | Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| MasterLabel | Type  string  Properties  Filter, Group, Sort  Description  The name of the deployment. |
| Metadata | Type  mns:[RecordActionDeployment](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_recordactiondeployment.htm "HTML (New Window)")  Properties  Create, Nillable, Update  Description  Metadata that defines record action deployments.  Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with the record action deployment, which is assigned to the AppExchange package. This name can contain only underscores and alphanumeric characters, and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. The namespace helps differentiate custom objects and fields from those in use by other record action deployments. |
| Recommendation | Type  mns:[RecordActionRecommendation](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_recordactiondeployment.htm#recordactiondeployment/recordActionRecommendation "HTML (New Window)")  Properties  Not applicable.  Description  Settings for how Next Best Action recommendations appear. This field is visible only in the metadata for a record. Available in API version 46.0 and later. |
| SelectableItems | Type  mns:[RecordActionSelectableItem](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_recordactiondeployment.htm#recordactiondeployment/recordActionDeploymentSelectableItemsID "HTML (New Window)")  Properties  Not applicable.  Description  A subset of actions that users can launch at runtime. This field is visible only in the metadata for a record. |
