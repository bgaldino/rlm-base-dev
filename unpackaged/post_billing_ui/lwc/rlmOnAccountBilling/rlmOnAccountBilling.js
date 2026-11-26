import { LightningElement, api, wire } from 'lwc';
import getBillingSummary from '@salesforce/apex/RLM_OnAccountBillingController.getBillingSummary';

// A status count the server could not read comes back null; it stays null rather than reading as 0.
const countOrNull = (value) => (value == null ? null : Number(value));

// Every balance part read and zero: a zero net alone could be a debit memo offset by a payment.
const BALANCE_PARTS = ['invoiceBalance', 'debitMemoBalance', 'creditMemoBalance', 'paymentBalance', 'refundBalance'];
const allBalancesZero = (summary) => BALANCE_PARTS.every((key) => summary[key] != null && Number(summary[key]) === 0);

// Shown for a balance whose read was refused (null from the server), never a zero.
const UNAVAILABLE = 'Unavailable';

export default class RlmOnAccountBilling extends LightningElement {
    _recordId;

    // A new record starts a new load: the spinner shows, and the previous record's figures, status
    // pill and error are cleared, until the new result lands.
    @api
    get recordId() { return this._recordId; }
    set recordId(value) {
        if (value !== this._recordId) {
            this.isLoading = true;
            this.data = null;
            this.errorMessage = '';
        }
        this._recordId = value;
    }

    isLoading = true;
    data = null;
    errorMessage = '';

    // Ready only on data or an error: the empty delivery a wire can make before the first server
    // result does not stop the spinner.
    @wire(getBillingSummary, { accountId: '$recordId' })
    wiredSummary({ data, error }) {
        if (data) {
            this.data = data;
            this.errorMessage = '';
            this.isLoading = false;
        } else if (error) {
            this.data = null;
            this.errorMessage = this.extractError(error);
            this.isLoading = false;
        }
    }

    get hasData() {
        return this.data != null && !this.errorMessage;
    }

    get hasError() {
        return !!this.errorMessage;
    }

    get isEmpty() {
        return !this.hasData && !this.hasError;
    }

    get currencyIsoCode() {
        return this.data?.currencyIsoCode || 'USD';
    }

    get showCurrencyNote() {
        return this.data?.isMultiCurrency === true;
    }

    get currencyTooltip() {
        return `All values converted to account currency (${this.currencyIsoCode})`;
    }

    // Due Amount = Invoice + Debit Memo. Null (shown as unavailable) when either part is: the
    // server returns null for a balance whose read was refused, never counted as zero.
    get dueAmount() {
        const d = this.data;
        if (d?.invoiceBalance == null || d?.debitMemoBalance == null) return null;
        return Number(d.invoiceBalance) + Number(d.debitMemoBalance);
    }

    // Adjusted Amount = Payment + Credit Memo - Refund; null when any part is.
    get adjustedAmount() {
        const d = this.data;
        if (d?.paymentBalance == null || d?.creditMemoBalance == null || d?.refundBalance == null) return null;
        return Number(d.paymentBalance) + Number(d.creditMemoBalance) - Number(d.refundBalance);
    }

    get formattedDueAmount() {
        return this.formatAmount(this.dueAmount);
    }

    get formattedAdjustedAmount() {
        return this.formatAmount(this.adjustedAmount);
    }

    get formattedInvoiceBalance() {
        return this.formatAmount(this.data?.invoiceBalance);
    }

    get formattedDebitMemoBalance() {
        return this.formatAmount(this.data?.debitMemoBalance);
    }

    get formattedCreditMemoBalance() {
        return this.formatAmount(this.data?.creditMemoBalance);
    }

    get formattedPaymentBalance() {
        return this.formatAmount(this.data?.paymentBalance);
    }

    // The refund shown as a deduction; no minus sign in front of "Unavailable".
    get formattedRefundDeduction() {
        const refund = this.data?.refundBalance;
        return refund == null ? UNAVAILABLE : '-' + this.formatAmount(refund);
    }

    get formattedNetBalance() {
        return this.formatAmount(this.data?.netAccountBalance);
    }

    get netAmountClass() {
        const net = this.data?.netAccountBalance;
        return net != null && Number(net) < 0 ? 'net-amount net-positive' : 'net-amount';
    }

