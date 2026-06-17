import { LightningElement, api, wire, track } from 'lwc';
import { getRecord, notifyRecordUpdateAvailable } from 'lightning/uiRecordApi';
import { NavigationMixin } from 'lightning/navigation';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import getInvoiceStatusCounts from '@salesforce/apex/RLM_InvoiceBatchRunMonitorController.getInvoiceStatusCounts';

const FIELDS = [
    'InvoiceBatchRun.InvoiceBatchRunNumber',
    'InvoiceBatchRun.Status',
    'InvoiceBatchRun.StatusSubtype',
    'InvoiceBatchRun.StartTime',
    'InvoiceBatchRun.CompletionTime',
    'InvoiceBatchRun.TotalFilteredBillingSchedules',
    'InvoiceBatchRun.TotalBsSuccessfullyProcessed',
    'InvoiceBatchRun.TotalBillingSchedulesFailed',
    'InvoiceBatchRun.TotalInvoicesGenerated',
    'InvoiceBatchRun.TotalInvSuccessfullyProcessed',
    'InvoiceBatchRun.TotalInvoicesFailed',
    'InvoiceBatchRun.TotalInvoicesCanceled',
    'InvoiceBatchRun.TotalDraftInvoices',
    'InvoiceBatchRun.TotalPostedInvoices',
    'InvoiceBatchRun.TotalInvoicedAmount',
    'InvoiceBatchRun.TotalDraftInvoiceAmount',
    'InvoiceBatchRun.DocGenStatus',
    'InvoiceBatchRun.InvoiceDocsGenerated',
    'InvoiceBatchRun.InvoiceDocsGenFailed',
    'InvoiceBatchRun.RecoveryStatus',
    'InvoiceBatchRun.CreditApplicationStatus',
    'InvoiceBatchRun.BatchJobId'
];

const SUBTYPE_PROGRESS = {
    'Billing Schedules Filtering Started':          { milestone: 1, sub: 'Started', pct: 10 },
    'Billing Schedules Filtering In Progress':      { milestone: 1, sub: 'In Progress', pct: 18 },
    'Billing Schedules Filtering Completed':        { milestone: 1, sub: 'Completed', pct: 25 },
    'Invoice Generation Started':                   { milestone: 2, sub: 'Started', pct: 33 },
    'Invoice Generation In Progress':               { milestone: 2, sub: 'In Progress', pct: 42 },
    'Invoice Generation Completed':                 { milestone: 2, sub: 'Completed', pct: 50 },
    'Invoice Generation Summarization In Progress': { milestone: 3, sub: 'In Progress', pct: 75 },
    'Completed':                                    { milestone: 4, sub: 'Completed', pct: 100 },
    'Failed':                                       { milestone: 4, sub: 'Failed', pct: 100 }
};

const MILESTONE_LABELS = [
    'Started',
    'Filtering Billing Schedules',
    'Generating Invoices',
    'Summarizing Run',
    'Completed'
];

const POLL_INTERVAL_MS = 2000;

export default class RlmInvoiceBatchRunMonitor extends NavigationMixin(LightningElement) {
    @api recordId;

    @track runData = null;
    error = null;
    _recordPollTimer = null;
    _invoicePollTimer = null;

    summaryExpanded = false;

    @track _liveInvoiceCounts = { Draft: 0, Pending: 0, Posted: 0, Error: 0 };

    _lastRecordData = null;
    _ibrIsRunning = false;
    _batchJobId = null;
    _prevCounts = { draft: -1, posting: -1, posted: -1, error: -1 };
    _changedFlags = { draft: false, posting: false, posted: false, error: false };

    get summaryChevron() { return this.summaryExpanded ? 'utility:chevrondown' : 'utility:chevronright'; }

    toggleSummary() {
        this.summaryExpanded = !this.summaryExpanded;
    }

