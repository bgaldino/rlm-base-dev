---
article_id: ind.qocal_qli_import_considerations_customize_flow.htm
title: Considerations for Customizing the Quote Line Item Import Flow
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_qli_import_considerations_customize_flow.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Considerations for Customizing the Quote Line Item Import Flow

When users select import lines, Transaction Management uses a flow to provide options for downloading a CSV template and uploading a CSV file for processing. Review these requirements and limits to customize the import flow effectively.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Custom Template Configuration

To use a static resource for a custom CSV template, modify the ComponentUploadCsvForProcessing component within the Import Quote Line Items page element.

Set the Use Static Resource for CSV File Template attribute to True.
Enter the name of the static resource in the Downloadable CSV Template Name attribute.
Clone and modify the flow to change the CSV template or other processing behaviors.
Import Limits and Variables

The flow manages specific data limits and requires certain input variables to function with Transaction Management.

Use the rowsImportLimit variable to set the maximum number of rows for a single import.
Users import up to 1000 quote line items together, even if the rowsImportLimit variable value exceeds 1000.
Users perform multiple imports until they reach the quote line item limit per quote.
The flow includes the quoteId and dataProcessingEngineDefinitionId input variables.
Transaction Management automatically passes values for these variables to the flow when a user clicks Import Quote Line Items.

After creating a custom flow, go to the Flow for Importing Quote Line Items field and select your new flow.

SEE ALSO
Automate Tasks with Flows
Transaction Management Limits
