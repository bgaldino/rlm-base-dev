import { LightningElement, api, track, wire } from 'lwc';
import { gql, graphql } from 'lightning/graphql';
import { NavigationMixin } from 'lightning/navigation';

/**
 * Invoice Health – displays invoice age, status flags, settlement progress, and disputes.
 */
export default class RlmInvoiceHealth extends NavigationMixin(LightningElement) {
    @api recordId;

    @track isLoading = true;
    @track error;
    @track errorMessage = '';

    @track activeTab = 'summary';

    invoiceData = null;
    invoiceLinesData = null;
    disputesData = null;

    _invoiceDataLoaded = false;
    _linesDataLoaded = false;
    _disputesLoaded = false;

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

    @wire(graphql, {
        query: '$queryDisputes',
        variables: '$invoiceVariables'
    })
    wiredDisputes({ data, errors }) {
        if (!this.recordId) {
            this._disputesLoaded = true;
            this.checkLoadingComplete();
            return;
        }
        if (errors && errors.length) {
            this.disputesData = null;
            this._disputesLoaded = true;
            this.checkLoadingComplete();
            return;
        }
        if (data) {
            this.processDisputes(data);
            this._disputesLoaded = true;
            this.checkLoadingComplete();
        }
    }

    checkLoadingComplete() {
        if (this._invoiceDataLoaded && this._linesDataLoaded && this._disputesLoaded) {
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
                                LineAmount { value }
                            }
                        }
                    }
                }
            }
        }
    `;

    queryDisputes = gql`
        query Disputes($invoiceId: ID!) {
            uiapi {
                query {
                    Dispute(where: { InvoiceId: { eq: $invoiceId } }, first: 50) {
                        edges {
                            node {
                                Id
                                Name { value }
                                DisputedAmount { value }
                                ApprovedAmount { value }
                                ReceivedDate { value }
                                Case {
                                    Id
                                    Subject { value }
                                    Status { value }
                                }
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

        const chargeTypeAgg = {};
        edges.forEach((edge) => {
            const chargeType = edge.node?.RLM_Charge_Type__c?.value || 'Other';
            const amount = Number(edge.node?.LineAmount?.value ?? 0);
            if (!chargeTypeAgg[chargeType]) {
                chargeTypeAgg[chargeType] = { count: 0, amount: 0 };
            }
            chargeTypeAgg[chargeType].count += 1;
            chargeTypeAgg[chargeType].amount += amount;
        });

        const chargeTypes = this.buildChargeTypeItems(chargeTypeAgg);

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

    buildChargeTypeItems(chargeTypeAgg) {
        return Object.entries(chargeTypeAgg)
            .sort((a, b) => b[1].count - a[1].count)
            .map(([type, agg]) => {
                const config = this.getChargeTypeConfig(type);
                return {
                    key: type,
                    icon: config.icon,
                    label: config.label,
                    count: agg.count,
                    countLabel: `${agg.count}`,
                    formattedAmount: this.formatCurrency(agg.amount),
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

    processDisputes(data) {
        const edges = data?.uiapi?.query?.Dispute?.edges || [];
        if (edges.length === 0) {
            this.disputesData = null;
            return;
        }

        let totalDisputed = 0;
        let totalApproved = 0;

        const disputes = edges.map((edge) => {
            const node = edge.node;
            const disputedAmt = Number(node?.DisputedAmount?.value ?? 0);
            const approvedAmt = Number(node?.ApprovedAmount?.value ?? 0);
            const caseNode = node?.Case;
            const caseStatus = caseNode?.Status?.value || 'Unknown';
            const caseSubject = caseNode?.Subject?.value || '';
            const caseId = caseNode?.Id || '';
            const receivedDate = node?.ReceivedDate?.value;

            totalDisputed += disputedAmt;
            totalApproved += approvedAmt;

            const disputeName = node?.Name?.value || '';
            return {
                id: node.Id,
                name: disputeName,
                navLabel: disputeName ? 'View dispute ' + disputeName : 'View dispute',
                disputedAmount: disputedAmt,
                approvedAmount: approvedAmt,
                formattedDisputed: this.formatCurrency(disputedAmt),
                formattedApproved: this.formatCurrency(approvedAmt),
                caseStatus,
                caseSubject,
                caseId,
                caseNavLabel: caseSubject ? 'View case ' + caseSubject : 'View case',
                hasCaseLink: !!caseId,
                statusClass: this.getDisputeStatusClass(caseStatus),
                formattedDate: receivedDate
                    ? new Date(receivedDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
                    : ''
            };
        });

        this.disputesData = {
            count: disputes.length,
            disputes,
            formattedTotalDisputed: this.formatCurrency(totalDisputed),
            formattedTotalApproved: this.formatCurrency(totalApproved)
        };
    }

    getDisputeStatusClass(status) {
        const s = (status || '').toLowerCase();
        if (s === 'closed') return 'dispute-status dispute-closed';
        if (s === 'new' || s === 'open' || s === 'pending' || s === 'working') return 'dispute-status dispute-pending';
        if (s.includes('error') || s.includes('escalat')) return 'dispute-status dispute-error';
        return 'dispute-status dispute-pending';
    }

    handleTabClick(event) {
        this.activeTab = event.currentTarget.dataset.tab;
    }

    get isSummaryTab() {
        return this.activeTab === 'summary';
    }

    get isDisputesTab() {
        return this.activeTab === 'disputes';
    }

    get summaryTabClass() {
        return 'tab-btn' + (this.activeTab === 'summary' ? ' tab-active' : '');
    }

    get disputesTabClass() {
        return 'tab-btn' + (this.activeTab === 'disputes' ? ' tab-active' : '');
    }

    handleNavigateToDispute(event) {
        const disputeId = event.currentTarget.dataset.id;
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: { recordId: disputeId, objectApiName: 'Dispute', actionName: 'view' }
        });
    }

    handleNavigateToCase(event) {
        const caseId = event.currentTarget.dataset.id;
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: { recordId: caseId, objectApiName: 'Case', actionName: 'view' }
        });
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

    get hasDisputes() {
        return this.disputesData !== null && this.disputesData.count > 0;
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