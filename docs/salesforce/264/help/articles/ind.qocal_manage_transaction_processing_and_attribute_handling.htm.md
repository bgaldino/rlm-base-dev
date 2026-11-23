---
article_id: ind.qocal_manage_transaction_processing_and_attribute_handling.htm
title: Set Up Transaction Processing for Complex Product Configurations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_manage_transaction_processing_and_attribute_handling.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_common_capabilities.htm
fetched_at: 2026-11-23
---

# Set Up Transaction Processing for Complex Product Configurations

To handle complex product configurations, increase the number of product attributes that a sales transaction can support. To control performance, you can also specify the number of records processed in a single transaction.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To configure transaction processing and attribute handling:	

Customize Application

AND

View Setup and Configuration

From Setup, in the Quick Find box, enter and then select Revenue Settings.
Turn on Increased Attribute Limits.
The default limit is 3,000 product attributes across all quote lines, but a standard transaction supports up to 10,000 product attributes. To increase the limit, contact Salesforce Customer Support.
IMPORTANT
If you increase the number of supported product attributes and then turn off Increased Attribute Limits, the attribute limit resets to the default value of 3,000. To restore a higher limit, contact Salesforce Customer Support.
If you turn off Increased Attribute Limits after creating quotes or orders that use higher attribute limits, reset the attribute limits before updating existing transactions. Existing quotes or orders can fail if the previous attribute limits are still applied.
To specify the number of records processed in a single transaction, in Revenue Settings, for Records Persisted per Transaction, select either 200 or 500 records.
A higher value can increase the processing load. Before updating this setting, make sure that the associated triggers, flows, and validation rules can handle the increased number of records per transaction within governor limits.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_manage_transaction_processing_and_attribute_handling.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
