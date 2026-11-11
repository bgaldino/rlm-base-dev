---
article_id: ind.sf_contracts_datatrueup_usecases.htm
title: Use Cases for Data True-Up
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_datatrueup_usecases.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_datatrueup_overview.htm
fetched_at: 2026-10-13
---

# Use Cases for Data True-Up

Explore common contract lifecycle scenarios where Data True-Up (DT) helps you maintain consistency between the document values and Salesforce record fields. Preserve redlines, minimize manual effort, and make sure that data stays aligned across teams and systems.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USE CASE	DESCRIPTION
Redline Preservation	

During negotiation, legal teams often redline contract documents directly in Microsoft Word. While making tracked edits, they update field values such as pricing terms, contract duration, or service start dates. For example, a lawyer updates the start date from August 1 to August 15 directly in the document.

With Data True-Up, review each affected token, compare it with the corresponding Salesforce field, and decide whether to update the document or the record. This process preserves redlines, so you keep the previous value for reference while ensuring the record stays accurate.


Syncing finance data during internal review	

When a contract record in Salesforce is linked to an external system, finance-related fields such as payment schedules or revenue recognition dates can change automatically. During an internal review, the legal team updates other terms directly in the document.

With Data True-Up, pull the latest finance data from Salesforce into the document before finalizing it. Ensuring that the document reflects the most current financial information without losing the legal team’s edits.


Adjust pricing after proposal revisions	

When a sales team revises a contract proposal based on customer feedback, the account executive updates pricing. For example, the account executive increases the consulting rate from $150 to $175 per hour. The account executive also adjusts hours from 200 to 220 directly in the line-item table after the document generation.

With Data True-Up configured to use DT_ prefixed line-item repeating tokens, run True-Up to compare the document’s line-item values with the Salesforce record. Confirm whether to overwrite the Salesforce line-item fields with the updated document values or update the document from Salesforce. Running Data True-Up in this scenario helps make sure that pricing adjustments and quantity changes remain consistent between the contract document and Salesforce records. Thus, reducing the manual reconciliation work and improves accuracy for billing and forecast reporting.


Keep related record information current in contracts	

Contract documents often include fields that originate from objects related to the contract, such as quote or opportunity, which changes independently of contract fields. For example, in manufacturing after negotiation with a customer, a sales coordinator updates the quote to reflect a revised delivery schedule. The coordinator also updates pricing for parts after the contract document generation.

With Data True-Up tokens that use the DT_ prefix and nested references to related objects, you can run Data True-Up to fetch updated related object field values from Salesforce and sync them into the contract document. Ensuring that the quote details such as delivery dates and pricing remain current in the contract document after negotiation. Keeping these related field values in sync reduces discrepancies between document content and Salesforce data and supports consistent planning and execution.
