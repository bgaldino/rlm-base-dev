import { LightningElement, api, track, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import { gql, graphql } from 'lightning/graphql';
import getRelatedNames from '@salesforce/apex/RLM_DisputeDetailsController.getRelatedNames';
import { parseDateOnly } from 'c/rlmDateOnly';

// Each read is loading until its own reply, then ready or unavailable (todo 509). A refused or failed
// read shows only its fixed sentence, never the platform's text (that goes to the console); a refused
// line read never reads as a dispute with no lines. A record change puts every read back to loading.
const LOADING = 'loading';
const READY = 'ready';
const UNAVAILABLE = 'unavailable';
const DISPUTE_UNAVAILABLE_TEXT = "Unable to read this case's dispute. Contact your administrator.";
const LINES_UNAVAILABLE_TEXT = "Unable to read this dispute's lines. Contact your administrator.";

/**
 * Dispute Details – shows the Dispute record linked to the current Case and its disputed lines.
 * Approved amounts are read-only here; they are edited on the dispute items themselves.
 */
export default class RlmDisputeDetails extends NavigationMixin(LightningElement) {
    _recordId;

    @api
    get recordId() { return this._recordId; }
    set recordId(value) {
        if (value !== this._recordId) {
            // A new case: both reads start over, and a line-names reply in flight is dropped.
            this._seq += 1;
            this.disputeState = LOADING;
            this.linesState = LOADING;
            this.disputeData = null;
            this.disputeItems = [];
            this._disputeId = null;
        }
        this._recordId = value;
    }

    // One state per read: the case's dispute and the dispute's lines. Each read's reply sets only its
    // own state.
    disputeState = LOADING;
    linesState = LOADING;
    @track disputeData = null;
    @track disputeItems = [];

    _disputeId = null;
    // Bumped by a record change, a different dispute, a line reply and a line failure: a line-names
    // reply applies only while it is still the latest.
    _seq = 0;

    // ── View state ──
    get isLoading() {
        if (!this.recordId) return false;
        if (this.disputeState === LOADING) return true;
        return this.disputeState === READY && this.hasData && this.linesState === LOADING;
    }

    get disputeUnavailable() { return !!this.recordId && this.disputeState === UNAVAILABLE; }
    get disputeUnavailableText() { return DISPUTE_UNAVAILABLE_TEXT; }
    get showDispute() { return !this.isLoading && this.disputeState === READY && this.hasData; }
    get noDispute() { return !this.recordId || (this.disputeState === READY && !this.hasData); }

    get linesUnavailable() { return this.linesState === UNAVAILABLE; }
    get linesUnavailableText() { return LINES_UNAVAILABLE_TEXT; }
    get showItems() { return this.linesState === READY && this.disputeItems.length > 0; }

    // The total of the lines' approved amounts: unavailable when the lines could not be read, never a
    // blank or $0.00 that reads as nothing approved.
    get formattedApprovedTotal() {
        if (this.linesState === UNAVAILABLE) return 'Unavailable';
        if (this.linesState !== READY) return '';
        const total = this.disputeItems.reduce((sum, item) => sum + (Number(item.approvedAmount) || 0), 0);
        return this.formatCurrency(total);
    }

    // ── Header getters ──
    get disputeName() {
        return this.showDispute ? this.disputeData.name : '';
    }

    get disputeRecordUrl() {
        return this.disputeData?.disputeUrl || '#';
    }

    get disputeRecordId() {
        return this.disputeData?.id || '';
    }

    // ── Dispute Query ──
    @wire(graphql, {
        query: '$queryDispute',
        variables: '$disputeVariables'
    })
    wiredDispute({ data, errors }) {
        if (errors && errors.length) {
            console.error('rlmDisputeDetails: the dispute read failed', errors);
            this.disputeState = UNAVAILABLE;
            this.disputeData = null;
            return;
        }
        // The empty delivery before the first reply is not an answer.
        if (!data) return;
        const node = data?.uiapi?.query?.Dispute?.edges?.[0]?.node;
        const id = node?.Id || null;
        if (id !== this._disputeId) {
            // A different dispute (or none): its lines are read afresh. The same dispute (a re-read)
            // leaves the lines' state as it is, since the line wire does not answer again.
            this._seq += 1;
            this.linesState = LOADING;
            this.disputeItems = [];
            this._disputeId = id;
        }
        this.disputeData = node ? this.shapeDispute(node) : null;
        this.disputeState = READY;
    }

    get disputeVariables() {
        return this.recordId ? { caseId: this.recordId } : undefined;
    }

    queryDispute = gql`
        query DisputeForCase($caseId: ID!) {
            uiapi {
                query {
                    Dispute(where: { CaseId: { eq: $caseId } }, first: 1) {
                        edges {
                            node {
                                Id
                                Name { value }
                                InvoiceId { value }
                                DisputedAmount { value }
                                ApprovedAmount { value }
                                ReceivedDate { value }
                                ResolutionAction { value }
                                ResolutionActionStatus { value }
                            }
                        }
                    }
                }
            }
        }
    `;

    // ── Dispute Items Query (with InvoiceLine relationship) ──
    @wire(graphql, {
        query: '$queryDisputeItems',
        variables: '$disputeItemsVariables'
    })
    wiredDisputeItems({ data, errors }) {
        if (!this._disputeId) return;
        if (errors && errors.length) {
            console.error('rlmDisputeDetails: the dispute line read failed', errors);
            this._seq += 1;
            this.linesState = UNAVAILABLE;
            this.disputeItems = [];
            return;
        }
        if (!data) return;
        this.processDisputeItems(data, (this._seq += 1));
    }

    get disputeItemsVariables() {
        return this._disputeId ? { disputeId: this._disputeId } : undefined;
    }

    queryDisputeItems = gql`
        query DisputeItemsForDispute($disputeId: ID!) {
            uiapi {
                query {
                    DisputeItem(where: { DisputeId: { eq: $disputeId } }, first: 500) {
                        edges {
                            node {
                                Id
                                InvoiceLineId { value }
                                DisputedAmount { value }
                                ApprovedAmount { value }
                                InvoiceLine {
                                    Name { value }
                                    Balance { value }
                                    RLM_Charge_Type__c { value }
                                    InvoiceLineStartDate { value }
                                    InvoiceLineEndDate { value }
                                }
                            }
                        }
                    }
                }
            }
        }
    `;

    shapeDispute(node) {
        const id = node.Id;
        const name = node?.Name?.value || '—';
        const invoiceId = node?.InvoiceId?.value || null;
        const disputedAmount = Number(node?.DisputedAmount?.value ?? 0);
        const receivedDate = node?.ReceivedDate?.value;
        const resolutionAction = node?.ResolutionAction?.value || 'N/A';
        const resolutionActionStatus = node?.ResolutionActionStatus?.value || 'N/A';

        const formattedReceivedDate = receivedDate
            ? parseDateOnly(receivedDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
            : '—';

        // Resolve Invoice DocumentNumber via Apex. The name is applied only while the dispute shown
        // still points at that invoice, so a late reply never lands on another dispute.
        if (invoiceId) {
            getRelatedNames({ invoiceIds: [invoiceId], invoiceLineIds: [] })
                .then((result) => {
                    const invoiceName = result?.invoiceNames?.[invoiceId];
                    if (invoiceName && this.disputeData?.invoiceId === invoiceId) {
                        this.disputeData = { ...this.disputeData, invoiceDisplayName: invoiceName };
                    }
                })
                .catch(() => { /* keep the dash */ });
        }

        return {
            id,
            name,
            invoiceId,
            // The invoice's document number once resolved; a dash until then, never the record Id.
            invoiceDisplayName: '—',
            hasInvoice: !!invoiceId,
            formattedDisputedAmount: this.formatCurrency(disputedAmount),
            formattedReceivedDate,
            resolutionAction,
            resolutionActionStatus,
            disputeUrl: this.buildRecordUrl(id),
            invoiceUrl: invoiceId ? this.buildRecordUrl(invoiceId) : null
        };
    }

    processDisputeItems(data, seq) {
        const edges = data?.uiapi?.query?.DisputeItem?.edges || [];

        const items = edges.map((edge) => {
            const node = edge.node;
            const invoiceLineId = node?.InvoiceLineId?.value || null;
            const disputedAmt = Number(node?.DisputedAmount?.value ?? 0);
            const approvedAmt = Number(node?.ApprovedAmount?.value ?? 0);

            // Read name, balance, charge type from GraphQL relationship traversal
            const gqlName = node?.InvoiceLine?.Name?.value || null;
            const gqlBalance = node?.InvoiceLine?.Balance?.value;
            const gqlChargeType = node?.InvoiceLine?.RLM_Charge_Type__c?.value || '—';
            const startDate = node?.InvoiceLine?.InvoiceLineStartDate?.value;
            const endDate = node?.InvoiceLine?.InvoiceLineEndDate?.value;
            const fmtDate = (d) => d ? parseDateOnly(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '';
            const billingPeriod = startDate && endDate ? `${fmtDate(startDate)} – ${fmtDate(endDate)}` : '—';

            return {
                id: node.Id,
                invoiceLineId,
                // A dash, never the record Id, until a name is resolved.
                invoiceLineName: gqlName || '—',
                hasInvoiceLine: !!invoiceLineId,
                invoiceLineUrl: invoiceLineId ? this.buildRecordUrl(invoiceLineId) : null,
                formattedDisputedAmount: this.formatCurrency(disputedAmt),
                approvedAmount: approvedAmt,
                formattedApprovedAmount: this.formatCurrency(approvedAmt),
                chargeType: gqlChargeType,
                billingPeriod,
                balance: gqlBalance != null ? this.formatCurrency(Number(gqlBalance)) : '—',
                _hasGqlName: !!gqlName
            };
        });

        // If GraphQL relationship didn't return names, fall back to Apex; the lines show once it
        // answers, and a name it cannot read stays a dash.
        const needsApex = items.some((i) => i.invoiceLineId && !i._hasGqlName);
        const invoiceLineIds = items.map((i) => i.invoiceLineId).filter(Boolean);
        if (!needsApex || invoiceLineIds.length === 0) {
            this._applyItems(items);
            return;
        }
        getRelatedNames({ invoiceIds: [], invoiceLineIds })
            .then((result) => {
                const lineNames = result?.lineNames || {};
                const lineBalances = result?.lineBalances || {};
                return items.map((item) => ({
                    ...item,
                    invoiceLineName: (item.invoiceLineId && lineNames[item.invoiceLineId]) || item.invoiceLineName,
                    balance: (item.balance === '—' && item.invoiceLineId && lineBalances[item.invoiceLineId] != null)
                        ? this.formatCurrency(lineBalances[item.invoiceLineId])
                        : item.balance
                }));
            })
            .catch(() => items)
            .then((named) => {
                // A reply for lines no longer shown does not touch the current load.
                if (seq === this._seq) this._applyItems(named);
            });
    }

    _applyItems(items) {
        this.disputeItems = items;
        this.linesState = READY;
    }

    // ── Getters ──
    get hasData() {
        return this.disputeData !== null;
    }

    get itemCount() {
        return this.disputeItems.length;
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
    }

    buildRecordUrl(recordId) {
        return `/lightning/r/${recordId}/view`;
    }

    handleLinkClick(event) {
        const id = event.currentTarget?.dataset?.id;
        if (!id) return;
        event.preventDefault();
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: {
                recordId: id,
                actionName: 'view'
            }
        });
    }
}
