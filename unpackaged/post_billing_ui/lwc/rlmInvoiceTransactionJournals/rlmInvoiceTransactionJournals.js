import { LightningElement, api, wire } from 'lwc';
import getByInvoice from '@salesforce/apex/RLM_TxnJournalRelatedListController.getByInvoice';

const COLUMNS = [
    {
        label: 'Name',
        fieldName: 'recordUrl',
        type: 'url',
        typeAttributes: { label: { fieldName: 'Name' }, target: '_blank' }
    },
    { label: 'Debit General Ledger Account', fieldName: 'DebitGeneralLedgerAccountName', type: 'text' },
    {
        label: 'Debit',
        fieldName: 'Debit',
        type: 'currency',
        typeAttributes: { currencyCode: { fieldName: 'CurrencyIsoCode' } }
    },
    { label: 'Credit General Ledger Account', fieldName: 'CreditGeneralLedgerAccountName', type: 'text' },
    {
        label: 'Credit',
        fieldName: 'Credit',
        type: 'currency',
        typeAttributes: { currencyCode: { fieldName: 'CurrencyIsoCode' } }
    }
];

export default class RlmInvoiceTransactionJournals extends LightningElement {
    @api recordId;
    columns = COLUMNS;
    rows = [];
    error;

    @wire(getByInvoice, { invoiceId: '$recordId' })
    wiredJournals({ data, error }) {
        if (data) {
            this.rows = data.map((row) => ({
                ...row,
                recordUrl: `/lightning/r/TransactionJournal/${row.Id}/view`,
                DebitGeneralLedgerAccountName: row.DebitGeneralLedgerAccount?.Name,
                CreditGeneralLedgerAccountName: row.CreditGeneralLedgerAccount?.Name
            }));
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
        return `Transaction Journals (${this.rows.length})`;
    }
}