---
article_id: ind.product_configurator_flow_product_header.htm
title: Product Header
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_product_header.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Product Header

Product Header shows product information at the top of each product or option in Product Configurator. The component shows product name, description, image, quantity input, pricing, and Product Selling Model (PSM) selection. It's a UI presentation component that publishes user changes via Lightning Message Service (LMS) events. Product Header has no output properties.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Product Header Responsibilities
Display product information including name, description, image, quantity, and price
Handle user input including quantity changes, PSM selection, and custom product name editing
Send user input to Data Manager via LMS events
Show configurable fields in the top and bottom regions of the configurator
Support standard and compact layout modes
Validate quantity input and custom product names
Product Header API Name

S01_Header

Product Header Input Properties

The Product Header receives input from parent or flow components, set by the customer.

PROPERTY	TYPE	REQUIRED	DESCRIPTION
header	Object	No	Main product header data (quantity, price, name, PSM)
currencyCode	String	No	Currency code for price display
quantityReadOnly	Boolean	No	Makes quantity field read-only
isClassContext (Product Classification Preview Mode)	Boolean	No	Whether the component is in class context mode
isApiInProgress (isApiInProgress)	Boolean	No	Whether an API call is in progress
isDesignTime (isDesignTime)	Boolean	No	Whether in design or preview mode
disabled	Boolean	No	Disables all inputs
layoutMode	String	No	Layout mode (standard or compact)
contextMetadata	String	No	Metadata for STI attributes (labels, data types) as a JSON String
eligiblePromotions	Array	No	List of promotions available for this product
isNonBlockingEnabled	Boolean	No	Whether non-blocking is enabled
Events the Product Header Listens To

Product Header listens to Lightning Message Service (LMS) events and wire adapters.

Product Header subscribes to the message channel to receive state updates as LMS events from the Data Manager. The Product Header listens to the LMS events shown in this table.

EVENT ACTION	HANDLER METHOD	WHAT IT DOES
valueChange	handleLmsMessage()	Tracks which field is being changed
navigate (type='cancel')	handleLmsMessage()	Tracks cancel navigation

The Product Header listens to the wire adapter event shown in this table.

WIRE ADAPTER	SOURCE	WHAT IT LISTENS FOR	HANDLER METHOD	PURPOSE
MessageContext	lightning/messageService	Message context for LMS	Not applicable (provides context)	Enables LMS communication
Events the Product Header Fires

The Product Header fires the Lightning Message Service (LMS) event shown in this table.

EVENT ACTION	WHEN IS IT FIRED	PURPOSE
LMS_EVENTS.VALUE_CHANGE	User changes fields	Notify Data Manager of the changes
