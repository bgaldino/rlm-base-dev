---
page_id: meta_businessprocesstypedefinition.htm
title: BusinessProcessTypeDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_businessprocesstypedefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Decision Explainer
parent_page: decision_explainer_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# BusinessProcessTypeDefinition

Represents the definition of the business process
type within an application domain.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on
customer implementations.

## Parent Type

This type extends the Metadata metadata type and inherits its
fullName field.

## File Suffix and Directory Location

BusinessProcessTypeDefinition components have the suffix
.businessProcessTypeDefinition and are stored in the
businessProcessTypeDefinition
folder.

## Version

BusinessProcessTypeDefinition components are available in API version 57.0 and
later.

## Fields

| Field Name | Description |
| --- | --- |
| applicationUsageType | Field Type  AppDomainUsageType (enumeration of type string)  Description  Required. The application's domain that defines the business process type definition. Possible value:   - `ExplainabilityService` |
| description | Field Type  string  Description  The description of the business process type definition. |
| masterLabel | Field Type  string  Description  Required. A user-friendly name for BusinessProcessTypeDefinition, which is defined when the BusinessProcessTypeDefinition is created. |

## Declarative Metadata Sample Definition

The following is an example of a BusinessProcessTypeDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>

<BusinessProcessTypeDefinition
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<masterLabel>ProcessType1</masterLabel>
	<description>Process Type 1</description>
	<applicationUsageType>ExplainabilityService</applicationUsageType>
</BusinessProcessTypeDefinition>
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
		<name>BusinessProcessTypeDefinition</name>
	</types>
	<version>57.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest
file. For information about using the manifest file, see Deploying and Retrieving Metadata with the Zip File.
