import { createElement } from 'lwc';
import RlmSplitInvoicesView from 'c/rlmSplitInvoicesView';
import { graphql } from 'lightning/graphql';
import getRelatedNames from '@salesforce/apex/RLM_SplitInvoicesController.getRelatedNames';

jest.mock(
    '@salesforce/apex/RLM_SplitInvoicesController.getRelatedNames',
    () => ({ default: jest.fn() }),
    { virtual: true }
);

const CURRENT_ID = '3tt000000000001AAA';
const SPLIT_ID = '3tt000000000002AAA';
const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

function splitNode(documentNumber) {
    return {
        Id: SPLIT_ID,
        DocumentNumber: { value: documentNumber },
        InvoiceDate: { value: '2026-01-15' },
        Balance: { value: 50 },
        Status: { value: 'Posted' },
        CorrelationIdentifier: { value: 'CORR-1' },
        BillingAccountId: { value: null },
        BillingArrangementId: { value: null },
        BillingProfileId: { value: null }
    };
}

// The stub adapter's instances carry no config here, so one payload answers both graphql wires;
// it is sent twice because the list wire reads only once the current invoice has given it the
// correlation id.
async function load(documentNumber) {
    getRelatedNames.mockResolvedValue({});
    const el = createElement('c-rlm-split-invoices-view', { is: RlmSplitInvoicesView });
    el.recordId = CURRENT_ID;
    document.body.appendChild(el);
    const payload = { uiapi: { query: {
        Invoice: { edges: [{ node: { Id: CURRENT_ID, CorrelationIdentifier: { value: 'CORR-1' } } }] },
        InvoiceByCorrelation: { edges: [{ node: splitNode(documentNumber) }] }
    } } };
    graphql.emit(payload);
    await flush();
    graphql.emit(payload);
    await flush();
    return el;
}

const rows = (el) => el.shadowRoot.querySelector('lightning-datatable')?.data || [];

describe('rlmSplitInvoicesView invoice link label', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    it('labels the invoice link with its document number', async () => {
        const el = await load('INV-0002');
        expect(rows(el).map((r) => r.Name)).toEqual(['INV-0002']);
    });

    // Pack 452: a null label would make the url column show the link itself (/lightning/r/<Id>/view).
    it('labels the invoice link with a dash, not the record link, when the document number is missing', async () => {
        const el = await load(null);
        expect(rows(el).map((r) => r.Name)).toEqual(['—']);
        expect(rows(el)[0].invoiceUrl).toContain(SPLIT_ID);
    });

    // The dash only shows if the url column's label is bound to Name.
    it('binds the invoice link label to the Name field', async () => {
        const el = await load('INV-0002');
        const columns = el.shadowRoot.querySelector('lightning-datatable').columns;
        const invoiceColumn = columns.find((c) => c.fieldName === 'invoiceUrl');
        expect(invoiceColumn.type).toBe('url');
        expect(invoiceColumn.typeAttributes?.label?.fieldName).toBe('Name');
    });
});
