---
article_id: ind.rev_agent_pcm_topic_product_selection.htm
title: "Subagent: Product Selection"
source_url: https://help.salesforce.com/s/articleView?id=ind.rev_agent_pcm_topic_product_selection.htm&type=5&release=262
release: 262
release_name: Summer '26
area: agents
fetched_at: 2026-05-12
---

# Subagent: Product Selection

Use Agentforce to power product discovery and filtering with AI-driven assistance. Sales users can use the Product Selection topic to search the product catalog, ask clarifying questions, and refine results based on customer criteria. The topic helps users explore available products, review key details, and receive recommendations that support accurate and complete quote building. You can customize the Product Selection topic to match your catalog, sales workflows, and conversational experience.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management Advanced license with the Agentforce Employee Agent add-on.
Topic Details
API Name	ProductSelection
Included actions	

Find Products

Get Product Details

Get Rule-Based Product Recommendations (Beta)


Required Setup	Set Up Agentforce for Revenue Management
Examples of Utterances Classified to This Topic
USER SAMPLE INPUT	ACTIONS ENGAGED	AGENT RESPONSE
“Find running shoes.”	FindProducts	The agent lists available running shoes from the catalog.
“Do you have wireless headphones?”	FindProducts	The agent returns wireless headphones that match the query.
“Give me details for Galaxy S24.”	GetProductDetails	The agent shows product details for Galaxy S24, such as description and attributes.
“What are the specs for Laptop Pro?”	GetProductDetails	The agent shows detailed information for Laptop Pro.
“What else should I add to this quote?”	GetRuleBasedProductRecommendations	The agent returns products that are recommended by configuration rules for the quote.
“Are there any recommended add-ons?”	GetRuleBasedProductRecommendations	The agent lists recommended products based on configuration rules.
Use Case: Search and Filter Products with Agentforce
Use AI-powered Product Selection in the Revenue Quote Management agent to search your catalog with natural language, filter results by customer criteria, ask clarifying questions about product attributes, and generate a shortlist of products to add to a quote.
