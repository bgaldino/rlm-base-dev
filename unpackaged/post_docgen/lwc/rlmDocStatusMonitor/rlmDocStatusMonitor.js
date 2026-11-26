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
// The only statuses that end the wait. The process status and the DocGenProcStsChgEvent status
// also take Waiting and Blocked (264 picklist and developer guide); those, like InProgress, keep
// the screen waiting, and MAX_WAIT_MS bounds the wait. Whether they are temporary is not measured:
// Help says requests over the throttling limits are blocked, not whether they run later.
const FINAL_STATUSES = new Set(['Success', 'Failure']);
// Reported to the flow when no final status (Success or Failure) has arrived after MAX_WAIT_MS. Any status other
// than Success takes the flow to its error screen; for TimedOut that screen says the process was
// still running and may finish, and for any other status it names the status.
const TIMED_OUT_STATUS = 'TimedOut';
// Re-read the process status this often until it is Success or Failure (todo 435): the platform
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
// processId restarts. A final status never changes, so the component remembers the one it read
// for its processId: put back on the page after it moved the flow on (or during the navigation
// delay), it moves the flow on again with that status straight away, without depending on the
// record wire re-emitting a cached value. Put back while still waiting, it starts a fresh run,
// which reads the status as soon as the subscription is live.
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
    // The final status read for _finalStatusFor (a processId).
    _finalStatus;
    _finalStatusFor;
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
            this.handleStatusChange(getFieldValue(data, STATUS_FIELD));
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
        if (this._finalStatusFor === this._processId) {
            this.finish(this._finalStatus);
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
            this.finish(TIMED_OUT_STATUS);
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

    // A status from the platform event or the record read. Only Success and Failure end the wait.
    handleStatusChange(newStatus) {
        if (!FINAL_STATUSES.has(newStatus)) return;
        this._finalStatus = newStatus;
        this._finalStatusFor = this._processId;
        this.finish(newStatus);
    }

    // Reports the outcome to the flow and moves it on, once per run.
    finish(outcome) {
        // An outcome that arrives after the screen is gone or after the flow moved on is ignored.
        if (!this._connected || this.hasNavigated) return;
        this._status = outcome;
        this.dispatchEvent(new FlowAttributeChangeEvent('status', this._status));
        this.hasNavigated = true;
        this.teardown();
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        this.navigationTimer = setTimeout(() => {
            this.navigationTimer = undefined;
            this.dispatchEvent(new FlowNavigationNextEvent());
        }, NAVIGATION_DELAY_MS);
    }
}
