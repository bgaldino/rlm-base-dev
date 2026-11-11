---
article_id: ind.sf_contracts_bulk_extra_overview.htm
title: Bulk Extraction with Contracts AI
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_bulk_extra_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_set_up_contracts_ai.htm
fetched_at: 2026-10-13
---

# Bulk Extraction with Contracts AI

Process documents directly from external repositories without uploading each file individually. Use Data Cloud and Document AI to extract large volumes of contract data and convert unstructured data into structured records. Create templates to define which contract fields and clauses to extract.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions

Documents stored in sources such as SharePoint, Amazon S3, or Google Cloud Storage are brought into an Unstructured Data Model Object (UDMO), which acts as the source for extraction. Extraction runs asynchronously. After you create and submit a configuration, Document AI processes documents in batches and writes extracted data to output Data Lake Objects (DLOs).

Key Capabilities
Extract fields and clauses from many contracts in bulk.
Process documents directly from external repositories without uploading each file individually.
Use extraction templates to define what data to extract, such as contract fields and clauses.
Automatically generate structured records for downstream contract creation.
Assign extracted results to business users for review and processing.
Set Up Bulk Contract Extraction
Bulk contract extraction uses Einstein Generative AI, Document AI, and Data Cloud.
Connect an External Repository for Bulk Contract Extraction
Connect an external document repository to Data Cloud so that bulk extraction can access your contract files without uploading them to Salesforce storage.
Create a Bulk Extraction Configuration
Define which documents to process in your connected external repository, the data to extract, and where to store the results.
Verify Bulk Extraction Results and Create a Contract Record
Before creating contract records, validate the extracted data, such as contract details and clauses.
Change Ownership of Bulk Extraction Results
As a Salesforce admin managing extractions for a team, assign extraction results to the appropriate users for review and contract creation by changing ownership.
Delete a Bulk Extraction Configuration
To delete a bulk extraction configuration, you must first delete all associated contract extraction results. Deleting a configuration doesn’t remove previously generated extraction results.
Considerations for Bulk Extraction
Understand the limits, permissions, and supported configurations for bulk extraction.
SEE ALSO
Compare Bulk and Single Document Extraction
Considerations for Bulk Extraction
