---
article_id: ind.product_catalog_productdiscoverycontext_context_definition.htm
title: Nodes and Attributes in the ProductDiscoveryContext Context Definition
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_productdiscoverycontext_context_definition.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Nodes and Attributes in the ProductDiscoveryContext Context Definition

The ProductDiscoveryContext context definition contains nodes and attributes that are used by and populated by Product Discovery, pricing procedure, qualification procedure, and object mapping.

REQUIRED EDITIONS
View supported products and editions.
The ProductDiscoveryContext Context Definition

The ProductDiscoveryContext context definition contains the Catalog, Category, Category Product, Pricing Product, and Account nodes.

IMPORTANT The qualification procedure and pricing procedure for product discovery must use the context definition selected on the Product Discovery Settings page.
Nodes and Attributes
NODE	ATTRIBUTE	TYPE	DESCRIPTION
Catalog (Root node)	CatalogId	Input	The Salesforce ID of the selected catalog.
CurrentDate	Input	The user’s current date and time.
Category (Child node of the Catalog node)	CategoryId	Input	The Salesforce ID of the category selected by the user.
IsCategoryQualified	Output	

The value that specifies whether a category is qualified.

The qualification procedure populates this value.


CategoryDisqualifiedReason	Output	

The reason for category disqualification.

If a category isn’t qualified, the qualification procedure populates this value.


ParentReference	Input	

A reference to the parent node.

This value is auto-populated.


CategoryProduct (Child node of the Category node)	Quantity	Input	The quantity of a specific product selected by a user.
IsQualified	Output	

Specifies whether a product is qualified.

The qualification procedure populates this value.


Reason	Output	

The reason for product disqualification.

If a product isn’t qualified, the qualification procedure populates this value.


AdditionalProductInformation	Input Output	Don’t use this attribute. This attribute is reserved for future use.
ParentReference	Input	

A reference to the parent node.

This value is auto-populated.


Id	Input	The Salesforce ID of the product.
ProductId	Input	The Salesforce ID of the product.
RootProductId	Input	The Salesforce ID of the root product.
ParentProductId	Input	The Salesforce ID of the parent product.
CategoryId	Input	This field isn’t used by default.
CatalogId	Input	This field isn’t used by default.
Name	Input	The name of the product.
Code	Input	The product code.
MaxQuantity	Input	The maximum quantity of the product that can be added.
MinQuantity	Input	The minimum quantity of the product that must be added.
PricingProduct (Child node of the Category node)	PricingId	Input	The Product’s Salesforce ID and the product selling model’s Salesforce ID.
PricingProductId	Input	The Salesforce ID of the product.
ProductSellingModelId	Input	The Salesforce ID of the product selling model.
ProductQuantity	Input	The product quantity selected by a user.
PricebookId	Input	The Salesforce ID of the price book.
PricingCurrencyCode	Input	The currency ISO code of the user’s account or the currency ISO code specified by the user.
UnitPrice	Output	The list price of the product based on the product selling model.
IsDerived	Output	Specifies whether the price of the product is derived from another source, such as a product or an asset.
NetUnitPrice	Output	The unit price of the item after applying discounts and before tax calculation.
SubTotal	Output	The total price of the product calculated by using the quantity, net unit price, and pricing terms.
PriceBookEntryId	Output	

The Salesforce ID of the price book entry.

The pricing procedure populates this value.


PriceWaterFall	Output	

The ID of the price waterfall.

A price waterfall provides insights into every step of the pricing process.


PricingErrorMessage	Output	The message that appears when price calculation errors occur.
AdditionalPricingInformation	Input Output	Don’t use this attribute. This attribute is reserved for future use.
ParentReference	Input	

A reference to the parent node.

This value is auto-populated.


Account (Root node)	id	Input	The Salesforce ID of the account.
AccountId	Input	The Salesforce ID of the account.
ContactId	Input	The Salesforce ID of the contact.
CurrencyIsoCode	Input Output	

The currency ISO code associated with the account.

This value is auto-populated from the account.
