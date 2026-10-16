---
article_id: release-notes.rn_salesforce_document_generation_clause_tokens_runtime_resolution.htm
title: Eliminate Manual Template Updates When Clause Content Changes
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_document_generation_clause_tokens_runtime_resolution.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_salesforce_document_generation.htm
fetched_at: 2026-09-30
---

# Eliminate Manual Template Updates When Clause Content Changes

Avoid manual updates when clause language and terms change. Apply clause tokens to a document template to make sure that every generated document uses the current approved content. Then when a clause changes, the generated documents automatically include the updated content.

Where: This change applies to Lightning Experience in Enterprise, Performance, Unlimited, and Developer editions of Agentforce Revenue Management, formerly Revenue Cloud, with the Revenue Events Starter Pack license, and the Revenue Cloud Advanced or Revenue Cloud Billing license.

Who:DocGen Designer with Clause Management Permissions.

How: Copy the clause template version identifier or latest clause template identifier into your document template where you want the clause to appear. When you generate a document, clause tokens resolve at run time.
