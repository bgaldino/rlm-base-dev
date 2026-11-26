import { LightningElement, track, wire } from 'lwc';
import getMetrics from '@salesforce/apex/RLM_BillingCaseMetricsController.getMetrics';

// Shown for a metric whose read was refused (null from the server), never a zero.
const UNAVAILABLE = 'Unavailable';

export default class RlmBillingCaseMetrics extends LightningElement {
    @track isLoading = true;
    @track metrics = null;

    // A metric the server could not read is null: it shows as unavailable, never as 0. A failed
    // call shows every metric as unavailable, not as zeros.
    @wire(getMetrics)
    wiredMetrics({ data, error }) {
        if (data) {
            const count = (value) => (value == null ? UNAVAILABLE : value);
            this.metrics = {
                openBillingCases: count(data.openBillingCases),
                openDisputes: count(data.openDisputes),
                disputedInvoices: count(data.disputedInvoices),
                totalDisputedAmount: data.totalDisputedAmount == null
                    ? UNAVAILABLE
                    : new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(data.totalDisputedAmount))
            };
            this.isLoading = false;
        } else if (error) {
            this.metrics = {
                openBillingCases: UNAVAILABLE,
                openDisputes: UNAVAILABLE,
                disputedInvoices: UNAVAILABLE,
                totalDisputedAmount: UNAVAILABLE
            };
            this.isLoading = false;
        }
    }

    get hasData() {
        return this.metrics !== null;
    }
}
