---
article_id: release-notes.rn_transaction_management_prevent_cross_industry_pricing_errors_with_subtype.htm
title: Limit a Procedure Plan to a Specific Industry
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_transaction_management_prevent_cross_industry_pricing_errors_with_subtype.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_transaction_management.htm
fetched_at: 2026-09-30
---

# Limit a Procedure Plan to a Specific Industry

Prevent pricing errors when you have multiple industries in a single org by defining which industry or vertical the procedure plan applies to. Use the new Subtype field to make sure that your plan shows only the pricing procedures matching the specific subtype. Then, when you configure a Life Sciences or Commerce procedure plan, you can add only pricing procedures intended for the selected industry or vertical.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

How: When you create a procedure plan definition, from the Subtype dropdown list, select the industry or vertical use case.

The Subtype field applies only to Revenue Cloud, with a process type value of Default.

SEE ALSO
Salesforce Help: Create a Custom Procedure Plan Definition
