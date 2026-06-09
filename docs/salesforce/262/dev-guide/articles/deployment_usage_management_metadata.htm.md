---
page_id: deployment_usage_management_metadata.htm
title: Usage Management Metadata
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_usage_management_metadata.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_B.htm
fetched_at: 2026-06-09
---

# Usage Management Metadata

This table provides the metadata deployment reference for Usage Management in Revenue
Cloud, including setup paths and configuration details.

| Type | Label | Setup Path | Details |
| --- | --- | --- | --- |
| Setup | Context Service | Context Service > Context Service Settings | Enable |
| Setup | Rate Management | Setup > Usage Management > Usage Management Settings | Enable Rate Management. |
| Setup | Rating Setup | Setup > Usage Management > Rate Management Setup | Rating Waterfall -> Enable / Disable based on preference. Rating Waterfall Persistence -> Enable / Disable based on preference. |
| Permission Sets | Rate Management: Admin | Setup > Users > Permission Sets |  |
| Permission Sets | Rate Management: Design Time User | Setup > Users > Permission Sets |  |
| Permission Sets | Rate Management: Manager | Setup > Users > Permission Sets |  |
| Permission Sets | Rate Management Run Time User | Setup > Users > Permission Sets |  |
| Decision Table Definition | Binding Object Rate Adjustment Resolution Entries | Setup > Decision Tables |  |
| Decision Table Definition | Binding Object Rate Card Entry Resolution Entries | Setup > Decision Tables |  |
| Decision Table Definition | Rate Card Entry Resolution Entries 2 | Setup > Decision Tables |  |
| Decision Table Definition | Rate Adjustment by Attribute Resolution Entries | Setup > Decision Tables |  |
| Decision Table Definition | Rate Adjustment by Tier Resolution Entries | Setup > Decision Tables |  |
| Decision Table Definition | Pricebook Rate Card Entries | Setup > Decision Tables |  |
| Decision Table Definition | Binding Object Volume-based Rate Adjustment | Setup > Decision Tables |  |
| Decision Table Definition | Binding Object Rate | Setup > Decision Tables |  |
| Decision Table Definition | Binding Object Tier-based Rate Adjustment | Setup > Decision Tables |  |
| Decision Table Definition | Binding Object Rate Card Entry | Setup > Decision Tables |  |
| Decision Table Definition | Asset Volume-based Rate Adjustment | Setup > Decision Tables |  |
| Decision Table Definition | Asset Rate | Setup > Decision Tables |  |
| Decision Table Definition | Asset Rate Card Entry | Setup > Decision Tables |  |
| Decision Table Definition | Asset Tier-based Rate Adjustment | Setup > Decision Tables |  |
| Decision Table Definition | Attribute-based Rate Adjustment by Rate Card Entry ID | Setup > Decision Tables |  |
| Decision Table Definition | Volume-based Rate Adjustment by Rate Card Entry ID | Setup > Decision Tables |  |
| Decision Table Definition | Tier-based Rate Adjustment by Rate Card Entry ID | Setup > Decision Tables |  |
| Decision Table Definition | Rate Adjustment by Attribute Entries 2 | Setup > Decision Tables |  |
| Decision Table Definition | Rate Adjustment by Tier Entries 2 | Setup > Decision Tables |  |
| Decision Table Definition | Rate Adjustment by Volume Entries 2 | Setup > Decision Tables |  |
| Decision Table Definition | Rate Card Entries 2 | Setup > Decision Tables |  |
| Flow | Call Rating Service | Setup > Flows |  |
| Flow | Call Entitlement Refresh Service | Setup > Flows |  |
| Flow | Create Summary | Setup > Flows |  |
| Flow | Generate Liable Summary | Setup > Flows |  |
| Flow | Generate Usage Rateable Summary | Setup > Flows |  |
| Flow | Generate Usage Summary | Setup > Flows |  |
| Flow | Orchestrate Usage Management | Setup > Flows |  |
| Data Processing Engine | Create Liable Summary Template | Setup > Data Processing Engine |  |
| Data Processing Engine | Create Usage Summary Template | Setup > Data Processing Engine |  |
