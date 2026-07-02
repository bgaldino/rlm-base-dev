---
article_id: ind.product_configurator_third_party_configurator_ui_component_javascript_file.htm
title: Third-Party Configurator UI Component JavaScript File
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_third_party_configurator_ui_component_javascript_file.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Third-Party Configurator UI Component JavaScript File

Every component has a JavaScript file. For the third-party configurator UI component, this file contains all the logic for sending and receiving data and interacting with the configurator.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

This JavaScript example uses Lightning Message Service events to send and receive data.

import {api, LightningElement} from 'lwc';

import {MessageContext, publish} from 'lightning/messageService';

import CONFIGR_CHANNEL from "@salesforce/messageChannel/lightning__productConfigurator_notification";

const LMS_EVENTS = Object.freeze({
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
    CUSTOM_PRODUCT_NAME: "CustomProductName"
});

export default class MyComponent extends LightningElement {
    
    @api transactionId;
    @api transactionLineId;
    @api currentTransactionLineId;
    @api parentName;
    @api origin;
    @api messages;
    @api header;
    @api optionGroups;
    @api summary;
    @api navigationRoute;
    @api searchInfo;
    @api currencyCode;
    @api transactionRecord;
    @api headerTitle;
    @api isDesignTime;
    // ... do @api annotations for each of the input properties you want from
    // Data Manager
    
    subscription = null; // Stores the subscription to the message service
    
    // Lifecycle hook that subscribes to the message channel when the component is initialized
    connectedCallback() {
       this.subscribeToMessageChannel();
    }

    // Subscribes to the Lightning Message Service channel to receive message
    subscribeToMessageChannel() {
       if (!this.subscription) {
           this.subscription = subscribe(
               this.messageContext,
               CONFIGR_CHANNEL,
               (message) => this.handleMessage(message)
           );
       }
    }
    
    handleMessage(message) {}
    
    // Send the message to LMS
    sendMessageToDataManager() {
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

        publish(MessageContext, CONFIGR_CHANNEL, bulkMessagePayload);
    }
}


Lightning Message Service for Third-Party Configurator UI Components
Use Lightning Message Service (LMS) events to enable a third-party component to communicate with the Data Manager component in the product configurator flow. Add LMS events to the JavaScript file for the component to send and receive data.
SEE ALSO
Create a Third-Party Configurator UI Component
