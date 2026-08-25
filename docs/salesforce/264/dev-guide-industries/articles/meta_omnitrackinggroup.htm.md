---
page_id: meta_omnitrackinggroup.htm
title: OmniTrackingGroup
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_omnitrackinggroup.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_metadata_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# OmniTrackingGroup

Represents a group of FlexCard and OmniScript components that have
			their user interactions tracked together in OmniAnalytics.

		
			

#### Note

This metadata type is part of Omnistudio Standard, not Omnistudio for Vlocity.

			

#### Important

 Where possible, we changed noninclusive terms to align with our
				company value of Equality. We maintained certain terms to avoid any effect on
				customer implementations. 

		

		

## Parent Type

			 This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its fullName field. 

	

## File Suffix and Directory Location

		
		

OmniTrackingGroup components have the suffix .OmniTrackingGroup and are stored in the OmniTrackingGroups folder.

	

	

## Version

		
		

OmniTrackingGroup components are available in API version 60.0 and later.

	

	

## Special Access Rules

		
			

Using OmniAnalytics requires having an Omnistudio license and enabling OmniAnalytics in
				Setup.

	

	

## Fields

		

		

			
			
			
				
					

					

				

			

			

				
					

				

: 

: 

				

				
					

				

: 

: 

#### 

#### 

				

				
					

				

: 

: 

				

				
					

				

: 

: 

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

: 

				

				
					

				

: 

: 

				

				
					

				

: 

: 

				

				

			
| Field Name | Description |
| --- | --- |
| description | **Field Type** string **Description** A description of the OmniTrackingGroup. |
| developerName | **Field Type** string **Description** Required. The unique name of the OmniTrackingGroup in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters. Note When creating large sets of data, always specify a unique DeveloperName for each record. If no DeveloperName is specified, performance may slow while Salesforce generates one for each record. Note Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field. |
| endDate | **Field Type** date **Description** The date when the OmniTrackingGroup became inactive. |
| groupType | **Field Type** OmniTrackingGroupType (enumeration of type string) **Description** Required. Specifies whether this OmniTrackingGroup sends tracking data to a third-party Analytics system such as Google Analytics. Values are: `External`—A third-party Analytics system is used. `Internal`—No third-party Analytics system is used. |
| isActive | **Field Type** boolean **Description** Required. Specifies whether the OmniTrackingGroup is active. |
| masterLabel | **Field Type** string **Description** Required. The unique master label of the OmniTrackingGroup. This internal label doesn’t get translated. |
| maxAgeInDays | **Field Type** int **Description** The maximum number of days the group and its analytics data is active beyond which the data is deleted. |
| omniExtTrackingDef | **Field Type** string **Description** The ID of the related OmniExtTrackingDef object. Required if GroupType is set to `External`. |
| omniTrackingComponentDefs | **Field Type** [OmniTrackingComponentDef[]](#OmniTrackingComponentDef) **Description** The OmniTrackingComponentDef objects related to this OmniTrackingGroup. |
| omniTrackingGroupKey | **Field Type** string **Description** A UUID generated internally by Salesforce to uniquely identify an OmniTrackingGroup record across all orgs. |
| startDate | **Field Type** date **Description** The date when the OmniTrackingGroup became active. |

	

		

## OmniTrackingComponentDef

		
		

Represents a FlexCard or OmniScript that is a member of an OmniTrackingGroup, which tracks user
				interactions in OmniAnalytics.

		

			
			
			
				
					

					

				

			

			

				
					

				

: 

: 

- 
- 

				

				
					

				

: 

: 

				

				
					

				

: 

: 

#### 

#### 

				

				
					

				

: 

: 

				

				
					

				

: 

: 

				

				
					

				

: 

: 

				

				

			
| Field Name | Description |
| --- | --- |
| componentType | **Field Type** OmniAnalyticsComponentType (enumeration of type string) **Description** Required. The type of component for which user interactions are tracked. Values are: `Flexcard` `Omniscript` |
| componentVersion | **Field Type** double **Description** Required. The version of the FlexCard or OmniScript. |
| developerName | **Field Type** string **Description** Required. The unique name of the OmniTrackingComponentDef in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters. Note When creating large sets of data, always specify a unique DeveloperName for each record. If no DeveloperName is specified, performance may slow while Salesforce generates one for each record. Note Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field. |
| masterLabel | **Field Type** string **Description** Required. The unique master label of the OmniTrackingComponentDef. This internal label doesn’t get translated. |
| omniTrackingComponentDefKey | **Field Type** string **Description** A UUID generated internally by Salesforce to uniquely identify an OmniTrackingComponentDef record across all orgs. |
| omniTrackingGroup | **Field Type** string **Description** The ID of the related OmniTrackingGroup object. |

	

		

## Declarative Metadata Sample Definition

		
			

The following is an example of an OmniTrackingGroup component.

			

```
<?xml version="1.0" encoding="UTF-8"?>
<OmniTrackingGroup xmlns="http://soap.sforce.com/2006/04/metadata">
    <developerName>Purchase_Tracking</developerName>
    <groupType>Internal</groupType>
    <isActive>true</isActive>
    <masterLabel>Purchase_Tracking</masterLabel>
    <omniTrackingComponentDefs>
        <componentType>Omniscript</componentType>
        <componentVersion>2</componentVersion>
        <developerName>Purchase_Funnel</developerName>
        <masterLabel>Purchase_Funnel</masterLabel>
    </omniTrackingComponentDefs>
</OmniTrackingGroup>
```

			

The following is an example `package.xml` that
			references the previous definition.

			

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>OmniTrackingGroup</name>
    </types>
    <version>60.0</version>
</Package>
```

		

		
		

## Wildcard Support in the Manifest File

			
			
			

This metadata type supports the wildcard character `*`
				(asterisk) in the package.xml manifest file. For information
				about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/file_based_zip_file.htm).
