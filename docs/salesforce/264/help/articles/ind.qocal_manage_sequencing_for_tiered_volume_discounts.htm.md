---
article_id: ind.qocal_manage_sequencing_for_tiered_volume_discounts.htm
title: Configure Line Item Sequencing for Tiered Volume Discounts
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_manage_sequencing_for_tiered_volume_discounts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_contract_features.htm
fetched_at: 2026-09-04
---

# Configure Line Item Sequencing for Tiered Volume Discounts

Define a sequencing field to control the order in which the system applies tiered or volume contractual discounts to sales transactions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To configure the Cumulative Quantity Pricing Sort Order Tag Configuration setting:	Customize Application

By default, the system sequences line items by quantity when applying tiered volume discounts, but you can override this behavior by setting a field in the Cumulative Quantity Pricing Sort Order Tag Configuration setting. To manage sequencing and apply discounts in sequence, your sales reps enter a sequence number in the configured field for each line item within the transaction.

Map the field that you want to use for sequencing to a custom context tag in your custom sales transaction context definition. See Context Definitions.

From Setup, in the Quick Find box, search for and select Revenue Settings.
For the Cumulative Quantity Pricing Sort Order Tag Configuration setting, enter the context tag of your field.
Save your changes.
