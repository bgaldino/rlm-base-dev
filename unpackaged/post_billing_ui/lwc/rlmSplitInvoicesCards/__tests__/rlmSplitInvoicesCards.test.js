import { createElement } from 'lwc';
import RlmSplitInvoicesCards from 'c/rlmSplitInvoicesCards';
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

function mount() {
    const el = createElement('c-rlm-split-invoices-cards', { is: RlmSplitInvoicesCards });
    el.recordId = CURRENT_ID;
    document.body.appendChild(el);
    return el;
}

function splitNode(documentNumber) {
    return {
        Id: SPLIT_ID,
        DocumentNumber: { value: documentNumber },
        InvoiceDate: { value: '2026-01-15' },
        TotalAmountWithTax: { value: 50 },
        Status: { value: 'Posted' },
        CorrelationIdentifier: { value: 'CORR-1' },
        BillingAccountId: { value: '001000000000001AAA' },
        BillingProfileId: { value: null },
        BillToContactId: { value: null },
        SettlementStatus: { value: 'Not Settled' }
    };
}

// The stub adapter's instances carry no config here, so one payload answers both graphql wires;
// it is sent twice because the list wire reads only once the current invoice has given it the
// correlation id.
async function loadSplit(documentNumber) {
    const el = mount();
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

const titles = (el) => [...el.shadowRoot.querySelectorAll('.card-title')].map((n) => n.textContent);
const values = (el) => [...el.shadowRoot.querySelectorAll('.card-value')].map((n) => n.textContent);

describe('rlmSplitInvoicesCards names', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    it('titles a card with its document number', async () => {
        getRelatedNames.mockResolvedValue({ accountNames: { '001000000000001AAA': 'Acme' } });
        const el = await loadSplit('INV-0002');
        expect(titles(el)).toEqual(['INV-0002']);
        expect(values(el)[0]).toBe('Acme');
    });

    // Pack 452: a missing document number shows a dash, never the record Id.
    it('titles a card with a dash, not the record Id, when the document number is missing', async () => {
        getRelatedNames.mockResolvedValue({});
        const el = await loadSplit(null);
        expect(titles(el)).toEqual(['—']);
    });

    it('keeps dashes for the names when the name lookup fails', async () => {
        getRelatedNames.mockRejectedValue(new Error('refused'));
        const el = await loadSplit(null);
        expect(titles(el)).toEqual(['—']);
        expect(values(el).slice(0, 3)).toEqual(['—', '—', '—']);
    });

    it('asks for no arrangement names (the cards show none)', async () => {
        getRelatedNames.mockResolvedValue({});
        await loadSplit('INV-0002');
        expect(getRelatedNames).toHaveBeenCalled();
        getRelatedNames.mock.calls.forEach(([args]) => expect(args).not.toHaveProperty('arrangementIds'));
    });
});
