---
article_id: ind.qocal_extract_product_mentions.htm
title: Configure Extract Product Mentions Template
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_extract_product_mentions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_foundational_setup_for_quotes_and_orders.htm
fetched_at: 2026-09-04
---

# Configure Extract Product Mentions Template

Use the Extract Product Mentions template to identify products and quantities from emails, Slack messages, or call summaries. This automation eliminates manual data entry by extracting product names, quantities, and attributes directly into quotes or transactions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management with the Einstein or Agentforce for Sales or Einstein 1 Sales add-on.
USER PERMISSIONS NEEDED
To manage prompt templates in Prompt Builder:	Prompt Template Manager permission set
To access and run the Extract Product Mentions prompt template:	Prompt Template User permission set

Set up Einstein Generative AI and Prompt Builder. When you use agents, turn on Agentforce and set up the Revenue Quote Management agent template.

Review or customize the standard Extract Product Mentions template to suit your business requirements.

From Setup, find and select Prompt Builder.
Under All Prompt Templates, select Extract Product Mentions to open the Prompt Template Workspace .
Review the template ingredients, including the participant, goal, instructions, and output examples.
Save as a new template to override the standard version. You only modify template instructions when overriding a standard template. To ground the template with more data sources like specific object fields, create a Flex prompt template.
Enter the template details
Test your custom prompt template.
Activate the template when you’re satisfied with the outputs.

After you configure the prompt template, integrate it into your sales processes using an invocable action, an agent action, the Connect REST API, or Connect in Apex.

Example: Extract Products from Opportunity Descriptions
The sales team at QuantumBit wants to streamline quote creation because critical product and pricing discussions often remain buried within the unstructured text of opportunity description fields. To resolve this issue, the Transaction Management Salesforce admin uses the Extract Product Mentions prompt template to automate the identification of these key details. By creating a custom Flex prompt template and deploying it as an agent action, the Salesforce admin enables sales reps to extract product names, quantities, and attributes directly from the opportunity description to expedite the quoting process.
