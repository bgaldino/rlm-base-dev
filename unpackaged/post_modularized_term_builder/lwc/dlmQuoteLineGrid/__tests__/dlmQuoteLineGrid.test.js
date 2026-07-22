/* global require */
import { createElement } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import DlmQuoteLineGrid from 'c/dlmQuoteLineGrid';
import getQuoteLines from '@salesforce/apex/RLM_DeltaLineController.getQuoteLines';
import updateLineDiscountAndDates from '@salesforce/apex/RLM_DeltaLineController.updateLineDiscountAndDates';
import deleteLines from '@salesforce/apex/RLM_DeltaLineController.deleteLines';
import updateTermName from '@salesforce/apex/RLM_DeltaLineController.updateTermName';

// refreshApex is a non-spyable stub under the default jest preset (a plain function returning a
// resolved Promise). Register a virtual spy so the tests can assert the grid forces a server round
// trip. The grid's own import resolves to this same spy. Save/delete/rename only await it, so a
// no-op resolving jest.fn() is behaviorally identical for those paths.
jest.mock(
    '@salesforce/apex',
    () => ({ refreshApex: jest.fn(() => Promise.resolve()) }),
    { virtual: true }
);

// getQuoteLines is consumed as a @wire — wrap it in an Apex test wire adapter so .emit() feeds the
// wire. The adapter is require()'d lazily inside the factory because jest.mock() is hoisted above
// imports and may not close over out-of-scope bindings. updateLineDiscountAndDates/deleteLines are
// imperative, so give them explicit jest.fn()s.
jest.mock(
    '@salesforce/apex/RLM_DeltaLineController.getQuoteLines',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DeltaLineController.updateLineDiscountAndDates',
    () => ({ default: jest.fn() }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DeltaLineController.deleteLines',
    () => ({ default: jest.fn() }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DeltaLineController.updateTermName',
    () => ({ default: jest.fn() }),
    { virtual: true }
);

const RECORD_ID = '0Q0000000000001AAA';

// eslint-disable-next-line @lwc/lwc/no-async-operation
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

// Two lines: line1 has editable attributes (expandable), line2 does not.
function makeData(overrides = {}) {
    return JSON.stringify({
        isSuccess: true,
        groups: [],
        ungrouped: [
            {
                id: 'line1',
                productName: 'Widget',
                productCode: 'W-1',
                discount: 10,
                startDate: '2026-01-01',
                endDate: '2026-12-31',
                netUnitPrice: 100,
                isContracted: true,
                hasEditableAttributes: true,
                parentLineId: null,
                ...(overrides.line1 || {})
            },
            {
                id: 'line2',
                productName: 'Gadget',
                productCode: 'G-1',
                discount: 0,
                startDate: null,
                endDate: null,
                netUnitPrice: 50,
                isContracted: false,
                hasEditableAttributes: false,
                parentLineId: null,
                ...(overrides.line2 || {})
            }
        ]
    });
}

// Two Terms, each with a fare child, plus an unrelated standalone line — for scope/rename tests.
function makeTermData(overrides = {}) {
    return JSON.stringify({
        isSuccess: true,
        groups: [],
        ungrouped: [
            {
                id: 'termA',
                productName: 'Route A',
                customProductName: 'Route A',
                catalogProductName: 'DL-TERM',
                isTerm: true,
                productCode: 'DL-TERM',
                discount: 0,
                hasEditableAttributes: true,
                parentLineId: null,
                ...(overrides.termA || {})
            },
            {
                id: 'fareA1',
                productName: 'Delta One',
                catalogProductName: 'Delta One',
                isTerm: false,
                productCode: 'DL-FARE-ONE',
                discount: 5,
                hasEditableAttributes: false,
                parentLineId: 'termA',
                ...(overrides.fareA1 || {})
            },
            {
                id: 'termB',
                productName: 'Route B',
                customProductName: null,
                catalogProductName: 'DL-TERM',
                isTerm: true,
                productCode: 'DL-TERM',
                discount: 0,
                hasEditableAttributes: false,
                parentLineId: null,
                ...(overrides.termB || {})
            },
            {
                id: 'fareB1',
                productName: 'Comfort',
                catalogProductName: 'Comfort',
                isTerm: false,
                productCode: 'DL-FARE-COMF',
                discount: 0,
                hasEditableAttributes: false,
                parentLineId: 'termB',
                ...(overrides.fareB1 || {})
            }
        ]
    });
}

function createComponent() {
    const element = createElement('c-dlm-quote-line-grid', { is: DlmQuoteLineGrid });
    element.recordId = RECORD_ID;
    document.body.appendChild(element);
    return element;
}

function termNameInput(element, lineId) {
    return element.shadowRoot.querySelector(`th lightning-input[data-id="${lineId}"]`);
}

function dataRows(element) {
    // Data rows are the <tr class="slds-hint-parent">; detail rows are .rlm-detail-row.
    return Array.from(element.shadowRoot.querySelectorAll('tr.slds-hint-parent'));
}

function expander(element, lineId) {
    return element.shadowRoot.querySelector(`lightning-button-icon[data-expander="${lineId}"]`);
}

function removeButton(element, lineId) {
    return element.shadowRoot.querySelector(`lightning-button-icon[data-id="${lineId}"]:not([data-expander])`);
}

describe('c-dlm-quote-line-grid', () => {
    beforeEach(() => {
        updateLineDiscountAndDates.mockResolvedValue(JSON.stringify({ isSuccess: true, updatedCount: 1 }));
        deleteLines.mockResolvedValue(JSON.stringify({ isSuccess: true, deletedCount: 1 }));
        updateTermName.mockResolvedValue(JSON.stringify({ isSuccess: true, customProductName: 'Renamed' }));
    });

    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('renders one data row per line with an expander only where hasEditableAttributes', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeData());
        await flushPromises();

        expect(dataRows(element).length).toBe(2);
        expect(expander(element, 'line1')).not.toBeNull();
        expect(expander(element, 'line2')).toBeNull();
    });

    it('toggles the inline attribute picker and wires aria-expanded / aria-controls', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeData());
        await flushPromises();

        const btn = expander(element, 'line1');
        expect(btn.getAttribute('aria-expanded')).toBe('false');
        // LWC rewrites id/aria-controls pairs with a scoping suffix; the value is non-empty and, once
        // expanded, points at the detail region (asserted below).
        expect(btn.getAttribute('aria-controls')).toBeTruthy();
        expect(element.shadowRoot.querySelector('c-dlm-line-attribute-picker')).toBeNull();

        btn.click();
        await flushPromises();

        const picker = element.shadowRoot.querySelector('c-dlm-line-attribute-picker');
        expect(picker).not.toBeNull();
        expect(picker.quoteLineItemId).toBe('line1');
        // Once expanded, the detail region renders and the expander reports aria-expanded=true.
        const expandedBtn = expander(element, 'line1');
        expect(expandedBtn.getAttribute('aria-expanded')).toBe('true');
        expect(expandedBtn.getAttribute('aria-controls')).toBeTruthy();
        const region = element.shadowRoot.querySelector('[data-detail="line1"]');
        expect(region).not.toBeNull();
        expect(region.getAttribute('role')).toBe('region');
        expect(region.getAttribute('aria-label')).toBe('Attributes for Widget');

        // Collapse again.
        expander(element, 'line1').click();
        await flushPromises();
        expect(element.shadowRoot.querySelector('c-dlm-line-attribute-picker')).toBeNull();
    });

    it('shows the prior-contract discount read-only in its own column', async () => {
        const element = createComponent();
        // line1 carries a prior-discount snapshot; line2 (no priorDiscount) shows an em dash.
        getQuoteLines.emit(makeData({ line1: { priorDiscount: 12.5 } }));
        await flushPromises();

        const priorCells = Array.from(element.shadowRoot.querySelectorAll('td.rlm-col-prior span'));
        expect(priorCells.length).toBe(2);
        expect(priorCells[0].textContent.trim()).toBe('12.5%');
        expect(priorCells[1].textContent.trim()).toBe('—');
        // The column is static text, never an editable control bound to the value.
        priorCells.forEach((cell) => expect(cell.querySelector('lightning-input')).toBeNull());
    });

    it('renders a 0% prior discount and an em dash when there is no prior value', async () => {
        const element = createComponent();
        // line1: explicit 0 prior (a real value → "0%"); line2: no priorDiscount key → em dash.
        getQuoteLines.emit(makeData({ line1: { priorDiscount: 0 } }));
        await flushPromises();

        const priorCells = Array.from(element.shadowRoot.querySelectorAll('td.rlm-col-prior span'));
        expect(priorCells[0].textContent.trim()).toBe('0%');
        expect(priorCells[1].textContent.trim()).toBe('—');
    });

    it('preserves an in-flight date draft across an unsolicited refresh', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeData());
        await flushPromises();

        // Edit line1's start date without saving. The handler reads event.target.value, so set the
        // stub input's value then dispatch a change whose target is that input. line1 is not a Term,
        // so its inputs are [startDate, endDate] — the first is the start date.
        const startInput = element.shadowRoot.querySelector('lightning-input[data-id="line1"]');
        startInput.value = '2026-03-01';
        startInput.dispatchEvent(new CustomEvent('change'));
        await flushPromises();

        // Unsolicited refresh (finder added a line elsewhere) — same rows re-emitted.
        getQuoteLines.emit(makeData());
        await flushPromises();

        // The Save button should be enabled (draft still dirty) — proves the draft survived.
        const saveBtn = Array.from(element.shadowRoot.querySelectorAll('lightning-button')).find(
            (b) => b.label === 'Save changes'
        );
        expect(saveBtn.disabled).toBe(false);
    });

    it('preserves an expanded row across a refresh', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeData());
        await flushPromises();

        expander(element, 'line1').click();
        await flushPromises();
        expect(element.shadowRoot.querySelector('c-dlm-line-attribute-picker')).not.toBeNull();

        // Refresh with the same dataset.
        getQuoteLines.emit(makeData());
        await flushPromises();

        // Still expanded.
        expect(element.shadowRoot.querySelector('c-dlm-line-attribute-picker')).not.toBeNull();
        expect(expander(element, 'line1').getAttribute('aria-expanded')).toBe('true');
    });

    it('blocks save when end date precedes start date', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeData());
        await flushPromises();

        // line1 currently has start 2026-01-01 / end 2026-12-31; move end before start.
        const inputs = element.shadowRoot.querySelectorAll('lightning-input[data-id="line1"]');
        // inputs order in row: [startDate, endDate] (the discount column is Modeling-tab only)
        const endInput = inputs[1];
        endInput.value = '2025-01-01';
        endInput.dispatchEvent(new CustomEvent('change'));
        await flushPromises();

        const saveBtn = Array.from(element.shadowRoot.querySelectorAll('lightning-button')).find(
            (b) => b.label === 'Save changes'
        );
        saveBtn.click();
        await flushPromises();

        expect(updateLineDiscountAndDates).not.toHaveBeenCalled();
    });

    it('sends only changed fields via the inputJson wrapper on a valid save', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeData());
        await flushPromises();

        // line1's inputs are [startDate, endDate]; edit only the start date.
        const startInput = element.shadowRoot.querySelector('lightning-input[data-id="line1"]');
        startInput.value = '2026-03-01';
        startInput.dispatchEvent(new CustomEvent('change'));
        await flushPromises();

        const saveBtn = Array.from(element.shadowRoot.querySelectorAll('lightning-button')).find(
            (b) => b.label === 'Save changes'
        );
        saveBtn.click();
        await flushPromises();

        expect(updateLineDiscountAndDates).toHaveBeenCalledTimes(1);
        const arg = updateLineDiscountAndDates.mock.calls[0][0];
        expect(Object.keys(arg)).toEqual(['inputJson']);
        const payload = JSON.parse(arg.inputJson);
        expect(payload.quoteId).toBe(RECORD_ID);
        expect(payload.lines).toEqual([{ id: 'line1', startDate: '2026-03-01' }]);
    });

    it('renders a remove action per row and calls deleteLines with the line id on click', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeData());
        await flushPromises();

        expect(removeButton(element, 'line1')).not.toBeNull();
        expect(removeButton(element, 'line2')).not.toBeNull();

        removeButton(element, 'line2').click();
        await flushPromises();

        expect(deleteLines).toHaveBeenCalledTimes(1);
        const arg = deleteLines.mock.calls[0][0];
        expect(Object.keys(arg)).toEqual(['inputJson']);
        const payload = JSON.parse(arg.inputJson);
        expect(payload.quoteId).toBe(RECORD_ID);
        expect(payload.lineIds).toEqual(['line2']);
    });

    it('surfaces an error and leaves the row when deleteLines reports failure', async () => {
        deleteLines.mockResolvedValue(JSON.stringify({ isSuccess: false, errorMessage: 'Nope.' }));
        const element = createComponent();
        getQuoteLines.emit(makeData());
        await flushPromises();

        removeButton(element, 'line1').click();
        await flushPromises();

        expect(element.shadowRoot.querySelector('[role="alert"]').textContent).toBe('Nope.');
        expect(dataRows(element).length).toBe(2);
    });

    it('shows the full quote (all four lines) when scopeRootLineId is unset', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeTermData());
        await flushPromises();
        expect(dataRows(element).length).toBe(4);
    });

    it('narrows to a Term root and its descendants when scopeRootLineId is set', async () => {
        const element = createComponent();
        element.scopeRootLineId = 'termA';
        getQuoteLines.emit(makeTermData());
        await flushPromises();

        // termA + fareA1 only.
        const rows = dataRows(element);
        expect(rows.length).toBe(2);
        expect(termNameInput(element, 'termA')).not.toBeNull();
        expect(termNameInput(element, 'termB')).toBeNull();
        expect(removeButton(element, 'fareA1')).not.toBeNull();
        expect(removeButton(element, 'fareB1')).toBeNull();
    });

    it('re-scopes without a refetch when scopeRootLineId changes', async () => {
        const element = createComponent();
        element.scopeRootLineId = 'termA';
        getQuoteLines.emit(makeTermData());
        await flushPromises();
        expect(removeButton(element, 'fareA1')).not.toBeNull();

        // Switch Terms — no new emit; the setter re-scopes the cached payload.
        element.scopeRootLineId = 'termB';
        await flushPromises();
        expect(removeButton(element, 'fareB1')).not.toBeNull();
        expect(removeButton(element, 'fareA1')).toBeNull();
    });

    it('renders an inline name input only on Term rows', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeTermData());
        await flushPromises();
        expect(termNameInput(element, 'termA')).not.toBeNull();
        expect(termNameInput(element, 'termB')).not.toBeNull();
        expect(termNameInput(element, 'fareA1')).toBeNull();
    });

    it('commits a Term rename on blur only when the value changed', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeTermData());
        await flushPromises();

        // Blur without change → no Apex call.
        const input = termNameInput(element, 'termA');
        input.dispatchEvent(new CustomEvent('blur'));
        await flushPromises();
        expect(updateTermName).not.toHaveBeenCalled();

        // Change then blur → one call with the trimmed name.
        input.value = 'ATL → LHR';
        input.dispatchEvent(new CustomEvent('change'));
        input.dispatchEvent(new CustomEvent('blur'));
        await flushPromises();

        expect(updateTermName).toHaveBeenCalledTimes(1);
        const payload = JSON.parse(updateTermName.mock.calls[0][0].inputJson);
        expect(payload).toEqual({ quoteId: RECORD_ID, lineId: 'termA', customProductName: 'ATL → LHR' });
    });

    it('renders an expander on fare rows as well as on Terms with editable attributes', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeTermData());
        await flushPromises();

        // termA has editable route attributes → expander; fareA1 / fareB1 are fare rows → expander;
        // termB has neither editable attributes nor a fare-code editor → no expander.
        expect(expander(element, 'termA')).not.toBeNull();
        expect(expander(element, 'fareA1')).not.toBeNull();
        expect(expander(element, 'fareB1')).not.toBeNull();
        expect(expander(element, 'termB')).toBeNull();
    });

    it('expands a fare row into the fare-code dual-listbox (not the attribute picker) and saves the selection', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeTermData());
        await flushPromises();

        // Nothing expanded yet: no dual-listbox in the DOM.
        expect(element.shadowRoot.querySelector('lightning-dual-listbox')).toBeNull();

        expander(element, 'fareA1').click();
        await flushPromises();

        // The fare detail hosts the dual-listbox and NOT the route-attribute picker.
        const dl = element.shadowRoot.querySelector('lightning-dual-listbox');
        expect(dl).not.toBeNull();
        expect(element.shadowRoot.querySelector('c-dlm-line-attribute-picker')).toBeNull();

        // The detail region is labelled for fare codes, not attributes.
        const region = element.shadowRoot.querySelector('[data-detail="fareA1"]');
        expect(region.getAttribute('aria-label')).toBe('Fare codes for Delta One');

        // Choosing codes marks the row dirty and the save sends only the fareCodes field.
        dl.dispatchEvent(new CustomEvent('change', { detail: { value: ['W', 'S', 'J'] } }));
        await flushPromises();

        const saveBtn = Array.from(element.shadowRoot.querySelectorAll('lightning-button')).find(
            (b) => b.label === 'Save changes'
        );
        expect(saveBtn.disabled).toBe(false);
        saveBtn.click();
        await flushPromises();

        expect(updateLineDiscountAndDates).toHaveBeenCalledTimes(1);
        const payload = JSON.parse(updateLineDiscountAndDates.mock.calls[0][0].inputJson);
        expect(payload.lines).toEqual([{ id: 'fareA1', fareCodes: ['W', 'S', 'J'] }]);
    });

    it('shows a compact fare-code summary on the collapsed fare row', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeTermData({ fareA1: { fareCodes: ['W', 'S'] } }));
        await flushPromises();

        // The always-visible cell summarizes the selection space-separated; the editor stays collapsed.
        const summary = element.shadowRoot.querySelector('.rlm-col-fares span[title="W S"]');
        expect(summary).not.toBeNull();
        expect(summary.textContent).toBe('W S');
        expect(element.shadowRoot.querySelector('lightning-dual-listbox')).toBeNull();
    });

    // Regression: adding the FIRST Term flips the workspace open and mounts this grid, whose host
    // calls refresh() in the same frame — before the getQuoteLines wire has provisioned. getQuoteLines
    // is cacheable=true and a host may have warmed the LDS cache with an empty (pre-add) payload, so
    // the grid must force one round trip on first delivery; otherwise it renders the stale empty cache
    // and the just-added Term never appears ("No quote lines yet" with the Term selected).
    it('forces a server refresh when refresh() is called before the wire provisions', async () => {
        const element = createComponent();

        // Wire has not provisioned yet (_wired undefined): refresh() latches instead of round-tripping.
        await element.refresh();
        expect(refreshApex).not.toHaveBeenCalled();

        // First delivery honors the pending refresh with exactly one forced round trip.
        getQuoteLines.emit(makeTermData());
        await flushPromises();
        expect(refreshApex).toHaveBeenCalledTimes(1);

        // The latch is one-shot: a later unsolicited delivery does not re-trigger a forced refresh.
        getQuoteLines.emit(makeTermData());
        await flushPromises();
        expect(refreshApex).toHaveBeenCalledTimes(1);
    });

    it('round-trips immediately when refresh() is called after the wire has provisioned', async () => {
        const element = createComponent();
        getQuoteLines.emit(makeTermData());
        await flushPromises();
        // First delivery had no pending refresh, so nothing was forced.
        expect(refreshApex).not.toHaveBeenCalled();

        await element.refresh();
        expect(refreshApex).toHaveBeenCalledTimes(1);
    });
});
