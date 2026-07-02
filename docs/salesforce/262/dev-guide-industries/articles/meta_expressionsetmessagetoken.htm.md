---
page_id: meta_expressionsetmessagetoken.htm
title: ExpressionSetMessageToken
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_expressionsetmessagetoken.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# ExpressionSetMessageToken

Represents an interface to retrieve, deploy,
create, update, or delete information on Expression Set Message Token.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on
customer implementations.

## Parent Type

This type extends the Metadata metadata type and inherits its
fullName field.

## File Suffix and Directory Location

ExpressionSetMessageToken components have the suffix
expressionSetMessageToken and are stored in the
ExpressionSetMessageToken folder.

## Version

ExpressionSetMessageToken components are available in API version 59.0 and later.

## Special Access Rules

InteractionCalculation.orgHasBREandDESAccess Org permission set license is required
for users to access this metadata type.

## Fields

| Field Name | Description |
| --- | --- |
| description | Field Type  string  Description  Required. Description of the expression set message token. |
| developerName | Field Type  string  Description  Required. Developer name of the expression set message token. |
| masterLabel | Field Type  string  Description  Required. A user-friendly name for ExpressionSetMessageToken, which is defined when the ExpressionSetMessageToken is created. |

## Declarative Metadata Sample Definition

The following is an example of an ExpressionSetMessageToken component.

```
<?xml version="1.0" encoding="UTF-8"?>
<ExpressionSetMessageToken xmlns="http://soap.sforce.com/2006/04/metadata">
    <developerName>token</developerName>
    <description>Description</description>
    <masterLabel>token</masterLabel>
</ExpressionSetMessageToken>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>ExpressionSetMessageToken</name>
    </types>
    <version>59.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see [Deploying and Retrieving
Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
