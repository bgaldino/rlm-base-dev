---
article_id: ind.sf_contracts_datatrueup_overview.htm
title: Keep Data in Sync by Using Data True-Up
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_datatrueup_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_documnet_actions_overview.htm
fetched_at: 2026-10-13
---

# Keep Data in Sync by Using Data True-Up

Use Data True-Up to keep contract documents and Salesforce records aligned. View token values from both sources, identify differences, and update either the document or the record without losing redlines. This bi-directional sync maintains accuracy throughout the contract lifecycle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
What Is Data True-Up

Data True-Up compares field-level token values between a contract document and the corresponding field in the associated Salesforce record. From the Microsoft 365 Word add-in, you can resolve mismatches by updating the document or the record field to keep data consistent.

Why Use It

Keep token values aligned between contract documents and Salesforce records, whether changes are made in the document or in Salesforce. You can pull updated field values or write back edits without losing formatting or redlines.

Data True-Up simplifies contract management and improves accuracy by:

Preserving document formatting and redlines.
Reducing manual errors and compliance risks.
Reducing time spent on data validation and reconciliation.
Keeping documents and records synced across all stages of negotiation.
How It Works

When you open a contract document in the Microsoft 365 Word add-in and initiate the Data True-Up process, the system scans the entire document. It identifies all types of content, including clauses, sections, and token values. After the scan, you can:

Pull the latest token values from the Salesforce record fields.
Compare each Data True-Up token value with its corresponding Salesforce record value in a side-by-side view.
Document value: The value currently present in the contract document.
Record value: The corresponding value, which is stored in the Salesforce record.
Check the sync status for each token to understand whether the values match, differ, or couldn’t be retrieved. The status appears as In Sync, Out of Sync, or Fetch Failed.
If necessary, modify document values, and then push updated document token values to Salesforce record fields.
Data True-Up Actions and Statuses
Understand the status indicators and available actions in the Data True-Up panel. Learn how each status reflects the state of your token data and what each button does during the Data True-up sync process.
Data True-Up Tokens in Document Templates
Use Data True-Up tokens in DOCX templates to enable two-way syncing between document content and Salesforce record field values.
Supported Data Type Fields for Data True-Up
Review the supported data types for use with Data True-Up tokens. It includes compatibility, descriptions, and any known issues or considerations.
Enable Data True-Up
Turn on the Data True-Up feature in Setup to allow document and record sync, and provide Field-Level Security (FLS) access to specific fields.
Compare and Sync Token Values in a Document
View the data true-up token values from the document and the Salesforce record side by side, and decide if the values need to be updated to ensure data accuracy.
Use Cases for Data True-Up
Explore common contract lifecycle scenarios where Data True-Up (DT) helps you maintain consistency between the document values and Salesforce record fields. Preserve redlines, minimize manual effort, and make sure that data stays aligned across teams and systems.
Limitations for Data True-Up
Review the limitations for Data True-Up token naming, template formats, supported features, and editing capabilities before configuring your templates. These restrictions affect token behavior, record updates, and template compatibility.
How to Keep Contract Line Items in Sync with Data True-Up
Data True-Up syncs line item details between a generated document and a Sales Contract Line Item record and its related records. Context Service document templates support Data True-Up line-item tokens.
Nested and Related Record Tokens in Data True-Up
If you have nested object references and lookup fields, you can pull data from the contract record and related objects, such as accounts, opportunities, quotes, and custom lookup records. Context Service document templates support Data True-Up nested tokens.
