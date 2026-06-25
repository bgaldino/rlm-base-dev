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

export default class RlmAccountBalanceCard extends LightningElement {
    @api recordId;
    invoiceData;
    billingData;
    isLoading = true;
    error;
    _invoiceReady = false;
    _billingReady = false;

    @wire(getInvoiceSummary, { accountId: '$recordId' })
    wiredInvoice(result) {
        this._invoiceReady = true;
        if (result.data) { this.invoiceData = result.data; }
        else if (result.error) { this.error = result.error.body?.message || 'Error loading invoice data'; }
        this._maybeFinish();
    }

    @wire(getBillingSummary, { accountId: '$recordId' })
    wiredBilling(result) {
        this._billingReady = true;
        if (result.data) { this.billingData = result.data; }
        this._maybeFinish();
    }

    _maybeFinish() {
        if (this._invoiceReady && this._billingReady) this.isLoading = false;
    }

    get hasData() { return !this.isLoading && this.invoiceData != null; }

    get totalInvoiceLabel() {
        const n = this.invoiceData?.totalInvoices || 0;
        return `${n} invoice${n !== 1 ? 's' : ''}`;
    }

    get totalReceivables() {
        return Number(this.billingData?.invoiceBalance || 0) + Number(this.billingData?.debitMemoBalance || 0);
    }
    get totalPayables() {
        return Number(this.billingData?.paymentBalance || 0)
             + Number(this.billingData?.creditMemoBalance || 0)
             - Number(this.billingData?.refundBalance || 0);
    }
    get netBalance() { return this.totalReceivables - this.totalPayables; }

    get formattedReceivables() { return this._fmtFull(this.totalReceivables); }
    get formattedPayables() { return this._fmtFull(this.totalPayables); }
    get formattedNetBalance() { return this._fmtFull(this.netBalance); }

    get statusInfo() {
        const b = this.billingData;
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

        if (totalInvoices === 0) return { label: 'No Billing Activity', cssClass: 'abc-pill abc-pill-gray', description: 'No invoices, payments, or billing records exist for this account.' };
        if (inCollections) return { label: 'In Collections', cssClass: 'abc-pill abc-pill-darkred', description: 'This account has been escalated to collections.' };
        if (writtenOff > 0) return { label: 'Written Off', cssClass: 'abc-pill abc-pill-slate', description: `${writtenOff} invoice(s) have been written off as uncollectible.` };
        if (delinquentCount > 0) return { label: 'Delinquent', cssClass: 'abc-pill abc-pill-darkred', description: `${delinquentCount} invoice(s) are 60+ days past due.` };
        if (disputeCount > 0) return { label: 'In Dispute', cssClass: 'abc-pill abc-pill-orange', description: `${disputeCount} open dispute(s) on this account's invoices.` };
        if (partiallyPaidOverdue > 0) return { label: 'Partially Paid', cssClass: 'abc-pill abc-pill-amber', description: `${partiallyPaidOverdue} overdue invoice(s) have partial payments.` };
        if (overdueCount > 0) return { label: 'Overdue', cssClass: 'abc-pill abc-pill-red', description: `${overdueCount} invoice(s) are past their due date.` };
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
            this._metricTooltipText = `Posted Invoices: ${this._fmtFull(b.invoiceBalance || 0)}\nDebit Memo Balance: ${this._fmtFull(b.debitMemoBalance || 0)}`;
        } else if (type === 'payables') {
            this._metricTooltipText = `Payments: ${this._fmtFull(b.paymentBalance || 0)}\nCredits: ${this._fmtFull(b.creditMemoBalance || 0)}\nRefunds: -${this._fmtFull(b.refundBalance || 0)}`;
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
        if (val == null) return '$0.00';
        return '$' + new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val);
    }
}