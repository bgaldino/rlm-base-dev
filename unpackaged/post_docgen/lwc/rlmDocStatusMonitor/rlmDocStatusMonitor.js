import { LightningElement, api } from 'lwc';
import { subscribe, unsubscribe, onError } from 'lightning/empApi';
import { FlowAttributeChangeEvent, FlowNavigationNextEvent } from 'lightning/flowSupport';

export default class RlmDocStatusMonitor extends LightningElement {
    @api processId;
    @api status = 'InProgress';
    hasNavigated = false;
    subscription = {};

    channelName = '/event/DocGenProcStsChgEvent';

    get isProcessing() {
        return this.status === 'InProgress';
    }

    connectedCallback() {
        if (this.processId) {
            this.handleSubscribe();
        }
    }

    disconnectedCallback() {
        if (this.subscription && this.subscription.channel) {
            unsubscribe(this.subscription, () => {});
        }
    }

    handleSubscribe() {
        const messageCallback = (response) => {
            const eventId = response.data.payload.DocGenProcessIdentifier;
            const eventStatus = response.data.payload.Status;

            if (eventId === this.processId) {
                this.status = eventStatus;
                this.dispatchEvent(new FlowAttributeChangeEvent('status', this.status));

                if (this.status !== 'InProgress' && !this.hasNavigated) {
                    this.hasNavigated = true;
                    this.handleNext();
                }
            }
        };

        subscribe(this.channelName, -1, messageCallback)
            .then(response => {
                this.subscription = response;
            })
            .catch(error => {
                console.error('rlmDocStatusMonitor: EMP API subscribe error', error);
            });

        onError(error => {
            console.error('rlmDocStatusMonitor: EMP API error', error);
        });
    }

    handleNext() {
        setTimeout(() => {
            this.dispatchEvent(new FlowNavigationNextEvent());
        }, 300);
    }
}
