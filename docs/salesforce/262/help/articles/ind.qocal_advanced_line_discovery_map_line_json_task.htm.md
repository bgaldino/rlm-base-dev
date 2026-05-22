---
article_id: ind.qocal_advanced_line_discovery_map_line_json_task.htm
title: Add Context Tag Mappings to the Discovery Procedure Map Line Item Element Using JSON
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_advanced_line_discovery_map_line_json_task.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Add Context Tag Mappings to the Discovery Procedure Map Line Item Element Using JSON

To configure a discovery procedure to use advanced detail line pricing with derived-pricing products, copy and paste the map line item for derived pricing JSON to a discovery procedure in Revenue Pricing.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To set up and use advanced detail line pricing:	

Salesforce admin

AND

Pricing Design Time User permission set

From the App Launcher, find and select Discovery Procedures, and then select a discovery procedure to update.
Add two new elements to the discovery procedure to price derived products: Discovery Settings and Map Line Item.
Add the context tag mappings to the map line item using this JSON.
{"componentName":"Map Line Item","businessKnowledgeModelName":"BreakdownLineMapping","usageType":"PricingDiscovery","elementAttributes":null,"parameters":null,"inputVariablesMappingText":{"section-0-input1":"LineItem","section-1-input1":"EffectiveFrom","section-2-input1":"EffectiveTo","section-3-input1":"DerivedPricingAttribute","section-0-output":"SalesTrxnItemDetailSource","section-1-output":"ItemDetailEffectiveFrom__std","section-2-output":"ItemDetailEffectiveTo__std","section-3-output":"ItemDetailDerivedPricingAttribute__std","sectionCount":"4","sectionJsonString1":"{\"whereConditions\":[{\"field\":{\"dataType\":\"Text\",\"name\":\"section-0-input1\",\"value\":\"LineItem\",\"allowCompatibleDataTypes\":true},\"value\":{\"dataType\":\"Text\",\"name\":\"section-0-output\",\"value\":\"SalesTrxnItemDetailSource\",\"allowCompatibleDataTypes\":true}}]}","sectionJsonString2":"{\"whereConditions\":[{\"field\":{\"dataType\":\"DateTime\",\"name\":\"section-1-input1\",\"value\":\"EffectiveFrom\",\"allowCompatibleDataTypes\":true},\"value\":{\"dataType\":\"DateTime\",\"name\":\"section-1-output\",\"value\":\"ItemDetailEffectiveFrom__std\",\"allowCompatibleDataTypes\":true}}]}","sectionJsonString3":"{\"whereConditions\":[{\"field\":{\"dataType\":\"DateTime\",\"name\":\"section-2-input1\",\"value\":\"EffectiveTo\",\"allowCompatibleDataTypes\":true},\"value\":{\"dataType\":\"DateTime\",\"name\":\"section-2-output\",\"value\":\"ItemDetailEffectiveTo__std\",\"allowCompatibleDataTypes\":true}}]}","sectionJsonString4":"{\"whereConditions\":[{\"field\":{\"dataType\":\"Boolean\",\"name\":\"section-3-input1\",\"value\":\"DerivedPricingAttribute\",\"allowCompatibleDataTypes\":true},\"value\":{\"dataType\":\"Boolean\",\"name\":\"section-3-output\",\"value\":\"ItemDetailDerivedPricingAttribute__std\",\"allowCompatibleDataTypes\":true}}]}"},"outputVariablesMappingText":{}}
Save your changes.
