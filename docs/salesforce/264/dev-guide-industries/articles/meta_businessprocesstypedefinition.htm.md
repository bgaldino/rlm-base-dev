---
page_id: meta_businessprocesstypedefinition.htm
title: BusinessProcessTypeDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_businessprocesstypedefinition.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Decision Explainer
parent_page: decision_explainer_metadata_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# BusinessProcessTypeDefinition

Represents the definition of the business process
			type within an application domain.

		
			

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

			
			

					
					
					
						
							

							

						

					

					
						
							

							

: 

: 

- 

						

						
							

							

: 

: 

						

						
							

							

: 

: 

						

					

				
| Field Name | Description |
| --- | --- |
| applicationUsageType | **Field Type** AppDomainUsageType (enumeration of type string) **Description** Required. The application's domain that defines the business process type definition. Possible value: `ExplainabilityService` |
| description | **Field Type** string **Description** The description of the business process type definition. |
| masterLabel | **Field Type** string **Description** Required. A user-friendly name for BusinessProcessTypeDefinition, which is defined when the BusinessProcessTypeDefinition is created. |

		

		

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
        file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip
        File](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/file_based_zip_file.htm).
