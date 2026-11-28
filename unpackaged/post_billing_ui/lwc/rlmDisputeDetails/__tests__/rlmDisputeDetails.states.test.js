// Todo 509: refused reads and re-reads. The dispute and its lines are each loading until their own reply,
// then ready or unavailable; a refused read shows only its fixed sentence, never the platform's text, and
// refused lines never read as a dispute with no lines.
import { createElement } from 'lwc';
import RlmDisputeDetails from 'c/rlmDisputeDetails';
import { graphql } from 'lightning/graphql';
import getRelatedNames from '@salesforce/apex/RLM_DisputeDetailsController.getRelatedNames';

jest.mock(
    '@salesforce/apex/RLM_DisputeDetailsController.getRelatedNames',
    () => ({ default: jest.fn() }),
    { virtual: true }
);

const CASE_ID = '500000000000001AAA';
const DISPUTE_A = '0Xd000000000001AAA';
const DISPUTE_B = '0Xd000000000002AAA';
const RAW = "Validation error of type FieldUndefined: Field 'Dispute' is undefined";
const DISPUTE_SENTENCE = "Unable to read this case's dispute. Contact your administrator.";
const LINES_SENTENCE = "Unable to read this dispute's lines. Contact your administrator.";
const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

// The wires by their variables: the dispute's carry the case id, the lines' the dispute id.
const toDispute = (config) => !!config?.variables?.caseId;
const toLines = (config) => !!config?.variables?.disputeId;

const dispute = (id) => ({ uiapi: { query: { Dispute: { edges: [{ node: {
    Id: id, Name: { value: 'D-' + id.slice(-4) }, InvoiceId: { value: null },
    DisputedAmount: { value: 10 }, ReceivedDate: { value: null }
} }] } } } });
const lines = { uiapi: { query: { DisputeItem: { edges: [{ node: {
    Id: 'a00000000000001AAA', InvoiceLineId: { value: null },
    DisputedAmount: { value: 10 }, ApprovedAmount: { value: 7 }, InvoiceLine: null
} }] } } } };

async function mount() {
    const el = createElement('c-rlm-dispute-details', { is: RlmDisputeDetails });
    el.recordId = CASE_ID;
    document.body.appendChild(el);
    await flush();
    return el;
}

async function withDispute(id = DISPUTE_A) {
    const el = await mount();
    graphql.emit(dispute(id), toDispute);
    await flush();
    return el;
}

const text = (el) => el.shadowRoot.textContent;
const spinner = (el) => el.shadowRoot.querySelector('lightning-spinner');
const approved = (el) => el.shadowRoot.querySelector('.amount-approved')?.textContent;
const linesSentence = (el) => el.shadowRoot.querySelector('.items-unavailable')?.textContent.trim();
const linesTable = (el) => el.shadowRoot.querySelector('.items-table');

describe('rlmDisputeDetails refused reads and re-reads', () => {
    beforeEach(() => {
        jest.spyOn(console, 'error').mockImplementation(() => {});
        getRelatedNames.mockResolvedValue({});
    });
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    it('shows the fixed sentence, not the platform text, when the dispute read is refused', async () => {
        const el = await mount();
        graphql.emitErrors([{ message: RAW }], toDispute);
        await flush();
        expect(el.shadowRoot.querySelector('.slds-text-color_error').textContent).toBe(DISPUTE_SENTENCE);
        expect(text(el)).not.toContain('Validation error');
        expect(text(el)).not.toContain('No dispute found');
    });

    it('says the lines could not be read, and the approved total is unavailable, when the line read is refused', async () => {
        const el = await withDispute();
        graphql.emitErrors([{ message: RAW }], toLines);
        await flush();
        expect(spinner(el)).toBeNull();
        expect(linesSentence(el)).toBe(LINES_SENTENCE);
        expect(approved(el)).toBe('Unavailable');
        expect(text(el)).not.toContain('Validation error');
    });

    it('drops the lines shown when a later line read is refused', async () => {
        const el = await withDispute();
        graphql.emit(lines, toLines);
        await flush();
        expect(linesTable(el)).not.toBeNull();
        graphql.emitErrors([{ message: RAW }], toLines);
        await flush();
        expect(linesTable(el)).toBeNull();
        expect(linesSentence(el)).toBe(LINES_SENTENCE);
    });

    // A guard, not a defect (it passes on main too): lines that recover are shown again.
    it('shows the lines and their approved total once a refused line read recovers', async () => {
        const el = await withDispute();
        graphql.emitErrors([{ message: RAW }], toLines);
        await flush();
        graphql.emit(lines, toLines);
        await flush();
        expect(linesSentence(el)).toBeUndefined();
        expect(approved(el)).toBe('$7.00');
    });

    it('keeps the approved total when the dispute is read again', async () => {
        const el = await withDispute();
        graphql.emit(lines, toLines);
        await flush();
        expect(approved(el)).toBe('$7.00');
        graphql.emit(dispute(DISPUTE_A), toDispute);
        await flush();
        expect(approved(el)).toBe('$7.00');
    });

    it('keeps the approved total unavailable when the dispute is read again after a refused line read', async () => {
        const el = await withDispute();
        graphql.emitErrors([{ message: RAW }], toLines);
        await flush();
        graphql.emit(dispute(DISPUTE_A), toDispute);
        await flush();
        expect(approved(el)).toBe('Unavailable');
        expect(linesSentence(el)).toBe(LINES_SENTENCE);
    });

    it("does not show the previous dispute's lines under a new dispute on the same case", async () => {
        const el = await withDispute();
        graphql.emit(lines, toLines);
        await flush();
        expect(linesTable(el)).not.toBeNull();
        graphql.emit(dispute(DISPUTE_B), toDispute);
        await flush();
        expect(linesTable(el)).toBeNull();
        expect(spinner(el)).not.toBeNull();
    });
});
