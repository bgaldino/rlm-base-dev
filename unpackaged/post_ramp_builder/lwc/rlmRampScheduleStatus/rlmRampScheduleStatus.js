import { LightningElement, api } from 'lwc';
import { FlowNavigationFinishEvent } from 'lightning/flowSupport';
import getJobStatus from '@salesforce/apex/RLM_RampScheduleStatusController.getJobStatus';
import getQuoteStatus from '@salesforce/apex/RLM_RampScheduleStatusController.getQuoteStatus';

const POLL_INTERVAL_MS = 3000;
const AUTO_CLOSE_DELAY_MS = 2000;

// Phases
const PHASE_JOB   = 'job';    // Waiting for Queueable to finish
const PHASE_QUOTE = 'quote';  // Waiting for CompletedWithTax
const PHASE_DONE  = 'done';
const PHASE_ERROR = 'error';

export default class RlmRampScheduleStatus extends LightningElement {
    /** AsyncApexJob ID returned by the Apex action */
    @api jobId;
    /** Quote record ID — used for phase 2 polling */
    @api quoteId;
    /** Display name of the quote for the success message */
    @api quoteName;

    _phase = PHASE_JOB;
    _intervalId = null;
    _errorMessage = '';
    _seenTransactionIncomplete = false;

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

    get isPhaseQuote() {
        return this._phase === PHASE_QUOTE;
    }

    get isDone() {
        return this._phase === PHASE_DONE;
    }

    get isError() {
        return this._phase === PHASE_ERROR;
    }

    get isPolling() {
        return this._phase === PHASE_JOB || this._phase === PHASE_QUOTE;
    }

    get statusLabel() {
        if (this._phase === PHASE_JOB)   return 'Configuring ramp segments\u2026';
        if (this._phase === PHASE_QUOTE) return 'Waiting for repricing to complete\u2026';
        if (this._phase === PHASE_DONE)  return 'Ramp Schedule Ready';
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
            } else if (this._phase === PHASE_QUOTE) {
                await this._pollQuote();
            }
        } catch (e) {
            // Network / Apex errors are transient — keep polling
            console.warn('RlmRampScheduleStatus poll error:', e);
        }
    }

    async _pollJob() {
        // If no jobId was supplied (e.g. DML path), skip straight to quote poll
        if (!this.jobId) {
            this._transitionToQuotePhase();
            return;
        }

        const result = await getJobStatus({ jobId: this.jobId });
        const status = (result && result.status) ? result.status : 'Unknown';

        if (status === 'Completed') {
            this._transitionToQuotePhase();
        } else if (status === 'Failed' || status === 'Aborted') {
            this._setError(
                'The ramp setup job encountered an error. ' +
                (result.extendedStatus || 'Please check the Apex Jobs log for details.')
            );
        }
        // Queued / Preparing / Processing → keep waiting
    }

    async _pollQuote() {
        const result = await getQuoteStatus({ quoteId: this.quoteId });
        const calcStatus    = (result && result.calculationStatus) ? result.calculationStatus : '';
        const validResult   = (result && result.validationResult)  ? result.validationResult  : '';

        // Track that the queueable restructured the quote (indicated by Transaction Incomplete)
        if (validResult === 'Transaction Incomplete') {
            this._seenTransactionIncomplete = true;
        }

        const isFullyPriced = calcStatus === 'CompletedWithTax';
        const needsReprice  = validResult === 'Transaction Incomplete';

        // Success: fully priced AND NOT waiting for another reprice cycle
        // Also require that we've seen Transaction Incomplete at least once to avoid
        // prematurely succeeding if the quote was already CompletedWithTax before the
        // queueable made any changes.
        if (isFullyPriced && !needsReprice && this._seenTransactionIncomplete) {
            this._setDone();
        }
    }

    _transitionToQuotePhase() {
        this._phase = PHASE_QUOTE;
        // Do an immediate quote poll without waiting for the next interval tick
        this._pollQuote().catch(() => {});
    }

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
