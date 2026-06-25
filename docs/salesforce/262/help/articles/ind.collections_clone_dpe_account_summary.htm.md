---
article_id: ind.collections_clone_dpe_account_summary.htm
title: Clone and Customize the Predefined Data Processing Engine Definition for Collections Summary
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_clone_dpe_account_summary.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_insights_account_page.htm
fetched_at: 2026-06-21
---

# Clone and Customize the Predefined Data Processing Engine Definition for Collections Summary

Clone and customize the predefined Data Processing Engine definition. This definition is designed to compute the aggregated summary of specific collection plan fields, such as the initial amount due, current amount due, payments received, and the average days past due for all collection plans linked to an account.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To clone and customize the prebuilt Data Processing Engine definition:	

Collections and Recovery Admin permission set

AND

Customize Application permission

AND

Modify All Data permission

AND

Data Pipelines Base User permission set

From Setup, in the Quick Find box, enter Data Processing Engine, and then select Data Processing Engine.
To download the predefined Data Processing Engine definition, Collections Summary for Account, from the action menu, click .
Open the definition that you downloaded, which is in the JSON format.
Replace the FullName according to your requirements. For example, CollectionsSummaryForCaroleWhite. Make sure that the full name doesn't contain any spaces or special characters.
{
  "FullName": "CollectionsSummaryForCaroleWhite",
  "Metadata": {
    "aggregates": [
      {
        "fields": [

Replace the label and name according to your requirements. For example, Collections Summary for Carole White.
"groupBy": [
          "AccountId"
        ],
        "label": "Collections Summary for Carole White",
        "name": "Collections_Summary_For_Carole_White",
        "sourceName": "Collection_Plan_Filter"
      }  

Make sure that the field aliases for the custom sourceFieldNames in the Data Processing Engine definition match those listed in the table. If you've created custom fields with different API names, update the corresponding field aliases accordingly.
	
SourceFieldName	Alias
DaysPastDue	AccountAverageDaysPastDue
CurrentDueAmount	AccountTotalCurrentDueAmount
InitialDueAmount	AccountTotalInitialDueAmount
TotalPaymentsReceived	AccountTotalPaymentsReceived
{
  "FullName": "Account Collections Summary","AccountCollectionsSummaryCloned",
  "Metadata": {
    "aggregates": [
      {
        "fields": [
          {
            "aggregateFunction": "Avg",
            "alias": "AccountAverageDaysPastDue",
            "sourceFieldName": "DaysPastDue"
          },
          {
            "aggregateFunction": "Sum",
            "alias": "AccountTotalCurrentDueAmount",
            "sourceFieldName": "CurrentDueAmount"
          },
          {
            "aggregateFunction": "Sum",
            "alias": "AccountTotalInitialDueAmount",
            "sourceFieldName": "InitialDueAmount"
          },
          {
            "aggregateFunction": "Sum",
            "alias": "AccountTotalPaymentsReceived",
            "sourceFieldName": "TotalPaymentsReceived"
          }
        ],
        "groupBy": [
          "AccountId"
        ],

Set isTemplate to False.
"isTemplate": false,
    "label": "Account Collections Summary","Account Collections Summary Cloned"
    "parameters": [
      {
        "dataType": "Text",
        "isMultiValue": false,
        "label": "Input Record Id",
        "name": "Input_Record_Id"
      }

Make sure that definitionRunMode is set to OnDemand.
"definitionRunMode": "OnDemand",
    "description": "Adds quote line items from a CSV file to a quote.",
    "doesGenAllFailedRecords": false,
    "executionPlatformObjectType": "None",
    "executionPlatformType": "CORE",

Set writebackUser to a user ID who plans to run this cloned Data Processing Engine definition. Make sure that this user has create, read, update, delete permissions on the Collection Plan and Account objects.
 "isChangedRow": false,
        "isExistingDataset": false,
        "label": "Collection Plan Writeback",
        "name": "Collection_Plan_Writeback",
        "operationType": "Update",
        "shouldCreateTargetObject": false,
        "sourceName": "Collection_Plan_Aggregate",
        "storageType": "sObject",
        "targetObjectName": "Account",
        "writebackRecordMaxLimit": 0,
        "writebackSequence": 1,
        "writebackUser": "<User ID who runs this cloned definition>"

Run the API endpoint and provide the content of the cloned and customized Data Processing Engine definition in JSON format as the payload.
/services/data/v65.0/tooling/sobjects/BatchCalcJobDefinition
From the API endpoint's response, note the record ID of the cloned and customized Data Processing Engine definition.
From Setup, in the Quick Find box, enter Data Processing Engine, and then select Data Processing Engine.
Make sure that the cloned and customized Data Processing Engine is listed.
