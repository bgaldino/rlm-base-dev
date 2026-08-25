---
page_id: sforce_api_associated_objects_share.htm
title: StandardObjectNameShare
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_associated_objects_share.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Associated Objects
parent_page: sforce_api_associated_objects_list.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# 
StandardObjectNameShare

StandardObjectNameShare is the model for all
			share objects associated with standard objects. These objects represent a sharing entry
			on the standard object.

		

The object name is variable and uses StandardObjectNameShare
				syntax. For example, AccountBrandShare is a sharing entry on an account brand. For
				specific version information, see the standard object documentation.

You can only create, edit, and delete sharing entries for
            standard objects whose RowCause field is set to `Manual`. Sharing entries for standard objects with
            different RowCause values are created as a result of your
            Salesforce org’s sharing configuration and are read-only. For some sharing mechanisms,
            such as sharing sets, sharing entries aren’t stored at all.

#### Note

While Salesforce currently maintains read-only sharing
            entries for multiple sharing mechanisms, it’s possible that we’ll stop storing certain
            share records to improve performance. As a best practice, don’t create customizations
            that rely on the availability of these sharing entries. Any changes to sharing behavior
            will be communicated before they occur.

		

## Supported Calls

			
			

`create()`, `delete()`, `describeSObjects()`,
					`query()`, `retrieve()`, `update()`, `upsert()`

		

		

## Special Access Rules

For specific special access rules, if any, see
			the documentation for the standard object. For example, for AccountBrandShare, see the
			special access rules for AccountBrand.

		

## Fields

			
			

					
					
					
						
							

							

						

					

					
						
							

							

: 

: 

: 
- 
- 
- 

						

						
							

							

: 

: 

: 

						

						
							

							

: 

: 

: 

						

						
							

							

: 

: 

: 

						

					

				
| Field Name | Details |
| --- | --- |
| AccessLevel | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** The level of access allowed. Values are: `All` (owner) `Edit` (read/write) `Read` (read only) |
| ParentId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** ID of the parent record. |
| RowCause | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort **Description** Reason that the sharing entry exists. |
| UserOrGroupId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** ID of the user or group that has been given access to the object. |
