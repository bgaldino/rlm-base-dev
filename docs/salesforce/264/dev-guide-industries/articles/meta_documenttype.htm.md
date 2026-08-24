---
page_id: meta_documenttype.htm
title: DocumentType
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_documenttype.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_metadata_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

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

		

		

			
			
			
				
					

					

				

			

			

				
					

				

: 

: 

				

				
					

				

: 

: 

				

				
					

				

: 

: 

				

				

			
| Field Name | Description |
| --- | --- |
| description | **Field Type** string **Description** A description of the DocumentType. |
| isActive | **Field Type** boolean **Description** Required. Specifies whether the DocumentType is active. |
| masterLabel | **Field Type** string **Description** Required. The master label of the DocumentType. This internal label doesn’t get translated. |

	

		

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
