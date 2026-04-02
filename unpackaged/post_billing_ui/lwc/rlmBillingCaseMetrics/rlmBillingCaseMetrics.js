import { LightningElement, track, wire } from 'lwc';
import getMetrics from '@salesforce/apex/RLM_BillingCaseMetricsController.getMetrics';

export default class RlmBillingCaseMetrics extends LightningElement {
    @track isLoading = true;
    @track metrics = null;

    @wire(getMetrics)
    wiredMetrics({ data, error }) {
        if (data) {
            const totalAmt = Number(data.totalDisputedAmount || 0);
            this.metrics = {
                openBillingCases: data.openBillingCases || 0,
                openDisputes: data.openDisputes || 0,
                disputedInvoices: data.disputedInvoices || 0,
                totalDisputedAmount: new Intl.NumberFormat('en-US', {
                    style: 'currency', currency: 'USD'
                }).format(totalAmt)
            };
            this.isLoading = false;
        } else if (error) {
            this.metrics = {
                openBillingCases: 0,
                openDisputes: 0,
                disputedInvoices: 0,
                totalDisputedAmount: '$0.00'
            };
            this.isLoading = false;
        }
    }

    get hasData() {
        return this.metrics !== null;
    }
}