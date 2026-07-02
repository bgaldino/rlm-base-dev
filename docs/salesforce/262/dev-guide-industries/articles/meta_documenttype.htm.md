---
page_id: meta_documenttype.htm
title: DocumentType
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_documenttype.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# DocumentType

Represents a document type.

## Parent Type

This type extends the Metadata metadata type and inherits its fullName field.

## File Suffix and Directory Location

DocumentType components have the suffix .documentType and are stored in the documentTypes folder.

## Version

DocumentType components are available in API version 59.0 and later.

## Special Access Rules

## Fields

| Field Name | Description |
| --- | --- |
| description | Field Type  string  Description  A description of the DocumentType. |
| isActive | Field Type  boolean  Description  Required. Specifies whether the DocumentType is active. |
| masterLabel | Field Type  string  Description  Required.  The master label of the DocumentType. This internal label doesn’t get translated. |

## Declarative Metadata Sample Definition

The following is an example of a DocumentType component.

```
<?xml version="1.0" encoding="UTF-8"?>
<DocumentType xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Utility_Bill</description>
    <isActive>true</isActive>
    <masterLabel>Utility_Bill</masterLabel>
</DocumentType>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>DocumentType</name>
    </types>
    <version>59.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see Deploying and Retrieving Metadata with the Zip File.
