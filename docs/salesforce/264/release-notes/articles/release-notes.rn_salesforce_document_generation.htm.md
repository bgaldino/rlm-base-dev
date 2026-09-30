---
article_id: release-notes.rn_salesforce_document_generation.htm
title: Salesforce Document Generation
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_document_generation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_revenue.htm
fetched_at: 2026-09-30
---

# Salesforce Document Generation

Build consistent, accurate documents by using reusable clauses for Salesforce Document Generation. Clauses in the Clause Library support both merge tokens and placeholder tokens. Quote Special Terms support placeholder tokens only. Reference clauses in document templates so templates stay current as clause content changes. Rich text tables now retain their formatting in generated Word documents, including pricing tables, comparison charts, and data summaries.

Populate Clause Content with Merge and Placeholder Tokens
Add tokens to clauses so that account names, payment terms, discount amounts, and other data flow automatically into your contract language. Merge tokens pull data from Salesforce records via Omnistudio Data Mapper or Context Service. Placeholder tokens contain default values like strings, dates, currencies, and percentages.
Eliminate Manual Template Updates When Clause Content Changes
Avoid manual updates when clause language and terms change. Apply clause tokens to a document template to make sure that every generated document uses the current approved content. Then when a clause changes, the generated documents automatically include the updated content.
Generate Documents That Include Tables in Rich Text Fields
Include tabular content, such as pricing tables, comparison charts, or data summaries, in your generated documents. When you copy a static table from an external source into a rich text field, the formatting, structure, and colors persist in the generated Word document. Only static table content is supported. You can’t use dynamic tokens in the table.
