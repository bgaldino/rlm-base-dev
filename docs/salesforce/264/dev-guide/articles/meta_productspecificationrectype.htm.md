---
page_id: meta_productspecificationrectype.htm
title: ProductSpecificationRecType
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_productspecificationrectype.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_metadata_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ProductSpecificationRecType

Represents the association of a product
			specification type with record types defined on the Product object. The product
			specification record type also determines if the product specification is sold
			commercially or not.

	
			

#### Important

 Where possible, we changed noninclusive terms to align with our
				company value of Equality. We maintained certain terms to avoid any effect on
				customer implementations. 

		

	

## Parent Type

			 This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/metadata.htm) metadata type
			and inherits its fullName field. 

	

## File Suffix and Directory Location

		
		

ProductSpecificationRecType components have the suffix .productSpecificationRecType and are stored in the productSpecificationRecTypes folder.

	

	

## Version

		
		

ProductSpecificationRecType components are available in API version 60.0 and later.

	

	

## Special Access Rules

Ensure Product Catalog Management is enabled to
				access this metadata type.

	

## Fields

		

		

			
			
			
				
					

					

				

			

			

				
					

				

: 

: 

				

				
					

				

: 

: 

				

				
					

				

: 

: 

				

				
					

				

: 

: 

				

				

			
| Field Name | Description |
| --- | --- |
| isCommercial | **Field Type** boolean **Description** Required. Indicates whether the product is sold commercially (`true`) or not (`false`). The default value is `true`. |
| masterLabel | **Field Type** string **Description** Required. A user-friendly name for the product specification record type, which is defined when the metadata component is created. |
| productSpecificationType | **Field Type** string **Description** Required. Product specification type that's associated with the record type. This field is unique within your organization. |
| recordType | **Field Type** string **Description** Required. Custom record type of Product2 object. |

	

		

## Declarative Metadata Sample Definition

		
			

The following is an example of a ProductSpecificationRecType component.

			

```

<ProductSpecificationRecType xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>sample</masterLabel>
   <recordType>Product2.Offer</recordType>
   <productSpecificationType>Placeholder</productSpecificationType>
   <isCommercial>true</isCommercial>
</ProductSpecificationRecType>
```

			

The following is an example `package.xml` that
			references the previous definition.

			

```

<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>ProductSpecificationRecType</name>
    </types>
    <types>
        <members>*</members>
        <name>ProductSpecificationType</name>
    </types>
    <types>
        <members>Product2.Offer</members>
        <name>RecordType</name>
    </types>
    <version>68.0</version>
</Package>
```

		

		

## Wildcard Support in the Manifest File

			
			

This metadata type supports the wildcard character `*`
				(asterisk) in the package.xml manifest file. For information
				about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/file_based_zip_file.htm).
