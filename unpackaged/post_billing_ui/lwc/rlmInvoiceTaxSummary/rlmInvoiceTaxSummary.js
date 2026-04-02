import { LightningElement, api, wire } from 'lwc';
import getTaxSummaryByInvoice from '@salesforce/apex/RLM_InvoiceTaxSummaryController.getTaxSummaryByInvoice';

const COLUMNS = [
    { label: 'Tax Name', fieldName: 'taxName', type: 'text' },
    {
        label: 'Tax Amount',
        fieldName: 'totalTaxAmount',
        type: 'currency',
        typeAttributes: { currencyCode: { fieldName: 'currencyIsoCode' } }
    }
];

export default class RlmInvoiceTaxSummary extends LightningElement {
    @api recordId;
    columns = COLUMNS;
    rows = [];
    error;

    @wire(getTaxSummaryByInvoice, { invoiceId: '$recordId' })
    wiredSummary({ data, error }) {
        if (data) {
            this.rows = data;
            this.error = undefined;
        } else if (error) {
            this.error = error;
            this.rows = [];
        }
    }

    get hasRows() {
        return this.rows.length > 0;
    }

    get cardTitle() {
        return `Tax Summary (${this.rows.length})`;
    }
}