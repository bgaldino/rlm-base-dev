---
article_id: ind.qocal_example_extract_product_mentions.htm
title: "Example: Extract Products from Opportunity Descriptions"
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_example_extract_product_mentions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_extract_product_mentions.htm
fetched_at: 2026-09-04
---

# Example: Extract Products from Opportunity Descriptions

The sales team at QuantumBit wants to streamline quote creation because critical product and pricing discussions often remain buried within the unstructured text of opportunity description fields. To resolve this issue, the Transaction Management Salesforce admin uses the Extract Product Mentions prompt template to automate the identification of these key details. By creating a custom Flex prompt template and deploying it as an agent action, the Salesforce admin enables sales reps to extract product names, quantities, and attributes directly from the opportunity description to expedite the quoting process.

Follow this example to create a Flex template that extracts details from an Opportunity's Description field.

Create a Flex Prompt Template
Open the Extract Product Mentions template in Prompt Builder and copy its instructions.
Return to the Prompt Builder page and click New Prompt Template.
Select Flex in the Prompt Template Type dropdown.
Specify a name and description.
Under Inputs, click Add to define the resource.
Name: Opportunity Data
API Name: Opportunity_Data
Source Type: Object
Object: Opportunity
Paste the copied instructions into the Prompt section.
In Template Settings, click Resources.
Under Inputs, select Opportunity, then select Description.
Test and click Activate.
Deploy the Template as an Agent Action
Create a custom agent action with a Prompt Template reference action type.
In Setup, select Agentforce Agents and click Revenue Quote Management.
Click Open in Builder.
On the Topics panel, click Quote Management and add your custom action.
Open an opportunity containing product details in its description.
Enter Extract product details for this opportunity in the agent chat window.
The agent retrieves product names, quantities, and attributes.
Add the extracted products to a new or existing quote.
