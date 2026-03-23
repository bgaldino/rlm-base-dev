import { LightningElement, api } from 'lwc';
import { FlowNavigationFinishEvent } from 'lightning/flowSupport';
import getJobStatus from '@salesforce/apex/RLM_RampScheduleStatusController.getJobStatus';
// import getQuoteStatus from '@salesforce/apex/RLM_RampScheduleStatusController.getQuoteStatus'; // TODO: re-enable for CompletedWithTax polling

const POLL_INTERVAL_MS = 3000;
const AUTO_CLOSE_DELAY_MS = 2000;

// Phases
const PHASE_JOB   = 'job';    // Waiting for Queueable to finish
// const PHASE_QUOTE = 'quote';  // TODO: Waiting for CompletedWithTax (repricing)
const PHASE_DONE  = 'done';
const PHASE_ERROR = 'error';

export default class RlmRampScheduleStatus extends LightningElement {
    /** AsyncApexJob ID returned by the Apex action */
    @api jobId;
    /** Quote record ID — reserved for phase 2 quote polling */
    @api quoteId;
    /** Display name of the quote for the success message */
    @api quoteName;

    _phase = PHASE_JOB;
    _intervalId = null;
    _errorMessage = '';

    // ── Lifecycle ──────────────────────────────────────────────────────────

    connectedCallback() {
        this._startPolling();
    }

    disconnectedCallback() {
        this._stopPolling();
    }

    // ── Getters for template ───────────────────────────────────────────────

    get isPhaseJob() {
        return this._phase === PHASE_JOB;
    }

    get isDone() {
        return this._phase === PHASE_DONE;
    }

    get isError() {
        return this._phase === PHASE_ERROR;
    }

    get isPolling() {
        return this._phase === PHASE_JOB;
    }

    get statusLabel() {
        if (this._phase === PHASE_JOB)  return 'Configuring ramp segments\u2026';
        if (this._phase === PHASE_DONE) return 'Ramp Schedule Ready';
        return 'Error';
    }

    get errorMessage() {
        return this._errorMessage;
    }

    get quoteDisplayName() {
        return this.quoteName || this.quoteId || 'the quote';
    }

    // ── Polling logic ──────────────────────────────────────────────────────

    _startPolling() {
        this._poll(); // immediate first check
        this._intervalId = setInterval(() => this._poll(), POLL_INTERVAL_MS);
    }

    _stopPolling() {
        if (this._intervalId !== null) {
            clearInterval(this._intervalId);
            this._intervalId = null;
        }
    }

    async _poll() {
        try {
            if (this._phase === PHASE_JOB) {
                await this._pollJob();
            }
            // TODO: add PHASE_QUOTE here once CompletedWithTax repricing is confirmed working
        } catch (e) {
            // Network / Apex errors are transient — keep polling
            console.warn('RlmRampScheduleStatus poll error:', e);
        }
    }

    async _pollJob() {
        // DML path (default): no jobId — groups were created synchronously, go straight to done.
        if (!this.jobId) {
            this._setDone();
            return;
        }

        const result = await getJobStatus({ jobId: this.jobId });
        const status = (result && result.status) ? result.status : 'Unknown';

        if (status === 'Completed') {
            // TODO: transition to PHASE_QUOTE to wait for CompletedWithTax once repricing is confirmed
            this._setDone();
        } else if (status === 'Failed' || status === 'Aborted') {
            this._setError(
                'The ramp setup job encountered an error. ' +
                (result.extendedStatus || 'Please check the Apex Jobs log for details.')
            );
        }
        // Queued / Preparing / Processing → keep waiting
    }

    /* TODO: re-enable once CompletedWithTax repricing is confirmed working
    async _pollQuote() {
        const result = await getQuoteStatus({ quoteId: this.quoteId });
        const calcStatus  = (result && result.calculationStatus) ? result.calculationStatus : '';
        const validResult = (result && result.validationResult)  ? result.validationResult  : '';

        if (validResult === 'Transaction Incomplete') {
            this._seenTransactionIncomplete = true;
        }

        const isFullyPriced = calcStatus === 'CompletedWithTax';
        const needsReprice  = validResult === 'Transaction Incomplete';

        if (isFullyPriced && !needsReprice && this._seenTransactionIncomplete) {
            this._setDone();
        }
    }
    */

    _setDone() {
        this._stopPolling();
        this._phase = PHASE_DONE;
        // Auto-close the Flow after a brief moment to let the user see the success state
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        setTimeout(() => {
            this.dispatchEvent(new FlowNavigationFinishEvent());
        }, AUTO_CLOSE_DELAY_MS);
    }

    _setError(message) {
        this._stopPolling();
        this._phase = PHASE_ERROR;
        this._errorMessage = message;
    }

    // ── User actions ───────────────────────────────────────────────────────

    handleClose() {
        this.dispatchEvent(new FlowNavigationFinishEvent());
    }
}
