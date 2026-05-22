---
article_id: ind.qocal_qli_import_create_custom_dpe_definition.htm
title: Customize Data Processing Engine Definitions for Quote Line Item Imports
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_qli_import_create_custom_dpe_definition.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Customize Data Processing Engine Definitions for Quote Line Item Imports

Modify the Data Processing Engine definition if you want users to import custom fields. Transaction Management uses this definition to process quote line items after a user uploads a CSV file.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create a Data Processing Engine definition:	

Customize Application

AND

Modify All Data

Before you begin, download the existing template.
In Setup, find and select Data Processing Engine.
Click  corresponding to the Create Quote Line Items from a CSV File template and select Download.
Because the execution platform type of the definition is Core, you can’t open it in the visual definition builder tool.
Open and edit the downloaded JSON file. Adhere to these requirements during customization.
Retain the default values for the definitionRunMode, executionPlatformType, and processType fields.
Keep the Get_Related_Quote_Line_Items_Relationships_and_Attributes and Consolidate_and_Write_Quote_Line_Item_and_Its_Related_Records nodes to create default child line items for bundled products and default quote line item attributes.
Maintain the Quote Line Reference parameter in the Get_Related_Quote_Line_Items_Relationships_and_Attributes custom node and the Consolidate_and_Write_Quote_Line_Item_and_Its_Related_Records node.
Set the value of the isTemplate field to false.
Use the API name for custom field aliases and change the suffix __c to _c.
For example, use the alias SpecialInstructions_c for the SpecialInstructions__c custom field.
Use the BatchCalcJobDefinition API to upload the updated Data Processing Engine definition.
Select the updated definition in the Data Processing Engine Definition for Importing Quote Line Items field.
EXAMPLE

In this example, the definition includes specific nodes and logic for processing data.

