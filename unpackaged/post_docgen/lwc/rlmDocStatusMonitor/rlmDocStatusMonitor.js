import { LightningElement, api, wire } from 'lwc';
import { subscribe, unsubscribe, onError } from 'lightning/empApi';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import { FlowAttributeChangeEvent, FlowNavigationNextEvent } from 'lightning/flowSupport';
import STATUS_FIELD from '@salesforce/schema/DocumentGenerationProcess.Status';

const POLL_INTERVAL_MS = 3000;

export default class RlmDocStatusMonitor extends LightningElement {
    @api processId;
    @api status = 'InProgress';
    hasNavigated = false;
    subscription = {};
    pollTimer;

    channelName = '/event/DocGenProcStsChgEvent';

    get isProcessing() {
        return this.status === 'InProgress';
    }

    // Poll fallback: wire to DGP record and advance if no longer InProgress
    @wire(getRecord, { recordId: '$processId', fields: [STATUS_FIELD] })
    wiredDgp({ data }) {
        if (data) {
            const polledStatus = getFieldValue(data, STATUS_FIELD);
            if (polledStatus && polledStatus !== 'InProgress') {
                this.handleStatusChange(polledStatus);
            }
        }
    }

    connectedCallback() {
        if (this.processId) {
            this.handleSubscribe();
        }
    }

    disconnectedCallback() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
        }
        if (this.subscription && this.subscription.channel) {
            unsubscribe(this.subscription, () => {});
        }
    }

    handleSubscribe() {
        const messageCallback = (response) => {
            const eventId = response.data.payload.DocGenProcessIdentifier;
            const eventStatus = response.data.payload.Status;
            if (eventId === this.processId) {
                this.handleStatusChange(eventStatus);
            }
        };

        subscribe(this.channelName, -1, messageCallback)
            .then(response => {
                this.subscription = response;
            })
            .catch(() => {});

        onError(() => {});
    }

    handleStatusChange(newStatus) {
        if (this.hasNavigated) return;
        this.status = newStatus;
        this.dispatchEvent(new FlowAttributeChangeEvent('status', this.status));
        if (this.status !== 'InProgress') {
            this.hasNavigated = true;
            this.handleNext();
        }
    }

    handleNext() {
        setTimeout(() => {
            this.dispatchEvent(new FlowNavigationNextEvent());
        }, 300);
    }
}
