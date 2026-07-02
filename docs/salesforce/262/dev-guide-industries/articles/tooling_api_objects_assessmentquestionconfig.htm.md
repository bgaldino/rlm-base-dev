---
page_id: tooling_api_objects_assessmentquestionconfig.htm
title: AssessmentQuestionConfig
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_assessmentquestionconfig.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_tooling_api_objects.htm
fetched_at: 2026-06-25
---

# AssessmentQuestionConfig

Represents the assessment question record metadata
configuration. This object is available in API version 56.0 and later.

## Supported SOAP API Calls

`describeSObjects()`, `query()`, `retrieve()`

## Supported REST API Methods

`GET, HEAD, Query`

## Special Access Rules

To use this tooling API object, you must enable
the Discovery Framework feature in your Salesforce org.

## Fields

| Field | Details |
| --- | --- |
| DeveloperName | Type  string  Properties  Filter, Group, Sort  Description  The unique name of the object in the API. This name can contain only underscores and alphanumeric characters, and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. In managed packages, this field prevents naming conflicts on package installations. With this field, a developer can change the object’s name in a managed package and the changes are reflected in a subscriber’s organization. Note Note When creating large sets of data, always specify a unique DeveloperName for each record. If no DeveloperName is specified, performance slows down while Salesforce generates one for each record. |
| Language | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Language of the assessment question. |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package.  Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| MasterLabel | Type  string  Properties  Filter, Group, Sort  Description  Label of the assessment question. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Namespace prefix associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. |
