---
page_id: meta_documentcategorydocumenttype.htm
title: DocumentCategoryDocumentType
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_documentcategorydocumenttype.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# DocumentCategoryDocumentType

Represents the junction between a DocumentCategory and a DocumentType. Puts a
DocumentType in a DocumentCategory.

## Parent Type

This type extends the Metadata metadata type and inherits its fullName field.

## File Suffix and Directory Location

DocumentCategoryDocumentType components have the suffix .documentCategoryDocumentType and are stored in the documentCategoryDocumentTypes folder.

## Version

DocumentCategoryDocumentType components are available in API version 59.0 and later.

## Special Access Rules

## Fields

| Field Name | Description |
| --- | --- |
| documentCategory | Field Type  string  Description  Required.  The master label of the related DocumentCategory. |
| documentType | Field Type  string  Description  Required.  The master label of the related DocumentType. |
| isProtected | Field Type  boolean  Description  An auto-generated value that doesn’t impact the behavior of the metadata type. The default value is `false`. |
| masterLabel | Field Type  string  Description  Required.  The master label of the DocumentCategoryDocumentType. This internal label doesn’t get translated. |

## Declarative Metadata Sample Definition

The following is an example of a DocumentCategoryDocumentType component.

```
<?xml version="1.0" encoding="UTF-8"?>
<DocumentCategoryDocumentType xmlns="http://soap.sforce.com/2006/04/metadata">
    <documentCategory>Address_Proof</documentCategory>
    <documentType>Utility_Bill</documentType>
    <masterLabel>junction1</masterLabel>
</DocumentCategoryDocumentType>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>DocumentCategory</name>
    </types>
    <types>
        <members>*</members>
        <name>DocumentCategoryDocumentType</name>
    </types>
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
