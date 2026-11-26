import { LightningElement, api, wire } from 'lwc';
import getInvoiceSummary from '@salesforce/apex/RLM_InvoiceSummaryController.getInvoiceSummary';
import getBillingSummary from '@salesforce/apex/RLM_OnAccountBillingController.getBillingSummary';

const ARROW_TIP = 14;

const SEG_COLORS = {
    current: '#5B91C7',
    debit: '#D4A017',
    dispute: '#E87722',
    overdue: '#C94444',
    promise: '#8B4C6A',
    paid: '#5B9E5B'
};

// A status count the server could not read comes back null; it stays null rather than reading as 0.
const countOrNull = (value) => (value == null ? null : Number(value));

// Every balance part read and zero: a zero net alone could be a debit memo offset by a payment.
const BALANCE_PARTS = ['invoiceBalance', 'debitMemoBalance', 'creditMemoBalance', 'paymentBalance', 'refundBalance'];
const allBalancesZero = (summary) => BALANCE_PARTS.every((key) => summary[key] != null && Number(summary[key]) === 0);

// Shown for a balance whose read was refused (null from the server), never a zero.
const UNAVAILABLE = 'Unavailable';

export default class RlmAccountBalanceCard extends LightningElement {
    _recordId;

    // A new record starts a new load: both wires count as pending again, so the spinner shows, and
    // the previous record's figures and errors are cleared until the new results land.
    @api
    get recordId() { return this._recordId; }
    set recordId(value) {
        if (value !== this._recordId) {
            this._invoiceReady = false;
            this._billingReady = false;
            this.isLoading = true;
            this.invoiceData = undefined;
            this.billingData = undefined;
            this.invoiceError = undefined;
            this.billingError = undefined;
        }
        this._recordId = value;
    }

    invoiceData;
    billingData;
    isLoading = true;
    invoiceError;
    billingError;
    _invoiceReady = false;
    _billingReady = false;

    // One error state per wire: a success on a rerun (new recordId, refresh) clears its own error and
    // an error drops its own stale data, so neither leaves the previous result on screen. A wire is
    // ready only once it delivers data or an error: the empty delivery a wire can make before the
    // first server result does not stop the spinner.
    @wire(getInvoiceSummary, { accountId: '$recordId' })
    wiredInvoice(result) {
        if (result.data) {
            this.invoiceData = result.data;
            this.invoiceError = undefined;
            this._invoiceReady = true;
        } else if (result.error) {
            this.invoiceData = undefined;
            this.invoiceError = result.error.body?.message || 'Error loading invoice data';
            this._invoiceReady = true;
        }
        this._maybeFinish();
    }

    @wire(getBillingSummary, { accountId: '$recordId' })
    wiredBilling(result) {
        if (result.data) {
            this.billingData = result.data;
            this.billingError = undefined;
            this._billingReady = true;
        } else if (result.error) {
            // No balances without the billing summary (e.g. its currency read was refused): show the
            // fixed message and hide the figures rather than a $0.00 that reads as a real balance.
            this.billingData = undefined;
            this.billingError = result.error.body?.message || 'Error loading billing data';
            this._billingReady = true;
        }
        this._maybeFinish();
    }

    get error() { return this.invoiceError || this.billingError; }
    get billingFailed() { return this.billingError != null; }

    _maybeFinish() {
        if (this._invoiceReady && this._billingReady) this.isLoading = false;
    }

    get hasData() { return !this.isLoading && this.invoiceData != null && !this.billingFailed; }

    get totalInvoiceLabel() {
        const n = this.invoiceData?.totalInvoices || 0;
        return `${n} invoice${n !== 1 ? 's' : ''}`;
    }

    // Each total is null (shown as unavailable) when any of its parts is: the server returns null for
    // a balance whose read was refused, and a refused part is never counted as zero.
    get totalReceivables() {
        const b = this.billingData;
        if (b?.invoiceBalance == null || b?.debitMemoBalance == null) return null;
        return Number(b.invoiceBalance) + Number(b.debitMemoBalance);
    }
    get totalPayables() {
        const b = this.billingData;
        if (b?.paymentBalance == null || b?.creditMemoBalance == null || b?.refundBalance == null) return null;
        return Number(b.paymentBalance) + Number(b.creditMemoBalance) - Number(b.refundBalance);
    }
    get netBalance() {
        const receivables = this.totalReceivables;
        const payables = this.totalPayables;
        return receivables == null || payables == null ? null : receivables - payables;
    }

    get formattedReceivables() { return this._fmtFull(this.totalReceivables); }
    get formattedPayables() { return this._fmtFull(this.totalPayables); }
    get formattedNetBalance() { return this._fmtFull(this.netBalance); }

