---
article_id: ind.product_configurator_flow_data_manager.htm
title: Data Manager
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_data_manager.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Data Manager

Data Manager is the state management and orchestration component for Product Configurator. This component stores product data and uses flow events to propagate the data to other components on the flow screen.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Data Manager Responsibilities
Maintain the transaction context and configuration state
Invoke the Configurator API and process responses
Process Lightning Message Service (LMS) events from UI components
Provide data to UI and expose reactive properties to child components
Support saving and loading favorite configurations
Data Manager API Name

S01_DataManager

Data Manager Input Properties

Data Manager accepts data from parent or flow component properties set by users.

PROPERTY	TYPE	REQUIRED	DESCRIPTION
transactionLineId	String	Yes	Root product or transaction line ID
currentTransactionLineId	String	Yes	Current line being viewed
transactionId	String	Yes	Sales Transaction ID (Quote, Order, and so on)
parentName	String	Yes	Name or title of the parent transaction that the configuration pertains to.
origin	String	Yes	Name of the transaction record's parent object. Example: 'Opportunity', 'Quote', 'Order', 'Asset', and so on. This identifies which Salesforce object type launches the configuration. Used for navigation, UI label and so on.
addedNodes	Array	No	Flow resource that contains a collection of Apex ProductConfig__SalesTransactionItem records associated with the parent record transaction.
isNonBlockingEnabled	Boolean	No	Turn on non-blocking mode. When turned on, this allows users to continue interacting with the UI while API calls are processing in the background. Changes are queued and processed asynchronously without blocking the UI. When turned off, the UI is locked during API calls.
areMessagesFixed	Boolean	No	Whether messages component has a fixed position. When true, the messages component stays fixed at the top of the screen and remains visible while scrolling (sticky positioning). When false, the messages component scrolls with the page content (relative positioning). Useful for keeping validation errors/warnings always visible during configuration
contextId	String	No	ID of the transaction context specified for Product Configurator
enableARCValidation	Boolean	No	Indicates whether ARC (Asset Renewal Configuration) validation runs during product configuration
transactionLineGroupId	String	No	ID of the group that contains the current transaction line being configured. For Quotes, this is the Quote Line Group ID. For Orders, this is the Order Item Group ID.
explainabilityEnabled	Boolean	No	When Explainability is enabled, Product Configurator provides detailed explanations for why products are hidden, disabled, or recommended. Shows rule execution details and business logic reasoning to help users understand configuration constraints.
userContext	Object	No	

API name of a flow variable that contains user qualification data. This variable is of type ProductConfig__UserContext and determines product eligibility based on user-specific attributes.

1. In Flow Builder, create a variable API name, for example, userContextData.

2. Use an Assignment or Get Records element to populate the variable, and set fields such as role, region, accountType, and so on. For example, {!userContextData.role} = {!$User.UserRole.Name}

3. In Data Manager, for User Context, select {!userContextData}. The Configurator API uses this data to evaluate qualification rules and filter which products are available. For example, if you have rules like "Show Enterprise Products only to Enterprise Sales reps", the API checks the user's role from this context.

Select a user context only if you have product qualification rules that depend on user-specific attributes like role, territory, and so on. If all products are available to all users, leave this field empty.

Data Manager Output Properties

Data Manager writes output properties that customers can read. An internal method generates data, and the FlowAttributeChangeEvent dispatches the data to the relevant property, as shown in this example.

this.dispatchEvent(
   new FlowAttributeChangeEvent(FLOW_REACTIVITY_MESSAGES, messages)
);


This table shows what data Data Manager provides to other components. The Data Source column identifies the internal process that generates the data.

PROPERTY	DATA TYPE	DESCRIPTION	DATA SOURCE
header	Object	Current product header information	mergeContexts()
messages	Array	Validation/error messages	API response + rules
optionGroups	Array	Product component groups (options)	mergeContexts()
attributeCategories	Array	Product attribute categories	mergeContexts()
summary	Object	Configuration summary (merged transaction tree)	mergeContexts()
navigationRoute	Array	Current navigation path, or breadcrumbs	buildNavigationInfo()
searchInfo	Array	Search data for product catalog	buildSearchInfo()
tabs	Array	Available tabs for multi-root bundles	buildTabs()
currencyCode	String	Currency code for pricing	API response
transactionRecord	Object	Transaction record details	populateTransactionRecord()
headerTitle	String	Header title text	generateHeaderTitle()
isInstantPricingToggleEnabled	Boolean	Whether instant pricing toggle is shown	setToggleStates()
isInstantPricingEnabled	Boolean	Current instant pricing state	Toggle/API
isProductValidationEnabled	Boolean	Current validation state	Toggle/API
showPrices	Boolean	Whether to show prices	State logic
showSummaryTotalSection	Boolean	Whether to show summary total section	Insurance override
favoriteData	

