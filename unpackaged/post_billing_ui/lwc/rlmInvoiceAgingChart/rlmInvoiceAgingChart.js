import { LightningElement, api, track, wire } from 'lwc';
import { gql, graphql } from 'lightning/graphql';

/**
 * Invoice Aging Chart – displays aging metrics and a bar chart for invoices
 * associated with the current Account.
 */
export default class RlmInvoiceAgingChart extends LightningElement {
    @api recordId;

    @track isLoading = true;
    @track error;
    @track errorMessage = '';

    // Metrics
    totalInvoices = 0;
    openInvoices = 0;
    overdueInvoices = 0;
    averageInvoiceAge = 0;
    maxInvoiceAge = 0;

    // Aging buckets
    bucket0to30 = 0;
    bucket30to60 = 0;
    bucket60to90 = 0;
    bucket90plus = 0;

    // For chart scaling
    maxBucketValue = 1;

    @wire(graphql, {
        query: '$queryInvoices',
        variables: '$invoiceVariables'
    })
    wiredInvoices({ data, errors }) {
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
            this.processInvoices(data);
            this.error = undefined;
            this.errorMessage = '';
            this.isLoading = false;
        }
    }

    get invoiceVariables() {
        return this.recordId ? { accountId: this.recordId } : undefined;
    }

    queryInvoices = gql`
        query InvoicesForAccount($accountId: ID!) {
            uiapi {
                query {
                    Invoice(
                        where: { BillingAccountId: { eq: $accountId } }
                        first: 2000
                    ) {
                        edges {
                            node {
                                Id
                                Status { value }
                                DaysInvoiceOpen { value }
                                DaysInvoiceOverdue { value }
                                SettlementStatus { value }
                                Balance { value }
                            }
                        }
                    }
                }
            }
        }
    `;

    processInvoices(data) {
        const edges = data?.uiapi?.query?.Invoice?.edges || [];
        
        let total = 0;
        let open = 0;
        let overdue = 0;
        let b0to30 = 0;
        let b30to60 = 0;
        let b60to90 = 0;
        let b90plus = 0;
        let totalOpenDays = 0;
        let maxOpenDays = 0;

        edges.forEach((edge) => {
            const node = edge.node;
            const status = (node?.Status?.value || '').toLowerCase();

            // Only include Posted invoices
            if (status !== 'posted') {
                return;
            }

            const daysOpen = node?.DaysInvoiceOpen?.value ?? 0;
            const daysOverdue = node?.DaysInvoiceOverdue?.value ?? 0;
            const settlementStatus = (node?.SettlementStatus?.value || '').toLowerCase();
            const balance = Number(node?.Balance?.value ?? 0);

            total++;

            // Open = Balance > 0 AND (Not Settled OR Partially Settled)
            const isNotSettled = settlementStatus.includes('not settled');
            const isPartiallySettled = settlementStatus.includes('partially') || (settlementStatus.includes('partial') && settlementStatus.includes('settled'));
            const isOpen = balance > 0 && (isNotSettled || isPartiallySettled);

            if (isOpen) {
                open++;
                totalOpenDays += daysOpen;
                if (daysOpen > maxOpenDays) {
                    maxOpenDays = daysOpen;
                }

                // Aging buckets based on DaysInvoiceOpen (only for open invoices)
                if (daysOpen < 30) {
                    b0to30++;
                } else if (daysOpen < 60) {
                    b30to60++;
                } else if (daysOpen < 90) {
                    b60to90++;
                } else {
                    b90plus++;
                }
            }

            // Overdue = DaysInvoiceOverdue > 0 AND Balance > 0
            if (daysOverdue > 0 && balance > 0) {
                overdue++;
            }
        });

        this.totalInvoices = total;
        this.openInvoices = open;
        this.overdueInvoices = overdue;
        this.averageInvoiceAge = open > 0 ? Math.round(totalOpenDays / open) : 0;
        this.maxInvoiceAge = maxOpenDays;
        this.bucket0to30 = b0to30;
        this.bucket30to60 = b30to60;
        this.bucket60to90 = b60to90;
        this.bucket90plus = b90plus;
        this.maxBucketValue = Math.max(b0to30, b30to60, b60to90, b90plus, 1);
    }

    // Computed bar styles for inline width
    get bar0to30Style() {
        const pct = (this.bucket0to30 / this.maxBucketValue) * 100;
        return `width: ${pct}%`;
    }
    get bar30to60Style() {
        const pct = (this.bucket30to60 / this.maxBucketValue) * 100;
        return `width: ${pct}%`;
    }
    get bar60to90Style() {
        const pct = (this.bucket60to90 / this.maxBucketValue) * 100;
        return `width: ${pct}%`;
    }
    get bar90plusStyle() {
        const pct = (this.bucket90plus / this.maxBucketValue) * 100;
        return `width: ${pct}%`;
    }

    get hasData() {
        return this.totalInvoices > 0;
    }

    readableError(err) {
        if (!err) return 'Unknown error';
        if (typeof err === 'string') return err;
        if (err.message) return err.message;
        if (err.body?.message) return err.body.message;
        return JSON.stringify(err);
    }
}