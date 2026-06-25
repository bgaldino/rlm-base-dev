import { LightningElement, api, wire } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { getRecord, getRecordNotifyChange } from 'lightning/uiRecordApi';
import { RefreshEvent } from 'lightning/refresh';
import issueRefund from '@salesforce/apex/RLM_RefundController.issueRefund';
import BALANCE_FIELD from '@salesforce/schema/Payment.Balance';

const FIELDS = [BALANCE_FIELD];

export default class RlmRefundButton extends LightningElement {
    @api recordId;
    @api objectApiName;

    isProcessing = false;
    balance = null;

    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    wiredRecord({ error, data }) {
        if (data) {
            this.balance = data.fields.Balance.value;
        } else if (error) {
            // eslint-disable-next-line no-console
            console.error('rlmRefundButton: unable to load payment balance', error);
        }
    }

    get isDisabled() {
        return this.isProcessing || this.balance === null || this.balance <= 0;
    }

    handleIssueRefund() {
        this.isProcessing = true;

        issueRefund({ recordId: this.recordId, objectType: this.objectApiName })
            .then((result) => {
                if (result && result.success) {
                    this.showToast('Success', result.message, 'success');
                    // Refresh the wired balance and the surrounding record view / related lists
                    // instead of a full page reload (location.reload is an anti-pattern in LWC).
                    getRecordNotifyChange([{ recordId: this.recordId }]);
                    this.dispatchEvent(new RefreshEvent());
                } else {
                    const message = (result && result.message) || 'Unable to process refund.';
                    this.showToast('Error', message, 'error');
                }
            })
            .catch((error) => {
                const message = error?.body?.message || error?.message || 'Unknown error occurred.';
                this.showToast('Error', message, 'error');
            })
            .finally(() => {
                this.isProcessing = false;
            });
    }

    showToast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
}
