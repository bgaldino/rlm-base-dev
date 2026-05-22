---
article_id: ind.product_configurator_flow_footer.htm
title: Footer
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_footer.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Footer

Footer is the action bar at the bottom of Product Configurator. The component shows validation messages and action buttons. Footer publishes Lightning Message Service (LMS) events to Data Manager when users click these actions. Button visibility depends on context, such as nested product, preview mode, instant pricing, validation, and so on. Footer has no output properties and doesn’t listen to any events.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Footer Responsibilities
Show buttons including Cancel, Save & Exit, Done, Update Prices, and Validate Product based on context
Show validation alerts, warnings, and error messages from Product Configurator
Adjust button labels and variants based on navigation depth. For example, the Done button and the Save & Exit button labels change from one to the other depending on context
Publish LMS events for navigation, pricing, validation, and preview to Data Manager when a user clicks an action
Prompt the user for confirmation to cancel an action and close Product Configurator
Show Close button instead of Save & Exit button in preview mode
Footer API Name

S01_Actions

Input Properties

Footer accepts data from parent or flow component properties, set by users.

PROPERTY	TYPE	REQUIRED	DESCRIPTION
navigationRoute	Array	No	Current navigation path
isClassContext (True when the record being previewed is a product classification (not a regular product)	Boolean	No	Whether the record is a product classification in preview mode.
isApiInProgress	Boolean	No	Whether an API call is in progress. Locks the component while the call runs.
isNonBlockingEnabled	Boolean	No	Whether non-blocking mode is enabled.
isDesignTime (General preview mode. True when any product or product classification is viewed in preview, for example, from App Builder or record page preview.)	Boolean	No	Whether the product or product classification is in preview mode.
isInstantPricingEnabled	Boolean	No	Whether instant pricing is enabled. If false, the Update Prices button is shown.
isInstantPricingToggleEnabled	Boolean	No	Whether the instant pricing toggle is shown.
isProductValidationEnabled	Boolean	No	Whether product validation is enabled.
messages	Array	No	Validation messages (alerts, warnings, errors) from the configurator.
Types of Events Footer Fires

Footer fires the LMS events shown in this table.

EVENT ACTION	WHEN IS IT FIRED	PURPOSE
navigate (type: done)	User clicks Done	Navigate up one level
navigate (type: cancel)	User confirms cancel	Close configurator without saving
navigate (type: save_and_exit)	User clicks Save & Exit	Save configuration and exit
updatePrices	User clicks Update Prices	Manually trigger pricing
validateProduct	User clicks Validate Product	Manually trigger validation
closePreview	User clicks Close in preview mode	Close preview window
