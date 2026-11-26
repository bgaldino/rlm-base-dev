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

// Pack 452: a name read for one dispute must not land on the next one when the record changes
// before the read returns.
describe('rlmDisputeDetails record change', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    const payload = (disputeId, invoiceId) => ({ uiapi: { query: {
        Dispute: { edges: [{ node: {
            Id: disputeId, Name: { value: 'D-' + disputeId.slice(-1) }, InvoiceId: { value: invoiceId },
            DisputedAmount: { value: 10 }, ReceivedDate: { value: null }
        } }] },
        DisputeItem: { edges: [] }
    } } });

    it('keeps the new dispute\'s invoice name when the previous dispute\'s read returns late', async () => {
        const INVOICE_B = '3tt000000000002AAA';
        let resolveFirst;
        getRelatedNames
            .mockImplementationOnce(() => new Promise((resolve) => { resolveFirst = resolve; }))
            .mockImplementation(() => Promise.resolve({ invoiceNames: { [INVOICE_B]: 'INV-B' } }));
        const el = createElement('c-rlm-dispute-details', { is: RlmDisputeDetails });
        el.recordId = CASE_ID;
        document.body.appendChild(el);
        graphql.emit(payload(DISPUTE_ID, INVOICE_ID));
        await flush();

        el.recordId = '500000000000002AAA';
        graphql.emit(payload('0Xd000000000002AAA', INVOICE_B));
        await flush();
        expect(invoiceLink(el)).toBe('INV-B');

        resolveFirst({ invoiceNames: { [INVOICE_ID]: 'INV-A' } });
        await flush();
        expect(invoiceLink(el)).toBe('INV-B');
    });
});

// Pack 452 (review 3): what a record change and a failed read leave on screen.
describe('rlmDisputeDetails stale state', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    const INVOICE_B = '3tt000000000002AAA';
    const DISPUTE_B = '0Xd000000000002AAA';
    const payloadFor = (disputeId, invoiceId, withLine) => ({ uiapi: { query: {
        Dispute: { edges: [{ node: {
            Id: disputeId, Name: { value: 'D-' + disputeId.slice(-4) }, InvoiceId: { value: invoiceId },
            DisputedAmount: { value: 10 }, ReceivedDate: { value: null }
        } }] },
        DisputeItem: { edges: withLine ? [{ node: {
            Id: 'a00' + disputeId.slice(-15), InvoiceLineId: { value: LINE_ID },
            DisputedAmount: { value: 10 }, ApprovedAmount: { value: 0 }, InvoiceLine: null
        } }] : [] }
    } } });
    const errorText = (el) => el.shadowRoot.querySelector('.slds-text-color_error')?.textContent;

    function mountOn(caseId) {
        const el = createElement('c-rlm-dispute-details', { is: RlmDisputeDetails });
        el.recordId = caseId;
        document.body.appendChild(el);
        return el;
    }

    beforeEach(() => {
        getRelatedNames.mockImplementation(({ invoiceIds }) => Promise.resolve(
            invoiceIds.length ? { invoiceNames: { [INVOICE_ID]: 'INV-A', [INVOICE_B]: 'INV-B' } } : { lineNames: {}, lineBalances: {} }
        ));
    });

    it('shows no previous dispute after a record change whose read fails', async () => {
        const el = mountOn(CASE_ID);
        graphql.emit(payloadFor(DISPUTE_ID, INVOICE_ID, false));
        await flush();
        expect(invoiceLink(el)).toBe('INV-A');
        el.recordId = '500000000000002AAA';
        await flush();
        expect(invoiceLink(el)).toBeUndefined();
        graphql.emitErrors([{ message: "Validation error of type FieldUndefined: Field 'Dispute' in type 'RecordQuery' is undefined" }]);
        await flush();
        expect(invoiceLink(el)).toBeUndefined();
        // A fixed sentence, never the UI API's validation text.
        expect(errorText(el)).toBe('Unable to read this case\'s dispute. Contact your administrator.');
        expect(errorText(el)).not.toContain('Validation error');
    });

    it('shows no dispute when a read of the same record fails after a success', async () => {
        const el = mountOn(CASE_ID);
        graphql.emit(payloadFor(DISPUTE_ID, INVOICE_ID, false));
        await flush();
        expect(invoiceLink(el)).toBe('INV-A');
        graphql.emitErrors([{ message: 'Dispute read failed.' }]);
        await flush();
        expect(invoiceLink(el)).toBeUndefined();
    });

    const header = (el) => el.shadowRoot.querySelector('.header-name-link');
    const spinner = (el) => el.shadowRoot.querySelector('lightning-spinner');
    const errorElement = (el) => el.shadowRoot.querySelector('.slds-text-color_error');

    // Line-name replies held until the test releases them, per call, in order.
    function holdLineNames() {
        const pending = [];
        getRelatedNames.mockImplementation(({ invoiceIds }) => {
            if (invoiceIds.length) return Promise.resolve({ invoiceNames: { [INVOICE_ID]: 'INV-A', [INVOICE_B]: 'INV-B' } });
            return new Promise((resolve) => { pending.push(resolve); });
        });
        return pending;
    }

    it('clears the previous dispute\'s header and error as soon as the record changes', async () => {
        const el = mountOn(CASE_ID);
        graphql.emit(payloadFor(DISPUTE_ID, INVOICE_ID, false));
        await flush();
        expect(header(el)).not.toBeNull();
        el.recordId = '500000000000002AAA';
        await flush();
        expect(header(el)).toBeNull();
        expect(errorElement(el)).toBeNull();
        expect(spinner(el)).not.toBeNull();
    });

    it('clears the previous record\'s error as soon as the record changes', async () => {
        const el = mountOn(CASE_ID);
        graphql.emitErrors([{ message: 'Dispute read failed.' }]);
        await flush();
        expect(errorElement(el)).not.toBeNull();
        el.recordId = '500000000000002AAA';
        await flush();
        expect(errorElement(el)).toBeNull();
        expect(header(el)).toBeNull();
    });

    it('keeps the spinner when the previous dispute\'s line names return before the next dispute loads', async () => {
        const pending = holdLineNames();
        const el = mountOn(CASE_ID);
        graphql.emit(payloadFor(DISPUTE_ID, INVOICE_ID, true));
        await flush();
        el.recordId = '500000000000002AAA';
        await flush();
        pending[0]({ lineNames: { [LINE_ID]: 'Line A' }, lineBalances: {} });
        await flush();
        expect(spinner(el)).not.toBeNull();
        expect(header(el)).toBeNull();
        // The next dispute's own line names are still pending: the spinner stays until they land.
        graphql.emit(payloadFor(DISPUTE_B, INVOICE_B, true));
        await flush();
        expect(spinner(el)).not.toBeNull();
        pending[1]({ lineNames: { [LINE_ID]: 'Line B' }, lineBalances: {} });
        await flush();
        expect(spinner(el)).toBeNull();
        expect(lineLink(el)).toBe('Line B');
    });

    it('keeps the spinner for the next dispute\'s line names after a fully loaded one', async () => {
        const pending = holdLineNames();
        const el = mountOn(CASE_ID);
        graphql.emit(payloadFor(DISPUTE_ID, INVOICE_ID, true));
        await flush();
        pending[0]({ lineNames: { [LINE_ID]: 'Line A' }, lineBalances: {} });
        await flush();
        expect(spinner(el)).toBeNull();
        el.recordId = '500000000000002AAA';
        graphql.emit(payloadFor(DISPUTE_B, INVOICE_B, true));
        await flush();
        expect(spinner(el)).not.toBeNull();
    });

    it('does not bring back a dispute whose invoice name returns after its read failed', async () => {
        let resolveName;
        getRelatedNames.mockImplementation(({ invoiceIds }) => (invoiceIds.length
            ? new Promise((resolve) => { resolveName = resolve; })
            : Promise.resolve({ lineNames: {}, lineBalances: {} })));
        const el = mountOn(CASE_ID);
        graphql.emit(payloadFor(DISPUTE_ID, INVOICE_ID, false));
        await flush();
        graphql.emitErrors([{ message: 'Dispute read failed.' }]);
        await flush();
        resolveName({ invoiceNames: { [INVOICE_ID]: 'INV-A' } });
        await flush();
        expect(invoiceLink(el)).toBeUndefined();
        expect(el.shadowRoot.querySelector('.detail-section')).toBeNull();
    });

    it('ignores a late line-name reply for the previous dispute', async () => {
        let resolveFirstLines;
        let lineCalls = 0;
        getRelatedNames.mockImplementation(({ invoiceIds }) => {
            if (invoiceIds.length) return Promise.resolve({ invoiceNames: {} });
            lineCalls++;
            if (lineCalls === 1) return new Promise((resolve) => { resolveFirstLines = resolve; });
            return Promise.resolve({ lineNames: { [LINE_ID]: 'Line B' }, lineBalances: {} });
        });
        const el = mountOn(CASE_ID);
        graphql.emit(payloadFor(DISPUTE_ID, INVOICE_ID, true));
        await flush();
        el.recordId = '500000000000002AAA';
        graphql.emit(payloadFor(DISPUTE_B, INVOICE_B, true));
        await flush();
        expect(lineLink(el)).toBe('Line B');
        resolveFirstLines({ lineNames: { [LINE_ID]: 'Line A' }, lineBalances: {} });
        await flush();
        expect(lineLink(el)).toBe('Line B');
    });
});