    get statusInfo() {
        const b = this.billingData;
        if (!b) return null;
        const totalInvoices = Number(b.totalInvoices || 0);
        const overdueCount = Number(b.overdueCount || 0);
        const delinquentCount = Number(b.delinquentCount || 0);
        const partiallyPaidOverdue = countOrNull(b.partiallyPaidOverdueCount);
        const openWithBalance = Number(b.openWithBalance || 0);
        const writtenOff = countOrNull(b.writtenOffCount);
        const disputeCount = countOrNull(b.disputeCount);
        // null: that read was refused, so the standing cannot be decided past that check.
        const inCollections = b.inCollections == null ? null : b.inCollections === true;
        const statusUnavailable = { label: 'Status Unavailable', cssClass: 'abc-pill abc-pill-gray', description: 'Some billing records on this account could not be read, so its standing is not shown.' };
        const net = b.netAccountBalance == null ? null : Number(b.netAccountBalance);

        // "No Billing Activity" claims no payments, memos, disputes, write-offs or collections either:
        // only when each of them is known to be none.
        if (totalInvoices === 0 && allBalancesZero(b) && inCollections === false && writtenOff === 0 && disputeCount === 0) return { label: 'No Billing Activity', cssClass: 'abc-pill abc-pill-gray', description: 'No invoices, payments, or billing records exist for this account.' };
        if (inCollections == null) return statusUnavailable;
        if (inCollections) return { label: 'In Collections', cssClass: 'abc-pill abc-pill-darkred', description: 'This account has been escalated to collections.' };
        if (writtenOff == null) return statusUnavailable;
        if (writtenOff > 0) return { label: 'Written Off', cssClass: 'abc-pill abc-pill-slate', description: `${writtenOff} invoice(s) have been written off as uncollectible.` };
        if (delinquentCount > 0) return { label: 'Delinquent', cssClass: 'abc-pill abc-pill-darkred', description: `${delinquentCount} invoice(s) are 60+ days past due.` };
        if (disputeCount == null) return statusUnavailable;
        if (disputeCount > 0) return { label: 'In Dispute', cssClass: 'abc-pill abc-pill-orange', description: `${disputeCount} open dispute(s) on this account's invoices.` };
        // Partially paid invoices are a subset of the overdue ones: with none overdue the count is a
        // real zero whether or not it could be read.
        if (partiallyPaidOverdue == null && overdueCount > 0) return statusUnavailable;
        if (partiallyPaidOverdue > 0) return { label: 'Partially Paid', cssClass: 'abc-pill abc-pill-amber', description: `${partiallyPaidOverdue} overdue invoice(s) have partial payments.` };
        if (overdueCount > 0) return { label: 'Overdue', cssClass: 'abc-pill abc-pill-red', description: `${overdueCount} invoice(s) are past their due date.` };
        if (net == null) return { label: 'Balance Unavailable', cssClass: 'abc-pill abc-pill-gray', description: 'Some balances on this account could not be read, so its standing is not shown.' };
        if (net < 0) return { label: 'Credit Balance', cssClass: 'abc-pill abc-pill-blue', description: 'Unapplied payments exceed outstanding receivables.' };
        if (openWithBalance === 0 && net <= 0) return { label: 'Fully Settled', cssClass: 'abc-pill abc-pill-green', description: 'All invoices paid in full with zero balance.' };
        return { label: 'Good Standing', cssClass: 'abc-pill abc-pill-mint', description: 'All invoices within payment terms.' };
    }

    get statusLabel() { return this.statusInfo?.label || ''; }
    get statusClass() { return this.statusInfo?.cssClass || 'abc-pill'; }
    get statusDescription() { return this.statusInfo?.description || ''; }

