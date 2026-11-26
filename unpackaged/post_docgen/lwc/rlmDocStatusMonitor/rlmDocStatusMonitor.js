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
// than Success takes the flow to its error screen; for TimedOut that screen says the process was
// still running and may finish, and for any other status it names the status.
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
        if (value) {
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
    // Set once the component is removed, so a subscription that resolves afterwards is released.
    _disconnected = false;
    _subscribing = false;
    pollTimer;
    pollStartedAt;
    navigationTimer;

    channelName = '/event/DocGenProcStsChgEvent';

    get isProcessing() {
        return this._status === PENDING_STATUS;
    }

    // Reads the status when processId is set and again each time startPolling() tells Lightning
    // Data Service the record may have changed.
    @wire(getRecord, { recordId: '$processId', fields: [STATUS_FIELD] })
    wiredDgp({ data, error }) {
        if (error) {
            // A refused or failed read (for example, no access to the process record): polling keeps
            // trying and the platform event can still advance the flow, so log it rather than stop.
            console.error('rlmDocStatusMonitor: status read failed', error);
            return;
        }
        if (data) {
            const polledStatus = getFieldValue(data, STATUS_FIELD);
            if (polledStatus && polledStatus !== PENDING_STATUS) {
                this.handleStatusChange(polledStatus);
            }
        }
    }

    connectedCallback() {
        this._connected = true;
        this._disconnected = false;
        if (!empErrorHandlerRegistered) {
            empErrorHandlerRegistered = true;
            onError(error => {
                console.error('rlmDocStatusMonitor: EMP channel error', error);
            });
        }
        // The processId setter subscribes and polls when the value arrives after this point.
        // Here: an id that was set before the component was (re)inserted.
        if (this.processId) {
            this.handleSubscribe();
            this.startPolling();
        }
    }

    disconnectedCallback() {
        this._connected = false;
        this._disconnected = true;
        this.stopPolling();
        if (this.navigationTimer) {
            clearTimeout(this.navigationTimer);
            this.navigationTimer = undefined;
        }
        if (this.subscription && this.subscription.channel) {
            unsubscribe(this.subscription, () => {});
            this.subscription = {};
        }
    }

    handleSubscribe() {
        // One subscription per component: none while one is live or still being set up.
        if (this._subscribing || (this.subscription && this.subscription.channel)) {
            return;
        }
        this._subscribing = true;
        const messageCallback = (response) => {
            const eventId = response.data.payload.DocGenProcessIdentifier;
            const eventStatus = response.data.payload.Status;
            if (eventId === this.processId) {
                this.handleStatusChange(eventStatus);
            }
        };

        subscribe(this.channelName, -1, messageCallback)
            .then(response => {
                this._subscribing = false;
                if (this._disconnected) {
                    // Removed while subscribing: release the subscription instead of keeping it.
                    unsubscribe(response, () => {});
                    return;
                }
                this.subscription = response;
                // An event published before the subscription was live is lost: read the status now.
                this.refreshStatus();
            })
            .catch(error => {
                this._subscribing = false;
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

    // Runs only while the interval is live: handleStatusChange() clears it before it sets
    // hasNavigated, and startPolling() starts none after navigation.
    poll() {
        if (Date.now() - this.pollStartedAt >= MAX_WAIT_MS) {
            this.stopPolling();
            this.handleStatusChange(TIMED_OUT_STATUS);
            return;
        }
        this.refreshStatus();
    }

    // Called by poll() (its interval is cleared on removal and on navigation) and once the EMP
    // subscription is live (that callback returns early after removal). A subscription can still
    // resolve after the flow moved on, hence the hasNavigated check.
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
        // Nothing to report once the flow has moved on or the screen is gone.
        if (this.hasNavigated || this._disconnected) return;
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
        this.navigationTimer = setTimeout(() => {
            this.navigationTimer = undefined;
            this.dispatchEvent(new FlowNavigationNextEvent());
        }, 300);
    }
}
