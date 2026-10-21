---
article_id: ind.sf_contracts_embed_salesforce_contracts_analytics_dashboards.htm
title: Salesforce Contracts Analytics Dashboard Attributes
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_embed_salesforce_contracts_analytics_dashboards.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_salesforce_contracts_analytics_post-installation_steps.htm
fetched_at: 2026-10-13
---

# Salesforce Contracts Analytics Dashboard Attributes

Salesforce Contracts Analytics includes dashboards that you can embed and access in Lightning Experience pages.

For more general instructions on embedding CRM Analytics dashboards to lightning pages, see Embed Dashboards in Lightning Pages.

Refer to the table to know more about dashboard-specific attributes.

NOTE Auto-embedding is limited to the Salesforce Contracts console app. The Salesforce console includes pre-configured embedded analytics components that become available after the required licenses are provisioned
DASHBOARD	DASHBOARD API	IS AUTO EMBEDDED?	FILTER STRING FOR MANUAL ADDITION
Contract Admin	Contract_Admin	Yes	not applicable
Sales Operation	Sales_Operation	Yes	not applicable
Contract Stage Insights	Contract_Stage_Insights	Yes	{"datasets":{"CLM_ContractHistory":[{"fields":["Contract.Id"],"filter":{"operator":"in","values":["$Id"]},"locked":null,"hidden":null}]}}
Contract Line Items Embedded	Contract_Line_Items_Embedded	Yes	{"datasets":{"CLM_Sales_Contract_Line":[{"fields":["Contract.Id"],"filter":{"operator":"in","values":["$Id"]},"locked":null,"hidden":null}]}}
Contracts Account Embedded	Contracts_Account_Embedded	No	{"datasets":{"CLM_Sales_Contract_Line":[{"fields":["Contract.Account.Id"],"filter":{"operator":"in","values":["$Id"]},"locked":null,"hidden":null}],"CLM_Contract":[{"fields":["AccountId"],"filter":{"operator":"in","values":["$Id"]},"locked":null,"hidden":null}]}}
Contracts Quote Embedded	Contracts_Quote_Embedded	No	{"datasets":{"CLM_Sales_Contract_Line":[{"fields":["Contract.SourceQuoteId"],"filter":{"operator":"in","values":["$Id"]},"locked":null,"hidden":null}]}}
B2B Sales Home Embedded	B2B_Sales_Home_Embedded	No	not applicable
Records That Need My Attention	Records_That_Need_My_Attention	Yes	not applicable
Records That Need My Attention Sales	Records_That_Need_My_Attention_Sales	Yes	not applicable
