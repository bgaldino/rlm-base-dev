---
article_id: release-notes.rn_billing_extend_tax_engine.htm
title: Extend the Revenue Standard Tax Engine to Match Your Tax Rules
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_extend_tax_engine.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing_tax_management.htm
fetched_at: 2026-09-30
---

# Extend the Revenue Standard Tax Engine to Match Your Tax Rules

Apply tax rates based on custom attributes, such as product category, customer attributes, or exemption criteria, without writing Apex code. Extend the Revenue Standard Tax Entries decision table with custom input and output fields, and automatically populate invoice tax line and credit memo tax line fields with matched values.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Advanced or Revenue Cloud Billing license.

Who: To create a custom metadata type and custom fields, you need the Tax Admin permission set. To change the decision table, you need the Rule Engine Designer permission set.

How: Create custom fields on tax rate, and then create a custom metadata type that maps billing transaction fields to decision table inputs. Clone the Revenue Standard Tax Entries decision table, and add custom input or output columns from tax rate. Then associate the decision table and custom metadata type with your Tax Engine record where the type is set to Revenue Standard Tax Engine.

SEE ALSO
Salesforce Help: Configure Tax Rates
