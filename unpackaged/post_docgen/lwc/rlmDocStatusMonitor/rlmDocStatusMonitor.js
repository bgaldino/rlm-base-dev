import { LightningElement, api, wire } from 'lwc';
import { subscribe, unsubscribe, onError } from 'lightning/empApi';
import { getRecord, getFieldValue, notifyRecordUpdateAvailable } from 'lightning/uiRecordApi';
import { FlowAttributeChangeEvent, FlowNavigationNextEvent } from 'lightning/flowSupport';
import STATUS_FIELD from '@salesforce/schema/DocumentGenerationProcess.Status';

// Module-level flag: onError is a global EMP handler — register it only once
// regardless of how many component instances exist on the page.
let empErrorHandlerRegistered = false;

// The status a process has while the platform is still generating.
const PENDING_STATUS = 'InProgress';
// Reported to the flow when the process is still pending after MAX_WAIT_MS. Any status other
// than Success takes the flow to its error screen, which names the status.
const TIMED_OUT_STATUS = 'TimedOut';
// Re-read the process status this often until it leaves InProgress (todo 435): the platform
// event alone can be missed, because the process can finish before the EMP subscription is live
// (subscribe with replay -1 receives only later events), and the record wire reads once and
// does not refresh by itself. Measured on 264: a quote proposal finished 4 s after the
// process was created, and the screen kept spinning after Success.
const POLL_INTERVAL_MS = 2000;
const MAX_WAIT_MS = 300000;

export default class RlmDocStatusMonitor extends LightningElement {
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
        if (value && this._connected) {
            this.startPolling();
        }
    }

    // Output to the flow. A getter/setter pair, so the component can update its own public
    // property without reassigning an @api field.
    _status = PENDING_STATUS;
    @api
    get status() {
        return this._status;
    }
    set status(value) {
        this._status = value;
    }
    hasNavigated = false;
    subscription = {};
    _connected = false;
    pollTimer;
    pollStartedAt;

    channelName = '/event/DocGenProcStsChgEvent';

    get isProcessing() {
        return this._status === PENDING_STATUS;
    }

    // Reads the status when processId is set and again each time startPolling() tells Lightning
    // Data Service the record may have changed.
    @wire(getRecord, { recordId: '$processId', fields: [STATUS_FIELD] })
    wiredDgp({ data }) {
        if (data) {
            const polledStatus = getFieldValue(data, STATUS_FIELD);
            if (polledStatus && polledStatus !== PENDING_STATUS) {
                this.handleStatusChange(polledStatus);
            }
        }
    }

    connectedCallback() {
        this._connected = true;
        if (!empErrorHandlerRegistered) {
            empErrorHandlerRegistered = true;
            onError(error => {
                console.error('rlmDocStatusMonitor: EMP channel error', error);
            });
        }
        // processId setter handles subscription when value is already set;
        // the setter also fires if processId is assigned after connectedCallback.
        if (this.processId) {
            this.startPolling();
        }
    }

    disconnectedCallback() {
        this._connected = false;
        this.stopPolling();
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
                // An event published before the subscription was live is lost: read the status now.
                this.refreshStatus();
            })
            .catch(error => {
                // EMP subscription failed — polling still advances the flow
                console.error('rlmDocStatusMonitor: EMP subscribe failed', error);
            });
    }

    startPolling() {
        if (this.pollTimer || this.hasNavigated) {
            return;
        }
        this.pollStartedAt = Date.now();
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        this.pollTimer = setInterval(() => this.poll(), POLL_INTERVAL_MS);
    }

    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = undefined;
        }
    }

    poll() {
        if (this.hasNavigated) {
            this.stopPolling();
            return;
        }
        if (Date.now() - this.pollStartedAt >= MAX_WAIT_MS) {
            this.stopPolling();
            this.handleStatusChange(TIMED_OUT_STATUS);
            return;
        }
        this.refreshStatus();
    }

    refreshStatus() {
        if (!this.processId || this.hasNavigated) {
            return;
        }
        notifyRecordUpdateAvailable([{ recordId: this.processId }]).catch(error => {
            // The next poll tries again; the platform event can still advance the flow.
            console.error('rlmDocStatusMonitor: status refresh failed', error);
        });
    }

    handleStatusChange(newStatus) {
        if (this.hasNavigated) return;
        this._status = newStatus;
        this.dispatchEvent(new FlowAttributeChangeEvent('status', this._status));
        if (this._status !== PENDING_STATUS) {
            this.hasNavigated = true;
            this.stopPolling();
            this.handleNext();
        }
    }

    handleNext() {
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        setTimeout(() => {
            this.dispatchEvent(new FlowNavigationNextEvent());
        }, 300);
    }
}
