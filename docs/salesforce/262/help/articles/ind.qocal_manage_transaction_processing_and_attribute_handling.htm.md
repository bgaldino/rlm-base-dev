---
article_id: ind.qocal_manage_transaction_processing_and_attribute_handling.htm
title: Set Up Transaction Processing for Complex Product Configurations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_manage_transaction_processing_and_attribute_handling.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Set Up Transaction Processing for Complex Product Configurations

To handle complex product configurations, increase the number of product attributes that a sales transaction can support. To control performance, you can also specify the number of records processed in a single transaction.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management where Transaction Management is enabled
USER PERMISSIONS NEEDED
To configure transaction processing and attribute handling:	

Customize Application

AND

View Setup and Configuration

From Setup, in the Quick Find box, enter and then select Revenue Settings.
Turn on Increased Attribute Limits.
The default limit is 3,000 product attributes across all quote lines, but a standard transaction supports up to 10,000 product attributes. To increase the limit, contact Salesforce Customer Support.
IMPORTANT If you increase the number of supported product attributes and then turn off Increased Attribute Limits, the attribute limit resets to the default value of 3,000. To restore a higher limit, contact Salesforce Customer Support.
To specify the number of records processed in a single transaction, in Revenue Settings, for Records Persisted per Transaction, select either 200 or 500 records.
A higher value can increase the processing load. Before updating this setting, make sure that the associated triggers, flows, and validation rules can handle the increased number of records per transaction within governor limits.
