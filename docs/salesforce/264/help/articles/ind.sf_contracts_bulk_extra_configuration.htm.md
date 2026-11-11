---
article_id: ind.sf_contracts_bulk_extra_configuration.htm
title: Create a Bulk Extraction Configuration
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_bulk_extra_configuration.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_bulk_extra_overview.htm
fetched_at: 2026-10-13
---

# Create a Bulk Extraction Configuration

Define which documents to process in your connected external repository, the data to extract, and where to store the results.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To create a bulk extraction configuration:	

CLM Admin User

AND

Contracts AI User

AND

Data Cloud Architect

Before you begin, make sure that you have an extraction template that defines the fields and clauses to extract. See Create a Contract Extraction Template for Extraction. For extraction context, you can use the standard ContractsExtractionContext mapping unless you require a cloned or custom context definition. See Use Context Definitions to Extract Contract Details. Build and save the template; test in preview before high-volume bulk runs.

From Setup, in the Quick Find box, enter Contracts AI, and then select Contract Extraction.
Click New Configuration.
Name the configuration, and click Next.
Select the data space and the UDMO that contains the source documents. Click Next.
For the file type to extract data from, select PDF, and click Next.
The system only processes documents that match the selected file type.
Select the contract extraction template that defines which fields and clauses to extract, and click Next.

If you don’t have a template, see Create a Contract Extraction Template for Extraction. The template you saved defines which fields and clauses to extract. This step only selects which template to use for this bulk job. The record type field populates automatically based on the selected template.

Select the document extraction LLM model to use for processing documents, and click Next.

If the extraction template that you selected has a predefined LLM model, you can’t change it. To use a different model, select a different template or update the template.

Enter a name for the DLO.
If your extraction template includes clause extraction, enter a name for the Clause DLO.
Save your changes.
After completing the configuration, the status changes to Submitted. Document AI starts processing documents asynchronously in batches. The extraction results appear in Contract Extraction Results.