// Pack 452 (round 13): a refused or failed read of the dispute's lines shows a sentence in place of
// the lines and the approved total as Unavailable, never "no lines".
describe('rlmDisputeDetails lines unavailable', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    it('shows the lines as unavailable and the approved total as Unavailable when the line read fails', async () => {
        jest.spyOn(console, 'error').mockImplementation(() => {});
        getRelatedNames.mockResolvedValue({ invoiceNames: { [INVOICE_ID]: 'INV-0001' } });
        const el = createElement('c-rlm-dispute-details', { is: RlmDisputeDetails });
        el.recordId = CASE_ID;
        document.body.appendChild(el);
        graphql.emit({ uiapi: { query: { Dispute: { edges: [{ node: {
            Id: DISPUTE_ID, Name: { value: 'D-0001' }, InvoiceId: { value: INVOICE_ID },
            DisputedAmount: { value: 10 }, ReceivedDate: { value: null }
        } }] } } } });
        await flush();
        // Only the dispute-lines wire fails: it is the last graphql wire instance created (this
        // component's second wire). The stub's configs are empty here, so the filter matches the
        // instance's own config object.
        const instances = Array.from(graphql._wireInstances);
        const linesWireConfig = instances[instances.length - 1].getConfig();
        graphql.emitErrors([{ message: "Validation error of type FieldUndefined: Field 'DisputeItem'" }],
            (config) => config === linesWireConfig);
        await flush();
        expect(el.shadowRoot.querySelector('.items-unavailable').textContent)
            .toBe('Unable to read this dispute\'s lines. Contact your administrator.');
        expect(el.shadowRoot.querySelector('.amount-approved').textContent).toBe('Unavailable');
        expect(el.shadowRoot.querySelector('.items-table')).toBeNull();
    });
});
