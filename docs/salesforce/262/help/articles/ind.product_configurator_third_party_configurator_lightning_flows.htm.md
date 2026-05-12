---
article_id: ind.product_configurator_third_party_configurator_lightning_flows.htm
title: Third-Party Configurator Lightning Flows
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_third_party_configurator_lightning_flows.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Third-Party Configurator Lightning Flows

Third-party users can build a third-party configurator as a replacement to the first-party configurator using the screen-based lightning flows. The screen-based lightning flow is either included in the managed package or custom built in the org.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

Both first-party and third-party configurators receive the same data when the screen-based Lightning Flow launches during a configuration process.

"configuratorContext": {
"transactionId": <the quote/order ID being configured>,
"transactionLineId": <the quote/order item ID being configured>,
"parentName": <the quote/order name>,
"origin": <"Quote" | "Order">,
"addedNodes": [{
"id": <a synthetic quote/order item Id>,
"pricebookEntry": <Pricebook Entry Id>,
"productSellingModel": <Product Selling Model Id>,
"unitPrice": <Unit Price>,
"quantity": <Quantity>,
"product": <Product2 Id>,
"businessObjectType": <QuoteLineItem or OrderItem>
}]
}


When the screen-based Lightning Flow built with the required data format, the screen-based Lightning Flow can be assigned to specific products, product classifications, or even entire organizations, where it functions as the designated configurator.

Third-party configurators offer greater flexibility. Third-party configurators can have their own solutions from scratch, bypassing features like Salesforce Pricing, Context Service, Configurator API, and Business Rules Engine. Third-party configurators can use any Salesforce APIs that are required. There’s no obligation to use any of the Agentforce Revenue Management specific APIs.

SEE ALSO
Define Product Configuration Flows
