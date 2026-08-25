---
page_id: meta_decisiontabledatasetlink.htm
title: DecisionTableDatasetLink
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_decisiontabledatasetlink.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_metadata_api.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# DecisionTableDatasetLink

Represents the information about a dataset link
      associated with a decision table. In a dataset link, select an object for whose records, the
      decision table must provide an outcome. This type extends the
      Metadata metadata type and inherits its fullName field.

    
      

#### Note

Dataset links are supported only for Standard decision
        tables.

    

    

## File Suffix and Directory Location

      
      
      

DecisionTableDatasetLink components have the suffix
          .decisionTableDatasetLink and are stored in the
          decisionTableDatasetLinks folder.

    

    

## Version

      
      

DecisionTableDatasetLink components are available in API version 51.0 and later.

    

    

## Special Access Rules

      
      

To use this metadata type, your Salesforce org must have the Loyalty Management or the
        Rebate Management license.

    

    

## Fields

      
      
      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

            

            
              

              

              

            

            
              

              

              

            

            
              

              

              

            

            
              

              

              

            

            
              

              

              

            

          

        
| Field Name | Field Type | Description |
| --- | --- | --- |
| decisionTableName | string | Required. The name of the associated decision table. |
| decisionTblDatasetParameters | [DecisionTblDatasetParameters](#dtparametersID) | Mapping between a decision table parameter and a field of the object selected in the dataset link. |
| description | string | The description of the dataset link. |
| isDefault | boolean | Indicates whether a dataset link is the default dataset link for a decision table. |
| setupName | string | Required. The name of the decision table dataset link, which appears in Setup. |
| sourceObject | string | Required. The name of the object being evaluated. |

    

    

## DecisionTblDatasetParameters

      
    

    
      

Represents the mapping between a decision table parameter and a field of
          the object selected in the dataset link.

      

The mapping allows the decision table to know which object fields must be compared to the
        input-output fields of the decision table.

    

    

## Fields

      
      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

            

            
              

              

              

            

          

        
| Field Name | Field Type | Description |
| --- | --- | --- |
| datasetFieldName | string | Required. Name of the dataset field whose value must be compared against an Input type decision table parameter when providing the outcome. |
| fieldName | string | Required. The API name of the decision table field that is selected as an input or output for the decision table dataset link. |

    

    

## Declarative Metadata Sample Definition

      
      

The following is an example of a DecisionTableDatasetLink component.

      

```

<?xml version="1.0" encoding="UTF-8"?>
<DecisionTableDatasetLink xmlns="http://soap.sforce.com/2006/04/metadata">
   <decisionTableName>Sample_DT</decisionTableName>
   <decisionTblDatasetParameters>
      <fieldName>IsDeleted</fieldName>
      <datasetFieldName>IsDeleted</datasetFieldName>
   </decisionTblDatasetParameters>
   <decisionTblDatasetParameters>
      <fieldName>LimitNumber</fieldName>
      <datasetFieldName>CallDurationInSeconds</datasetFieldName>
   </decisionTblDatasetParameters>
   <decisionTblDatasetParameters>
      <fieldName>Name</fieldName>
      <datasetFieldName>Subject</datasetFieldName>
   </decisionTblDatasetParameters>
   <description>DSL created for md-common tests</description>
   <isDefault>false</isDefault>
   <sourceObject>Task</sourceObject>
   <setupName>DSL Sample</setupName>
</DecisionTableDatasetLink>
```

      

The following is an example of a default DecisionTableDatasetLink component.

      

```

<?xml version="1.0" encoding="UTF-8"?>
<DecisionTableDatasetLink xmlns="http://soap.sforce.com/2006/04/metadata">
   <decisionTableName>Sample_DT</decisionTableName>
   <isDefault>true</isDefault>
   <sourceObject>WorkBadgeDefinition</sourceObject>
   <setupName>Default DSL Sample</setupName>
</DecisionTableDatasetLink>
```

      

The following is an example `package.xml` that
        references the previous definition.

      

```

<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
   <fullName>Sample DT Package</fullName>
   <description>Package created for md-common tests</description>
   <types>
      <members>Sample_DT</members>
      <name>DecisionTable</name>
   </types>
   <types>
      <members>DSL_Sample</members>
      <members>Sample_DT_Default</members>
      <name>DecisionTableDatasetLink</name>
   </types>
   <version>51.0</version>
</Package>
```
