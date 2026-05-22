---
article_id: ind.pricing_configure_decision_explainer_for_price_waterfall.htm
title: Configure Decision Explainer for Price Waterfall
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_configure_decision_explainer_for_price_waterfall.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Configure Decision Explainer for Price Waterfall

Map expression set message tokens and explainability message templates to pricing elements to customize the decision explanations in the price waterfall.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To configure decision explainer:	Salesforce Pricing Design Time
Create an Expression Set Message Token

Create tokens to represent specific values (like a net unit price) that you want to display dynamically in your explanation messages.

From Setup, in the Quick Find box, enter Decision Explainer, and then select Expression Set Message Token.
Click New Expression Set Message Token.
Provide a Name, Label, and Description (optional). For example, enter NetUnitPrice as the name and label.
Save your changes to use the token in explainability messages.
Create an Explainability Message Template

Define the success and failure messages that appear in the waterfall, and embed your tokens to show dynamic values.

From Setup, in the Quick Find box, enter Decision Explainer, and then select Explainability Message Template.
Click New Explainability Message Template.
Specify these details:
Name: Enter a name, for example, Successful message.
Label: Enter a label.
Message: Enter your custom text. To use a token, follow the format ${TokenName}. Example: My net unit price is ${NetUnitPrice}.
Expression Set Step Type: Business Element.
Usage Type: Pricing.
Save your changes.
Repeat these steps to create a template for failure messages if needed.
Configure the Pricing Procedure for Decision Explainer

Enable decision explanations within your pricing procedure and map your templates to the specific pricing elements.

Open your pricing procedure in the pricing procedure builder.
If the procedure is active, deactivate it to make edits.
Refresh the procedure to ensure the latest metadata is available.
Choose an element for which you would like to enable decision explainer.
Click 'Pricing Procedure Properties (gear icon) and select the Show decision explainer checkbox to enable decision explainer for the element.
In the Element Details panel, under the Decision Explainer section, enable Show decision explanation.
Configure the output messages:
When Step Returns Output: Search for and select the Success message template you created earlier.
Map Tokens: Click the icon next to the template field to map your message token (e.g., NetUnitPrice) to the corresponding Context Definition tag.
* When Step Errors: Search for and select the Failure message template you created earlier.
Save and activate your pricing procedure.

Click Simulate to verify that the price waterfall displays your custom explanation messages and dynamic token values for each step.
