---
article_id: ind.product_catalog_data_import_by_using_csv_files.htm
title: Data Import Through CSV Files in Product Catalog Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_data_import_by_using_csv_files.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_products.htm
fetched_at: 2026-09-04
---

# Data Import Through CSV Files in Product Catalog Management

Catalog admins and product designers can create records by importing CSV files into Product Catalog Management.

REQUIRED EDITIONS
View supported products and editions.

Summary of Steps

Clone the predefined Data Processing Engine templates that map column headers in CSV files to the object fields.
Allow the import of custom fields, customize the Data Processing Engine definitions. Catalog admins and product designers can download the predefined CSV templates, add columns for custom fields, and add data to the CSV template.
After the CSV file is ready, import the file to Product Catalog Management by using the definitions.
Set Up Data Processing Engine Definitions for Product Catalog Management

Product Catalog Management provides data processing engine definition templates that map columns in the CSV file templates to various Product Catalog Management objects. Use the templates to create data processing engine definitions. Import data to custom fields by customizing the data processing engine definitions to map the custom fields to the object fields.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To manage Data Processing Engine definitions:	
Customize Application
Modify All Data
Advanced CSV Data Import permission set

Before you begin:

Make sure that your org supports CSV import feature from Product Catalog Management.
Turn on Data Cloud.
To import data to custom fields, create custom fields on the objects. See Create Custom Fields.
To set up data cloud in sandbox, see Data Cloud in a Sandbox

To set up Data Processing Engine definitions, follow these instructions:

From Setup, in the Quick Find box, enter Data Processing Engine and select it.
Click the data process engine definition template that you want to use.
From the Save dropdown, select Save as.
Select Standard as the process type.
Save your changes.
To import custom fields:
In the Data Source node, add the column headers for custom fields as source fields.
See Use a CSV File as a Data Source.
NOTE The column header name can’t exceed 35 characters.
In each Writeback Object node, map the column headers from the CSV file to the custom fields of the object.
See Writeback Objects.
Save your changes.
Activate the Data Processing Engine definition.
Use CSV Files to Import Data in Product Catalog Management

Catalog admins and product designers can easily create records by importing data to Product Catalog Management by using CSV files and data processing engine definitions.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To download CSV templates:	Advanced CSV Data Import permission set
To upload CSV files:	Advanced CSV Data Import permission set
From the Product Catalog Management app’s home page, click Download CSV Templates, and then download the necessary template.
To import data into custom fields, add the field names used in the data source element of the data processing engine definition as the column headers.
Add data to the CSV template.
From the Product Catalog Management app’s home page, click Import Data.
The CSV File Import page appears. If you encounter an error on clicking Import Data, then the CSV File Import tab is likely hidden. Contact your Salesforce Admin to adjust the tab's visibility settings. See Make the CSV File Import Option Visible in Existing Orgs
From the Import dropdown, select Import using DPE Template.
Upload the CSV file, select the corresponding data processing engine definition, and then click Start Import.
NOTE  A Data Processing Engine definition processes data from each row. If a CSV file contains multiple objects with varying record counts, empty cells are sent to the Writeback Object node, and result in errors.
 If a CSV file has 30 product qualification records and 20 product disqualification records, then empty values are sent to the Product Disqualification Writeback Object node 10 times, and 10 errors are written to the failure log.
The import process begins. After the import process is complete, a log is generated and appears on the CSV File Import page.
