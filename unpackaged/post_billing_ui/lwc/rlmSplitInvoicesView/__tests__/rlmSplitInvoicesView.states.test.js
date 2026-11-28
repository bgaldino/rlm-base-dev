// Todo 509: refused reads and record changes. Each read (the current invoice, the split list) is loading
// until its own reply, then ready or unavailable; an unavailable read shows only the fixed sentence,
// never the platform's text and never "No split invoices found"; a record change drops every reply for
// the previous record.
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
const OTHER_ID = '3tt000000000009AAA';
const SPLIT_ID = '3tt000000000002AAA';
const ACCOUNT_ID = '001000000000001AAA';
const RAW = "Validation error of type FieldUndefined: Field 'CorrelationIdentifier' is undefined";
const SENTENCE = 'Unable to read the split invoices. Contact your administrator.';
const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

// The wires by their variables: the current invoice's carry the record id, the list's the correlation id.
const toCurrent = (config) => !!config?.variables?.id;
const toList = (config) => !!config?.variables?.correlation;

const current = (id, correlation) => ({ uiapi: { query: { Invoice: { edges: [{ node: {
    Id: id, CorrelationIdentifier: { value: correlation }
} }] } } } });
const list = (accountId) => ({ uiapi: { query: { InvoiceByCorrelation: { edges: [{ node: {
    Id: SPLIT_ID, DocumentNumber: { value: 'INV-0002' }, InvoiceDate: { value: '2026-01-15' },
    Balance: { value: 50 }, Status: { value: 'Posted' }, CorrelationIdentifier: { value: 'CORR-1' },
    BillingAccountId: { value: accountId || null }, BillingArrangementId: { value: null }, BillingProfileId: { value: null }
} }] } } } });

// Mounted, with the wires' variables in place so each emit reaches its own wire.
async function mount() {
    const el = createElement('c-rlm-split-invoices-view', { is: RlmSplitInvoicesView });
    el.recordId = CURRENT_ID;
    document.body.appendChild(el);
    await flush();
    return el;
}

async function loaded() {
    const el = await mount();
    graphql.emit(current(CURRENT_ID, 'CORR-1'), toCurrent);
    await flush();
    graphql.emit(list(), toList);
    await flush();
    return el;
}

const text = (el) => el.shadowRoot.textContent;
const table = (el) => el.shadowRoot.querySelector('lightning-datatable');
const spinner = (el) => el.shadowRoot.querySelector('lightning-spinner');
const errorText = (el) => el.shadowRoot.querySelector('.slds-text-color_error')?.textContent.trim();

describe('rlmSplitInvoicesView refused reads and record changes', () => {
    beforeEach(() => {
        jest.spyOn(console, 'error').mockImplementation(() => {});
        getRelatedNames.mockResolvedValue({});
    });
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();

    });

    it('shows the fixed sentence, not the platform text, when the current invoice read is refused', async () => {
        const el = await mount();
        graphql.emitErrors([{ message: RAW }], toCurrent);
        await flush();
        expect(errorText(el)).toBe(SENTENCE);
        expect(text(el)).not.toContain('Validation error');
        expect(text(el)).not.toContain('No split invoices found');
        expect(spinner(el)).toBeNull();
    });

    it('shows the fixed sentence, not "No split invoices found", when the list read is refused', async () => {
        const el = await mount();
        graphql.emit(current(CURRENT_ID, 'CORR-1'), toCurrent);
        await flush();
        graphql.emitErrors([{ message: RAW }], toList);
        await flush();
        expect(errorText(el)).toBe(SENTENCE);
        expect(text(el)).not.toContain('Validation error');
        expect(text(el)).not.toContain('No split invoices found');
        expect(spinner(el)).toBeNull();
    });

    it('keeps a refused list unavailable when the current invoice is read again', async () => {
        const el = await mount();
        graphql.emit(current(CURRENT_ID, 'CORR-1'), toCurrent);
        await flush();
        graphql.emitErrors([{ message: RAW }], toList);
        await flush();
        graphql.emit(current(CURRENT_ID, 'CORR-1'), toCurrent);
        await flush();
        expect(errorText(el)).toBe(SENTENCE);
        expect(text(el)).not.toContain('No split invoices found');
    });

    it('keeps a refused current-invoice read unavailable when the list answers again', async () => {
        const el = await loaded();
        expect(table(el)).not.toBeNull();
        graphql.emitErrors([{ message: RAW }], toCurrent);
        await flush();
        graphql.emit(list(), toList);
        await flush();
        expect(errorText(el)).toBe(SENTENCE);
        expect(table(el)).toBeNull();
    });

    // A guard, not a defect (it passes on main too): a list that recovers is shown again.
    it('clears the sentence when the refused list is read again successfully', async () => {
        const el = await mount();
        graphql.emit(current(CURRENT_ID, 'CORR-1'), toCurrent);
        await flush();
        graphql.emitErrors([{ message: RAW }], toList);
        await flush();
        graphql.emit(list(), toList);
        await flush();
        expect(errorText(el)).toBeUndefined();
        expect(table(el).data.map((r) => r.Name)).toEqual(['INV-0002']);
    });

    it('shows the fixed sentence, not the platform text, when a refresh fails', async () => {
        const el = await mount();
        const refresh = () => Promise.reject(new Error(RAW));
        graphql.emit(current(CURRENT_ID, 'CORR-1'), toCurrent, refresh);
        await flush();
        graphql.emit(list(), toList, refresh);
        await flush();
        await el.refresh();
        await flush();
        expect(errorText(el)).toBe(SENTENCE);
        expect(text(el)).not.toContain('Validation error');
    });

    it('shows only the spinner after a record change until the new record reads', async () => {
        const el = await loaded();
        expect(table(el)).not.toBeNull();
        el.recordId = OTHER_ID;
        await flush();
        expect(table(el)).toBeNull();
        expect(text(el)).not.toContain('No split invoices found');
        expect(spinner(el)).not.toBeNull();
    });

    it('drops a names reply for the previous record', async () => {
        let resolveOld;
        getRelatedNames.mockImplementation(() => new Promise((resolve) => { resolveOld = resolve; }));
        const el = await mount();
        graphql.emit(current(CURRENT_ID, 'CORR-1'), toCurrent);
        await flush();
        graphql.emit(list(ACCOUNT_ID), toList);
        await flush();
        el.recordId = OTHER_ID;
        await flush();
        graphql.emit(current(OTHER_ID, null), toCurrent);
        await flush();
        expect(text(el)).toContain('No split invoices found');
        resolveOld({ accountNames: { [ACCOUNT_ID]: 'Old Account' } });
        await flush();
        expect(table(el)).toBeNull();
        expect(text(el)).toContain('No split invoices found');
    });
});
