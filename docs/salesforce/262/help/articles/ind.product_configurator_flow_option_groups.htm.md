---
article_id: ind.product_configurator_flow_option_groups.htm
title: Option Groups
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_option_groups.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Option Groups

Option Groups is the container component that shows child products organized into groups. The component manages option selection, dynamic option addition, cloning, and search navigation. Option Groups has no output properties.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Option Groups Responsibilities
Show product options organized by groups
Support tabs and accordion display
Process selection changes from child option components
Show window for browsing and adding dynamic options
Show window for cloning existing transaction items
Handle navigation to searched options
Publish Lightning Message Service (LMS) events to send selection changes, clone requests, and navigation to Data Manager
Manage context definition changes for customizable fields
Option Groups API Name

S01_OptionGroups

Input Properties

Option Groups receives input from parent or flow components, set by the customer.

PROPERTY	TYPE	REQUIRED	DESCRIPTION
optionGroups	Array	Yes	Array of option groups from DataManager
salesTransactionItems	Array	No	Transaction items data
contextDefinition	String	No	Context definition ID
contextMetadata	String/Object	No	Metadata for STI attributes
portion1SelectedFields	String/Array	No	Custom fields for portion 1
portion2SelectedFields	String/Array	No	Custom fields for portion 2
currencyCode	String	No	Currency code for price display
isDesignTime	Boolean	No	Whether in design or preview mode
disabled	Boolean	No	Disables all option selection controls (checkboxes, radio buttons, quantity inputs, configure buttons).
isApiInProgress	Boolean	No	Whether API call is in progress
variant	String	No	Display mode: "tabs" or "accordions"
layoutMode	String	No	Layout mode: "standard" or "compact"
isNonBlockingEnabled	Boolean	No	Enable non-blocking mode
isGroupRampEnabled	Boolean	No	Enable group ramp functionality
showInlineAttributes	String	No	Whether to show inline attributes
numberOfInlineAttributes	Number	No	Number of inline attributes to display
searchResultOptionId	String	No	PRC ID of search result option
Events Option Groups Listens To

Option Groups listens to the getProductFlowByProductId wire adapter. When a user selects Add Options for a dynamic option group, the wire adapter fetches the associated Flow API name to open the dynamic option flow window.

WIRE ADAPTER	SOURCE	WHAT IT LISTENS FOR	HANDLER METHOD	PURPOSE
getProductFlowByProductId	lightning/industriesEpcApi	Product flow data for dynamic options	setFlowId()	Retrieves flow API name for dynamic option window
Events Option Groups Fires

Option Groups fires LMS events and the FlowAttributeChange event.

Option Groups fires the LMS events shown in this table.

EVENT ACTION	WHEN IS IT FIRED	PURPOSE
LMS_EVENTS.VALUE_CHANGE	User changes attribute value	Notify DataManager of the changes to the options
cloneItems	User clones transaction items	Notify DataManager to clone STIs
contextDefinitionChange	Context definition changes	Notify DataManager of context definition change
navigate (search)	User cancels search mode	Notify DataManager to clear search result

This table shows the LMS_EVENTS.VALUE_CHANGE payload field types for Option Groups.

FIELD	WHEN IS IT FIRED	PURPOSE
isSelected	When a product is selected or deselected	Notify DataManager of the changes to the options for selecting a product
Quantity	When quantity is changed	Notify DataManager of the changes to the options for changing the quantity
AttributeField	When the attribute value in option card is changed	Notify DataManager of the changes to the options for changing the attribute value
ProductSellingModel	When ProductSellingModel value is changed	Notify DataManager of the changes to the Product Selling Model value change
CustomProductName	When a custom product name is changed	Notify DataManager of the changes to the options - changing the product name
ContextFields	When Context field values is changed in option card	Notify DataManager of the changes to the options change in context value
addedNodes	When there’s a change in addedNodes	Notify DataManager of the changes to the addedNodes
PromotionAdd	When promotion is added	Notify DataManager of promotion add
PromotionRemove	When promotion is removed	Notify DataManager of promotion remove

Option Groups fires the FlowAttributeChange event shown in this table.

EVENT ACTION	WHEN IS IT FIRED	PURPOSE
FLOW_ATTRIBUTE_CHANGE	User changes inline attribute	Notify flow of attribute change
