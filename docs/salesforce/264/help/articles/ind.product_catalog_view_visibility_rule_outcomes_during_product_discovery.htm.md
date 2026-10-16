---
article_id: ind.product_catalog_view_visibility_rule_outcomes_during_product_discovery.htm
title: Product Visibility and Recommendations in Real Time
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_view_visibility_rule_outcomes_during_product_discovery.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_enhanced_product_discovery_experience.htm
fetched_at: 2026-09-04
---

# Product Visibility and Recommendations in Real Time

As you browse the catalog, Product Discovery evaluates the current transaction against configuration rules. Based on the rules you configure, Product Discovery shows messages, disables products, and recommended products directly in the browsing experience.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To view visibility rules:	Product Catalog Management Designer
Visibility Rules

Visibility rules control how products appear in the catalog based on your current transaction. When configured rules evaluate the transaction, products that don't meet the conditions are restricted or hidden from selection. This makes sure that sales reps see only the products that are valid for the current context, reducing errors and improving accuracy during the quoting process.

On the Browse Products page, browse or search for products.
To find products disabled by rules, apply the Disqualified filter.
Review the message to understand why a product is disabled.
EXAMPLE Example: Disable products based on the transaction.

Use a disable rule to make certain products disabled in Product Discovery when the transaction meets specific conditions. In this example, when the transaction includes a Desktop Computer, Product Discovery disables a set of related products while users browse the catalog.

@(virtual = "true")
type Transaction {
  @(sourceContextNode = "SalesTransaction.SalesTransactionItem")
  relation lineitems : LineItem;
  rule(
    lineitems[DesktopComputer],
    "disable",
    "relation", "LineItem",
    "type", "DisabledProducts",
    "message", "These products are unavailable based on the current transaction."
  );
}
type LineItem;
type DesktopComputer : LineItem;
type DisabledProducts;
type Monitor  : DisabledProducts;
type Keyboard : DisabledProducts;
type Mouse    : DisabledProducts;

Product Recommendations

Recommendation rules show suggested products based on your current transaction. You can review these suggestions, understand why they’re recommended, and easily add them to your quote.

On the Browse Products page, click Recommendations in the left panel.
Review the suggested products and the messages explaining why they’re recommended.
Add recommended products directly from the list to the transaction, or continue browsing.

To view products that are disabled but also recommended, use the Disqualified filter.

EXAMPLE Example: Recommend products based on the transaction.

Recommendation rules show relevant products based on the current transaction. Recommended products appear in the Recommendations panel and can be added to the transaction, but the rules don't restrict or prevent product selection.

In this example, when the transaction includes a Primary Product, Product Discovery recommends a group of products while users browse the catalog.

@(virtual = "true")
type Transaction {
  @(sourceContextNode = "SalesTransaction.SalesTransactionItem")
  relation lineitems : LineItem;
  rule(
    lineitems[Laptop],
    "recommend",
    "type", "RecommendedProducts",
    "message", "Consider these add-ons for the selected laptop."
  );
}
type LineItem;
type Laptop : LineItem;

type RecommendedProducts;
type Headset      : RecommendedProducts;
type Mouse     : RecommendedProducts;
type ExtendedWarranty : RecommendedProducts;

Auto-Add and Auto-Delete

Product Discovery evaluates configured rules and automatically adds or removes products from a transaction when the specified conditions are met.

On the Browse Products page, add a product that triggers a rule to add products.
Click Preview to view the transaction.
Review the products that were automatically added to the transaction.
EXAMPLE Example: Automatically add products based on the transaction.
@(virtual = "true")
type Transaction {
  @(sourceContextNode = "SalesTransaction.SalesTransactionItem")
  relation lineitems : LineItem;
  rule(
  require(lineitems[APIAccessRequests], lineitems[QuantumBitDatabase], "Unable to add Quantum Bit Database");
}

type LineItem;
type APIAccessRequests : LineItem;

type QuantumBitDatabase : RequiredProducts;

Messages

Messages display error, warning, or informational alerts based on the current transaction. They appear at the top of the Browse Products page when a message rule applies, providing guidance without interrupting browsing.

On the Browse Products page, select or add a product.
If an alert appears at the top of the page, click Errors, Warnings, or Info to view the messages.
EXAMPLE Example: Display messages based on the current transaction

Use a message rule to show info, warning, or error messages in Product Discovery when the transaction meets specific conditions. Message rules guide users by explaining important conditions or considerations as they browse the catalog.

In this example, when the transaction includes a Primary Product, Product Discovery shows a message to inform the user.

@(virtual = "true")
type Transaction {
  @(sourceContextNode = "SalesTransaction.SalesTransactionItem")
  relation lineitems : LineItem;

  rule(
    lineitems[PrimaryProduct],
    "message",
    "info",
    "message", "Info: Review available options before continuing."
  );

  rule(
    lineitems[PrimaryProduct],
    "message",
    "warning",
    "message", "Warning: This selection may require additional review."
  );

  rule(
    lineitems[PrimaryProduct],
    "message",
    "error",
    "message", "Error: This selection requires a correction before you proceed."
  );
}
