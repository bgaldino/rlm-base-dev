---
page_id: deployment_salesforce_pricing_metadata.htm
title: Salesforce Pricing Metadata
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_salesforce_pricing_metadata.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_B.htm
fetched_at: 2026-06-09
---

# Salesforce Pricing Metadata

This table provides the metadata deployment reference for Salesforce Pricing in Revenue
Cloud, including setup paths and configuration details.

| Type | Label | Setup Path | Details |
| --- | --- | --- | --- |
| Setup | Context Service | Context Service > Context Service Settings | Enable. This is a prerequisite to Salesforce Pricing settings. |
| Setup | Salesforce Pricing Settings | Setup > Salesforce Pricing > Salesforce Pricing Settings | Enable |
| Setup | Pricing Recipes | Setup > Salesforce Pricing > Pricing Recipes |  |
| Setup | Salesforce Pricing Setup | Setup > Salesforce Pricing > Salesforce Pricing Setup |  |
| Field | Select a Pricing Recipe | Setup > Salesforce Pricing > Salesforce Pricing Setup |  |
| Field | Select a Pricing Procedure | Setup > Salesforce Pricing > Salesforce Pricing Setup |  |
| Flag | Sync Pricing Data | Setup > Salesforce Pricing > Salesforce Pricing Setup | Decision tables are refreshed. |
| Flag | Activate Price Waterfall for API Responses | Setup > Salesforce Pricing > Salesforce Pricing Setup |  |
| Flag | Turn On Price Waterfall Persistence | Setup > Salesforce Pricing > Salesforce Pricing Setup |  |
| Field | Price Tracking History | Setup > Salesforce Pricing > Salesforce Pricing Setup | Includes two fields of type flag. 1. Enable Maximum Price 2. Enable Minimum Price |
| Field | Proration Settings | Setup > Salesforce Pricing > Salesforce Pricing Setup | Includes two fields of type field. 1. Evergreen 2. One Time |
| Flag | Turn On Price Logs Capture | Setup > Salesforce Pricing > Salesforce Pricing Setup |  |
| Flag | Turn on Parallel Execution | Setup > Salesforce Pricing > Salesforce Pricing Setup |  |
| Setup | Procedure Plan Definition | Procedure Plan Setup > Procedure Plan Definitions | For Procedure Plan definitions, if Apex is selected, the Apex class must be migrated. Packaging isn't supported in Winter' 26. See [Customize Your Procedure Plans With Apex Hooks](https://help.salesforce.com/s/articleView?id=ind.pricing_customize_pricing_procedures_with_apex_hooks.htm&language=en_US "HTML (New Window)"). |
| Permission Sets | Salesforce Pricing Admin | Setup > Users > Permission Sets |  |
| Permission Sets | Salesforce Pricing Design Time User | Setup > Users > Permission Sets |  |
| Permission Sets | Salesforce Pricing Manager | Setup > Users > Permission Sets |  |
| Permission Sets | Salesforce Pricing Run Time User | Setup > Users > Permission Sets |  |
| Decision Table Definition | Asset Action Source Entries | Setup > Decision Table |  |
| Decision Table Definition | Asset Action Source Entries V2 | Setup > Decision Table |  |
| Decision Table Definition | Attribute Discount Entries | Setup > Decision Table |  |
| Decision Table Definition | Bundle Based Adjustment Entries | Setup > Decision Table |  |
| Decision Table Definition | Contract Pricing Adjustment Tiers | Setup > Decision Table |  |
| Decision Table Definition | Contract Pricing Entries | Setup > Decision Table |  |
| Decision Table Definition | Contract Pricing Volume Tiers | Setup > Decision Table |  |
| Decision Table Definition | Contract Pricing Volume Tiers V2 | Setup > Decision Table |  |
| Decision Table Definition | Derived Pricing Entries | Setup > Decision Table |  |
| Decision Table Definition | Index Rate | Setup > Decision Table |  |
| Decision Table Definition | Price Book Entries | Setup > Decision Table |  |
| Decision Table Definition | Price Book Entries V2 | Setup > Decision Table |  |
| Decision Table Definition | Pricebook Rate Card Entries | Setup > Decision Table |  |
| Decision Table Definition | Product Price Range Entries | Setup > Decision Table |  |
| Decision Table Definition | Product Price Range Entries V2 | Setup > Decision Table |  |
| Decision Table Definition | Tiered Adjustment Entries | Setup > Decision Table |  |
| Decision Table Definition | Volume Discount Entries | Setup > Decision Table |  |
