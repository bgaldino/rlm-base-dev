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
const NAVIGATION_DELAY_MS = 300;

// Lifecycle, in two methods:
// - start() begins one "run" for the current processId: it tears down whatever ran before,
//   resets the run's state, then subscribes to the platform event and polls the status. It does
//   nothing until the component is on the page and has a processId.
// - teardown() ends the run: it clears the poll interval and the navigation timer, releases the
//   subscription, and invalidates a subscription still being set up (it is released when it
//   resolves).
// connectedCallback() calls start(), disconnectedCallback() calls teardown(), and a new
// processId restarts. A component put back on the page after it already moved the flow on
// starts a fresh run: it re-reads the status and moves the flow on again when the status is
// final, so the screen never sits empty.
export default class RlmDocStatusMonitor extends LightningElement {
    _processId;
    @api
    get processId() {
        return this._processId;
    }
    set processId(value) {
        const changed = value !== this._processId;
        this._processId = value;
        // Flow runtimes can set an input after connectedCallback, and can set it again with the
        // same value; only a new value starts a new run.
        if (changed) {
            this.start();
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

    _connected = false;
    hasNavigated = false;
    subscription = {};
    // Incremented by teardown(): a subscription that resolves for an older run is released.
    _run = 0;
    pollTimer;
    pollStartedAt;
    navigationTimer;

    channelName = '/event/DocGenProcStsChgEvent';

    get isProcessing() {
        return this._status === PENDING_STATUS;
    }

    // Reads the status when processId is set and again each time refreshStatus() tells Lightning
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
        if (!empErrorHandlerRegistered) {
            empErrorHandlerRegistered = true;
            onError(error => {
                console.error('rlmDocStatusMonitor: EMP channel error', error);
            });
        }
        this.start();
    }

    disconnectedCallback() {
        this._connected = false;
        this.teardown();
    }

    start() {
        this.teardown();
        this.hasNavigated = false;
        this._status = PENDING_STATUS;
        if (!this._connected || !this._processId) {
            return;
        }
        const run = this._run;
        subscribe(this.channelName, -1, response => {
            const payload = response.data.payload;
            if (payload.DocGenProcessIdentifier === this._processId) {
                this.handleStatusChange(payload.Status);
            }
        })
            .then(subscription => {
                if (run !== this._run) {
                    // The run ended while subscribing: release the subscription instead of keeping it.
                    unsubscribe(subscription, () => {});
                    return;
                }
                this.subscription = subscription;
                // An event published before the subscription was live is lost: read the status now.
                this.refreshStatus();
            })
            .catch(error => {
                // EMP subscription failed — polling still advances the flow
                console.error('rlmDocStatusMonitor: EMP subscribe failed', error);
            });
        this.pollStartedAt = Date.now();
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        this.pollTimer = setInterval(() => this.poll(), POLL_INTERVAL_MS);
    }

    teardown() {
        this._run += 1;
        clearInterval(this.pollTimer);
        this.pollTimer = undefined;
        clearTimeout(this.navigationTimer);
        this.navigationTimer = undefined;
        if (this.subscription.channel) {
            unsubscribe(this.subscription, () => {});
        }
        this.subscription = {};
    }

    poll() {
        if (Date.now() - this.pollStartedAt >= MAX_WAIT_MS) {
            this.handleStatusChange(TIMED_OUT_STATUS);
            return;
        }
        this.refreshStatus();
    }

    refreshStatus() {
        notifyRecordUpdateAvailable([{ recordId: this._processId }]).catch(error => {
            // The next poll tries again; the platform event can still advance the flow.
            console.error('rlmDocStatusMonitor: status refresh failed', error);
        });
    }

    handleStatusChange(newStatus) {
        // A status that arrives after the screen is gone or after the flow moved on is ignored.
        if (!this._connected || this.hasNavigated) return;
        this._status = newStatus;
        this.dispatchEvent(new FlowAttributeChangeEvent('status', this._status));
        if (this._status !== PENDING_STATUS) {
            this.hasNavigated = true;
            this.teardown();
            // eslint-disable-next-line @lwc/lwc/no-async-operation
            this.navigationTimer = setTimeout(() => {
                this.navigationTimer = undefined;
                this.dispatchEvent(new FlowNavigationNextEvent());
            }, NAVIGATION_DELAY_MS);
        }
    }
}
