---
article_id: ind.product_catalog_einstein_generate_product_description.htm
title: Write Product Descriptions with Einstein Generative AI
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_einstein_generate_product_description.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Write Product Descriptions with Einstein Generative AI

Einstein generative AI uses your instructions to generate revised product descriptions. Product descriptions support instructions only in English but you can generate descriptions in all supported languages. Any user can generate product descriptions by using Einstein but only the Salesforce admin and Product Catalog Designer can accept or reject the recommendations.

REQUIRED EDITIONS
View supported products and editions.
IMPORTANT This tool uses generative AI, which is known to include incorrect or harmful responses. Before using externally, review the output for accuracy and safety. You assume responsibility for the output when making business decisions.
Set Up Einstein Generative AI in Product Discovery

Before you can generate product descriptions by using generative AI, enable Einstein in your org.

Set Up Einstein generative AI.
In Setup, find and select Product Discovery Settings.
Turn on Generate Product Descriptions with Einstein AI.
Add the Einstein Generative AI Recommendation component to the product page layout, and then configure it.
See Create and Configure Lightning Experience Record Pages.
Add a tab to the Product record page.
Drag the Einstein Generative AI Recommendation component onto the new tab.
To edit the properties of the component, click the Einstein Generative AI Recommendation component.
Enter PCM as the app name.
To add a default instruction text for your product description, enter your instructions in the Product Description Instructions field.
Save your changes.
Generate a Product Description
Open a product record page.
To generate a product description, go to the tab that has the Einstein Generative AI Recommendation component.
If the Current field is blank, enter a draft product description.
In Instructions, use the default instruction, or enter a new instruction for your product.
If data translations are set up for your organization, select Translate to all languages.
To generate a description, click Create.
You can edit or accept the text, or regenerate a description.
To save and update the description for the product, click Accept.
