---
article_id: ind.product_configurator_flow_header.htm
title: Header
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_header.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Header

Header, also called Config Header, is a control panel component that displays the configuration header with toggles, tabs, and informational banners at the top of Product Configurator. The component provides controls for users to toggle instant pricing, validation, and layout modes, and to navigate between multiple root products via tabs. Header has no output properties, and doesn’t listen to any events.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Header Responsibilities
Show the configuration title
Provide toggle controls for instant pricing, validation, and layout modes
Show tabs for multi-root bundle configurations
Show banners for outdated prices, validation, and price ramps
Send toggle and navigation Lightning Message Service (LMS) events to Data Manager
Show Favorites button, when it’s enabled
Header API Name

S01_ConfigHeader

Input Properties

Header accepts data from these parent and flow component properties, set by users.

PROPERTY	TYPE	REQUIRED	DESCRIPTION
isDesignTime	Boolean	No	Whether in design or preview mode
isApiInProgress	Boolean	No	Whether API call is in progress
layoutMode	String	No	Layout mode: "standard" or "compact"
isPriceRampEnabled	Boolean	No	Whether price ramps are enabled
title	String	No	Configuration title
tabs	Array	No	Array of tabs for multi-root bundles
isInstantPricingToggleEnabled	Boolean	No	Whether instant pricing toggle is visible
isInstantPricingEnabled	Boolean	No	

Indicates whether Instant Pricing is enabled by default.

Use only the system default value for this property. If you enter any other value, the instant pricing functionality doesn't work.


rootProductId	String	No	Root product ID
explainabilityEnabled	Boolean	No	Whether the explainability toggle is enabled (explainability log collected during configuration).
showPrices	Boolean	No	Whether to show pricing information at run time
favoriteData	String	No	Configuration data for favorites
isNonBlockingEnabled	Boolean	No	Whether non-blocking mode is enabled
isGroupRampEnabled	Boolean	No	Whether group ramp deals are enabled for the product
currentGroupName	String	No	Name of the current group for the transaction item being configured.
Events Header Fires

Header fires the LMS events shown in this table.

EVENT ACTION	WHEN IS IT FIRED	PURPOSE
toggleInstantPricing	User toggles instant pricing	Toggle instant pricing on or off
toggleCompactLayout	User toggles compact layout	Toggle layout mode
toggleRulesValidation	User toggles validation	Toggle validation on/off
updatePrices	User clicks "Update Prices" link	Manually trigger pricing
navigate	User selects a tab	Go to selected root product