String (JSON)

	Configuration data for favorites	getFavoriteData()
isConfiguratorDisabled	Boolean	Whether configurator is disabled	UI state
isApiInProgress	Boolean	Whether API call is in progress	API lifecycle
isPriceRampEnabled	Boolean	Whether price ramps are enabled	Context check
isGroupRampEnabled	Boolean	Whether group ramps are enabled	Group calculation
salesTransactionItems	Array	All transaction items	API response
layoutMode	String	Layout mode (standard or compact)	Toggle
searchResultOptionId	String	Selected search result option ID	Search navigation
rootProductId	String	Root product ID	Catalog data
currentGroupName	String	Current group name	getCurrentGroupName()
contextMetadata	Object	Context metadata for customizable Sales Transaction Item attributes. Contains field definitions (labels, data types, picklist values) for custom attributes that can be displayed in the UI.	Context parsing
eligiblePromotions	Array	Eligible promotions list	Promotion API
Events Data Manager Listens To

Data Manager listens to Lightning Message Service (LMS) events and wire adapters.

To listen to LMS events, Data Manager subscribes to the message channel and receives LMS events that other components published there. This table shows LMS event actions, their handler methods, and what the actions do.

EVENT ACTION	HANDLER METHOD	WHAT IT DOES
valueChange	setState()	Updates configuration state (selections, quantities, attributes)
navigate	navigate()	Navigates through bundle hierarchy
closePreview	closePreview()	Closes preview window
toggleInstantPricing	setInstantPricing()	Toggles instant pricing on/off
toggleExplainability	setExplainability()	Toggles explainability on/off
toggleRulesValidation	setProductValidation()	Toggles validation on/off
updatePrices	updatePrices()	Manually triggers pricing
validateProduct	validateProduct()	Manually triggers validation
cloneItems	cloneItems()	Clones transaction items
toggleCompactLayout	setLayoutModeOnToggle()	Toggles layout mode
contextDefinitionChanged	setContextDefinition()	Updates context definition
saveFavConfiguration	handleSaveConfiguration()	Saves configuration as favorite
loadFavorite	handleLoadFavorite()	Loads favorite configuration

Wire adapters automatically listen for data changes from the Salesforce platform, and pass the data changes to Data Manager. This table shows the wire adapter events Data Manager listens to.

WIRE ADAPTER	SOURCE	WHAT IT LISTENS FOR	HANDLER METHOD	PURPOSE
MessageContext	lightning/messageService	Message context for LMS	

Not applicable (provides context)

	Enables LMS communication
getContextServiceDefinition	lightning/industriesContextApi	Context definition changes	

gotContextDefinition()

	Listens for context definition data
getObjectInfos (2nd)	lightning/uiObjectInfoApi	Transaction item object info	getObjectInfos()	Listens for transaction item metadata
Events Data Manager Fires

Data Manager fires custom events, toast events, and flow attribute change events.

This table shows custom events Data Manager fires, including bubbling and composed events.

EVENT NAME	BUBBLES	COMPOSED	WHEN IT FIRES	PURPOSE
loading	Yes	Yes	During initial load	Notify parent of loading state
proceed	Yes	Yes	Cancel at root OR close window	Close configurator without saving
save	Yes	Yes	Save and exit navigation	Save configuration and exit
close_modal	Yes	Yes	Close preview	Close preview window
showConflictToast	Yes	Yes	Non-blocking API conflicts detected	Show conflict warning toast

This table shows the toast event Data Manager fires.

EVENT NAME	WHEN IS IT FIRED	PURPOSE
ShowToastEvent	After loading favorite successfully	Notify user of successful favorite load

Data Manager dispatches FlowAttributeChange events for all reactive properties on every UI update.
