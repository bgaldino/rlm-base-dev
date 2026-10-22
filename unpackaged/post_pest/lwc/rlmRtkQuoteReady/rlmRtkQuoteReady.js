import { LightningElement, api } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';

export default class RlmRtkQuoteReady extends NavigationMixin(LightningElement) {
    @api accountName;
    @api quoteId;
    @api zoneCode;
    @api zoneMultiplier;
    @api message;
    @api success;

    get isSuccess() {
        return this.success === true || this.success === 'true';
    }

    get shellClass() {
        return this.isSuccess ? 'shell ok' : 'shell bad';
    }

    get headline() {
        return this.isSuccess ? 'Quote ready at the door' : 'Could not create the quote';
    }

    get zoneLabel() {
        const m = this.zoneMultiplier != null ? this.zoneMultiplier : '';
        return this.zoneCode ? `${this.zoneCode} · ×${m}` : '';
    }

    openQuote() {
        if (!this.quoteId) return;
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: {
                recordId: this.quoteId,
                objectApiName: 'Quote',
                actionName: 'view'
            }
        });
    }
}
