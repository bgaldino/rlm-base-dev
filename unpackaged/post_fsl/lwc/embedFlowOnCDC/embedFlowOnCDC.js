import { LightningElement, track, api } from 'lwc';
import { subscribe, unsubscribe, isEmpEnabled } from 'lightning/empApi';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class EmbedFlowOnCDC extends LightningElement {
    @api flowApiName = 'Remote_Hands_Hours_Message'; // Your Flow API Name
    @track showFlow = false;
    subscription = {};
    @api channelName = '/data/QuoteChangeEvent'; // CDC Channel for Quote

    async connectedCallback() {
        if (!await isEmpEnabled()) {
            this.showToast('Error', 'EMP API is not enabled. Please contact your administrator.', 'error');
            console.error('EMP API is not enabled.');
            return;
        }
        this.handleSubscribe();
    }

    disconnectedCallback() {
        this.handleUnsubscribe();
    }

    handleSubscribe() {
        const messageCallback = (response) => {
            console.log('New message received: ', JSON.stringify(response));

            // Ensure payload and ChangeEventHeader exist
            if (response && response.data && response.data.payload && response.data.payload.ChangeEventHeader) {
                const changedFields = response.data.payload.ChangeEventHeader.changedFields;
                const recordIds = response.data.payload.ChangeEventHeader.recordIds; // Useful for context

                // Check if the change event is for the Quote_Message__c field
                if (changedFields && changedFields.includes('Quote_Message__c')) {
                    console.log(`Quote_Message__c changed for Quote record(s): ${recordIds.join(', ')}. Showing flow.`);
                    // You might want to add more specific logic here to check
                    // if the CDC event is relevant to a specific record if this LWC
                    // is placed on a record page. For example, if you only want the flow
                    // to trigger for the *current* quote record:
                    // if (this.recordId && recordIds.includes(this.recordId)) {
                    //    this.showFlow = true;
                    // } else if (!this.recordId) { // If not on a record page, or no recordId context
                           this.showFlow = true;
                    // }
                }
            } else {
                console.warn('Received CDC event with unexpected structure: ', JSON.stringify(response));
            }
        };

        subscribe(this.channelName, -1, messageCallback).then(response => {
            console.log('Successfully subscribed to : ', JSON.stringify(response.channel));
            this.subscription = response;
        }).catch(error => {
            console.error('Failed to subscribe to Change Data Capture events: ', JSON.stringify(error));
            this.showToast('Subscription Error', 'Failed to subscribe to Change Data Capture events. Check console.', 'error');
        });
    }

    handleUnsubscribe() {
        if (this.subscription && Object.keys(this.subscription).length > 0) {
            unsubscribe(this.subscription, response => {
                console.log('Successfully unsubscribed: ', JSON.stringify(response));
            }).catch(error => {
                console.error('Failed to unsubscribe: ', JSON.stringify(error));
                this.showToast('Unsubscribe Error', 'Failed to unsubscribe. Check console.', 'error');
            });
        }
    }

    handleStatusChange(event) {
        console.log('Flow status: ', event.detail.status);
        if (event.detail.status === 'FINISHED' || event.detail.status === 'FINISHED_SCREEN') {
            this.showFlow = false;
            // Optionally, display a success message or perform other actions
            this.showToast('Success', 'Flow Completed!', 'success');
            console.log('Flow finished, hiding component.');
        } else if (event.detail.status === 'ERROR') {
            console.error('Flow Error: ', event.detail.error);
            this.showToast('Flow Error', 'An error occurred in the flow. ' + event.detail.error, 'error');
            // Optionally hide the flow on error too, or allow retry
            // this.showFlow = false;
        }
    }

    showToast(title, message, variant, mode = 'dismissible') {
        const event = new ShowToastEvent({
            title: title,
            message: message,
            variant: variant,
            mode: mode
        });
        this.dispatchEvent(event);
    }

    // If you intend to use this on a record page and want to react only to
    // changes on THAT specific record, you would uncomment the @api recordId
    // and add checks in the messageCallback.
    // @api recordId;
}