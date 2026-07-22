/* global require */
import { createElement } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import getQuoteLines from '@salesforce/apex/RLM_DeltaLineController.getQuoteLines';
import getBuilderState from '@salesforce/apex/RLM_DeltaTermBuilderController.getBuilderState';
import addTerm from '@salesforce/apex/RLM_DeltaTermBuilderController.addTerm';
import DlTermBuilder from 'c/dlTermBuilder';

// The orchestrator hosts a real c/dlQuoteLineGrid (and c/dlAddFareClass). Stub every Apex module the
// orchestrator and its children import so the tree mounts. getQuoteLines is the grid's @wire; the rest
// are imperative. refreshApex is the observable: the grid forces it only after its host asks it to
// refetch (grid.refresh() latches _refreshPending → wiredLines fires refreshApex on the next delivery),
// so a refreshApex call after the first Term is added proves the host drove the newly shown grid to
// reload rather than leaving it on the stale, pre-add quoteId-keyed cache.
//
// SCOPE NOTE: the real in-browser bug is a microtask-ordering RACE — _refreshGrid() runs its
// querySelector on the synchronous tick before selectedTermId's re-render mounts the grid, so the
// latch (renderedCallback consuming _needsGridRefresh) is what carries the refresh across the mount.
// jsdom/jest resolves the add flow's awaits such that the grid is already mounted when _refreshGrid()
// runs, so this harness exercises the base if-branch, not the latch. This test therefore guards that
// adding the first Term refetches the grid at all (a real regression guard — it fails if the refresh
// is dropped, verified by fully no-op'ing _refreshGrid); the latch's browser-only timing value is
// covered by live verification. The LMC-specific race is guarded directly in the modular build's
// dlmTermWorkspace.test.js, where the mechanism is jest-reproducible.
// c/dlCreateContractModal extends LightningModal; it's never opened here, so a bare base class is
// enough to let the import resolve.
jest.mock('lightning/modal', () => ({ __esModule: true, default: class {} }), { virtual: true });
jest.mock(
    '@salesforce/apex',
    () => ({ refreshApex: jest.fn(() => Promise.resolve()) }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DeltaLineController.getQuoteLines',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);
// Imperative Apex — orchestrator + grid + add-fare surfaces. No-op resolving stubs.
const okJson = () => Promise.resolve(JSON.stringify({ isSuccess: true }));
jest.mock('@salesforce/apex/RLM_DeltaTermBuilderController.createNegotiation', () => ({ default: jest.fn(okJson) }), { virtual: true });
jest.mock('@salesforce/apex/RLM_DeltaTermBuilderController.getNegotiationsForAccount', () => ({ default: jest.fn(okJson) }), { virtual: true });
jest.mock('@salesforce/apex/RLM_DeltaTermBuilderController.getBuilderState', () => ({ default: jest.fn() }), { virtual: true });
jest.mock('@salesforce/apex/RLM_DeltaTermBuilderController.addTerm', () => ({ default: jest.fn() }), { virtual: true });
jest.mock('@salesforce/apex/RLM_DeltaTermBuilderController.updateNegotiationDates', () => ({ default: jest.fn(okJson) }), { virtual: true });
jest.mock('@salesforce/apex/RLM_DeltaLineController.updateLineDiscountAndDates', () => ({ default: jest.fn(okJson) }), { virtual: true });
jest.mock('@salesforce/apex/RLM_DeltaLineController.deleteLines', () => ({ default: jest.fn(okJson) }), { virtual: true });
jest.mock('@salesforce/apex/RLM_DeltaLineController.updateTermName', () => ({ default: jest.fn(okJson) }), { virtual: true });
jest.mock('@salesforce/apex/RLM_DeltaTermBuilderController.getFareChoices', () => ({ default: jest.fn(okJson) }), { virtual: true });
jest.mock('@salesforce/apex/RLM_DeltaTermBuilderController.addFareClassesToTerm', () => ({ default: jest.fn(okJson) }), { virtual: true });

const QUOTE_ID = '0Q0000000000001AAA';
const TERM_ID = '0QL000000000001AAA';

// eslint-disable-next-line @lwc/lwc/no-async-operation
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

function stateWithTerms(terms, selectedTermId) {
    return JSON.stringify({
        isSuccess: true,
        quote: { name: 'Negotiation' }, // no accountId → no loadNegotiations back-fill
        terms,
        selectedTermId: selectedTermId || null
    });
}

function grid(element) {
    return element.shadowRoot.querySelector('c-dl-quote-line-grid');
}

function addTermButton(element) {
    return element.shadowRoot.querySelector('.dl-tb-add-term__btn');
}

describe('c-dl-term-builder — add the first Term refreshes the newly mounted grid', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    // Regression: adding the FIRST Term flips showWorkspace true, but the grid mounts on the NEXT
    // re-render — not on the synchronous tick that sets selectedTermId. The old _refreshGrid() ran
    // querySelector immediately, found no grid, and skipped the refresh, so the grid provisioned from
    // the stale (pre-add) getQuoteLines cache and stranded "No quote lines yet" until a page reload.
    // The latch + renderedCallback must force a refetch once the grid appears.
    it('refetches the grid when the first Term is added (grid mounts from hidden)', async () => {
        // Open the quote with ZERO terms → workspace/grid hidden.
        getBuilderState.mockResolvedValueOnce(stateWithTerms([]));
        // The post-add reload returns one Term → selection resolves, workspace shows, grid mounts.
        getBuilderState.mockResolvedValue(
            stateWithTerms([{ id: TERM_ID, displayName: 'Route A' }], TERM_ID)
        );
        addTerm.mockResolvedValue(JSON.stringify({ isSuccess: true, addedCount: 1 }));

        const element = createElement('c-dl-term-builder', { is: DlTermBuilder });
        element.quoteRecordId = QUOTE_ID; // deep-link straight into the quote
        document.body.appendChild(element);
        await flushPromises();

        // No Term yet → grid not mounted, no refetch yet.
        expect(grid(element)).toBeNull();
        expect(refreshApex).not.toHaveBeenCalled();
        const btn = addTermButton(element);
        expect(btn).toBeTruthy();

        // Add the first Term.
        btn.click();
        await flushPromises();

        // Grid is now mounted; its wire hasn't delivered real data yet, so the host's refresh latched
        // _refreshPending inside the grid.
        expect(grid(element)).not.toBeNull();

        // First real wire delivery → the latched refresh forces the server round trip. Without the
        // host driving the refresh (e.g. _refreshGrid no-op'd), _refreshPending stays false and this
        // delivery calls no refreshApex — the grid would sit on the stale pre-add cache.
        getQuoteLines.emit(
            JSON.stringify({ isSuccess: true, groups: [], ungrouped: [] })
        );
        await flushPromises();
        expect(refreshApex).toHaveBeenCalled();
    });
});
