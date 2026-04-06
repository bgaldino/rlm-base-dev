import { LightningElement, api, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import getPaymentScheduleItems from '@salesforce/apex/RLM_PaymentsDataController.getPaymentScheduleItems';
import getAccountOptions from '@salesforce/apex/RLM_PaymentsDataController.getAccountOptions';
import getCurrencyOptions from '@salesforce/apex/RLM_PaymentsDataController.getCurrencyOptions';
import getOrgDefaultCurrency from '@salesforce/apex/RLM_PaymentsDataController.getOrgDefaultCurrency';

export default class RlmPaymentsData extends NavigationMixin(LightningElement) {
    @api recordId;
    
    accountOptions = [];
    currencyOptions = [];
    selectedAccountId = '';
    selectedCurrency = '';
    
    statusSummaries = [];
    error;
    isLoading = true;
    orgDefaultCurrency = 'USD';
    
    // Card styling based on status
    statusStyles = {
        'Failed': {
            cardClass: 'status-card failed-card',
            headerClass: 'failed-header'
        },
        'Ready for Processing': {
            cardClass: 'status-card ready-card',
            headerClass: 'ready-header'
        },
        'Applied': {
            cardClass: 'status-card applied-card',
            headerClass: 'applied-header'
        },
        'Draft': {
            cardClass: 'status-card draft-card',
            headerClass: 'draft-header'
        },
        'Processing': {
            cardClass: 'status-card processing-card',
            headerClass: 'processing-header'
        }
    };
    
    connectedCallback() {
        this.loadCurrencies();
    }
    
    loadCurrencies() {
        Promise.all([
            getOrgDefaultCurrency(),
            getCurrencyOptions()
        ]).then(([defaultCode, options]) => {
            this.orgDefaultCurrency = defaultCode || 'USD';
            this.currencyOptions = Array.isArray(options) ? options : [];
            if (!this.selectedCurrency) {
                this.selectedCurrency = this.orgDefaultCurrency;
            }
        }).catch(err => {
            this.currencyOptions = [
                { value: '', label: 'All Currencies' },
                { value: 'USD', label: 'USD' }
            ];
            this.selectedCurrency = this.orgDefaultCurrency || 'USD';
        });
    }
    
    @wire(getAccountOptions)
    wiredAccountOptions({ error, data }) {
        if (data) {
            this.accountOptions = data;
        }
    }
    
    get effectiveRecordId() {
        // Return undefined (not null) when no account is selected so the wire adapter
        // does not fire until a valid ID is available.
        return this.selectedAccountId && this.selectedAccountId !== '' ? this.selectedAccountId : undefined;
    }
    
    @wire(getPaymentScheduleItems, { recordId: '$effectiveRecordId', currencyCode: '$selectedCurrency' })
    wiredPaymentItems({ error, data }) {
        this.isLoading = false;
        if (data) {
            this.processData(data);
            this.error = undefined;
        } else if (error) {
            this.error = this.reduceErrors(error);
            this.statusSummaries = [];
        }
    }
    
    handleAccountChange(event) {
        this.selectedAccountId = event.detail.value || '';
        this.selectedCurrency = this.orgDefaultCurrency || '';
        this.isLoading = true;
    }
    
    handleCurrencyChange(event) {
        this.selectedCurrency = event.detail.value || '';
        this.isLoading = true;
    }
    
    processData(data) {
        this.statusSummaries = data.map(summary => {
            const style = this.statusStyles[summary.status] || {
                cardClass: 'status-card default-card',
                headerClass: 'default-header'
            };
            
            return {
                ...summary,
                cardClass: style.cardClass,
                headerClass: style.headerClass,
                hasItems: summary.itemCount > 0,
                items: summary.items.map(item => ({
                    ...item,
                    recordUrl: `/lightning/r/PaymentScheduleItem/${item.id}/view`,
                    paymentUrl: item.paymentId ? `/lightning/r/Payment/${item.paymentId}/view` : null,
                    invoices: item.invoices ? item.invoices.map(invoice => this.processInvoice(invoice)) : []
                }))
            };
        });
    }
    
    processInvoice(invoice) {
        const isSettled = invoice.isSettled;
        return {
            ...invoice,
            recordUrl: `/lightning/r/Invoice/${invoice.id}/view`,
            displayNumber: invoice.invoiceNumber || invoice.documentNumber || 'N/A',
            statusLabel: isSettled ? 'Settled' : 'Open',
            invoiceClass: isSettled ? 'invoice-row settled' : 'invoice-row open',
            statusLineClass: isSettled ? 'status-line settled-line' : 'status-line open-line',
            statusBadgeClass: isSettled ? 'status-badge settled-badge' : 'status-badge open-badge',
            balanceClass: isSettled ? 'amount-value-small settled-amount' : 'amount-value-small open-amount'
        };
    }
    
    get hasData() {
        return this.statusSummaries && this.statusSummaries.some(s => s.itemCount > 0);
    }
    
    get noAccountSelected() {
        return !this.selectedAccountId || this.selectedAccountId === '';
    }
    
    get totalAccountsReceivables() {
        if (!this.statusSummaries || this.statusSummaries.length === 0) return 0;
        return this.statusSummaries.reduce((sum, s) => sum + (Number(s.totalRequestedAmount) || 0), 0);
    }
    
    get progressBarSegments() {
        if (!this.statusSummaries || this.statusSummaries.length === 0) return [];
        const totalAmount = this.totalAccountsReceivables;
        const totalCount = this.statusSummaries.reduce((sum, s) => sum + (s.itemCount || 0), 0);
        const useAmount = totalAmount > 0;
        const total = useAmount ? totalAmount : totalCount;
        if (total <= 0) return [];
        const segmentBgColors = {
            'Failed': '#ea001e',
            'Ready for Processing': '#fe9339',
            'Applied': '#2e844a',
            'Draft': '#0176d3',
            'Processing': '#5a1ba9'
        };
        const segmentColors = {
            'Failed': 'progress-segment-failed',
            'Ready for Processing': 'progress-segment-ready',
            'Applied': 'progress-segment-applied',
            'Draft': 'progress-segment-draft',
            'Processing': 'progress-segment-processing'
        };
        return this.statusSummaries
            .filter(s => useAmount ? (Number(s.totalRequestedAmount) || 0) > 0 : (s.itemCount || 0) > 0)
            .map(s => {
                const amount = useAmount ? (Number(s.totalRequestedAmount) || 0) : (s.itemCount || 0);
                const widthPercent = total > 0 ? Math.max((amount / total) * 100, 0.5) : 0;
                const label = s.status === 'Applied' ? 'Settled Invoices' : s.status;
                const bg = segmentBgColors[s.status] || '#706e6b';
                return {
                    key: s.status,
                    status: s.status,
                    label,
                    widthPercent,
                    amount,
                    itemCount: s.itemCount || 0,
                    segmentClass: segmentColors[s.status] || 'progress-segment-default',
                    tooltip: `${label}: ${s.itemCount} item(s)`,
                    segmentStyle: `width: ${widthPercent}%; background-color: ${bg}; min-width: 4px;`,
                    dotStyle: `background-color: ${bg};`
                };
            });
    }
    
    get displayCurrency() {
        return this.selectedCurrency || this.orgDefaultCurrency || 'USD';
    }
    
    get region1Summaries() {
        if (!this.statusSummaries || this.statusSummaries.length === 0) return [];
        return this.statusSummaries.filter(s => s.status === 'Failed' || s.status === 'Ready for Processing');
    }
    
    get region2Summaries() {
        if (!this.statusSummaries || this.statusSummaries.length === 0) return [];
        return this.statusSummaries.filter(s => s.status === 'Applied' || s.status === 'Draft');
    }
    
    get region3Summaries() {
        if (!this.statusSummaries || this.statusSummaries.length === 0) return [];
        return this.statusSummaries.filter(s => s.status === 'Processing');
    }
    
    reduceErrors(error) {
        if (typeof error === 'string') {
            return error;
        }
        if (error.body) {
            if (typeof error.body.message === 'string') {
                return error.body.message;
            }
            if (error.body.pageErrors && error.body.pageErrors.length > 0) {
                return error.body.pageErrors.map(e => e.message).join(', ');
            }
        }
        if (error.message) {
            return error.message;
        }
        return 'Unknown error';
    }
    
    handleItemClick(event) {
        const itemId = event.currentTarget.dataset.id;
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: {
                recordId: itemId,
                objectApiName: 'PaymentScheduleItem',
                actionName: 'view'
            }
        });
    }
}