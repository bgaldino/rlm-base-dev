import { LightningElement, api, track, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import { gql, graphql } from 'lightning/graphql';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import getRelatedNames from '@salesforce/apex/RLM_DisputeDetailsController.getRelatedNames';
import saveApprovedAmounts from '@salesforce/apex/RLM_DisputeDetailsController.saveApprovedAmounts';

/**
 * Dispute Details – shows the Dispute record linked to the current Case,
 * with editable approved amounts on dispute items.
 */
export default class RlmDisputeDetails extends NavigationMixin(LightningElement) {
    @api recordId;

    @track isLoading = true;
    @track isSaving = false;
    @track error;
    @track errorMessage = '';
    @track disputeData = null;
    @track disputeItems = [];

    _disputeId = null;
    _disputeLoaded = false;
    _itemsLoaded = false;
    _rawDisputedAmount = 0;

    // ── Header getters ──
    get disputeName() {
        return this.disputeData?.name || '';
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
        if (!this.recordId) {
            this._disputeLoaded = true;
            this._itemsLoaded = true;
            this.checkLoadingComplete();
            return;
        }
        if (errors && errors.length) {
            this.error = errors;
            this.errorMessage = this.readableError(errors[0]);
            this._disputeLoaded = true;
            this._itemsLoaded = true;
            this.checkLoadingComplete();
            return;
        }
        if (data) {
            this.processDispute(data);
            this.error = undefined;
            this.errorMessage = '';
            this._disputeLoaded = true;
            if (!this._disputeId) {
                this._itemsLoaded = true;
            }
            this.checkLoadingComplete();
        }
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
            this.disputeItems = [];
            this._itemsLoaded = true;
            this.checkLoadingComplete();
            return;
        }
        if (data) {
            this.processDisputeItems(data);
        }
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

    checkLoadingComplete() {
        if (this._disputeLoaded && this._itemsLoaded) {
            this.isLoading = false;
        }
    }

    processDispute(data) {
        const node = data?.uiapi?.query?.Dispute?.edges?.[0]?.node;
        if (!node) {
            this.disputeData = null;
            this._disputeId = null;
            return;
        }

        const id = node.Id;
        const name = node?.Name?.value || '—';
        const invoiceId = node?.InvoiceId?.value || null;
        const disputedAmount = Number(node?.DisputedAmount?.value ?? 0);
        const receivedDate = node?.ReceivedDate?.value;
        const resolutionAction = node?.ResolutionAction?.value || 'N/A';
        const resolutionActionStatus = node?.ResolutionActionStatus?.value || 'N/A';

        const formattedReceivedDate = receivedDate
            ? new Date(receivedDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
            : '—';

        this._disputeId = id;
        this._rawDisputedAmount = disputedAmount;

        this.disputeData = {
            id,
            name,
            invoiceId,
            invoiceDisplayName: invoiceId || '—',
            hasInvoice: !!invoiceId,
            formattedDisputedAmount: this.formatCurrency(disputedAmount),
            formattedReceivedDate,
            resolutionAction,
            resolutionActionStatus,
            disputeUrl: this.buildRecordUrl(id),
            invoiceUrl: invoiceId ? this.buildRecordUrl(invoiceId) : null
        };

        // Resolve Invoice DocumentNumber via Apex
        if (invoiceId) {
            getRelatedNames({ invoiceIds: [invoiceId], invoiceLineIds: [] })
                .then((result) => {
                    const invoiceNames = result.invoiceNames || {};
                    if (invoiceNames[invoiceId]) {
                        this.disputeData = {
                            ...this.disputeData,
                            invoiceDisplayName: invoiceNames[invoiceId]
                        };
                    }
                })
                .catch(() => { /* keep ID as fallback */ });
        }
    }

    processDisputeItems(data) {
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
            const fmtDate = (d) => d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '';
            const billingPeriod = startDate && endDate ? `${fmtDate(startDate)} – ${fmtDate(endDate)}` : '—';

            return {
                id: node.Id,
                invoiceLineId,
                invoiceLineName: gqlName || invoiceLineId || '—',
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

        this.disputeItems = items;
        this.recalculateTotalApproved();

        // If GraphQL relationship didn't return names, fall back to Apex
        const needsApex = items.some((i) => i.invoiceLineId && !i._hasGqlName);
        const invoiceLineIds = items.map((i) => i.invoiceLineId).filter(Boolean);

        if (needsApex && invoiceLineIds.length > 0) {
            getRelatedNames({ invoiceIds: [], invoiceLineIds })
                .then((result) => {
                    const lineNames = result.lineNames || {};
                    const lineBalances = result.lineBalances || {};
                    this.disputeItems = this.disputeItems.map((item) => ({
                        ...item,
                        invoiceLineName: (item.invoiceLineId && lineNames[item.invoiceLineId]) || item.invoiceLineName,
                        balance: (item.balance === '—' && item.invoiceLineId && lineBalances[item.invoiceLineId] != null)
                            ? this.formatCurrency(lineBalances[item.invoiceLineId])
                            : item.balance
                    }));
                })
                .catch(() => { /* keep existing data */ })
                .finally(() => {
                    this._itemsLoaded = true;
                    this.checkLoadingComplete();
                });
        } else {
            this._itemsLoaded = true;
            this.checkLoadingComplete();
        }
    }

    // ── Editable Approved Amount ──
    handleApprovedAmountChange(event) {
        const itemId = event.currentTarget.dataset.id;
        const newValue = Number(event.target.value ?? 0);
        this.disputeItems = this.disputeItems.map((item) => {
            if (item.id === itemId) {
                return { ...item, approvedAmount: newValue };
            }
            return item;
        });
        this.recalculateTotalApproved();
    }

    recalculateTotalApproved() {
        const total = this.disputeItems.reduce((sum, item) => sum + (Number(item.approvedAmount) || 0), 0);
        if (this.disputeData) {
            this.disputeData = {
                ...this.disputeData,
                formattedApprovedAmount: this.formatCurrency(total)
            };
        }
    }

    handleSave() {
        this.isSaving = true;
        const items = this.disputeItems.map((item) => ({
            id: item.id,
            approvedAmount: item.approvedAmount
        }));
        saveApprovedAmounts({ items })
            .then(() => {
                this.dispatchEvent(
                    new ShowToastEvent({
                        title: 'Success',
                        message: 'Approved amounts saved.',
                        variant: 'success'
                    })
                );
            })
            .catch((err) => {
                this.dispatchEvent(
                    new ShowToastEvent({
                        title: 'Error saving',
                        message: this.readableError(err),
                        variant: 'error'
                    })
                );
            })
            .finally(() => {
                this.isSaving = false;
            });
    }

    // ── Getters ──
    get hasData() {
        return this.disputeData !== null;
    }

    get hasItems() {
        return this.disputeItems.length > 0;
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

    readableError(err) {
        if (!err) return 'Unknown error';
        if (typeof err === 'string') return err;
        if (err.message) return err.message;
        if (err.body?.message) return err.body.message;
        return JSON.stringify(err);
    }
}