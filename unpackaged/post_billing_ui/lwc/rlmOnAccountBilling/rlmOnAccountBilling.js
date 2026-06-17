import { LightningElement, api, wire } from 'lwc';
import getBillingSummary from '@salesforce/apex/RLM_OnAccountBillingController.getBillingSummary';

export default class RlmOnAccountBilling extends LightningElement {
    @api recordId;

    isLoading = true;
    data = null;
    errorMessage = '';

    @wire(getBillingSummary, { accountId: '$recordId' })
    wiredSummary({ data, error }) {
        this.isLoading = false;
        if (data) {
            this.data = data;
            this.errorMessage = '';
        } else if (error) {
            this.data = null;
            this.errorMessage = this.extractError(error);
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

    // Due Amount = Invoice + Debit Memo
    get dueAmount() {
        return Number(this.data?.invoiceBalance || 0)
             + Number(this.data?.debitMemoBalance || 0);
    }

    // Adjusted Amount = Payment + Credit Memo - Refund
    get adjustedAmount() {
        return Number(this.data?.paymentBalance || 0)
             + Number(this.data?.creditMemoBalance || 0)
             - Number(this.data?.refundBalance || 0);
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

    get formattedRefundBalance() {
        return this.formatAmount(this.data?.refundBalance);
    }

    get formattedNetBalance() {
        return this.formatAmount(this.data?.netAccountBalance);
    }

    get netAmountClass() {
        const net = Number(this.data?.netAccountBalance || 0);
        return net < 0 ? 'net-amount net-positive' : 'net-amount';
    }

    get rlmBillingStatus() {
        if (!this.data) return null;
        const d = this.data;
        const totalInvoices = Number(d.totalInvoices || 0);
        const overdueCount = Number(d.overdueCount || 0);
        const delinquentCount = Number(d.delinquentCount || 0);
        const partiallyPaidOverdue = Number(d.partiallyPaidOverdueCount || 0);
        const openWithBalance = Number(d.openWithBalance || 0);
        const writtenOff = Number(d.writtenOffCount || 0);
        const disputeCount = Number(d.disputeCount || 0);
        const inCollections = d.inCollections === true;
        const net = Number(d.netAccountBalance || 0);

        if (totalInvoices === 0) {
            return {
                label: 'No Billing Activity',
                cssClass: 'status-pill status-no-activity',
                description: 'No invoices, payments, or billing records exist for this account.'
            };
        }
        if (inCollections) {
            return {
                label: 'In Collections',
                cssClass: 'status-pill status-collections',
                description: 'This account has been escalated to collections for significantly overdue balances.'
            };
        }
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
        if (disputeCount > 0) {
            return {
                label: 'In Dispute',
                cssClass: 'status-pill status-dispute',
                description: `${disputeCount} open dispute(s) on this account's invoices are pending resolution.`
            };
        }
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
        const amount = Number(value || 0);
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