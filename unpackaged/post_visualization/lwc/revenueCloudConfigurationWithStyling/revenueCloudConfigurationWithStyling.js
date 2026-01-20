import { api, LightningElement, track } from 'lwc';

export default class RevenueCloudConfigurationWithStyling extends LightningElement {
    @api configuratorContext;
    @api renderContext = '3D';
    @api salesTransactionItems = [];
    @api overrideRecordId = '';
    @api size = 'Medium';
    @api optionGroups = [];
    
    @track isPinned = false;
    
    get pinIconName() {
        return this.isPinned ? 'utility:pinned' : 'utility:pin';
    }
    
    get containerClass() {
        return this.isPinned ? 'container pinned' : 'container';
    }
    
    get pinButtonClass() {
        return this.isPinned ? 'pin-button pinned' : 'pin-button';
    }
    
    togglePin() {
        this.isPinned = !this.isPinned;
    }
    
    @api
    raiseInteractionEvent(eventName, action, field, value, keyvalues) {
        const childComponent = this.template.querySelector('c-revenue-cloud-configuration');
        if (childComponent) {
            childComponent.raiseInteractionEvent(eventName, action, field, value, keyvalues);
        }
    }
    
    @api
    getCurrentCanvas() {
        const childComponent = this.template.querySelector('c-revenue-cloud-configuration');
        if (childComponent) {
            return childComponent.getCurrentCanvas();
        }
        return null;
    }
}