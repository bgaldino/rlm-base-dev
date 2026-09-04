---
article_id: ind.product_configurator_set_up_a_custom_dynamic_addition_screen_flow.htm
title: Set Up a Custom Dynamic Addition Screen Flow
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_set_up_a_custom_dynamic_addition_screen_flow.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_explore_the_product_configurator_flow.htm
fetched_at: 2026-09-04
---

# Set Up a Custom Dynamic Addition Screen Flow

Build a screen flow that replaces the default add-products experience for a product classification during bundle configurations. When a product classification uses a Dynamic Addition Flow, Product Configurator can open your own flow with a custom interface and logic. Publish the product selections back to the Configurator as an addedNodes payload with Lightning Message Service (LMS) so that your quote or order lines stay in sync.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS
NEEDED
To clone the default product configurator flow and create a product configuration flow:	Product Configurator
Clone and customize the Default Product Configurator Flow, add a new screen flow, and then define these input attributes:
ATTRIBUTE	DATA TYPE	FLOW COMPONENT
Transaction ID	String	Product Configurator Data Manager
Option Groups	Apex-Defined (ProductConfig__OptionGroup)	Product Configurator Option Groups
Sales Transaction Items	Apex-Defined (ProductConfig__SalesTransactionItem)	Product Configurator Option Groups

The Product Configurator passes the transaction ID, the option group data, and the parent sales transaction items to your flow through these attributes.

In the flow, create the addedNodes payload to be passed back to Configurator.

The addedNodes value is an array of objects. Each object has a path in the form [transactionId, nodeId] and an addedObject, such as a quote line item or a quote line item relationship.

{
  "addedNodes": [
    {
      "path": [
        "0Q0xx0000004EvcCAE",
        "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589"
      ],
      "addedObject": {
        "id": "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "SalesTransactionItemSource": "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "SalesTransactionItemParent": "0Q0xx0000004EvcCAE",
        "PricebookEntry": "01uxx00000090VuAAI",
        "ProductSellingModel": "0jPxx00000001KHEAY",
        "UnitPrice": 15.26,
        "Quantity": 1,
        "Product": "01txx0000006lfHAAQ",
        "businessObjectType": "QuoteLineItem"
      }
    },
    {
      "path": [
        "0Q0xx0000004EvcCAE",
        "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "ref_d85b036d_d305_4bb6_aba8_a1dff645a664"
      ],
      "addedObject": {
        "id": "ref_d85b036d_d305_4bb6_aba8_a1dff645a664",
        "MainItem": "0QLxx0000004QdRGAU",
        "AssociatedItem": "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "ProductRelatedComponent": "0dSxx00000001p6EAA",
        "ProductRelationshipType": null,
        "AssociatedItemPricing": "NotIncludedInBundlePrice",
        "AssociatedQuantScaleMethod": "Proportional",
        "businessObjectType": "QuoteLineRelationship"
      }
    }
  ]
}
Publish the addedNodes to the Product Configurator with Lightning Message Service (LMS). From a custom Lightning Web Component (LWC) in your screen flow, publish a valueChanged event with the field set to addedNodes.
import MessageChannel from "@salesforce/messageChannel/lightning__productConfigurator_notification";

publish(createMessageContext(), MessageChannel, {
  action: "valueChanged",
  data: [{
    field: "addedNodes",
    addedNodes: this.addedNodes
  }]
});

The Product Configurator reads the field as STATE_FIELDS.ADDED_NODES and applies the nodes.

Save and activate the flow, and then copy the flow API name.
Create a product configuration flow and specify these:
For Flow Identifier, enter the flow API name that you copied in step 4.
Set the status as Active.
In the product configuration flow, create a new Product Configuration Flow Assignment for a product classification with these specifications:
Select the product classification that you want to assign to the product configuration flow.
Select the Assignment Type as Dynamic Addition Flow.

When sales reps dynamically add child components during bundle configurations, your custom screen flow opens for the product classifications you assigned the flow to.