    get rlmBillingStatus() {
        if (!this.data) return null;
        const d = this.data;
        const totalInvoices = Number(d.totalInvoices || 0);
        const overdueCount = Number(d.overdueCount || 0);
        const delinquentCount = Number(d.delinquentCount || 0);
        const partiallyPaidOverdue = countOrNull(d.partiallyPaidOverdueCount);
        const openWithBalance = Number(d.openWithBalance || 0);
        const writtenOff = countOrNull(d.writtenOffCount);
        const disputeCount = countOrNull(d.disputeCount);
        // null: that read was refused, so the standing cannot be decided past that check.
        const inCollections = d.inCollections == null ? null : d.inCollections === true;
        const statusUnavailable = {
            label: 'Status Unavailable',
            cssClass: 'status-pill status-no-activity',
            description: 'Some billing records on this account could not be read, so its standing is not shown.'
        };
        const net = d.netAccountBalance == null ? null : Number(d.netAccountBalance);

        // "No Billing Activity" claims no payments, memos, disputes, write-offs or collections either:
        // only when each of them is known to be none.
        if (totalInvoices === 0 && allBalancesZero(d) && inCollections === false && writtenOff === 0 && disputeCount === 0) {
            return {
                label: 'No Billing Activity',
                cssClass: 'status-pill status-no-activity',
                description: 'No invoices, payments, or billing records exist for this account.'
            };
        }
        if (inCollections == null) return statusUnavailable;
        if (inCollections) {
            return {
                label: 'In Collections',
                cssClass: 'status-pill status-collections',
                description: 'This account has been escalated to collections for significantly overdue balances.'
            };
        }
        if (writtenOff == null) return statusUnavailable;
        if (writtenOff > 0) {
            return {
                label: 'Written Off',
                cssClass: 'status-pill status-written-off',
                description: `${writtenOff} invoice(s) have been written off as uncollectible for this account.`
            };
        }
        if (delinquentCount > 0) {
            return {
                label: 'Delinquent',
                cssClass: 'status-pill status-delinquent',
                description: `${delinquentCount} invoice(s) are 60+ days past due. Immediate attention required.`
            };
        }
        if (disputeCount == null) return statusUnavailable;
        if (disputeCount > 0) {
            return {
                label: 'In Dispute',
                cssClass: 'status-pill status-dispute',
                description: `${disputeCount} open dispute(s) on this account's invoices are pending resolution.`
            };
        }
        // Partially paid invoices are a subset of the overdue ones: with none overdue the count is a
        // real zero whether or not it could be read.
        if (partiallyPaidOverdue == null && overdueCount > 0) return statusUnavailable;
        if (partiallyPaidOverdue > 0) {
            return {
                label: 'Partially Paid',
                cssClass: 'status-pill status-partial',
                description: `${partiallyPaidOverdue} overdue invoice(s) have partial payments applied but still carry a remaining balance.`
            };
        }
        if (overdueCount > 0) {
            return {
                label: 'Overdue',
                cssClass: 'status-pill status-overdue',
                description: `${overdueCount} invoice(s) are past their due date with outstanding balance.`
            };
        }
        if (net == null) {
            return {
                label: 'Balance Unavailable',
                cssClass: 'status-pill status-no-activity',
                description: 'Some balances on this account could not be read, so its standing is not shown.'
            };
        }
        if (net < 0) {
            return {
                label: 'Credit Balance',
                cssClass: 'status-pill status-credit',
                description: 'This account has a credit balance — unapplied payments exceed outstanding receivables.'
            };
        }
        if (openWithBalance === 0 && net <= 0) {
            return {
                label: 'Fully Settled',
                cssClass: 'status-pill status-settled',
                description: 'All invoices for this account have been paid in full with zero outstanding balance.'
            };
        }
        return {
            label: 'Good Standing',
            cssClass: 'status-pill status-good',
            description: 'All invoices are within payment terms — no overdue balances.'
        };
    }

    get statusLabel() {
        return this.rlmBillingStatus?.label || '';
    }

    get statusClass() {
        return this.rlmBillingStatus?.cssClass || 'status-pill';
    }

    get statusDescription() {
        return this.rlmBillingStatus?.description || '';
    }

    showStatusTooltip = false;
    statusTooltipStyle = '';

    handleStatusEnter(event) {
        const rect = event.currentTarget.getBoundingClientRect();
        this.statusTooltipStyle = `top:${rect.bottom + 6}px;left:${rect.left}px`;
        this.showStatusTooltip = true;
    }

    handleStatusLeave() {
        this.showStatusTooltip = false;
    }

    formatAmount(value) {
        if (value == null) return UNAVAILABLE;
        const amount = Number(value);
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: this.currencyIsoCode,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    extractError(error) {
        if (!error) return 'Unknown error';
        if (error.body?.message) return error.body.message;
        if (error.message) return error.message;
        return 'Unable to load billing summary.';
    }
}