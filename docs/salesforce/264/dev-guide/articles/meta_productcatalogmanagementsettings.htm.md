---
page_id: meta_productcatalogmanagementsettings.htm
title: ProductCatalogManagementSettings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_productcatalogmanagementsettings.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_metadata_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ProductCatalogManagementSettings

Represents the settings for Product Catalog
			Management.

	
		

## Parent Type and Manifest Access

			
			

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its fullName
				field.

			

In the package manifest, all the settings metadata types for the org are accessed
				using the “Settings” name. See [Settings](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_settings.htm) for more details.

		

		

## File Suffix and Directory Location

			
			

ProductCatalogManagementSettings values are stored in the
					ProductCatalogManagementSettings.settings file in the
					settings folder. The .settings files
				are different from other named components, because there is only one settings file
				for each settings component.

		

	

## Version

		
		

ProductCatalogManagementSettings components are available in API version 64.0 and later.

	

	

## Special Access Rules

		
			

These settings are available when Product Catalog Management is enabled.

	

	

## Fields

		

		

			
			
			
				
					

					

				

			

			

				
					

				

: 

: 

				

				
					

				

: 

: 

				

				

			
| Field Name | Description |
| --- | --- |
| productDeepCloneContextDefOrgValue | **Field Type** string **Description** Name of the context definition that you want to use to deep clone the product. |
| productDeepCloneExpressionSetOrgValue | **Field Type** string **Description** Expression set that contains the rules that you want to apply to deep clone the product. |

	

		

## Declarative Metadata Sample Definition

		
			

The following is an example of a ProductCatalogManagementSettings component.

			

```
<ProductCatalogManagementSettings xmlns="http://soap.sforce.com/2006/04/metadata">
<productDeepCloneContextDefOrgValue>ProductDeepCloneContextDefinition</productDeepCloneContextDefOrgValue>
<productDeepCloneExpressionSetOrgValue>ProductDeepCloneExpressionSet</productDeepCloneExpressionSetOrgValue>
</ProductCatalogManagementSettings>
```

			

The following is an example `package.xml` that
			references the previous definition.

			

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>ProductCatalogManagement</members>
        <name>Settings</name>
    </types>
    <version>68.0</version>
</Package>
```

		

		

## Wildcard Support in the Manifest File

			
			

The wildcard character `*` (asterisk) in the
					package.xml manifest file doesn’t apply to metadata types
				for feature settings. The wildcard applies only when retrieving all settings, not
				for an individual setting. For details, see [Settings](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_settings.htm). For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/file_based_zip_file.htm).