    handleSummaryKeydown(event) {
        if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
            event.preventDefault();
            this.toggleSummary();
        }
    }

    connectedCallback() {
        this.startInvoicePoll();
    }

    disconnectedCallback() {
        this.stopAllTimers();
    }

    startInvoicePoll() {
        if (this._invoicePollTimer) return;
        this.fetchInvoiceCounts();
        this._invoicePollTimer = setInterval(() => {
            this.fetchInvoiceCounts();
        }, POLL_INTERVAL_MS);
    }

    stopAllTimers() {
        if (this._recordPollTimer) {
            clearInterval(this._recordPollTimer);
            this._recordPollTimer = null;
        }
        if (this._invoicePollTimer) {
            clearInterval(this._invoicePollTimer);
            this._invoicePollTimer = null;
        }
    }

    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    wiredRecord({ data, error }) {
        if (data) {
            this.error = null;
            this._lastRecordData = data;
            this.buildRunData();
            this.manageRecordPoll();
        } else if (error) {
            this.error = error.body?.message || 'Unable to load record';
            this.runData = null;
        }
    }

    fetchInvoiceCounts() {
        if (!this.recordId) return;
        getInvoiceStatusCounts({ invoiceBatchRunId: this.recordId })
            .then(result => {
                this._liveInvoiceCounts = result || { Draft: 0, Pending: 0, Posted: 0, Error: 0 };
                this.buildRunData();
            })
            .catch(() => {});
    }

    buildRunData() {
        if (!this._lastRecordData) return;
        const data = this._lastRecordData;
        const f = data.fields;
        const status = f.Status?.value || '';
        const subtype = f.StatusSubtype?.value || '';
        const startTime = f.StartTime?.value;
        const completionTime = f.CompletionTime?.value;

        const defaultProgress = (!subtype && status === 'Started')
            ? { milestone: 0, sub: 'Completed', pct: 5 }
            : { milestone: -1, sub: '', pct: 0 };
        const progress = SUBTYPE_PROGRESS[subtype] || defaultProgress;
        const isFailed = subtype === 'Failed' || status === 'Failed';
        const isCompleted = subtype === 'Completed' || status === 'Completed';
        const isRunning = !isFailed && !isCompleted;
        this._ibrIsRunning = isRunning;

        const totalBS = f.TotalFilteredBillingSchedules?.value || 0;
        const successBS = f.TotalBsSuccessfullyProcessed?.value || 0;
        const failedBS = f.TotalBillingSchedulesFailed?.value || 0;
        const totalInv = f.TotalInvoicesGenerated?.value || 0;
        const successInv = f.TotalInvSuccessfullyProcessed?.value || 0;
        const failedInv = f.TotalInvoicesFailed?.value || 0;
        const cancelledInv = f.TotalInvoicesCanceled?.value || 0;
        const draftInv = f.TotalDraftInvoices?.value || 0;
        const postedInv = f.TotalPostedInvoices?.value || 0;
        const totalAmount = f.TotalInvoicedAmount?.value || 0;
        const draftAmount = f.TotalDraftInvoiceAmount?.value || 0;
        const docsGen = f.InvoiceDocsGenerated?.value || 0;
        const docsFailed = f.InvoiceDocsGenFailed?.value || 0;
        const docGenStatus = f.DocGenStatus?.value || '';
        const recoveryStatus = f.RecoveryStatus?.value || '';
        const creditStatus = f.CreditApplicationStatus?.value || '';
        this._batchJobId = f.BatchJobId?.value || null;

        const elapsed = this.calcElapsed(startTime, completionTime, isRunning);

        const milestones = MILESTONE_LABELS.map((label, i) => {
            let state = 'pending';
            let subLabel = '';

            if (i < progress.milestone) {
                state = 'completed';
            } else if (i === progress.milestone) {
                if (i === 4) {
                    state = isFailed ? 'failed' : 'completed';
                } else if (progress.sub === 'Completed') {
                    state = 'completed';
                } else {
                    state = 'active';
                    subLabel = progress.sub;
                }
            }

            const displayLabel = (i === 4 && isFailed) ? 'Failed' : label;

            return {
                label: displayLabel,
                index: i,
                state,
                subLabel,
                hasSubLabel: !!subLabel,
                isCompleted: state === 'completed',
                isActive: state === 'active',
                isFailed: state === 'failed',
                isPending: state === 'pending',
                cssClass: `phase-step ${state}`,
                dotClass: `step-dot ${state}`
            };
        });

        const lc = this._liveInvoiceCounts;
        const liveDraft = lc.Draft || 0;
        const livePosting = lc.Pending || 0;
        const livePosted = lc.Posted || 0;
        const liveError = lc.Error || 0;
        const liveTotal = liveDraft + livePosting + livePosted + liveError;

        const prev = this._prevCounts;
        const isFirstLoad = prev.draft === -1;
        this._changedFlags = {
            draft: !isFirstLoad && liveDraft !== prev.draft,
            posting: !isFirstLoad && livePosting !== prev.posting,
            posted: !isFirstLoad && livePosted !== prev.posted,
            error: !isFirstLoad && liveError !== prev.error
        };
        this._prevCounts = { draft: liveDraft, posting: livePosting, posted: livePosted, error: liveError };

        const cf = this._changedFlags;
        const countBase = 'inv-flow-count';

        this.runData = {
            status, subtype, isFailed, isCompleted, isRunning,
            progressPct: isFailed ? 100 : progress.pct,
            progressStyle: `width: ${isFailed ? 100 : progress.pct}%`,
            barClass: isFailed ? 'progress-fill failed' : isCompleted ? 'progress-fill completed' : 'progress-fill running',
            milestones,
            elapsed,
            startFormatted: this.fmtDateTime(startTime),
            completionFormatted: completionTime ? this.fmtDateTime(completionTime) : (isRunning ? 'In Progress...' : '—'),
            totalBS, successBS, failedBS,
            bsHasFailures: failedBS > 0,
            bsStatusLabel: failedBS > 0 ? `${failedBS} failed` : 'Success',
            bsStatusClass: failedBS > 0 ? 'metric-card-rate-error' : 'metric-card-rate',
            totalInv, successInv, failedInv, cancelledInv, draftInv, postedInv,
            invHasFailures: failedInv > 0,
            invStatusLabel: failedInv > 0 ? `${failedInv} failed` : 'Success',
            invStatusClass: failedInv > 0 ? 'metric-card-rate-error' : 'metric-card-rate',
            totalAmountFmt: this.fmtCurrency(totalAmount),
            draftAmountFmt: this.fmtCurrency(draftAmount),
            failedBSClass: failedBS > 0 ? 'metric-val danger' : 'metric-val',
            failedInvClass: failedInv > 0 ? 'metric-val danger' : 'metric-val',
            docsGen, docsFailed, docGenStatus,
            hasDocGen: docsGen > 0 || docsFailed > 0 || !!docGenStatus,
            recoveryStatus: recoveryStatus || '—',
            creditStatus: creditStatus || '—',
            hasRecovery: !!recoveryStatus,
            hasCredits: !!creditStatus,
            liveDraft,
            livePosting,
            livePosted,
            liveError,
            liveTotal,
            invFlowClass: isRunning ? 'inv-flow inv-flow-active' : 'inv-flow',
            draftCountClass: cf.draft ? `${countBase} count-changed` : countBase,
            postingCountClass: cf.posting ? `${countBase} count-changed` : countBase,
            postedCountClass: cf.posted ? `${countBase} count-changed` : countBase,
            errorCountClass: cf.error ? `${countBase} count-changed` : countBase,
            hasErrors: liveError > 0,
            hasInvoiceActivity: liveTotal > 0,
            showInvoiceStats: isRunning || liveTotal > 0,
            summaryReady: isCompleted || isFailed
        };

        if (!isRunning) {
            if (this._invoicePollTimer) {
                clearInterval(this._invoicePollTimer);
                this._invoicePollTimer = null;
            }
        }
    }

    calcElapsed(start, end, isRunning) {
        if (!start) return '—';
        const s = new Date(start);
        const e = end ? new Date(end) : new Date();
        const diffMs = e - s;
        if (diffMs < 0) return '—';
        const mins = Math.floor(diffMs / 60000);
        const secs = Math.floor((diffMs % 60000) / 1000);
        if (mins > 60) {
            const hrs = Math.floor(mins / 60);
            const remMins = mins % 60;
            return `${hrs}h ${remMins}m${isRunning ? ' (running)' : ''}`;
        }
        return `${mins}m ${secs}s${isRunning ? ' (running)' : ''}`;
    }

    fmtDateTime(val) {
        if (!val) return '—';
        return new Date(val).toLocaleString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric',
            hour: 'numeric', minute: '2-digit', hour12: true
        });
    }

    fmtCurrency(val) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(val);
    }

    manageRecordPoll() {
        if (this._ibrIsRunning && !this._recordPollTimer) {
            this._recordPollTimer = setInterval(() => {
                notifyRecordUpdateAvailable([{ recordId: this.recordId }]);
            }, POLL_INTERVAL_MS);
        }
        if (!this._ibrIsRunning && this._recordPollTimer) {
            clearInterval(this._recordPollTimer);
            this._recordPollTimer = null;
        }
    }

    handleMonitorBatchJob() {
        if (!this._batchJobId) {
            this.dispatchEvent(new ShowToastEvent({
                title: 'Batch Job Not Available',
                message: 'Please wait for the Batch Job to be initiated, try again after some time.',
                variant: 'warning'
            }));
            return;
        }
        this[NavigationMixin.Navigate]({
            type: 'standard__webPage',
            attributes: {
                url: `/lightning/setup/MonitorWorkflowServices/${this._batchJobId}/BatchJobs/view`
            }
        });
    }

    get hasData() {
        return !!this.runData;
    }
}