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

// Each read is loading until its own reply, then ready or unavailable (todo 509). A refused or failed
// read shows only UNAVAILABLE_TEXT, never the platform's text (that goes to the console) and never an
// empty "No split invoices found"; a record change puts every read back to loading.
const LOADING = 'loading';
const READY = 'ready';
const UNAVAILABLE = 'unavailable';
const UNAVAILABLE_TEXT = 'Unable to read the split invoices. Contact your administrator.';

export default class RlmSplitInvoicesView extends NavigationMixin(LightningElement) {
    _recordId;

    // recordId injected by the flexipage when placed on Invoice record page
    @api
    get recordId() { return this._recordId; }
    set recordId(value) {
        if (value !== this._recordId) {
            // A new record: both reads start over, and a names reply in flight is dropped.
            this._seq += 1;
            this.currentState = LOADING;
            this.listState = LOADING;
            this.correlationIdentifier = undefined;
            this.allRows = [];
            this.rows = [];
        }
        this._recordId = value;
    }

    // One state per read: the current invoice (its correlation id) and the split list. Each read's
    // reply sets only its own state.
    currentState = LOADING;
    listState = LOADING;
    // Bumped by a record change, a new correlation id, a list reply and a list failure: a names reply
    // applies only while it is still the latest.
    _seq = 0;

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

    // The view's one state: the current invoice's, then (when it has a correlation id) the list's.
    get state() {
        if (!this.recordId) return READY;
        if (this.currentState !== READY) return this.currentState;
        if (!this.correlationIdentifier) return READY;
        return this.listState;
    }
    get isLoading() { return this.state === LOADING; }
    get isUnavailable() { return this.state === UNAVAILABLE; }
    get unavailableText() { return UNAVAILABLE_TEXT; }
    get hasRows() { return this.state === READY && this.rows.length > 0; }
    get isEmpty() { return this.state === READY && this.rows.length === 0; }

    // Wire 1: current invoice by recordId → get CorrelationIdentifier
    @wire(graphql, {
        query: '$queryCurrentInvoice',
        variables: '$currentInvoiceVariables'
    })
    wiredCurrentInvoice({ data, errors, refresh }) {
        this._refreshCurrent = refresh;
        if (errors && errors.length) {
            this._fail('current', errors);
            return;
        }
        // The empty delivery before the first reply is not an answer.
        if (!data) return;
        const current = data?.uiapi?.query?.Invoice?.edges?.[0]?.node;
        const correlation = current?.CorrelationIdentifier?.value ?? null;
        if (correlation !== this.correlationIdentifier) {
            // A different correlation id: its list is read afresh. The same id (a re-read of this
            // invoice) leaves the list's state as it is, since the list wire does not answer again.
            this._seq += 1;
            this.listState = LOADING;
            this.allRows = [];
            this.rows = [];
        }
        this.correlationIdentifier = correlation;
        this.currentState = READY;
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
        if (!this.correlationIdentifier) return;
        if (errors && errors.length) {
            this._fail('list', errors);
            return;
        }
        if (!data) return;
        const seq = (this._seq += 1);
        const listEdges = data?.uiapi?.query?.InvoiceByCorrelation?.edges || [];
        const allShaped = listEdges.map((e) => this.shapeRow(e.node)).filter((r) => !!r);
        const rows = allShaped.filter((r) => r.Id !== this.recordId);

        const accountIds = [...new Set(rows.map((r) => r.billingAccountId).filter(Boolean))];
        const arrangementIds = [...new Set(rows.map((r) => r.billingArrangementId).filter(Boolean))];
        const profileIds = [...new Set(rows.map((r) => r.billingProfileId).filter(Boolean))];

        if (accountIds.length === 0 && arrangementIds.length === 0 && profileIds.length === 0) {
            this._showRows(rows);
            return;
        }

        // The list shows once its names are read; a name that cannot be read stays a dash.
        getRelatedNames({ accountIds, arrangementIds, profileIds, contactIds: [] })
            .then((result) => {
                const accountNames = result?.accountNames || {};
                const arrangementNames = result?.arrangementNames || {};
                const profileNames = result?.profileNames || {};
                return rows.map((r) => ({
                    ...r,
                    billingAccountName: (r.billingAccountId && accountNames[r.billingAccountId]) || r.billingAccountName,
                    billingArrangementName: (r.billingArrangementId && arrangementNames[r.billingArrangementId]) || r.billingArrangementName,
                    billingProfileName: (r.billingProfileId && profileNames[r.billingProfileId]) || r.billingProfileName
                }));
            })
            .catch(() => rows)
            .then((named) => {
                if (seq === this._seq) this._showRows(named);
            });
    }

    _showRows(rows) {
        this.allRows = this.sortData(rows, this.sortedBy, this.sortedDirection);
        this.rows = this.allRows;
        this.listState = READY;
    }

    // A refused or failed read: its own state becomes unavailable and the platform's text goes to the
    // console only. A list failure also drops its rows and any names reply in flight.
    _fail(source, error) {
        console.error(`rlmSplitInvoicesView: the ${source} invoice read failed`, error);
        if (source === 'current') {
            this.currentState = UNAVAILABLE;
            return;
        }
        this._seq += 1;
        this.listState = UNAVAILABLE;
        this.allRows = [];
        this.rows = [];
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
        // The invoice link's label: a missing document number shows a dash, never the link (an Id).
        const name = documentNumber || '—';
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
            billingAccountName: '—',
            billingArrangementId: arrangementId,
            billingArrangementName: '—',
            billingProfileId: profileId,
            billingProfileName: '—',
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

    // Re-reads both invoices. Nothing is cleared first: a re-read whose result is unchanged may not
    // answer again. A re-read that fails marks its own read unavailable.
    @api async refresh() {
        const recordId = this.recordId;
        await this._refreshRead('current', this._refreshCurrent, recordId);
        await this._refreshRead('list', this._refreshList, recordId);
    }

    async _refreshRead(source, refresh, recordId) {
        try {
            await refresh?.();
        } catch (err) {
            if (this.recordId === recordId) this._fail(source, err);
        }
    }
}