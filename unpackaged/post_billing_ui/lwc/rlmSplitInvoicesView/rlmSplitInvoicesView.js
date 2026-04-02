import { LightningElement, api, track, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import { gql, graphql } from 'lightning/graphql';
import getRelatedNames from '@salesforce/apex/RLM_SplitInvoicesController.getRelatedNames';

/**
 * Split Invoices View
 *
 * LDS-first implementation that:
 * - Loads current Invoice's CorrelationIdentifier via GraphQL wire
 * - Queries all Invoice records sharing the same CorrelationIdentifier
 * - Displays a simple list of split invoices
 * - Allows navigation to any related Invoice and a quick return to current
 *
 * Uses @wire(graphql) because lightning/graphql is a wire adapter; imperative graphql()
 * is not supported and causes "this.callback is not a function".
 *
 * Object: Invoice (Revenue Cloud Billing standard)
 * Fields used:
 *  Id, Name (display), CorrelationIdentifier, BillingAccountId, DocumentNumber,
 *  InvoiceDate, Balance, Status, BillingArrangementId, BillingProfileId
 */
export default class RlmSplitInvoicesView extends NavigationMixin(LightningElement) {
    // recordId injected by the flexipage when placed on Invoice record page
    @api recordId;

    // UI state
    @track isLoading = true;
    @track error;
    @track errorMessage = '';

    // Data (correlationIdentifier drives second wire reactively)
    correlationIdentifier;
    allRows = [];
    @track rows = [];

    // Stored for refresh
    _refreshCurrent;
    _refreshList;

    // Sorting
    sortedBy = 'InvoiceDate';
    sortedDirection = 'asc';

    // Datatable columns (Invoice is link; Account, Billing Arrangement, Billing Profile are text)
    columns = [
        { label: 'Account', fieldName: 'billingAccountName', type: 'text', sortable: true },
        {
            label: 'Invoice',
            fieldName: 'invoiceUrl',
            type: 'url',
            sortable: true,
            typeAttributes: { label: { fieldName: 'Name' }, target: '_blank' }
        },
        { label: 'Invoice Date', fieldName: 'InvoiceDate', type: 'date', sortable: true },
        { label: 'Balance', fieldName: 'Balance', type: 'currency', sortable: true },
        { label: 'Status', fieldName: 'Status', type: 'text', sortable: true },
        { label: 'Billing Arrangement', fieldName: 'billingArrangementName', type: 'text', sortable: true },
        { label: 'Billing Profile', fieldName: 'billingProfileName', type: 'text', sortable: true },
        {
            type: 'action',
            typeAttributes: {
                rowActions: [
                    { label: 'View Invoice', name: 'open_invoice' },
                    { label: 'View Billing Account', name: 'open_ba' },
                    { label: 'View Billing Arrangement', name: 'open_arrangement' },
                    { label: 'View Billing Profile', name: 'open_profile' }
                ]
            }
        }
    ];

    // Wire 1: current invoice by recordId → get CorrelationIdentifier
    @wire(graphql, {
        query: '$queryCurrentInvoice',
        variables: '$currentInvoiceVariables'
    })
    wiredCurrentInvoice({ data, errors, refresh }) {
        this._refreshCurrent = refresh;
        if (!this.recordId) {
            this.isLoading = false;
            return;
        }
        if (errors && errors.length) {
            this.error = errors;
            this.errorMessage = this.readableError(errors[0]);
            this.rows = [];
            this.isLoading = false;
            return;
        }
        const current = data?.uiapi?.query?.Invoice?.edges?.[0]?.node;
        this.correlationIdentifier = current?.CorrelationIdentifier?.value ?? null;
        if (!this.correlationIdentifier) {
            this.allRows = [];
            this.rows = [];
            this.isLoading = false;
        }
    }

    get currentInvoiceVariables() {
        return this.recordId ? { id: this.recordId } : undefined;
    }

    // Wire 2: invoices by CorrelationIdentifier via GraphQL
    @wire(graphql, {
        query: '$queryInvoicesByCorrelation',
        variables: '$invoicesByCorrelationVariables'
    })
    wiredInvoicesByCorrelation({ data, errors, refresh }) {
        this._refreshList = refresh;
        if (this.correlationIdentifier === undefined) return;
        if (!this.correlationIdentifier) return;
        if (errors && errors.length) {
            this.error = errors;
            this.errorMessage = this.readableError(errors[0]);
            this.rows = [];
            this.isLoading = false;
            return;
        }
        const listEdges = data?.uiapi?.query?.InvoiceByCorrelation?.edges || [];
        const allShaped = listEdges.map((e) => this.shapeRow(e.node)).filter((r) => !!r);
        const rows = allShaped.filter((r) => r.Id !== this.recordId);
        this.error = undefined;
        this.errorMessage = '';

        const accountIds = [...new Set(rows.map((r) => r.billingAccountId).filter(Boolean))];
        const arrangementIds = [...new Set(rows.map((r) => r.billingArrangementId).filter(Boolean))];
        const profileIds = [...new Set(rows.map((r) => r.billingProfileId).filter(Boolean))];

        if (accountIds.length === 0 && arrangementIds.length === 0 && profileIds.length === 0) {
            this.allRows = this.sortData(rows, this.sortedBy, this.sortedDirection);
            this.rows = this.allRows;
            this.isLoading = false;
            return;
        }

        getRelatedNames({ accountIds, arrangementIds, profileIds, contactIds: [] })
            .then((result) => {
                const accountNames = result.accountNames || {};
                const arrangementNames = result.arrangementNames || {};
                const profileNames = result.profileNames || {};
                const merged = rows.map((r) => ({
                    ...r,
                    billingAccountName: (r.billingAccountId && accountNames[r.billingAccountId]) || r.billingAccountName,
                    billingArrangementName: (r.billingArrangementId && arrangementNames[r.billingArrangementId]) || r.billingArrangementName,
                    billingProfileName: (r.billingProfileId && profileNames[r.billingProfileId]) || r.billingProfileName
                }));
                this.allRows = this.sortData(merged, this.sortedBy, this.sortedDirection);
                this.rows = this.allRows;
            })
            .catch(() => {
                this.allRows = this.sortData(rows, this.sortedBy, this.sortedDirection);
                this.rows = this.allRows;
            })
            .finally(() => {
                this.isLoading = false;
            });
    }

    get invoicesByCorrelationVariables() {
        return this.correlationIdentifier
            ? { correlation: this.correlationIdentifier }
            : undefined;
    }

    // GraphQL: current invoice by Id (UI API: fields are on node, not under "fields")
    queryCurrentInvoice = gql`
        query CurrentInvoice($id: ID!) {
            uiapi {
                query {
                    Invoice(
                        where: { Id: { eq: $id } }
                        first: 1
                    ) {
                        edges {
                            node {
                                Id
                                CorrelationIdentifier { value }
                            }
                        }
                    }
                }
            }
        }
    `;

    // GraphQL: invoices by CorrelationIdentifier (UI API - uses same schema as wire 1, so CorrelationIdentifier works)
    queryInvoicesByCorrelation = gql`
        query InvoicesByCorrelation($correlation: String!) {
            uiapi {
                query {
                    InvoiceByCorrelation: Invoice(
                        where: { CorrelationIdentifier: { eq: $correlation } }
                        orderBy: { DocumentNumber: { order: ASC } }
                        first: 500
                    ) {
                        edges {
                            node {
                                Id
                                DocumentNumber { value }
                                InvoiceDate { value }
                                Balance { value }
                                Status { value }
                                CorrelationIdentifier { value }
                                BillingAccountId { value }
                                BillingArrangementId { value }
                                BillingProfileId { value }
                            }
                        }
                    }
                }
            }
        }
    `;

    shapeRow(node) {
        if (!node) return undefined;
        const id = node.Id;
        const documentNumber = node?.DocumentNumber?.value;
        const name = documentNumber;
        const invoiceDate = node?.InvoiceDate?.value;
        const balance = node?.Balance?.value;
        const status = node?.Status?.value;
        const baId = node?.BillingAccountId?.value || null;
        const arrangementId = node?.BillingArrangementId?.value || null;
        const profileId = node?.BillingProfileId?.value || null;
        return {
            Id: id,
            Name: name,
            DocumentNumber: documentNumber,
            InvoiceDate: invoiceDate,
            Balance: balance,
            Status: status,
            billingAccountId: baId,
            billingAccountName: baId || null,
            billingArrangementId: arrangementId,
            billingArrangementName: arrangementId || null,
            billingProfileId: profileId,
            billingProfileName: profileId || null,
            invoiceUrl: this.buildRecordUrl(id),
            billingAccountUrl: baId ? this.buildRecordUrl(baId) : null,
            billingArrangementUrl: arrangementId ? this.buildRecordUrl(arrangementId) : null,
            billingProfileUrl: profileId ? this.buildRecordUrl(profileId) : null
        };
    }

    handleSort(event) {
        const { fieldName, sortDirection } = event.detail;
        this.sortedBy = fieldName;
        this.sortedDirection = sortDirection;
        this.rows = this.sortData([...this.rows], fieldName, sortDirection);
    }

    handleRowAction(event) {
        const action = event.detail.action.name;
        const row = event.detail.row;
        switch (action) {
            case 'open_invoice':
                this.navigateToRecord(row.Id, 'Invoice');
                break;
            case 'open_ba':
                if (row.billingAccountId) this.navigateToRecord(row.billingAccountId);
                break;
            case 'open_arrangement':
                if (row.billingArrangementId) this.navigateToRecord(row.billingArrangementId);
                break;
            case 'open_profile':
                if (row.billingProfileId) this.navigateToRecord(row.billingProfileId);
                break;
            default:
        }
    }

    sortData(data, field, direction) {
        const multiplier = direction === 'asc' ? 1 : -1;
        return [...data].sort((a, b) => {
            const v1 = a[field] ?? '';
            const v2 = b[field] ?? '';
            if (v1 > v2) return 1 * multiplier;
            if (v1 < v2) return -1 * multiplier;
            return 0;
        });
    }

    // Navigation helpers
    buildRecordUrl(id) {
        return `/lightning/r/${id}/view`;
    }

    navigateToRecord(id, objectApiName) {
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: {
                recordId: id,
                actionName: 'view',
                objectApiName
            }
        });
    }

    readableError(e) {
        if (!e) return 'Unknown error';
        if (Array.isArray(e.body)) return e.body.map((x) => x.message).join(', ');
        if (e.body && e.body.message) return e.body.message;
        if (e.message) return e.message;
        try {
            return JSON.stringify(e);
        } catch {
            return 'Unknown error';
        }
    }

    @api async refresh() {
        this.isLoading = true;
        this.error = undefined;
        try {
            await this._refreshCurrent?.();
            await this._refreshList?.();
        } catch (err) {
            this.error = err;
            this.errorMessage = this.readableError(err);
        } finally {
            this.isLoading = false;
        }
    }
}