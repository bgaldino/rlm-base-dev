import { LightningElement, api, track, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import { gql, graphql } from 'lightning/graphql';
import invoiceCardLogo from '@salesforce/resourceUrl/RLM_InvoiceCardLogo';
import getRelatedNames from '@salesforce/apex/RLM_SplitInvoicesController.getRelatedNames';
import { parseDateOnly } from 'c/rlmDateOnly';

// Each read is loading until its own reply, then ready or unavailable (todo 509), as in
// rlmSplitInvoicesView. A refused or failed read shows only UNAVAILABLE_TEXT, never the platform's text
// (that goes to the console) and never an empty "No split invoices found"; a record change puts every
// read back to loading.
const LOADING = 'loading';
const READY = 'ready';
const UNAVAILABLE = 'unavailable';
const UNAVAILABLE_TEXT = 'Unable to read the split invoices. Contact your administrator.';

/**
 * Split Invoices Cards – card-based view of split invoices sharing the same CorrelationIdentifier.
 */
export default class RlmSplitInvoicesCards extends NavigationMixin(LightningElement) {
    _recordId;

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

    correlationIdentifier;
    allRows = [];
    @track rows = [];

    _refreshCurrent;
    _refreshList;

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

    get invoiceCardLogoUrl() {
        return invoiceCardLogo;
    }

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
        // Exclude the current invoice (the record we're on)
        const rows = allShaped.filter((r) => r.Id !== this.recordId);

        const accountIds = [...new Set(rows.map((r) => r.billingAccountId).filter(Boolean))];
        const profileIds = [...new Set(rows.map((r) => r.billingProfileId).filter(Boolean))];
        const contactIds = [...new Set(rows.map((r) => r.billToContactId).filter(Boolean))];

        if (accountIds.length === 0 && profileIds.length === 0 && contactIds.length === 0) {
            this._showRows(rows);
            return;
        }

        // The cards show once their names are read; a name that cannot be read stays a dash.
        getRelatedNames({ accountIds, profileIds, contactIds })
            .then((result) => {
                const accountNames = result?.accountNames || {};
                const profileNames = result?.profileNames || {};
                const contactNames = result?.contactNames || {};
                return rows.map((r) => ({
                    ...r,
                    billingAccountName: (r.billingAccountId && accountNames[r.billingAccountId]) || r.billingAccountName,
                    billingProfileName: (r.billingProfileId && profileNames[r.billingProfileId]) || r.billingProfileName,
                    billToContactName: (r.billToContactId && contactNames[r.billToContactId]) || r.billToContactName
                }));
            })
            .catch(() => rows)
            .then((named) => {
                if (seq === this._seq) this._showRows(named);
            });
    }

    _showRows(rows) {
        this.allRows = rows;
        this.rows = rows;
        this.listState = READY;
    }

    // A refused or failed read: its own state becomes unavailable and the platform's text goes to the
    // console only. A list failure also drops its rows and any names reply in flight.
    _fail(source, error) {
        console.error(`rlmSplitInvoicesCards: the ${source} invoice read failed`, error);
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

    queryCurrentInvoice = gql`
        query CurrentInvoice($id: ID!) {
            uiapi {
                query {
                    Invoice(where: { Id: { eq: $id } }, first: 1) {
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
                                TotalAmountWithTax { value }
                                Status { value }
                                CorrelationIdentifier { value }
                                BillingAccountId { value }
                                BillingProfileId { value }
                                BillToContactId { value }
                                SettlementStatus { value }
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
        // A missing document number shows a dash, never the record Id.
        const name = documentNumber || '—';
        const invoiceDate = node?.InvoiceDate?.value;
        const totalWithTax = node?.TotalAmountWithTax?.value;
        const status = node?.Status?.value ?? '';
        const baId = node?.BillingAccountId?.value || null;
        const profileId = node?.BillingProfileId?.value || null;
        const billToContactId = node?.BillToContactId?.value || null;
        const settlementStatus = node?.SettlementStatus?.value ?? '';

        const statusLower = status.toLowerCase();
        let statusBadgeClass = 'card-badge card-badge-neutral';
        if (statusLower === 'posted' || statusLower.includes('paid')) statusBadgeClass = 'card-badge card-badge-success';
        else if (statusLower.includes('draft')) statusBadgeClass = 'card-badge card-badge-warning';
        else if (statusLower.includes('error') || statusLower.includes('cancel')) statusBadgeClass = 'card-badge card-badge-danger';

        const settlementLower = (settlementStatus || '').toLowerCase();
        let settlementStatusClass = 'card-value';
        if (settlementLower.includes('not settled') || settlementLower === 'unsettled') settlementStatusClass = 'card-value card-value-settlement-unsettled';
        else if (settlementLower.includes('partially settled') || settlementLower.includes('partial')) settlementStatusClass = 'card-value card-value-settlement-partial';
        else if (settlementLower.includes('completely settled') || (settlementLower.includes('settled') && !settlementLower.includes('partial'))) settlementStatusClass = 'card-value card-value-settlement-settled';

        let formattedTotalWithTax = '';
        if (totalWithTax != null && totalWithTax !== '') {
            const num = Number(totalWithTax);
            if (!Number.isNaN(num)) formattedTotalWithTax = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
            else formattedTotalWithTax = String(totalWithTax);
        }
        const formattedDate = invoiceDate
            ? parseDateOnly(invoiceDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
            : '';

        return {
            Id: id,
            Name: name,
            DocumentNumber: documentNumber,
            InvoiceDate: invoiceDate,
            TotalWithTax: totalWithTax,
            Status: status,
            formattedTotalWithTax,
            formattedDate,
            statusBadgeClass,
            billingAccountId: baId,
            billingAccountName: '—',
            billingProfileId: profileId,
            billingProfileName: '—',
            invoiceUrl: this.buildRecordUrl(id),
            billingAccountUrl: baId ? this.buildRecordUrl(baId) : null,
            billingProfileUrl: profileId ? this.buildRecordUrl(profileId) : null,
            noAccount: !baId,
            noProfile: !profileId,
            billToContactId,
            billToContactName: '—',
            settlementStatus: settlementStatus || '—',
            settlementStatusClass
        };
    }

    handleLinkClick(event) {
        const action = event.currentTarget?.dataset?.action;
        const id = event.currentTarget?.dataset?.id;
        if (!id || !action) return;
        event.preventDefault();
        if (action === 'open_invoice') this.navigateToRecord(id, 'Invoice');
        else if (action === 'open_ba') this.navigateToRecord(id);
        else if (action === 'open_profile') this.navigateToRecord(id);
    }

    buildRecordUrl(id) {
        return `/lightning/r/${id}/view`;
    }

    navigateToRecord(id, objectApiName) {
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: { recordId: id, actionName: 'view', objectApiName }
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