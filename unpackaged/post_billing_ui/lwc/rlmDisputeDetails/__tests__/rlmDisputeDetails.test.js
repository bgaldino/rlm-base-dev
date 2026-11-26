import { createElement } from 'lwc';
import RlmDisputeDetails from 'c/rlmDisputeDetails';
import { graphql } from 'lightning/graphql';
import getRelatedNames from '@salesforce/apex/RLM_DisputeDetailsController.getRelatedNames';

jest.mock(
    '@salesforce/apex/RLM_DisputeDetailsController.getRelatedNames',
    () => ({ default: jest.fn() }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DisputeDetailsController.saveApprovedAmounts',
    () => ({ default: jest.fn() }),
    { virtual: true }
);

const CASE_ID = '500000000000001AAA';
const DISPUTE_ID = '0Xd000000000001AAA';
const INVOICE_ID = '3tt000000000001AAA';
const LINE_ID = '5TV000000000001AAA';

const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

async function load(names) {
    getRelatedNames.mockImplementation(({ invoiceIds }) => (
        names == null ? Promise.reject(new Error('refused'))
            : Promise.resolve(invoiceIds.length ? { invoiceNames: names.invoiceNames || {} } : { lineNames: names.lineNames || {}, lineBalances: {} })
    ));
    const el = createElement('c-rlm-dispute-details', { is: RlmDisputeDetails });
    el.recordId = CASE_ID;
    document.body.appendChild(el);
    // The stub adapter's instances carry no config here, so one payload answers both graphql
    // wires; the items wire reads once the dispute wire has set the dispute id.
    const payload = { uiapi: { query: {
        Dispute: { edges: [{ node: {
            Id: DISPUTE_ID, Name: { value: 'D-0001' }, InvoiceId: { value: INVOICE_ID },
            DisputedAmount: { value: 10 }, ReceivedDate: { value: null }
        } }] },
        DisputeItem: { edges: [{ node: {
            Id: 'a00000000000001AAA', InvoiceLineId: { value: LINE_ID },
            DisputedAmount: { value: 10 }, ApprovedAmount: { value: 0 }, InvoiceLine: null
        } }] }
    } } };
    graphql.emit(payload);
    await flush();
    return el;
}

const invoiceLink = (el) => el.shadowRoot.querySelector('.detail-field .detail-link')?.textContent;
const lineLink = (el) => el.shadowRoot.querySelector('.detail-link-sm')?.textContent;

describe('rlmDisputeDetails names', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    it('shows the invoice document number and the line name once resolved', async () => {
        const el = await load({ invoiceNames: { [INVOICE_ID]: 'INV-0001' }, lineNames: { [LINE_ID]: 'Line 1' } });
        expect(invoiceLink(el)).toBe('INV-0001');
        expect(lineLink(el)).toBe('Line 1');
    });

    // Pack 452: an unresolved name shows a dash, never the record Id.
    it('shows dashes, not record Ids, when the names cannot be resolved', async () => {
        const el = await load(null);
        expect(invoiceLink(el)).toBe('—');
        expect(lineLink(el)).toBe('—');
    });

    it('shows dashes when the lookup returns no name', async () => {
        const el = await load({});
        expect(invoiceLink(el)).toBe('—');
        expect(lineLink(el)).toBe('—');
    });
});