The Get Unique Products node uses an aggregate function to count unique product codes from filtered quote line item rows.
The appended node combines quote line item rows with and without product selling models.
The Consolidate and Write Quote Line Item and its Related Records node consolidates quote line items, relationships, and attributes. It then writes them together to target objects.
Filters restrict rows based on the QuoteId input variable and identify products without selling models.
Expression fields identify blank selling models and determine default values for StartDate and SubscriptionTerm.
{
  "FullName" : "SpecialInstructions_c",
  "Metadata" : {
    "aggregates" : [ {
      "description" : "Gets a list of unique products from the quote line item rows and their count.",
      "fields" : [ {
        "aggregateFunction" : "Count",
        "alias" : "UniqueProductCodeCount",
        "sourceFieldName" : "ProductCode"
      } ],
      "groupBy" : [ "ProductCode", "QuoteId" ],
      "label" : "Get Unique Products",
      "name" : "Get_Unique_Products",
      "sourceName" : "Filter_Quote_Line_Item_Rows_by_Quote_ID"
    } ],
    "appends" : [ {
      "description" : "Combines quote line item rows that have a product selling model with those that don’t have one.",
      "isDisjointedSchema" : false,
      "label" : "Combine Quote Line Item Rows With and Without Product Selling Models",
      "name" : "Combine_Quote_Line_Item_Rows_With_and_Without_Product_Selling_Models",
      "sources" : [ "Add_Product_Fields_to_Quote_Line_Item_Rows_with_Product_Selling_Models", "Add_Product_Fields_to_Quote_Line_Item_Rows_Without_Product_Selling_Models" ]
    } ],
    "atomicWritebacks" : [ {
      "description" : "Consolidates quote line item, quote line relationship, and quote line item attribute records, and then writes all the records together to the target objects.",
      "label" : "Consolidate and Write Quote Line Item and Its Related Records",
      "name" : "Consolidate_and_Write_Quote_Line_Item_and_Its_Related_Records",
      "writebackObjectRelationships" : [ {
        "childWritebackObjectName" : "Create_Quote_Line_Item_Relationship",
        "parentWritebackObjectName" : "Create_Quote_Line_Item_Records",
        "sequenceNumber" : 1
      }, {
        "childWritebackObjectName" : "Create_Quote_Line_Attributes",
        "parentWritebackObjectName" : "Create_Quote_Line_Item_Records",
        "sequenceNumber" : 1
      } ],
      "writebackSequence" : 1
    } ],
    "customNodes" : [ {
      "description" : "Gets child line item, relationship, and attribute records for the input quote line items. It also adds QuoteLineReference values to these records. The Composite Writeback node uses these values to write the related records together.",
      "extensionName" : "GetRelatedLinesRelationshipsAndAttributes",
      "extensionNamespace" : "TransactionManagement",
      "label" : "Get Related Quote Line Items, Relationships, and Attributes",
      "name" : "Get_Related_Quote_Line_Items_Relationships_and_Attributes",
      "parameters" : [ {
        "name" : "Attribute_AttributeName",
        "value" : "Attribute_AttributeName"
      }, {
        "name" : "Attribute_AttributeValue",
        "value" : "Attribute_AttributeValue"
      }, {
        "name" : "Attribute_AttributePicklistValueId",
        "value" : "Attribute_AttributePicklistValueId"
      }, {
        "name" : "Attribute_AttributeDefinitionId",
        "value" : "Attribute_AttributeDefinitionId"
      }, {
        "name" : "Relationship_MainQuoteLineId",
        "value" : "Relationship_MainQuoteLineId"
      }, {
        "name" : "Relationship_AssociatedQuoteLineId",
        "value" : "Relationship_AssociatedQuoteLineId"
      }, {
        "name" : "Relationship_ProductRelationshipTypeId",
        "value" : "Relationship_ProductRelationshipTypeId"
      }, {
        "name" : "Relationship_AssociatedQuoteLinePricing",
        "value" : "Relationship_AssociatedQuoteLinePricing"
      }, {
        "name" : "Relationship_AssociatedQuantScaleMethod",
        "value" : "Relationship_AssociatedQuantScaleMethod"
      }, {
        "name" : "Relationship_ProductRelatedComponent",
        "value" : "Relationship_ProductRelatedComponent"
      }, {
        "name" : "RowType",
        "value" : "RowType"
      }, {
        "name" : "QuoteLineReference",
        "value" : "QuoteLineReference"
      } ],
      "sources" : [ "Add_Default_Fields_to_Quote_Line_Item_Rows" ]
    } ],
    "dataSpaceApiName" : "default",
    "datasources" : [ {
      "description" : "Gets all rows from the CSV file, which is used as a data source to create quote line item records.",
      "fields" : [ {
        "alias" : "BillingFrequency",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "BillingFrequency"
      }, {
        "alias" : "SubscriptionTerm",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "SubscriptionTerm"
      }, {
        "alias" : "StartDate",
        "dataType" : "Date",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "StartDate"
      }, {
        "alias" : "SalesPrice",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "SalesPrice"
      }, {
        "alias" : "QuoteId",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "QuoteId"
      }, {
        "alias" : "Quantity",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "Quantity"
      }, {
        "alias" : "ProductSellingModelName",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "ProductSellingModelName"
      }, {
        "alias" : "ProductName",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "ProductName"
      }, {
        "alias" : "ProductDescription",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "ProductDescription"
      }, {
        "alias" : "ProductCode",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "ProductCode"
      }, {
        "alias" : "EndDate",
        "dataType" : "Date",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "EndDate"
      }, {
        "alias" : "DiscountPercentage",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "DiscountPercentage"
      }, {
        "alias" : "DiscountAmount",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "DiscountAmount"
      }, {
        "alias" : "ServiceDate",
        "dataType" : "Date",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "ServiceDate"
      }, {
        "alias" : "RowNumber",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : true,
        "name" : "RowNumber"
      }, {
        "alias" : "QuoteLineGroupId",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "QuoteLineGroupId"
      }, {
        "alias" : "SpecialInstructions_c",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "SpecialInstructions"
      } ],
      "fileIdentifier" : "{!CSV_File_ID}",
      "fileSource" : "ContentManagement",
      "label" : "Get Quote Line Item Rows from a CSV File",
      "name" : "Get_Quote_Line_Item_Rows_from_a_CSV_File",
      "sourceName" : "Get_Quote_Line_Items_from_a_CSV_File_CSV",
      "type" : "CSV"
    }, {
      "description" : "Gets all price book entries, which are used as a data source to populate pricing information.",
      "fields" : [ {
        "alias" : "IsActive",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "IsActive"
      }, {
        "alias" : "Pricebook2Id",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "Pricebook2Id"
      }, {
        "alias" : "Id",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "Id"
      }, {
        "alias" : "Product2Id",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "Product2Id"
      }, {
        "alias" : "ProductCode",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "ProductCode"
      }, {
        "alias" : "ProductSellingModelId",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "ProductSellingModelId"
      } ],
      "label" : "Get Price Book Entries from Salesforce Object",
      "name" : "Get_Price_Book_Entries_from_Salesforce_Object",
      "sourceName" : "PricebookEntry",
      "type" : "StandardObject"
    }, {
      "description" : "Gets all product selling models, which are used as a data source to populate the method by which a product is sold.",
      "fields" : [ {
        "alias" : "ProductSellingModelId",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "Id"
      }, {
        "alias" : "ProductSellingModelName",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "Name"
      }, {
        "alias" : "SellingModelType",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "SellingModelType"
      }, {
        "alias" : "PricingTerm",
        "dataType" : "Numeric",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "PricingTerm"
      } ],
      "label" : "Get Product Selling Models from Salesforce Object",
      "name" : "Get_Product_Selling_Models_from_Salesforce_Object",
      "sourceName" : "ProductSellingModel",
      "type" : "StandardObject"
    }, {
      "description" : "Gets all quotes and their related price book IDs. Price books contain the list of products and their prices.",
      "fields" : [ {
        "alias" : "Pricebook2Id",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "Pricebook2Id"
      }, {
        "alias" : "Id",
        "dataType" : "Text",
        "displaySequence" : 1,
        "isPrimaryKey" : false,
        "name" : "Id"
      } ],
      "label" : "Get Quote and Related Price Books from Salesforce Object",
      "name" : "Get_Quote_and_Related_Price_Books_from_Salesforce_Object",
      "sourceName" : "Quote",
      "type" : "StandardObject"
    } ],
    "definitionRunMode" : "OnDemand",
    "description" : "Adds quote line items from a CSV file to a quote.",
    "doesGenAllFailedRecords" : false,
    "executionPlatformObjectType" : "None",
    "executionPlatformType" : "CORE",
    "filters" : [ {
      "criteria" : [ {
        "inputVariable" : "QuoteId",
        "operator" : "Equals",
        "sequence" : 1,
        "sourceFieldName" : "QuoteId"
      } ],
      "description" : "Filters the quote line item rows where the QuoteId field value matches the Quote ID variable value.",
      "filterCondition" : "1",
      "isDynamicFilter" : false,
      "label" : "Filter Quote Line Item Rows by Quote ID",
      "name" : "Filter_Quote_Line_Item_Rows_by_Quote_ID",
      "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
    }, {
      "criteria" : [ {
        "inputVariable" : "QuoteId",
        "operator" : "Equals",
        "sequence" : 1,
        "sourceFieldName" : "Id"
      } ],
      "description" : "Filters the quote record where the ID matches the value in the Quote ID variable.",
      "filterCondition" : "1",
      "isDynamicFilter" : false,
      "label" : "Filter Quote with Matching Quote ID",
      "name" : "Filter_Quote_with_Matching_Quote_ID",
      "sourceName" : "Get_Quote_and_Related_Price_Books_from_Salesforce_Object"
    }, {
      "criteria" : [ {
        "inputVariable" : "Pricebook2Id",
        "operator" : "Equals",
        "sequence" : 1,
        "sourceFieldName" : "Pricebook2Id"
      } ],
      "description" : "Filters the price book record where the ID matches the value in the Price Book ID input variable.",
      "filterCondition" : "1",
      "isDynamicFilter" : false,
      "label" : "Filter Price Book Entries by Price Book ID",
      "name" : "Filter_Price_Book_Entries_by_Price_Book_ID",
      "sourceName" : "Get_Price_Book_Entries_from_Salesforce_Object"
    }, {
      "criteria" : [ {
        "operator" : "Equals",
        "sequence" : 1,
        "sourceFieldName" : "IsProductSellingModelEmpty",
        "value" : "0"
      } ],
      "description" : "Filters quote line item rows that have a product selling model.",
      "filterCondition" : "1",
      "isDynamicFilter" : false,
      "label" : "Filter Quote Line Item Rows with Product Selling Models",
      "name" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models",
      "sourceName" : "Identify_Quote_Line_Item_Rows_Without_Product_Selling_Models"
    }, {
      "criteria" : [ {
        "operator" : "Equals",
        "sequence" : 1,
        "sourceFieldName" : "IsProductSellingModelEmpty",
        "value" : "1"
      } ],
      "description" : "Filters quote line item rows that don’t have a product selling model.",
      "filterCondition" : "1",
      "isDynamicFilter" : false,
      "label" : "Filter Quote Line Item Rows without Product Selling Models",
      "name" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models",
      "sourceName" : "Identify_Quote_Line_Item_Rows_Without_Product_Selling_Models"
    }, {
      "criteria" : [ {
        "operator" : "Equals",
        "sequence" : 1,
        "sourceFieldName" : "IsProductSellingModelBlank",
        "value" : "1"
      } ],
      "description" : "Filters products that don't have a product selling model.",
      "filterCondition" : "1",
      "isDynamicFilter" : false,
      "label" : "Filter Products Without Product Selling Model",
      "name" : "Filter_Products_Without_Product_Selling_Model",
      "sourceName" : "Identify_Products_Without_Product_Selling_Models"
    }, {
      "criteria" : [ {
        "operator" : "Equals",
        "sequence" : 1,
        "sourceFieldName" : "RowType",
        "value" : "QuoteLineItem"
      } ],
      "description" : "Filters all the quote line item records.",
      "filterCondition" : "1",
      "isDynamicFilter" : false,
      "label" : "Filter Quote Line Item Rows",
      "name" : "Filter_Quote_Line_Item_Rows",
      "sourceName" : "Get_Related_Quote_Line_Items_Relationships_and_Attributes"
    }, {
      "criteria" : [ {
        "operator" : "Equals",
        "sequence" : 1,
        "sourceFieldName" : "RowType",
        "value" : "QuoteLineRelationship"
      } ],
      "description" : "Filters all the quote line item relationship records.",
      "filterCondition" : "1",
      "isDynamicFilter" : false,
      "label" : "Filter Quote Line Item Relationship",
      "name" : "Filter_Quote_Line_Item_Relationship",
      "sourceName" : "Get_Related_Quote_Line_Items_Relationships_and_Attributes"
    }, {
      "criteria" : [ {
        "operator" : "Equals",
        "sequence" : 1,
        "sourceFieldName" : "RowType",
        "value" : "QuoteLineItemAttribute"
      } ],
      "description" : "Filters all the quote line item attribute records.",
      "filterCondition" : "1",
      "isDynamicFilter" : false,
      "label" : "Filter Quote Line Attributes",
      "name" : "Filter_Quote_Line_Attributes",
      "sourceName" : "Get_Related_Quote_Line_Items_Relationships_and_Attributes"
    } ],
    "isTemplate" : false,
    "joins" : [ {
      "description" : "Adds price book entry fields to the products based on the product code.",
      "fields" : [ {
        "alias" : "ProductCode_CSV",
        "sourceFieldName" : "ProductCode",
        "sourceName" : "Get_Unique_Products"
      }, {
        "alias" : "Id",
        "sourceFieldName" : "Id",
        "sourceName" : "Filter_Price_Book_Entries_by_Price_Book_ID"
      }, {
        "alias" : "IsActive",
        "sourceFieldName" : "IsActive",
        "sourceName" : "Filter_Price_Book_Entries_by_Price_Book_ID"
      }, {
        "alias" : "Pricebook2Id",
        "sourceFieldName" : "Pricebook2Id",
        "sourceName" : "Filter_Price_Book_Entries_by_Price_Book_ID"
      }, {
        "alias" : "Product2Id",
        "sourceFieldName" : "Product2Id",
        "sourceName" : "Filter_Price_Book_Entries_by_Price_Book_ID"
      }, {
        "alias" : "ProductCode",
        "sourceFieldName" : "ProductCode",
        "sourceName" : "Filter_Price_Book_Entries_by_Price_Book_ID"
      }, {
        "alias" : "ProductSellingModelId",
        "sourceFieldName" : "ProductSellingModelId",
        "sourceName" : "Filter_Price_Book_Entries_by_Price_Book_ID"
      } ],
      "joinKeys" : [ {
        "primarySourceFieldName" : "ProductCode",
        "secondarySourceFieldName" : "ProductCode"
      } ],
      "label" : "Add Price Book Entries to Products",
      "name" : "Add_Price_Book_Entries_to_Products",
      "primarySourceName" : "Get_Unique_Products",
      "secondarySourceName" : "Filter_Price_Book_Entries_by_Price_Book_ID",
      "type" : "Inner"
    }, {
      "description" : "Adds the price book ID to quote line item rows based on the quote ID.",
      "fields" : [ {
        "alias" : "DiscountAmount",
        "sourceFieldName" : "DiscountAmount",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "DiscountPercentage",
        "sourceFieldName" : "DiscountPercentage",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "EndDate",
        "sourceFieldName" : "EndDate",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "ProductCode",
        "sourceFieldName" : "ProductCode",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "ProductDescription",
        "sourceFieldName" : "ProductDescription",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "ProductName",
        "sourceFieldName" : "ProductName",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "ProductSellingModelName",
        "sourceFieldName" : "ProductSellingModelName",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "Quantity",
        "sourceFieldName" : "Quantity",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "QuoteId",
        "sourceFieldName" : "QuoteId",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "QuoteLineGroupId",
        "sourceFieldName" : "QuoteLineGroupId",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "RowNumber",
        "sourceFieldName" : "RowNumber",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "SalesPrice",
        "sourceFieldName" : "SalesPrice",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "ServiceDate",
        "sourceFieldName" : "ServiceDate",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "SpecialInstructions_c",
        "sourceFieldName" : "SpecialInstructions_c",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "StartDate",
        "sourceFieldName" : "StartDate",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "SubscriptionTerm",
        "sourceFieldName" : "SubscriptionTerm",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "BillingFrequency",
        "sourceFieldName" : "BillingFrequency",
        "sourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File"
      }, {
        "alias" : "Pricebook2Id",
        "sourceFieldName" : "Pricebook2Id",
        "sourceName" : "Filter_Quote_with_Matching_Quote_ID"
      } ],
      "joinKeys" : [ {
        "primarySourceFieldName" : "QuoteId",
        "secondarySourceFieldName" : "Id"
      } ],
      "label" : "Add Price Book ID to Quote Line Item Rows",
      "name" : "Add_Price_Book_ID_to_Quote_Line_Item_Rows",
      "primarySourceName" : "Get_Quote_Line_Item_Rows_from_a_CSV_File",
      "secondarySourceName" : "Filter_Quote_with_Matching_Quote_ID",
      "type" : "Inner"
    }, {
      "description" : "Adds product selling model fields to products based on the product selling model ID.",
      "fields" : [ {
        "alias" : "Pricebook2Id",
        "sourceFieldName" : "Pricebook2Id",
        "sourceName" : "Add_Price_Book_Entries_to_Products"
      }, {
        "alias" : "PricebookEntryId",
        "sourceFieldName" : "Id",
        "sourceName" : "Add_Price_Book_Entries_to_Products"
      }, {
        "alias" : "Product2Id",
        "sourceFieldName" : "Product2Id",
        "sourceName" : "Add_Price_Book_Entries_to_Products"
      }, {
        "alias" : "ProductCode",
        "sourceFieldName" : "ProductCode_CSV",
        "sourceName" : "Add_Price_Book_Entries_to_Products"
      }, {
        "alias" : "PricingTerm",
        "sourceFieldName" : "PricingTerm",
        "sourceName" : "Get_Product_Selling_Models_from_Salesforce_Object"
      }, {
        "alias" : "ProductSellingModelName",
        "sourceFieldName" : "ProductSellingModelName",
        "sourceName" : "Get_Product_Selling_Models_from_Salesforce_Object"
      }, {
        "alias" : "SellingModelType",
        "sourceFieldName" : "SellingModelType",
        "sourceName" : "Get_Product_Selling_Models_from_Salesforce_Object"
      } ],
      "joinKeys" : [ {
        "primarySourceFieldName" : "ProductSellingModelId",
        "secondarySourceFieldName" : "ProductSellingModelId"
      } ],
      "label" : "Add Product Selling Models to Products",
      "name" : "Add_Product_Selling_Models_to_Products",
      "primarySourceName" : "Add_Price_Book_Entries_to_Products",
      "secondarySourceName" : "Get_Product_Selling_Models_from_Salesforce_Object",
      "type" : "LeftOuter"
    }, {
      "description" : "Adds price book entry and product selling model fields to quote line item rows that have a product selling model, based on product code, price book ID, and product selling model name.",
      "fields" : [ {
        "alias" : "DiscountAmount",
        "sourceFieldName" : "DiscountAmount",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "DiscountPercentage",
        "sourceFieldName" : "DiscountPercentage",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "EndDate",
        "sourceFieldName" : "EndDate",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "ProductDescription",
        "sourceFieldName" : "ProductDescription",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "ProductName",
        "sourceFieldName" : "ProductName",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "Quantity",
        "sourceFieldName" : "Quantity",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "QuoteId",
        "sourceFieldName" : "QuoteId",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "QuoteLineGroupId",
        "sourceFieldName" : "QuoteLineGroupId",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "SalesPrice",
        "sourceFieldName" : "SalesPrice",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "ServiceDate",
        "sourceFieldName" : "ServiceDate",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "SpecialInstructions_c",
        "sourceFieldName" : "SpecialInstructions_c",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "StartDate",
        "sourceFieldName" : "StartDate",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "SubscriptionTerm",
        "sourceFieldName" : "SubscriptionTerm",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "BillingFrequency",
        "sourceFieldName" : "BillingFrequency",
        "sourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models"
      }, {
        "alias" : "PricebookEntryId",
        "sourceFieldName" : "PricebookEntryId",
        "sourceName" : "Add_Product_Selling_Models_to_Products"
      }, {
        "alias" : "PricingTerm",
        "sourceFieldName" : "PricingTerm",
        "sourceName" : "Add_Product_Selling_Models_to_Products"
      }, {
        "alias" : "Product2Id",
        "sourceFieldName" : "Product2Id",
        "sourceName" : "Add_Product_Selling_Models_to_Products"
      }, {
        "alias" : "SellingModelType",
        "sourceFieldName" : "SellingModelType",
        "sourceName" : "Add_Product_Selling_Models_to_Products"
      } ],
      "joinKeys" : [ {
        "primarySourceFieldName" : "ProductCode",
        "secondarySourceFieldName" : "ProductCode"
      }, {
        "primarySourceFieldName" : "Pricebook2Id",
        "secondarySourceFieldName" : "Pricebook2Id"
      }, {
        "primarySourceFieldName" : "ProductSellingModelName",
        "secondarySourceFieldName" : "ProductSellingModelName"
      } ],
      "label" : "Add Product Fields to Quote Line Item Rows with Product Selling Models",
      "name" : "Add_Product_Fields_to_Quote_Line_Item_Rows_with_Product_Selling_Models",
      "primarySourceName" : "Filter_Quote_Line_Item_Rows_with_Product_Selling_Models",
      "secondarySourceName" : "Add_Product_Selling_Models_to_Products",
      "type" : "LeftOuter"
    }, {
      "description" : "Adds price book entry and product selling model fields to quote line item rows that don’t have a product selling model, based on product code, price book ID, and product selling model name.",
      "fields" : [ {
        "alias" : "DiscountAmount",
        "sourceFieldName" : "DiscountAmount",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "DiscountPercentage",
        "sourceFieldName" : "DiscountPercentage",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "EndDate",
        "sourceFieldName" : "EndDate",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "ProductDescription",
        "sourceFieldName" : "ProductDescription",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "ProductName",
        "sourceFieldName" : "ProductName",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "Quantity",
        "sourceFieldName" : "Quantity",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "QuoteId",
        "sourceFieldName" : "QuoteId",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "QuoteLineGroupId",
        "sourceFieldName" : "QuoteLineGroupId",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "SalesPrice",
        "sourceFieldName" : "SalesPrice",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "ServiceDate",
        "sourceFieldName" : "ServiceDate",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "SpecialInstructions_c",
        "sourceFieldName" : "SpecialInstructions_c",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "StartDate",
        "sourceFieldName" : "StartDate",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "SubscriptionTerm",
        "sourceFieldName" : "SubscriptionTerm",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "BillingFrequency",
        "sourceFieldName" : "BillingFrequency",
        "sourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models"
      }, {
        "alias" : "PricebookEntryId",
        "sourceFieldName" : "PricebookEntryId",
        "sourceName" : "Filter_Products_Without_Product_Selling_Model"
      }, {
        "alias" : "PricingTerm",
        "sourceFieldName" : "PricingTerm",
        "sourceName" : "Filter_Products_Without_Product_Selling_Model"
      }, {
        "alias" : "Product2Id",
        "sourceFieldName" : "Product2Id",
        "sourceName" : "Filter_Products_Without_Product_Selling_Model"
      }, {
        "alias" : "SellingModelType",
        "sourceFieldName" : "SellingModelType",
        "sourceName" : "Filter_Products_Without_Product_Selling_Model"
      } ],
      "joinKeys" : [ {
        "primarySourceFieldName" : "ProductCode",
        "secondarySourceFieldName" : "ProductCode"
      }, {
        "primarySourceFieldName" : "Pricebook2Id",
        "secondarySourceFieldName" : "Pricebook2Id"
      } ],
      "label" : "Add Product Fields to Quote Line Item Rows Without Product Selling Models",
      "name" : "Add_Product_Fields_to_Quote_Line_Item_Rows_Without_Product_Selling_Models",
      "primarySourceName" : "Filter_Quote_Line_Item_Rows_Without_Product_Selling_Models",
      "secondarySourceName" : "Filter_Products_Without_Product_Selling_Model",
      "type" : "LeftOuter"
    } ],
    "label" : "SpecialInstructions_c",
    "parameters" : [ {
      "dataType" : "FileIdentifier",
      "description" : "The ID of the CSV file that contains the quote line item rows that must be processed to create records.",
      "isMultiValue" : false,
      "label" : "CSV File ID",
      "name" : "CSV_File_ID"
    }, {
      "dataType" : "Text",
      "description" : "The ID of the quote for which quote line items must be created.",
      "isMultiValue" : false,
      "label" : "Quote ID",
      "name" : "QuoteId"
    }, {
      "dataType" : "Text",
      "description" : "The ID of the price book associated with the quote to which the quote line items must be added.",
      "isMultiValue" : false,
      "label" : "Price Book ID",
      "name" : "Pricebook2Id"
    } ],
    "processType" : "RevenueTransactionManagement",
    "status" : "Active",
    "transforms" : [ {
      "name" : "Identify_Quote_Line_Item_Rows_Without_Product_Selling_Models",
      "sourceName" : "Add_Price_Book_ID_to_Quote_Line_Item_Rows",
      "label" : "Identify Quote Line Item Rows without Product Selling Models",
      "transformationType" : "Expression",
      "partitionBy" : [ ],
      "orderBy" : [ ],
      "expressionFields" : [ {
        "alias" : "IsProductSellingModelEmpty",
        "expression" : "IF(ISBLANK({ProductSellingModelName} ),1,0)",
        "dataType" : "Numeric",
        "length" : 1,
        "decimalPlaces" : 0
      } ],
      "droppedFields" : [ ]
    }, {
      "name" : "Identify_Products_Without_Product_Selling_Models",
      "sourceName" : "Add_Product_Selling_Models_to_Products",
      "label" : "Identify Products Without Product Selling Models",
      "transformationType" : "Expression",
      "partitionBy" : [ ],
      "orderBy" : [ ],
      "expressionFields" : [ {
        "alias" : "IsProductSellingModelBlank",
        "expression" : "IF(ISBLANK({ProductSellingModelName} ),1,0)",
        "dataType" : "Numeric",
        "length" : 1,
        "decimalPlaces" : 0
      } ],
      "droppedFields" : [ ]
    }, {
      "name" : "Add_Default_Fields_to_Quote_Line_Item_Rows",
      "sourceName" : "Combine_Quote_Line_Item_Rows_With_and_Without_Product_Selling_Models",
      "label" : "Add Default Fields to Quote Line Item Rows",
      "transformationType" : "Expression",
      "partitionBy" : [ ],
      "orderBy" : [ ],
      "expressionFields" : [ {
        "alias" : "DefaultPeriodBoundary",
        "expression" : "IF({SellingModelType} == \"TermDefined\" || {SellingModelType} == \"Evergreen\",\"Anniversary\",NULL)",
        "dataType" : "Text",
        "length" : 100
      }, {
        "alias" : "DefaultStartDate",
        "expression" : "IF({SellingModelType} == \"OneTime\",{StartDate},IF({SellingModelType} == \"TermDefined\" &&  ISBLANK({StartDate}),TODAY(),IF({SellingModelType} == \"Evergreen\" &&  ISBLANK({StartDate}),TODAY(),{StartDate})))",
        "dataType" : "Date"
      }, {
        "alias" : "DefaultSubscriptionTerm",
        "expression" : "IF({SellingModelType} == \"OneTime\" || {SellingModelType} == \"Evergreen\",{SubscriptionTerm},IF({SellingModelType} == \"TermDefined\" && ISBLANK({SubscriptionTerm}),IF(ISBLANK({EndDate}),TEXT(FLOOR({PricingTerm})),{SubscriptionTerm}),{SubscriptionTerm}))",
        "dataType" : "Text",
        "length" : 100
      } ],
      "droppedFields" : [ ]
    } ],
    "writebacks" : [ {
      "name" : "Create_Quote_Line_Item_Records",
      "label" : "Create Quote Line Item Records",
      "sourceName" : "Filter_Quote_Line_Item_Rows",
      "targetObjectName" : "QuoteLineItem",
      "writebackRecordMaxLimit" : 0,
      "isChangedRow" : false,
      "shouldCreateTargetObject" : false,
      "isExistingDataset" : false,
      "description" : "Creates quote line item records for all the rows in the CSV file, including their child line items.",
      "canWrtbckToNonEditableFields" : false,
      "storageType" : "sObject",
      "operationType" : "Insert",
      "writebackSequence" : 1,
      "fields" : [ {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "PricebookEntryId",
        "targetFieldName" : "PricebookEntryId"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "Product2Id",
        "targetFieldName" : "Product2Id"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "Quantity",
        "targetFieldName" : "Quantity"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "QuoteId",
        "targetFieldName" : "QuoteId"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "DiscountAmount",
        "targetFieldName" : "DiscountAmount"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "DiscountPercentage",
        "targetFieldName" : "Discount"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "DefaultStartDate",
        "targetFieldName" : "StartDate"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "DefaultPeriodBoundary",
        "targetFieldName" : "PeriodBoundary"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "DefaultSubscriptionTerm",
        "targetFieldName" : "SubscriptionTerm"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "EndDate",
        "targetFieldName" : "EndDate"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "ProductDescription",
        "targetFieldName" : "Description"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "ProductName",
        "targetFieldName" : "CustomProductName"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "SalesPrice",
        "targetFieldName" : "UnitPrice"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "ServiceDate",
        "targetFieldName" : "ServiceDate"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "QuoteLineGroupId",
        "targetFieldName" : "QuoteLineGroupId"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "BillingFrequency",
        "targetFieldName" : "BillingFrequency"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "SpecialInstructions_c",
        "targetFieldName" : "SpecialInstructions__c"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "QuoteLineReference",
        "targetFieldName" : "QuoteLineReference"
      } ]
    }, {
      "name" : "Create_Quote_Line_Item_Relationship",
      "label" : "Create Quote Line Item Relationship",
      "sourceName" : "Filter_Quote_Line_Item_Relationship",
      "targetObjectName" : "QuoteLineRelationship",
      "writebackRecordMaxLimit" : 0,
      "isChangedRow" : false,
      "shouldCreateTargetObject" : false,
      "isExistingDataset" : false,
      "description" : "Creates quote line item relationship records for all the quote line items.",
      "canWrtbckToNonEditableFields" : false,
      "storageType" : "sObject",
      "operationType" : "Insert",
      "writebackSequence" : 2,
      "fields" : [ {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "Relationship_AssociatedQuoteLinePricing",
        "targetFieldName" : "AssociatedQuoteLinePricing"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "Relationship_ProductRelationshipTypeId",
        "targetFieldName" : "ProductRelationshipTypeId"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "Relationship_AssociatedQuantScaleMethod",
        "targetFieldName" : "AssociatedQuantScaleMethod"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "Relationship_ProductRelatedComponent",
        "targetFieldName" : "ProductRelatedComponentId"
      }, {
        "isAutogenerated" : false,
        "parentName" : "QuoteLineItem",
        "relationshipName" : "MainQuoteLine",
        "runtimeParameter" : false,
        "sourceFieldName" : "Relationship_MainQuoteLineId",
        "targetFieldName" : "QuoteLineReference"
      }, {
        "isAutogenerated" : false,
        "parentName" : "QuoteLineItem",
        "relationshipName" : "AssociatedQuoteLine",
        "runtimeParameter" : false,
        "sourceFieldName" : "Relationship_AssociatedQuoteLineId",
        "targetFieldName" : "QuoteLineReference"
      } ]
    }, {
      "name" : "Create_Quote_Line_Attributes",
      "label" : "Create Quote Line Attributes",
      "sourceName" : "Filter_Quote_Line_Attributes",
      "targetObjectName" : "QuoteLineItemAttribute",
      "writebackRecordMaxLimit" : 0,
      "isChangedRow" : false,
      "shouldCreateTargetObject" : false,
      "isExistingDataset" : false,
      "description" : "Creates quote line item attribute records for all the quote line items.",
      "canWrtbckToNonEditableFields" : false,
      "storageType" : "sObject",
      "operationType" : "Insert",
      "writebackSequence" : 2,
      "fields" : [ {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "Attribute_AttributeDefinitionId",
        "targetFieldName" : "AttributeDefinitionId"
      }, {
        "isAutogenerated" : false,
        "parentName" : "QuoteLineItem",
        "relationshipName" : "QuoteLineItem",
        "runtimeParameter" : false,
        "sourceFieldName" : "QuoteLineReference",
        "targetFieldName" : "QuoteLineReference"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "Attribute_AttributeName",
        "targetFieldName" : "AttributeName"
      }, {
        "isAutogenerated" : false,
        "runtimeParameter" : false,
        "sourceFieldName" : "Attribute_AttributePicklistValueId",
        "targetFieldName" : "AttributePicklistValueId"
      } ]
    } ]
  }
}
