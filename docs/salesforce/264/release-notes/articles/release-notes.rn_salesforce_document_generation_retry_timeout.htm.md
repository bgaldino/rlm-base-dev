---
article_id: release-notes.rn_salesforce_document_generation_retry_timeout.htm
title: Handle Document Generation Timeouts with Configurable Retry
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_document_generation_retry_timeout.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_salesforce_document_generation.htm
fetched_at: 2026-11-23
---

# Handle Document Generation Timeouts with Configurable Retry

When document generation takes longer than expected, users can retry the request from Omniscript or the Generate Document experience instead of starting over. Admins can set a custom timeout on the generate-and-preview Lightning web component so users see a retry option within a predictable window.

Where: This change applies to Lightning Experience in Enterprise, Performance, and Unlimited editions with Salesforce Document Generation.

Who: To use document generation in Omniscript, you need the Omnistudio Admin or Omnistudio User permission set with DocGen Designer or DocGen User, or the DocGen Runtime Community User permission. The Generate Document component doesn't require an Omnistudio license.

How: To configure the timeout, set the retry-timeout property on the osGenerateAndPreviewDocument Lightning web component in the GenerateDocument step of your Omniscript and screenflow. Enter a value in milliseconds from 15,000 through 180,000; Omniscript adjusts out-of-range values to the nearest supported limit. If you don't set a value, Omniscript uses the default polling limit of about 3 minutes. When generation exceeds the timeout, users can select Retry up to 3 times, and each retry starts a new document generation request. The same timeout and retry behavior applies in Screen Flow and on Lightning record pages.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_document_generation_retry_timeout.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
