import { LightningElement, api, track, wire } from 'lwc';
import { gql, graphql } from 'lightning/graphql';

/**
 * Invoice Health – displays invoice age, status flags, and settlement progress.
 */
export default class RlmInvoiceHealth extends LightningElement {
    @api recordId;

    @track isLoading = true;
    @track error;
    @track errorMessage = '';

    // Invoice data
    invoiceData = null;

    // Invoice lines data
    invoiceLinesData = null;
    _invoiceDataLoaded = false;
    _linesDataLoaded = false;

    @wire(graphql, {
        query: '$queryInvoice',
        variables: '$invoiceVariables'
    })
    wiredInvoice({ data, errors }) {
        if (!this.recordId) {
            this.isLoading = false;
            return;
        }
        if (errors && errors.length) {
            this.error = errors;
            this.errorMessage = this.readableError(errors[0]);
            this.isLoading = false;
            return;
        }
        if (data) {
            this.processInvoice(data);
            this.error = undefined;
            this.errorMessage = '';
            this._invoiceDataLoaded = true;
            this.checkLoadingComplete();
        }
    }

    @wire(graphql, {
        query: '$queryInvoiceLines',
        variables: '$invoiceVariables'
    })
    wiredInvoiceLines({ data, errors }) {
        if (!this.recordId) {
            this._linesDataLoaded = true;
            this.checkLoadingComplete();
            return;
        }
        if (errors && errors.length) {
            // Don't fail the whole component for lines error, just skip
            this.invoiceLinesData = null;
            this._linesDataLoaded = true;
            this.checkLoadingComplete();
            return;
        }
        if (data) {
            this.processInvoiceLines(data);
            this._linesDataLoaded = true;
            this.checkLoadingComplete();
        }
    }

    checkLoadingComplete() {
        if (this._invoiceDataLoaded && this._linesDataLoaded) {
            this.isLoading = false;
        }
    }

    get invoiceVariables() {
        return this.recordId ? { invoiceId: this.recordId } : undefined;
    }

    queryInvoice = gql`
        query InvoiceHealth($invoiceId: ID!) {
            uiapi {
                query {
                    Invoice(where: { Id: { eq: $invoiceId } }, first: 1) {
                        edges {
                            node {
                                Id
                                DocumentNumber { value }
                                Status { value }
                                DaysInvoiceOpen { value }
                                DueDate { value }
                                TotalChargeAmount { value }
                                TotalTaxAmount { value }
                                TotalAmountWithTax { value }
                                Balance { value }
                                SettlementStatus { value }
                                FullSettlementDate { value }
                                NetPaymentsApplied { value }
                                NetCreditsApplied { value }
                                TotalConvertedNegAmount { value }
                            }
                        }
                    }
                }
            }
        }
    `;

    queryInvoiceLines = gql`
        query InvoiceLines($invoiceId: ID!) {
            uiapi {
                query {
                    InvoiceLine(where: { InvoiceId: { eq: $invoiceId } }, first: 2000) {
                        edges {
                            node {
                                Id
                                RLM_Charge_Type__c { value }
                            }
                        }
                    }
                }
            }
        }
    `;

    processInvoiceLines(data) {
        const edges = data?.uiapi?.query?.InvoiceLine?.edges || [];
        const totalLines = edges.length;

        if (totalLines === 0) {
            this.invoiceLinesData = {
                totalLines: 0,
                chargeTypes: []
            };
            return;
        }

        // Count by charge type
        const chargeTypeCounts = {};
        edges.forEach((edge) => {
            const chargeType = edge.node?.RLM_Charge_Type__c?.value || 'Other';
            chargeTypeCounts[chargeType] = (chargeTypeCounts[chargeType] || 0) + 1;
        });

        // Build structured charge type items
        const chargeTypes = this.buildChargeTypeItems(chargeTypeCounts);

        this.invoiceLinesData = {
            totalLines,
            chargeTypes
        };
    }

    getChargeTypeConfig(type) {
        const typeLower = type.toLowerCase();
        // Map charge types to icons and labels
        const configs = [
            { match: (t) => t.includes('one time') || t.includes('one-time') || t.includes('onetime'), icon: 'utility:record', label: 'One-time Charges', colorClass: 'ct-onetime' },
            { match: (t) => t.includes('milestone'), icon: 'utility:checkin', label: 'Milestone Charges', colorClass: 'ct-milestone' },
            { match: (t) => t.includes('monthly'), icon: 'utility:date_input', label: 'Monthly Charges', colorClass: 'ct-monthly' },
            { match: (t) => t.includes('quarterly'), icon: 'utility:date_input', label: 'Quarterly Charges', colorClass: 'ct-quarterly' },
            { match: (t) => t.includes('semi-annual') || t.includes('semiannual'), icon: 'utility:date_input', label: 'Semi-Annual Charges', colorClass: 'ct-semiannual' },
            { match: (t) => t.includes('annual') || t.includes('yearly'), icon: 'utility:event', label: 'Annual Charges', colorClass: 'ct-annual' },
            { match: (t) => t.includes('daily'), icon: 'utility:clock', label: 'Daily Charges', colorClass: 'ct-daily' },
            { match: (t) => t.includes('usage'), icon: 'utility:metrics', label: 'Usage Charges', colorClass: 'ct-usage' }
        ];
        for (const cfg of configs) {
            if (cfg.match(typeLower)) {
                return cfg;
            }
        }
        return { icon: 'utility:question', label: type + ' Charges', colorClass: 'ct-other' };
    }

