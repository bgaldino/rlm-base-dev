---
page_id: meta_batchprocessjobdefinition.htm
title: BatchProcessJobDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_batchprocessjobdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_metadata.htm
fetched_at: 2026-06-25
---

# BatchProcessJobDefinition

Represents the details of a Batch Management job
definition.

This type extends the Metadata metadata type and inherits
its fullName field.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we
changed noninclusive terms to align with our company value of Equality. We maintained
certain terms to avoid any effect on customer implementations.

## File Suffix and Directory Location

BatchProcessJobDefinition components have the suffix
.batchProcessJobDefinition and are stored in the
batchProcessJobDefinitions folder.

## Version

BatchProcessJobDefinition components are available in API version 51.0 and later.

## Special Access Rules

To use this metadata type, your Salesforce org must have the Loyalty Management or the
Rebate Management license. The Loyalty Program Process type is only available in orgs that
have Loyalty Management enabled.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| batchSize | integer | Required. Number of records that each Batch Management job can process. Flow type Batch Management jobs can process up to 2000 records and Loyalty Program Process type Batch Management jobs can process up to 250 records. |
| dataSource | [BatchDataSource](#batchdatasourceID)[] | Required. Source of information whose records must be processed by the Batch Management job. |
| description | string | Description of the Batch Management job, up to 255 characters. |
| executionProcessApiName | string | API name of process that must be executed by the Batch Management job. This field is available in API version 55.0 and later.  - If the batch job’s type is Flow, enter the API name of an active flow that the   batch job must execute. - If the batch job’s type is Loyalty Program Process, enter:   - Transaction\_Journals if you want the batch job to process Transaction     Journal records by applying the applicable active loyalty program process of     the type TransactionJournal.   - API name of an active loyalty process of the type TierProcessing if you     want the batch job to run the loyalty program process to assess the tier of     eligible members. The API name consists of the name of the process, the     process type, and the name of the loyalty program separated by two     consecutive underscores. For example, the process API name is `Update Member Tier__TierProcessing__Inner     Circle` if the process name is Update Member Tier, the process     type is TierProcessing, and the loyalty program name is Inner Circle.   You can use database-based APEX classes that let you use flex queues in the Batch Management job, allowing to place more than 5 jobs in a queue. This functionality is applicable to all Industry Clouds that use managed packages. See [Apex Flex Queue](https://help.salesforce.com/s/articleView?id=platform.code_apex_flex_queue.htm&type=5&language=en_US "HTML (New Window)"). |
| flowApiName | string | API name of an active flow process that must be executed by the Batch Management job. You can either specify the flow API name in the `executionProcessApiName` field or in the `flowApiName` field. |
| flowInputVariable | string | Input variable of associated flow that is used by the batch job to uniquely identify records. |
| masterLabel | string | Required. Name of the Batch Management job, up to 80 characters. |
| processGroup | string | Required. Name of the group for which the Batch Management job processes records. |
| retryCount | integer | Required. Number of times this Batch Management job must be rerun in case it fails. The maximum retry count is 3. Valid values are 1–3. |
| retryInterval | integer | Required. Number of milliseconds after which the Batch Management job must be rerun in case it fails. Valid values are 1,000–10,000. |
| status | string | Indicates the status of the Batch Management job. Valid values are `Active` and `Inactive`. |
| type | string (enumeration of type string) | The type of process that the Batch Management job must execute. This field is available in API version 55.0 and later. Valid values are:  - `BulkUpdate` - `Calc`—Data Processing Engine - `ConsumptionOveragesCalculation` - `DecisionTableRefresh` - `DeepCloneSalesAgreement` - `FlattenAccountIOUHierarchyBatchJob` - `Flow` - `EnergyUseRecordCreationBatchJob` - `EntitlementCreationBatchJob` - `HighScaleBreProcess` - `IndustriesLSCommercial` - `InvoiceDTPRunBatchJob` - `InvoiceRecoveryRunBatchJob` - `InvoiceRunBatchJob` - `LifeSciProviderActivityGoalSharingBatchJob` - `LoyaltyProgramProcess` - `NetUnitRateCalculation` - `NextGenCommitmentBatchProcessingJob` - `ManagerProvisioning` - `PbbToOptyConversion` - `ProductCatalogCacheRefresh` - `PromotionChannelPropagationBatchJob` - `RatableSummaryCreation` - `ServiceProcess` - `StoreAssortmentPropagationBatchJob` - `SummaryCreation` - `WorkDotComToHRManagerProvisioning` |

## BatchDataSource

Represents the source of information whose records must be processed by the Batch
Management job.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| condition | string | Required. Criteria defined to filter the records. |
| criteria | string | Type of filter criteria that’s used to filter records for processing. |
| dataSourceType | string | Type of data source that's used to create the batch job definition. Valid values are:  - SingleSobject - MultiSobject   Available in API version 64.0 and later. |
| filters | [BatchDataSrcFilterCriteria](#batchdatasrcfiltercriteriaID)[] | Filter criterion that decides which records must be processed by the Batch Management job. |
| orderFields | [BatchDataSourceOrderField](#BatchDataSourceOrderField) | Fields that are used to order the records before the records are added to a batch in a job. |
| sourceObject | string | Required. API name of an object whose records must be processed by the batch job. If the batch job type is Loyalty Program Process, the source object must be:   - TransactionJournal if the batch job is used to process transaction journals by   applying the applicable loyalty program process. - An object that stores the details of loyalty program members whose tier must   be assessed by the loyalty program process specified in the   executionProcessApiName field. |
| sourceObjectField | string | API name of the source object field that uniquely identifies records for which the batch job is executed. This field is available in API version 57.0 and later. This field is only applicable when the batch job’s type is Loyalty Program Process and a TierProcess type active loyalty program process is specified in the executionProcessApiName field. Specify the API name of a field that is a lookup to the LoyaltyProgramMember object and uniquely identifies the members whose tier must be assessed. |

## BatchDataSrcFilterCriteria

Represents the filter conditions that decide which records must be processed by the Batch
Management job.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| domainObjectName | string | Name of the object the field is associated with. Available in API version 64.0 and later. |
| dynamicValueType | string | Data type of the input variable used as a filter. |
| fieldName | string | Required. Name of the field that must be used to filter records. |
| fieldPath | string | Stores the path to a field in the object. Available in API version 64.0 and later. |
| fieldValue | string | Required. Value of the field that must be filtered. Specify the field if `isDynamicValue` is set to `False`. |
| isDynamicValue | boolean | Required. Indicates whether the filter criteria is dynamic. |
| operator | string (enumeration of type string) | Required. Operator that is specified in the filter criteria. Valid values are:  - `equals` - `excludes` - `greaterThan` - `greaterThanOrEqualTo` - `in` - `includes` - `lessThan` - `LessThanOrEqualTo` - `GreaterOrEqual` - `like` - `notEquals` - `notIn` |
| sequenceNo | integer | Required. Sequence number used to refer the criteria in a filter. |

## BatchDataSourceOrderField

Represents the fields that are used to group data.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| domainObjectName | string | Required. Name of the object the field is associated with. Available in API version 64.0 and later. |
| fieldName | string | Required. Name of the field that must be used to filter records. Available in API version 64.0 and later. |
| fieldPath | string | Required. Stores the path to a field in the object. Available in API version 64.0 and later. |

## Declarative Metadata Sample Definition

The following is an example of a BatchProcessJobDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>
<BatchProcessJobDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
   <batchSize>10</batchSize>
   <dataSource>
      <condition>1</condition>
      <criteria>all</criteria>
      <filters>
         <dynamicValue>false</dynamicValue>
         <dynamicValueType>string</dynamicValueType>
         <fieldName>Name</fieldName>
         <fieldValue>abcd</fieldValue>
         <operator>equals</operator>
         <sequenceNo>1</sequenceNo>
      </filters>
      <sourceObject>Account</sourceObject>
   </dataSource>
   <flowApiName>Flow1</flowApiName>
   <flowInputVariable>recordId</flowInputVariable>
   <masterLabel>BatchJob1</masterLabel>
   <processGroup>Loyalty</processGroup>
   <retryCount>2</retryCount>
   <retryInterval>1000</retryInterval>
   <status>Inactive</status>
   <description>test</description>
   <type>Flow</type>
   <executionProcessApiName>testFlow</executionProcessApiName>
</BatchProcessJobDefinition>
```

The following is an example of a Flow object used in Metadata API.

```
<?xml version="1.0" encoding="UTF-8"?>
<!--
   ~ Copyright 2020 Salesforce, Inc.
   ~ All Rights Reserved
   ~ Company Confidential
-->
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
   <apiVersion>51.0</apiVersion>
   <interviewLabel>Flow1 {!$Flow.CurrentDateTime}</interviewLabel>
   <label>Flow1</label>
   <processMetadataValues>
      <name>BuilderType</name>
      <value>
         <stringValue>LightningFlowBuilder</stringValue>
      </value>
   </processMetadataValues>
   <processMetadataValues>
      <name>OriginBuilderType</name>
      <value>
         <stringValue>LightningFlowBuilder</stringValue>
      </value>
   </processMetadataValues>
   <processType>AutoLaunchedFlow</processType>
   <recordLookups>
      <name>getAcc</name>
      <label>getAcc</label>
      <locationX>614</locationX>
      <locationY>465</locationY>
      <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
      <filterLogic>and</filterLogic>
      <filters>
         <field>Id</field>
         <operator>EqualTo</operator>
         <value>
            <elementReference>recordId</elementReference>
         </value>
      </filters>
      <getFirstRecordOnly>true</getFirstRecordOnly>
      <object>Account</object>
      <storeOutputAutomatically>true</storeOutputAutomatically>
   </recordLookups>
   <start>
      <locationX>73</locationX>
      <locationY>213</locationY>
      <connector>
         <targetReference>getAcc</targetReference>
      </connector>
   </start>
   <status>Draft</status>
   <variables>
      <name>recordId</name>
      <dataType>String</dataType>
      <isCollection>false</isCollection>
      <isInput>true</isInput>
      <isOutput>false</isOutput>
   </variables>
</Flow>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
   <types>
      <members>*</members>
      <name>BatchProcessJobDefinition</name>
   </types>
   <types>
      <members>Flow1</members>
      <name>Flow</name>
   </types>
   <version>51.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest
file. For information about using the manifest file, see Deploying and Retrieving Metadata with the Zip File.
