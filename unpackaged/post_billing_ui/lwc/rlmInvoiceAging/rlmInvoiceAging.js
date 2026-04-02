import { LightningElement, api, wire } from 'lwc';
import getInvoiceAgingData from '@salesforce/apex/RLM_InvoiceAgingController.getInvoiceAgingData';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class RlmInvoiceAging extends LightningElement {
    @api recordId; // Account Id from the page context
    
    isLoading = true;
    error;
    
    // Key Metrics
    totalInvoices = 0;
    overdueInvoices = 0;
    totalInvoiceAmount = 0;
    averageInvoiceAge = 0;
    currencyCode = 'USD';
    
    // Aging breakdown
    lessThan30Days = 0;
    days30To60 = 0;
    moreThan60Days = 0;
    
    isExpanded = true;

    @wire(getInvoiceAgingData, { accountId: '$recordId' })
    wiredInvoiceData({ error, data }) {
        this.isLoading = true;
        if (data) {
            this.processInvoiceData(data);
            this.error = undefined;
            this.isLoading = false;
        } else if (error) {
            this.error = error;
            this.isLoading = false;
            this.showErrorToast();
        }
    }

    processInvoiceData(data) {
        if (!data || !data.invoices) {
            this.resetData();
            return;
        }

        // Calculate key metrics
        this.totalInvoices = data.totalInvoices || 0;
        this.overdueInvoices = data.overdueInvoices || 0;
        this.totalInvoiceAmount = data.totalAmount || 0;
        this.averageInvoiceAge = data.averageAge || 0;
        this.currencyCode = data.currencyCode || 'USD';
        
        // Aging breakdown
        this.lessThan30Days = data.lessThan30 || 0;
        this.days30To60 = data.days30To60 || 0;
        this.moreThan60Days = data.moreThan60 || 0;
    }

    resetData() {
        this.totalInvoices = 0;
        this.overdueInvoices = 0;
        this.totalInvoiceAmount = 0;
        this.averageInvoiceAge = 0;
        this.lessThan30Days = 0;
        this.days30To60 = 0;
        this.moreThan60Days = 0;
    }

    get formattedTotalAmount() {
        return this.formatCurrency(this.totalInvoiceAmount);
    }

    get formattedAverageAge() {
        return this.averageInvoiceAge.toFixed(2);
    }

    get hasOverdueInvoices() {
        return this.overdueInvoices > 0;
    }

    get overdueStatus() {
        return this.hasOverdueInvoices ? 'Overdue' : 'Current';
    }

    get overdueStatusClass() {
        return this.hasOverdueInvoices ? 'status-badge overdue' : 'status-badge current';
    }

    get chartData() {
        const maxValue = Math.max(this.lessThan30Days, this.days30To60, this.moreThan60Days);
        const chartHeight = 150;
        
        return [
            {
                label: '<30 days',
                count: this.lessThan30Days,
                height: maxValue > 0 ? (this.lessThan30Days / maxValue) * chartHeight : 0,
                color: '#1bc5bd',
                key: 'less30'
            },
            {
                label: '30-60 days',
                count: this.days30To60,
                height: maxValue > 0 ? (this.days30To60 / maxValue) * chartHeight : 0,
                color: '#ffa800',
                key: 'days3060'
            },
            {
                label: '60+ days',
                count: this.moreThan60Days,
                height: maxValue > 0 ? (this.moreThan60Days / maxValue) * chartHeight : 0,
                color: '#f64e60',
                key: 'more60'
            }
        ];
    }

    get maxChartValue() {
        return Math.max(this.lessThan30Days, this.days30To60, this.moreThan60Days, 1);
    }

    formatCurrency(amount) {
        if (amount === null || amount === undefined) return '--';
        const currency = this.currencyCode || 'USD';
        const opts = { style: 'currency', currency, minimumFractionDigits: 2 };
        if (Math.abs(amount) >= 1000000) {
            return new Intl.NumberFormat('en-US', opts).format(amount / 1000000) + 'M';
        }
        if (Math.abs(amount) >= 1000) {
            return new Intl.NumberFormat('en-US', opts).format(amount / 1000) + 'K';
        }
        return new Intl.NumberFormat('en-US', opts).format(amount);
    }

    toggleSection() {
        this.isExpanded = !this.isExpanded;
    }

    get sectionIcon() {
        return this.isExpanded ? 'utility:chevrondown' : 'utility:chevronright';
    }

    get sectionClass() {
        return this.isExpanded ? 'slds-section slds-is-open' : 'slds-section';
    }

    showErrorToast() {
        const evt = new ShowToastEvent({
            title: 'Error loading invoice data',
            message: this.error?.body?.message || 'An error occurred while loading invoice aging data',
            variant: 'error',
        });
        this.dispatchEvent(evt);
    }

    get hasData() {
        return this.totalInvoices > 0;
    }
}