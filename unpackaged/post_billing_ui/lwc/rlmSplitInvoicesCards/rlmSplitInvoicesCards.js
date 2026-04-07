import { LightningElement, api, track, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import { gql, graphql } from 'lightning/graphql';
import invoiceCardLogo from '@salesforce/resourceUrl/RLM_InvoiceCardLogo';
import getRelatedNames from '@salesforce/apex/RLM_SplitInvoicesController.getRelatedNames';

/**
 * Split Invoices Cards – card-based view of split invoices sharing the same CorrelationIdentifier.
 */
export default class RlmSplitInvoicesCards extends NavigationMixin(LightningElement) {
    @api recordId;

    @track isLoading = true;
    @track error;
    @track errorMessage = '';

    correlationIdentifier;
    allRows = [];
    @track rows = [];

    _refreshCurrent;
    _refreshList;

    get hasRows() {
        return Array.isArray(this.rows) && this.rows.length > 0;
    }

    get invoiceCardLogoUrl() {
        return invoiceCardLogo;
    }

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
        // Exclude the current invoice (the record we're on)
        const rows = allShaped.filter((r) => r.Id !== this.recordId);
        this.allRows = rows;
        this.error = undefined;
        this.errorMessage = '';

        const accountIds = [...new Set(rows.map((r) => r.billingAccountId).filter(Boolean))];
        const profileIds = [...new Set(rows.map((r) => r.billingProfileId).filter(Boolean))];
        const contactIds = [...new Set(rows.map((r) => r.billToContactId).filter(Boolean))];

        if (accountIds.length === 0 && profileIds.length === 0 && contactIds.length === 0) {
            this.rows = rows;
            this.isLoading = false;
            return;
        }

        getRelatedNames({ accountIds, arrangementIds: [], profileIds, contactIds })
            .then((result) => {
                const accountNames = result.accountNames || {};
                const profileNames = result.profileNames || {};
                const contactNames = result.contactNames || {};
                const merged = rows.map((r) => ({
                    ...r,
                    billingAccountName: (r.billingAccountId && accountNames[r.billingAccountId]) || r.billingAccountName,
                    billingProfileName: (r.billingProfileId && profileNames[r.billingProfileId]) || r.billingProfileName,
                    billToContactName: (r.billToContactId && contactNames[r.billToContactId]) || r.billToContactName
                }));
                this.rows = merged;
            })
            .catch(() => {
                this.rows = rows;
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
                                BillingArrangementId { value }
                                BillingProfileId { value }
                                BillToContactId { value }
                                SettlementStatus { value }
                                BillingArrangementVerNumber { value }
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
        const name = documentNumber || id;
        const invoiceDate = node?.InvoiceDate?.value;
        const totalWithTax = node?.TotalAmountWithTax?.value;
        const status = node?.Status?.value ?? '';
        const baId = node?.BillingAccountId?.value || null;
        const arrangementId = node?.BillingArrangementId?.value || null;
        const profileId = node?.BillingProfileId?.value || null;
        const billToContactId = node?.BillToContactId?.value || null;
        const settlementStatus = node?.SettlementStatus?.value ?? '';
        const billingArrangementVersionNumber = node?.BillingArrangementVerNumber?.value || null;

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
            ? new Date(invoiceDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
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
            billingAccountName: baId || '—',
            billingArrangementId: arrangementId,
            billingArrangementName: arrangementId || '—',
            billingProfileId: profileId,
            billingProfileName: profileId || '—',
            billingArrangementVerNumber: billingArrangementVersionNumber,
            invoiceUrl: this.buildRecordUrl(id),
            billingAccountUrl: baId ? this.buildRecordUrl(baId) : null,
            billingArrangementUrl: arrangementId ? this.buildRecordUrl(arrangementId) : null,
            billingProfileUrl: profileId ? this.buildRecordUrl(profileId) : null,
            noAccount: !baId,
            noArrangement: !arrangementId,
            noProfile: !profileId,
            billToContactId,
            billToContactName: billToContactId || '—',
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
        else if (action === 'open_arrangement') this.navigateToRecord(id);
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

    readableError(e) {
        if (!e) return 'Unknown error';
        if (Array.isArray(e.body)) return e.body.map((x) => x.message).join(', ');
        if (e.body?.message) return e.body.message;
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