---
page_id: meta_applicationsubtypedefinition.htm
title: ApplicationSubtypeDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_applicationsubtypedefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Decision Explainer
parent_page: decision_explainer_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# ApplicationSubtypeDefinition

Represents a subtype of an application. Create
application subtype definitions to define the types of applications used in your
Decision Explainer entities.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on
customer implementations.

## Parent Type

This type extends the Metadata metadata type and inherits its
fullName field.

## File Suffix and Directory Location

ApplicationSubtypeDefinition components have the suffix
.applicationSubtypeDefinition and are stored in the
applicationSubtypeDefinition folder.

## Version

ApplicationSubtypeDefinition components are available in API version 57.0 and
later.

## Fields

| Field Name | Description |
| --- | --- |
| applicationUsageType | Field Type  AppDomainUsageType (enumeration of type string)  Description  Required.  The application's domain that defines the application's subtype.  Possible value:   - `ExplainabilityService` |
| description | Field Type  string  Description  The description of the application subtype definition. |
| masterLabel | Field Type  string  Description  Required. A user-friendly name for ApplicationSubtypeDefinition, which is defined when the ApplicationSubtypeDefinition is created. |

## Declarative Metadata Sample Definition

The following is an example of an ApplicationSubtypeDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>
<ApplicationSubtypeDefinition
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<masterLabel>ApplicationSubtype1</masterLabel>
	<description>Application Subtype 1</description>
	<applicationUsageType>ExplainabilityService</applicationUsageType>
</ApplicationSubtypeDefinition>
```

The following is an example `package.xml` that references
the previous
definition.

```
<?xml version="1.0" encoding="UTF-8"?>

<Package
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<types>
		<members>*</members>
		<name>ApplicationSubtypeDefinition</name>
	</types>
	<version>57.0</version>
</Package>
```
