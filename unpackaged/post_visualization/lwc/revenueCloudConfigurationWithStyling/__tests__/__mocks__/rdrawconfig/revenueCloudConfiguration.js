import { LightningElement, api } from 'lwc';

export default class RevenueCloudConfiguration extends LightningElement {
    @api configuratorContext;
    @api renderContext;
    @api salesTransactionItems;
    @api overrideRecordId;
    @api size;
    @api optionGroups;

    @api
    raiseInteractionEvent(eventName, action, field, value, keyvalues) {
        // Mock implementation
    }

    @api
    getCurrentCanvas() {
        return { mockCanvas: true };
    }
}
