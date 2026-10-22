import { LightningElement, api, wire } from 'lwc';
import { subscribe, unsubscribe, onError } from 'lightning/empApi';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import { refreshApex } from '@salesforce/apex';
import { NavigationMixin } from 'lightning/navigation';
import FORM_FACTOR from '@salesforce/client/formFactor';
import {
    FlowAttributeChangeEvent,
    FlowNavigationNextEvent,
    FlowNavigationFinishEvent
} from 'lightning/flowSupport';
import STATUS_FIELD from '@salesforce/schema/DocumentGenerationProcess.Status';
import REFERENCE_FIELD from '@salesforce/schema/DocumentGenerationProcess.ReferenceObject';

const MOBILE_RETURN_DELAY_MS = 2500;

// Module-level flag: onError is a global EMP handler — register it only once
// regardless of how many component instances exist on the page.
let empErrorHandlerRegistered = false;

export default class RlmDocStatusMonitor extends NavigationMixin(LightningElement) {
    @api availableActions = [];
    isMobile = FORM_FACTOR !== 'Large';
    referenceId;
    returned = false;

    // Use a setter so EMP subscribes even if processId is assigned after connectedCallback
    // (Flow components can set @api inputs post-lifecycle in some runtimes).
    _processId;
    @api
    get processId() {
        return this._processId;
    }
    set processId(value) {
        this._processId = value;
        // Subscribe only if not already subscribed (subscription.channel is set on success)
        if (value && !(this.subscription && this.subscription.channel)) {
            this.handleSubscribe();
        }
    }

    @api status = 'InProgress';
    hasNavigated = false;
    subscription = {};

    channelName = '/event/DocGenProcStsChgEvent';

    get isProcessing() {
        return this.status === 'InProgress';
    }

    // Wire fallback: @wire re-evaluates when processId changes and whenever LDS refreshes.
    // This ensures the flow advances even if the EMP platform event subscription drops.
    @wire(getRecord, { recordId: '$processId', fields: [STATUS_FIELD], optionalFields: [REFERENCE_FIELD] })
    wiredDgp(result) {
        this.wiredResult = result;
        const { data } = result;
        if (data) {
            this.referenceId = getFieldValue(data, REFERENCE_FIELD) || this.referenceId;
            const polledStatus = getFieldValue(data, STATUS_FIELD);
            if (polledStatus && polledStatus !== 'InProgress') {
                this.handleStatusChange(polledStatus);
            }
        }
    }

    connectedCallback() {
        if (!empErrorHandlerRegistered) {
            empErrorHandlerRegistered = true;
            onError(error => {
                // eslint-disable-next-line no-console
                console.error('rlmDocStatusMonitor: EMP channel error', error);
            });
        }
        // processId setter handles subscription when value is already set;
        // the setter also fires if processId is assigned after connectedCallback.
        if (this.isMobile) {
            // The mobile app never receives the completion event; generation finishes
            // server-side, so leave the flow instead of waiting on it.
            // eslint-disable-next-line @lwc/lwc/no-async-operation
            this.returnTimer = setTimeout(() => this.returnToRecord(), MOBILE_RETURN_DELAY_MS);
            return;
        }
        // empApi is unavailable in the Salesforce mobile app, so poll as well.
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        this.pollTimer = setInterval(() => {
            if (this.hasNavigated) {
                clearInterval(this.pollTimer);
                return;
            }
            if (this.wiredResult) {
                refreshApex(this.wiredResult);
            }
        }, 3000);
    }

    returnToRecord() {
        if (this.returned) return;
        clearTimeout(this.returnTimer);
        if (!this.referenceId) {
            // Quote Id not loaded yet; try again shortly.
            // eslint-disable-next-line @lwc/lwc/no-async-operation
            this.returnTimer = setTimeout(() => this.returnToRecord(), 1000);
            return;
        }
        this.returned = true;
        if ((this.availableActions || []).includes('FINISH')) {
            this.dispatchEvent(new FlowNavigationFinishEvent());
        }
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: { recordId: this.referenceId, actionName: 'view' }
        });
    }

    disconnectedCallback() {
        clearInterval(this.pollTimer);
        clearTimeout(this.returnTimer);
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
            .catch(error => {
                // EMP subscription failed — wire fallback above will still advance the flow
                // eslint-disable-next-line no-console
                console.error('rlmDocStatusMonitor: EMP subscribe failed', error);
            });
    }

    handleStatusChange(newStatus) {
        if (this.hasNavigated || this.returned) return;
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