    buildChargeTypeItems(chargeTypeCounts) {
        return Object.entries(chargeTypeCounts)
            .sort((a, b) => b[1] - a[1])
            .map(([type, count]) => {
                const config = this.getChargeTypeConfig(type);
                return {
                    key: type,
                    icon: config.icon,
                    label: config.label,
                    count,
                    countLabel: `${count}`,
                    colorClass: `ct-icon ${config.colorClass}`
                };
            });
    }

    processInvoice(data) {
        const node = data?.uiapi?.query?.Invoice?.edges?.[0]?.node;
        if (!node) {
            this.invoiceData = null;
            return;
        }

        const status = node?.Status?.value || '';
        const daysOpen = Number(node?.DaysInvoiceOpen?.value ?? 0);
        const dueDate = node?.DueDate?.value;
        const totalCharges = Number(node?.TotalChargeAmount?.value ?? 0);
        const totalTax = Number(node?.TotalTaxAmount?.value ?? 0);
        const totalAmount = Number(node?.TotalAmountWithTax?.value ?? 0);
        const balance = Number(node?.Balance?.value ?? 0);
        const settlementStatus = node?.SettlementStatus?.value || '';
        const fullSettlementDate = node?.FullSettlementDate?.value;
        const totalPayments = Math.abs(Number(node?.NetPaymentsApplied?.value ?? 0));
        const totalCredits = Math.abs(Number(node?.NetCreditsApplied?.value ?? 0));
        const totalConvertedNeg = Math.abs(Number(node?.TotalConvertedNegAmount?.value ?? 0));
        const adjustedCredits = Math.max(totalCredits - totalConvertedNeg, 0);

        // Calculate days until due
        let daysUntilDue = null;
        let daysUntilDueText = '';
        let isDueUrgent = false;
        let isOverdue = false;
        if (dueDate) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const due = new Date(dueDate);
            due.setHours(0, 0, 0, 0);
            const diffMs = due - today;
            daysUntilDue = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
            if (daysUntilDue < 0) {
                daysUntilDueText = `${Math.abs(daysUntilDue)} days overdue`;
                isOverdue = true;
            } else if (daysUntilDue === 0) {
                daysUntilDueText = 'Due today';
                isDueUrgent = true;
            } else if (daysUntilDue <= 7) {
                daysUntilDueText = `${daysUntilDue} days until due`;
                isDueUrgent = true;
            } else {
                daysUntilDueText = `${daysUntilDue} days until due`;
            }
        }

        // Status flags
        const statusLower = status.toLowerCase();
        const flaggedStatuses = ['draft', 'in review', 'error'];
        const normalStatuses = ['draft', 'posted', 'voided', 'canceled', 'cancelled'];
        const isStatusFlagged = flaggedStatuses.some(s => statusLower.includes(s));
        const isStatusStuck = !normalStatuses.some(s => statusLower === s) && statusLower !== '';
        const statusClass = (isStatusFlagged || isStatusStuck) ? 'status-flagged' : 'status-normal';
        let statusMessage = '';
        if (statusLower.includes('error')) {
            statusMessage = 'Invoice has an error';
        } else if (statusLower.includes('draft')) {
            statusMessage = 'Invoice is still in Draft';
        } else if (statusLower.includes('in review')) {
            statusMessage = 'Invoice is pending review';
        } else if (isStatusStuck) {
            statusMessage = `Invoice stuck in "${status}" status`;
        }

        // Settlement progress
        let paymentPercent = 0;
        let creditPercent = 0;
        let balancePercent = 0;
        const absTotalAmount = Math.abs(totalAmount);
        if (absTotalAmount > 0) {
            paymentPercent = Math.min((totalPayments / absTotalAmount) * 100, 100);
            creditPercent = Math.min((adjustedCredits / absTotalAmount) * 100, 100 - paymentPercent);
            balancePercent = Math.max(100 - paymentPercent - creditPercent, 0);
        }
        const isFullySettled = balance === 0 && absTotalAmount > 0;
        const formattedSettlementDate = fullSettlementDate
            ? new Date(fullSettlementDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
            : '';

        this.invoiceData = {
            daysOpen,
            daysUntilDueText,
            isDueUrgent,
            isOverdue,
            hasDueDate: !!dueDate,
            status,
            statusClass,
            statusMessage,
            isStatusFlagged: isStatusFlagged || isStatusStuck,
            paymentPercent: paymentPercent.toFixed(1),
            creditPercent: creditPercent.toFixed(1),
            balancePercent: balancePercent.toFixed(1),
            paymentStyle: `width: ${paymentPercent}%`,
            creditStyle: `width: ${creditPercent}%`,
            balanceStyle: `width: ${balancePercent}%`,
            isFullySettled,
            formattedSettlementDate,
            formattedBalance: this.formatCurrency(balance),
            formattedTotalCharges: this.formatCurrency(totalCharges),
            formattedTotalTax: this.formatCurrency(totalTax),
            formattedTotal: this.formatCurrency(totalAmount),
            formattedConvertedNeg: this.formatCurrency(totalConvertedNeg),
            formattedNetCredits: this.formatCurrency(totalCredits),
            formattedBalanceReduced: this.formatCurrency(adjustedCredits)
        };
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
    }

    get hasData() {
        return this.invoiceData !== null;
    }

    get hasLinesData() {
        return this.invoiceLinesData !== null;
    }

    get dueDateClass() {
        if (!this.invoiceData) return 'due-normal';
        if (this.invoiceData.isOverdue) return 'due-overdue';
        if (this.invoiceData.isDueUrgent) return 'due-urgent';
        return 'due-normal';
    }

    readableError(err) {
        if (!err) return 'Unknown error';
        if (typeof err === 'string') return err;
        if (err.message) return err.message;
        if (err.body?.message) return err.body.message;
        return JSON.stringify(err);
    }
}