---
page_id: meta-businessprocesstypedefinition
title: BusinessProcessTypeDefinition
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta-businessprocesstypedefinition.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Decision Explainer
parent_page: decision-explainer-metadata-api-parent
legacy_page_id: meta_businessprocesstypedefinition.htm
fetched_at: 2026-11-25
---

# BusinessProcessTypeDefinition

Represents the definition of the business process type within an application domain.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

## File Suffix and Directory Location

BusinessProcessTypeDefinition components have the suffix `.businessProcessTypeDefinition` and are stored in the `businessProcessTypeDefinition` folder.

## Version

BusinessProcessTypeDefinition components are available in API version 57.0 and later.

## Fields

### applicationUsageType

- 

**Field Type**: AppDomainUsageType (enumeration of type string)

- 

**Description**: Required. The application’s domain that defines the business process type definition.

Possible value:

  - `ExplainabilityService`

### description

- **Field Type**: string

- **Description**: The description of the business process type definition.

### masterLabel

- **Field Type**: string

- **Description**: Required. A user-friendly name for BusinessProcessTypeDefinition, which is defined when the BusinessProcessTypeDefinition is created.

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

The following is an example `package.xml` that references the previous definition.

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

### Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the `package.xml` manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta-businessprocesstypedefinition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