    get segments() {
        const d = this.invoiceData;
        if (!d) return [];

        const raw = [];
        if ((d.currentAmount || 0) > 0) raw.push({ key: 'current', label: 'Current', amount: d.currentAmount, count: d.currentCount, unit: 'invoice' });
        if ((d.debitAmount || 0) > 0) raw.push({ key: 'debit', label: 'Debits', amount: d.debitAmount, count: d.debitCount, unit: 'debit memo' });
        if ((d.disputeAmount || 0) > 0) raw.push({ key: 'dispute', label: 'Dispute', amount: d.disputeAmount, count: d.disputeCount, unit: 'dispute' });
        if ((d.overdueAmount || 0) > 0) raw.push({ key: 'overdue', label: 'Overdue', amount: d.overdueAmount, count: d.overdueCount, unit: 'invoice' });
        if ((d.promiseToPayAmount || 0) > 0) raw.push({ key: 'promise', label: 'Promise to Pay', amount: d.promiseToPayAmount, count: d.promiseToPayCount, unit: 'item' });
        if ((d.paidAmount || 0) > 0) raw.push({ key: 'paid', label: 'Paid', amount: d.paidAmount, count: d.paidCount, unit: 'payment' });

        if (!raw.length) return [];
        const total = raw.reduce((a, r) => a + r.amount, 0);
        if (total <= 0) return [];

        const n = raw.length;
        const evenPct = 100 / n;

        const widths = raw.map(r => {
            const pct = (r.amount / total) * 100;
            return evenPct * 0.55 + pct * 0.45;
        });

        let cumLeft = 0;
        return raw.map((r, i) => {
            const isFirst = i === 0;
            const isLast = i === n - 1;
            const left = cumLeft;
            const width = widths[i];
            cumLeft += width;

            let clipPath;
            if (n === 1) clipPath = 'none';
            else if (isFirst) clipPath = `polygon(0 0, calc(100% - ${ARROW_TIP}px) 0, 100% 50%, calc(100% - ${ARROW_TIP}px) 100%, 0 100%)`;
            else if (isLast) clipPath = `polygon(0 0, 100% 0, 100% 100%, 0 100%, ${ARROW_TIP}px 50%)`;
            else clipPath = `polygon(0 0, calc(100% - ${ARROW_TIP}px) 0, 100% 50%, calc(100% - ${ARROW_TIP}px) 100%, 0 100%, ${ARROW_TIP}px 50%)`;

            const z = n - i;
            const color = SEG_COLORS[r.key] || '#666';
            const padLeft = isFirst ? 8 : 18;
            const padRight = isLast ? 8 : 12;

            return {
                ...r,
                style: `left:${left}%;width:${width}%;background:${color};clip-path:${clipPath};z-index:${z};padding-left:${padLeft}px;padding-right:${padRight}px;`,
                formattedAmount: this._fmtCompact(r.amount),
                countLabel: `${r.count} ${r.unit}${r.count !== 1 ? 's' : ''}`
            };
        });
    }

    get hasSegments() { return this.segments.length > 0; }

    // Segments whose read was refused come back null: they are not drawn (as a zero segment is
    // not), so the card says which could not be read rather than letting the gap read as "none".
    get unavailableSegmentsNote() {
        const d = this.invoiceData;
        if (!d) return '';
        const names = [];
        if (d.debitAmount == null) names.push('debit memos');
        if (d.disputeAmount == null) names.push('disputes');
        if (d.promiseToPayAmount == null) names.push('promises to pay');
        if (d.paidAmount == null) names.push('paid invoices');
        if (!names.length) return '';
        const list = names.length > 1 ? `${names.slice(0, -1).join(', ')} and ${names[names.length - 1]}` : names[0];
        const text = `${list} could not be read and are not shown.`;
        return text.charAt(0).toUpperCase() + text.slice(1);
    }

    showStatusTooltip = false;
    statusTooltipStyle = '';

    handleStatusEnter(event) {
        const rect = event.currentTarget.getBoundingClientRect();
        this.statusTooltipStyle = `top:${rect.bottom + 6}px;left:${rect.left}px`;
        this.showStatusTooltip = true;
    }
    handleStatusLeave() { this.showStatusTooltip = false; }

    _activeMetric = null;
    _metricTooltipStyle = '';
    _metricTooltipText = '';

    get showMetricTooltip() { return this._activeMetric != null; }
    get metricTooltipStyle() { return this._metricTooltipStyle; }
    get metricTooltipLines() {
        return (this._metricTooltipText || '').split('\n').map((l, i) => ({ key: 'tt' + i, text: l }));
    }

    handleMetricEnter(event) {
        const type = event.currentTarget.dataset.type;
        const b = this.billingData;
        if (!b) return;
        if (type === 'receivables') {
            this._metricTooltipText = `Posted Invoices: ${this._fmtFull(b.invoiceBalance)}\nDebit Memo Balance: ${this._fmtFull(b.debitMemoBalance)}`;
        } else if (type === 'payables') {
            this._metricTooltipText = `Payments: ${this._fmtFull(b.paymentBalance)}\nCredits: ${this._fmtFull(b.creditMemoBalance)}\nRefunds: ${this._fmtDeduction(b.refundBalance)}`;
        }
        const rect = event.currentTarget.getBoundingClientRect();
        this._metricTooltipStyle = `top:${rect.bottom + 4}px;left:${rect.left + rect.width / 2}px`;
        this._activeMetric = type;
    }
    handleMetricLeave() { this._activeMetric = null; }

    _fmtCompact(val) {
        if (val == null) return '$0';
        const abs = Math.abs(val);
        if (abs >= 1000000) return '$' + (val / 1000000).toFixed(2) + 'M';
        if (abs >= 1000) return '$' + (val / 1000).toFixed(2) + 'k';
        return '$' + new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val);
    }
    _fmtFull(val) {
        if (val == null) return UNAVAILABLE;
        return '$' + new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val);
    }
    _fmtDeduction(val) {
        return val == null ? UNAVAILABLE : '-' + this._fmtFull(val);
    }
}