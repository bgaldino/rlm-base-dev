---
article_id: ind.product_configurator_third_party_configurator_ui_component_lightning_message_service.htm
title: Lightning Message Service for Third-Party Configurator UI Components
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_third_party_configurator_ui_component_lightning_message_service.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_third_party_configurator_ui_component_javascript_file.htm
fetched_at: 2026-09-04
---

# Lightning Message Service for Third-Party Configurator UI Components

Use Lightning Message Service (LMS) events to enable a third-party component to communicate with the Data Manager component in the product configurator flow. Add LMS events to the JavaScript file for the component to send and receive data.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

This example shows available LMS events.

export const LMS_EVENTS = Object.freeze({
    VALUE_CHANGE: "valueChanged",
    NAVIGATE: "navigate",
    CLOSE_PREVIEW: "closePreview",
    TOGGLE_INSTANT_PRICING: "toggleInstantPricing",
    TOGGLE_RULES_VALIDATION: "toggleRulesValidation",
    TOGGLE_COMPACT_LAYOUT: "toggleCompactLayout",
    UPDATE_PRICES: "updatePrices",
    VALIDATE_PRODUCT: "validateProduct",
    CLONE_ITEMS: "cloneItems",
});

You can use LMS events to update a specific set of supported fields on a sales transaction item, including selection, quantity, attribute, pricing, and promotion fields. Each field must be set up as editable. An LMS event can't update a read-only field or a field outside the supported set.

NOTE To update a field that isn't in the supported set, use a flow, formula field, or trigger as a workaround.

To update a field, pass in the attribute name of the field and the new value, as shown here.

{
key: ["0QLxx0000004jGGGAY"],
field: "SalesTrxnItemDescription"
value: "Updated description"
}

This example shows the supported modifiable fields.

export const STATE_FIELDS = Object.freeze({
    IS_SELECTED: "isSelected",
    QUANTITY: "Quantity",
    ATTRIBUTE_FIELD: "AttributeField",
    PRODUCT_SELLING_MODEL: "ProductSellingModel",
    PRICING_TERM_UNIT: "PricingTermUnit",
    SUBSCRIPTION_TERM: "SubscriptionTerm",
    SELLING_MODEL_TYPE: "SellingModelType",
    PRICE_BOOK_ENTRY: "PricebookEntry",
    IS_DELETED: "Deleted",
    UNIT_PRICE: "UnitPrice",
    CUSTOM_PRODUCT_NAME: "CustomProductName",
    ADDED_NODES: "<TBD>",
    PROMOTION_ADD: "<TBD>",
    PROMOTION_REMOVE: "<TBD>",
    CONTEXT_FIELDS: "<TBD>",
});

This example shows the payload for the valueChanged event.

NOTE For custom fields, use this payload format in place of the standard format:
{
action: LMS_EVENTS.VALUE_CHANGE,
data: [
{
key: ["<id>"],
values: [
{
field: <field api name>,
value: <value>,
}
]
}
]
}
const bulkMessagePayload = {
    action: LMS_EVENTS.VALUE_CHANGE,
    data: [
        // Change 1: update the root product's quantity field
        {
            key: ["0QLxx0000004jGGGAY"],
            field: STATE_FIELDS.QUANTITY,
            value: 100
        },
        // Change 2: update the root product's attribute
        {
            key: ["0QLxx0000004jGGGAY"],
            field: STATE_FIELDS.ATTRIBUTE_FIELD,
            attributeId: "0tjxx0000000001AAA",
            value: "New Value"
        },
        // Change 3: update another one of root product's attributes
        {
            key: ["0QLxx0000004jGGGAY"],
            field: STATE_FIELDS.ATTRIBUTE_FIELD,
            attributeId: "0tjxx0000000001AAB",
            value: "0xxxx0000000001AAB"
        },
        // Change 4: create a picklist attribute that does not exist (non-defaulted picklist)
        {
            key: ["0QLxx0000004jGGGAY"],
            field: STATE_FIELDS.ATTRIBUTE_FIELD,
            attributeId: "0tjxx0000000001AAC",
            value: "0xxxx0000000001AAB"
        },
        // Change 5: select a static child product
        {
            key: ["0QLxx0000004jGGGAY"],
            productRelatedComponentId: '0dSxx00000000XtEAI', // the static child PRC to select
            field: STATE_FIELDS.IS_SELECTED,
            value: true
        },
        // Change 6: select a dynamic option with a child option below it
        {
            field: STATE_FIELDS.IS_SELECTED,
            selectedDynamicOptions: dynamicOptionsForInputPayload,
            productRelatedComponent: prcForInputPayload
        },
        // Change 7: change the PSM for the root product from onetime to termed
        {
            key: ["0QLxx0000004jGGGAY"],
            field: STATE_FIELDS.PRODUCT_SELLING_MODEL,
            value: {
                psmId: "0jPxx00000002JZEAX",
                pbeId: "01uxx000000A0tKAAX"
            }
        },
        // Change 8: deselect a child static option
        {
            key: ["0QLxx0000004jGGGAY", '0QLxx0000004jGHGAY'],
            field: STATE_FIELDS.IS_SELECTED,
            value: false
        }
    ]
};

publish(MessageContext, MessageChannel, bulkMessagePayload);
