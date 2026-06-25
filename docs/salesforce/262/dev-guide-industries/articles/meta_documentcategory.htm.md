---
page_id: meta_documentcategory.htm
title: DocumentCategory
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_documentcategory.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# DocumentCategory

Represents a document category.

## Parent Type

This type extends the Metadata metadata type and inherits its fullName field.

## File Suffix and Directory Location

DocumentCategory components have the suffix .documentCategory and are stored in the documentCategory folder.

## Version

DocumentCategory components are available in API version 59.0 and later.

## Special Access Rules

## Fields

| Field Name | Description |
| --- | --- |
| description | Field Type  string  Description  A description of the DocumentCategory. |
| isProtected | Field Type  boolean  Description  An auto-generated value that doesn’t impact the behavior of the metadata type. The default value is `false`. |
| masterLabel | Field Type  string  Description  Required.  The master label of the DocumentCategory. This internal label doesn’t get translated. |

## Declarative Metadata Sample Definition

The following is an example of a DocumentCategory component.

```
<?xml version="1.0" encoding="UTF-8"?>
<DocumentCategory xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>Address_Proof</masterLabel>
</DocumentCategory>
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
    <version>59.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see Deploying and Retrieving Metadata with the Zip File.
