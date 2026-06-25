import { LightningElement, api, wire } from 'lwc';
import getInvoiceSummary from '@salesforce/apex/RLM_InvoiceSummaryController.getInvoiceSummary';
import getBillingSummary from '@salesforce/apex/RLM_OnAccountBillingController.getBillingSummary';

const ARROW_TIP = 18;

export default class RlmInvoiceSummaryBar extends LightningElement {
    @api recordId;
    data;
    billing;
    isLoading = true;
    error;
    _invoiceReady = false;
    _billingReady = false;

    @wire(getInvoiceSummary, { accountId: '$recordId' })
    wiredInvoice(result) {
        this._invoiceReady = true;
        if (result.data) { this.data = result.data; }
        else if (result.error) { this.error = result.error.body?.message || 'Error loading data'; }
        this._checkReady();
    }

    @wire(getBillingSummary, { accountId: '$recordId' })
    wiredBilling(result) {
        this._billingReady = true;
        if (result.data) { this.billing = result.data; }
        this._checkReady();
    }

    _checkReady() {
        if (this._invoiceReady && this._billingReady) this.isLoading = false;
    }

    get hasData() { return !this.isLoading && this.data != null; }

    get formattedTotalDue() { return this._fmtFull(this.data?.totalDue || 0); }
    get totalInvoiceLabel() {
        const n = this.data?.totalInvoices || 0;
        return `${n} invoice${n !== 1 ? 's' : ''}`;
    }

    // ── Status pill (reused from Account Balance card) ──────
    get rlmBillingStatus() {
        const b = this.billing;
        if (!b) return null;
        const totalInvoices = Number(b.totalInvoices || 0);
        const overdueCount = Number(b.overdueCount || 0);
        const delinquentCount = Number(b.delinquentCount || 0);
        const partiallyPaidOverdue = Number(b.partiallyPaidOverdueCount || 0);
        const openWithBalance = Number(b.openWithBalance || 0);
        const writtenOff = Number(b.writtenOffCount || 0);
        const disputeCount = Number(b.disputeCount || 0);
        const inCollections = b.inCollections === true;
        const net = Number(b.netAccountBalance || 0);

        if (totalInvoices === 0) return { label: 'No Billing Activity', cssClass: 'status-pill status-no-activity', description: 'No invoices, payments, or billing records exist for this account.' };
        if (inCollections) return { label: 'In Collections', cssClass: 'status-pill status-collections', description: 'This account has been escalated to collections for significantly overdue balances.' };
        if (writtenOff > 0) return { label: 'Written Off', cssClass: 'status-pill status-written-off', description: `${writtenOff} invoice(s) have been written off as uncollectible.` };
        if (delinquentCount > 0) return { label: 'Delinquent', cssClass: 'status-pill status-delinquent', description: `${delinquentCount} invoice(s) are 60+ days past due.` };
        if (disputeCount > 0) return { label: 'In Dispute', cssClass: 'status-pill status-dispute', description: `${disputeCount} open dispute(s) on this account's invoices.` };
        if (partiallyPaidOverdue > 0) return { label: 'Partially Paid', cssClass: 'status-pill status-partial', description: `${partiallyPaidOverdue} overdue invoice(s) have partial payments.` };
        if (overdueCount > 0) return { label: 'Overdue', cssClass: 'status-pill status-overdue', description: `${overdueCount} invoice(s) are past their due date.` };
        if (net < 0) return { label: 'Credit Balance', cssClass: 'status-pill status-credit', description: 'Unapplied payments exceed outstanding receivables.' };
        if (openWithBalance === 0 && net <= 0) return { label: 'Fully Settled', cssClass: 'status-pill status-settled', description: 'All invoices paid in full with zero balance.' };
        return { label: 'Good Standing', cssClass: 'status-pill status-good', description: 'All invoices within payment terms.' };
    }

    get statusLabel() { return this.rlmBillingStatus?.label || ''; }
    get statusClass() { return this.rlmBillingStatus?.cssClass || 'status-pill'; }
    get statusDescription() { return this.rlmBillingStatus?.description || ''; }

    showStatusTooltip = false;
    statusTooltipStyle = '';

    handleStatusEnter(event) {
        const rect = event.currentTarget.getBoundingClientRect();
        this.statusTooltipStyle = `top:${rect.bottom + 6}px;left:${rect.left}px`;
        this.showStatusTooltip = true;
    }
    handleStatusLeave() { this.showStatusTooltip = false; }

