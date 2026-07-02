---
article_id: ind.product_catalog_enhanced_product_discovery_experience.htm
title: Enhanced Product Discovery Experience
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_enhanced_product_discovery_experience.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Enhanced Product Discovery Experience

The enhanced Product Discovery experience helps you build accurate transactions as you browse the product catalog. You see real-time transaction details in the transaction preview, along with constraint rule outcomes, such as rule messages, disabled products, and product recommendations. When you add a product, Product Discovery saves it directly to the transaction, so you can continue browsing without leaving the page.

REQUIRED EDITIONS
View supported products and editions.

As you browse the catalog, Product Discovery keeps the Product List page and the transaction preview in sync with your transaction. Each time you add a product, Product Discovery evaluates the updated transaction against configuration rules and updates rule messages, disabled products, recommendations, and the preview.

Key Capabilities

The enhanced Product Discovery experience combines several capabilities on the Product List page.

Key Capabilities of enhanced Product Discovery
CAPABILITY	DESCRIPTION
Transaction preview during browsing.	The transaction preview shows your current transaction in real time and updates automatically as you add or remove products. You can review products, quantities, and pricing while you continue browsing the catalog.
Visibility rules during product selection.	

You can define constraint rules in a CML constraint model in Product Configurator to disable products, display rule messages, and show product recommendations. As you browse and add products, Product Discovery evaluates these rules and updates the configuration rule outcomes in the Product Discovery experience. You see rule messages at the top of the page, disabled products appear as disabled in the Disqualification filter. This immediate feedback helps you understand constraints as you make selections and avoid issues later in the transaction.

NOTE Product Discovery uses configuration rules, which you define as constraint rules in a constraint model written in CML.
When more than one message rule applies, Product Discovery shows multiple messages in the message bar.
When a product is both recommended and disabled, you can’t add it. Disabled rules take precedence.
When a disabled rule and a disqualification rule apply to the same product, Product Discovery shows messages from both rules, and you can't add the product.

When a disabled rule or a disqualification rule applies, Product Discovery hides the affected products from the product list. Apply the Disqualified filter to view them.


Product recommendations based on transaction.	Product Discovery shows rule-based recommendations defined by configuration rules, based on your current transaction. You can add recommended products directly from the Recommendations list. Product Discovery shows the rule-based recommendations defined by configuration rules, based on your current transaction. You can add recommended products directly from the Recommendations list. Product Discovery honors qualification rules when showing recommended products.
Autosave for committed changes.	When you add a product, Product Discovery saves it directly to the transaction. You don’t need a separate save action, so you can continue adding products while the transaction preview stays in sync.
Things to Know
In transactions with many line items, adding or removing multiple products at the same time can occasionally lead to unexpected behavior. To ensure consistent results, add or remove products sequentially.
The transaction preview displays committed transaction data only.
Configuration rules are evaluated based on the current transaction and not all catalog results.
If you turn off the feature, users see the older preview experience. The earlier preview doesn’t provide the same real-time updates or configuration rule visibility.
Set Up Enhanced Product Discovery Features
Turn on enhanced Product Discovery features so that Product Discovery can show transaction previews, configuration rule outcomes, and rule-based recommendations, and automatically save product changes while users browse the catalog.
Preview Transactions While Browsing the Catalog
Use the transaction preview to review product selections, quantities, and pricing in real time without leaving Product Discovery. The preview shows up to the 50 most recently added items in the transaction. For bundled products, the preview displays only the main product, while quantities and pricing include totals from all products in the bundle.
View Visibility Rule Outcomes During Product Discovery
As you browse the catalog, Product Discovery evaluates the current transaction against configuration rules. Based on the rules you configure, Product Discovery shows messages, disables products, and recommended products directly in the browsing experience.
