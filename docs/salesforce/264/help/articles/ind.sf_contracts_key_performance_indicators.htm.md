---
article_id: ind.sf_contracts_key_performance_indicators.htm
title: Key Performance Indicators in Salesforce Contracts Analytics
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_key_performance_indicators.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_salesforce_contracts_analytics_dashboards.htm
fetched_at: 2026-10-13
---

# Key Performance Indicators in Salesforce Contracts Analytics

Learn the definitions and calculations of key metrics shown in Salesforce Contracts Analytics.

This table lists the key metrics and their calculations.

METRICS	DESCRIPTION	CALCULATIONS	DASHBOARD NAME


#Total Contracts Initiated

	Number of contracts created in a selected duration.	Number of all contract records created in the selected duration.	Contract Admin, Sales Admin
#Contracts Canceled or Expired	Number of contracts canceled or expired in a selected duration.	Number of all Contracts where the status is "Contract Expired" or "Canceled".	Contract Admin
%Cancellation or Expired	Percentage of contracts canceled or expired in a selected duration.	(Number of Contracts Canceled or Expired / Total Contracts Initiated) * 100	Contract Admin
Average Completion Time	Average time to complete a contract.	

Average completion time of contracts where the status is Activated, Contracts Expired, Contract Terminated or Canceled.

For the contracts in Activated, Contract Expired, or Contract Terminated status, the end date is the activated date of the contract. For the contracts in Canceled status, the end date is the date the contract was last modified.

Start Date is the Created By date

Completion Time = End Date - Start Date

	Contract Admin
Total Active Contract Revenue	Revenue from all the contracts in the active status.	Total price of all sales contract lines where the contract status is Active.	Sales Admin
Total Draft Contract Revenue	Revenue from all the contracts in the draft status.	Total price of all sales contract lines where the contract status is Draft.	Sales Admin
Total Expired/Canceled Contract Revenue	Revenue from all the contracts in the expired or canceled status.	Total price of all sales contract lines where the contract status is Expired or Canceled.	Sales Admin