    // ── Arrow segments ──────────────────────────────────────
    get segments() {
        const d = this.data;
        if (!d) return [];
        const raw = [];
        if ((d.currentAmount || 0) > 0) raw.push({ key: 'current', label: 'Current', color: '#5B91C7', amount: d.currentAmount, count: d.currentCount, unit: 'invoice' });
        if ((d.overdueAmount || 0) > 0) raw.push({ key: 'overdue', label: 'Overdue', color: '#C94444', amount: d.overdueAmount, count: d.overdueCount, unit: 'invoice' });
        if ((d.debitAmount || 0) > 0) raw.push({ key: 'debit', label: 'Debits', color: '#D4A017', amount: d.debitAmount, count: d.debitCount, unit: 'debit memo' });
        if ((d.disputeAmount || 0) > 0) raw.push({ key: 'dispute', label: 'Dispute', color: '#E87722', amount: d.disputeAmount, count: d.disputeCount, unit: 'dispute' });
        if ((d.promiseToPayAmount || 0) > 0) raw.push({ key: 'promise', label: 'Promise to Pay', color: '#8B4C6A', amount: d.promiseToPayAmount, count: d.promiseToPayCount, unit: 'item' });
        if ((d.paidAmount || 0) > 0) raw.push({ key: 'paid', label: 'Paid (30d)', color: '#5B9E5B', amount: d.paidAmount, count: d.paidCount, unit: 'invoice' });

        if (raw.length === 0) return [];
        const total = raw.reduce((s, r) => s + (r.amount || 0), 0);
        if (total <= 0) return [];

        const len = raw.length;
        this._gridCols = raw.map(s => {
            const pct = (s.amount / total) * 100;
            const even = 100 / len;
            return (even * 0.6 + pct * 0.4).toFixed(2);
        });

        return raw.map((s, i) => {
            const isFirst = i === 0;
            const isLast = i === len - 1;
            let clipPath;
            if (len === 1) clipPath = 'none';
            else if (isFirst) clipPath = `polygon(0 0, calc(100% - ${ARROW_TIP}px) 0, 100% 50%, calc(100% - ${ARROW_TIP}px) 100%, 0 100%)`;
            else if (isLast) clipPath = `polygon(0 0, 100% 0, 100% 100%, 0 100%, ${ARROW_TIP}px 50%)`;
            else clipPath = `polygon(0 0, calc(100% - ${ARROW_TIP}px) 0, 100% 50%, calc(100% - ${ARROW_TIP}px) 100%, 0 100%, ${ARROW_TIP}px 50%)`;

            const ml = i > 0 ? '-6px' : '0';
            return {
                ...s,
                barStyle: `background:${s.color};clip-path:${clipPath};margin-left:${ml};`,
                formattedAmount: this._fmtCompact(s.amount),
                countLabel: `${s.count} ${s.unit}${s.count !== 1 ? 's' : ''}`,
                segClass: `arrow-segment ${isFirst ? 'seg-first' : ''} ${isLast ? 'seg-last' : ''}`
            };
        });
    }

    get hasSegments() { return this.segments.length > 0; }

    renderedCallback() {
        if (!this._gridCols || !this._gridCols.length) return;
        const segs = this.template.querySelectorAll('.arrow-segment');
        if (!segs || !segs.length) return;
        segs.forEach((el, i) => {
            const v = this._gridCols[i];
            if (v != null) {
                el.style.flexGrow = String(v);
                el.style.flexShrink = '1';
                el.style.flexBasis = '0';
            }
        });
    }

    // ── Bottom balance metrics ──────────────────────────────
    get totalReceivables() {
        return Number(this.billing?.invoiceBalance || 0) + Number(this.billing?.debitMemoBalance || 0);
    }
    get totalPayables() {
        return Number(this.billing?.paymentBalance || 0) + Number(this.billing?.creditMemoBalance || 0) - Number(this.billing?.refundBalance || 0);
    }
    get netBalance() { return this.totalReceivables - this.totalPayables; }

    get formattedReceivables() { return this._fmtFull(this.totalReceivables); }
    get formattedPayables() { return this._fmtFull(this.totalPayables); }
    get formattedNetBalance() { return this._fmtFull(this.netBalance); }
    get netMetricClass() { return this.netBalance <= 0 ? 'metric-value metric-net-positive' : 'metric-value'; }

    // Tooltip content
    get receivablesTooltip() {
        const b = this.billing;
        if (!b) return '';
        return `Posted Invoices: ${this._fmtFull(b.invoiceBalance || 0)}\nDebit Memo Balance: ${this._fmtFull(b.debitMemoBalance || 0)}`;
    }
    get payablesTooltip() {
        const b = this.billing;
        if (!b) return '';
        return `Payments: ${this._fmtFull(b.paymentBalance || 0)}\nCredits: ${this._fmtFull(b.creditMemoBalance || 0)}\nRefunds: -${this._fmtFull(b.refundBalance || 0)}`;
    }
    get netTooltip() {
        return `Total Receivables: ${this.formattedReceivables}\nTotal Payables: -${this.formattedPayables}`;
    }

    _activeTooltip = null;
    _tooltipStyle = '';
    _tooltipText = '';

    get showTooltip() { return this._activeTooltip != null; }
    get tooltipStyle() { return this._tooltipStyle; }
    get tooltipLines() {
        return (this._tooltipText || '').split('\n').map((l, i) => ({ key: 'tt' + i, text: l }));
    }

    handleBalEnter(event) {
        const type = event.currentTarget.dataset.type;
        if (type === 'receivables') this._tooltipText = this.receivablesTooltip;
        else if (type === 'payables') this._tooltipText = this.payablesTooltip;
        else if (type === 'net') this._tooltipText = this.netTooltip;

        const rect = event.currentTarget.getBoundingClientRect();
        this._tooltipStyle = `top:${rect.bottom + 4}px;left:${rect.left + rect.width / 2}px`;
        this._activeTooltip = type;
    }
    handleBalLeave() { this._activeTooltip = null; }

    // ── Helpers ─────────────────────────────────────────────
    _fmtCompact(val) {
        if (val == null) return '$0';
        const abs = Math.abs(val);
        if (abs >= 1000000) return '$ ' + (val / 1000000).toFixed(2) + 'M';
        if (abs >= 1000) return '$ ' + (val / 1000).toFixed(2) + 'k';
        return '$ ' + new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val);
    }

    _fmtFull(val) {
        if (val == null) return '$0.00';
        return '$' + new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val);
    }
}