/* global require */
import { createElement } from 'lwc';
import { subscribe } from 'lightning/messageService';
import DlmTermWorkspace from 'c/dlmTermWorkspace';

// The workspace hosts a real c/dlmQuoteLineGrid and c/dlmAddFareClass. Those children pull in Apex
// modules that don't resolve under jest, so stub every one. getQuoteLines is a @wire (wrap it in an
// Apex test wire adapter); the rest are imperative no-op jest.fn()s. refreshApex is stubbed so the
// grid mounts cleanly — the tests here spy on the grid's own refresh() method, so the grid's internal
// refetch path is irrelevant.
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
jest.mock(
    '@salesforce/apex/RLM_DeltaLineController.updateLineDiscountAndDates',
    () => ({ default: jest.fn(() => Promise.resolve('{}')) }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DeltaLineController.deleteLines',
    () => ({ default: jest.fn(() => Promise.resolve('{}')) }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DeltaLineController.updateTermName',
    () => ({ default: jest.fn(() => Promise.resolve('{}')) }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DeltaTermBuilderController.getFareChoices',
    () => ({ default: jest.fn(() => Promise.resolve('{}')) }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DeltaTermBuilderController.addFareClassesToTerm',
    () => ({ default: jest.fn(() => Promise.resolve('{}')) }),
    { virtual: true }
);

const QUOTE_ID = '0Q0000000000001AAA';
const TERM_ID = '0QL000000000001AAA';

// eslint-disable-next-line @lwc/lwc/no-async-operation
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

// Mount prop-driven (as the shell embeds it): quoteId + selectedTermId set → showWorkspace true → the
// grid is mounted. Returns the element plus the captured LMC handler so a test can inject a message.
async function createPropDriven({ selectedTermId = TERM_ID } = {}) {
    const element = createElement('c-dlm-term-workspace', { is: DlmTermWorkspace });
    element.quoteId = QUOTE_ID;
    element.selectedTermId = selectedTermId;
    document.body.appendChild(element);
    await flushPromises();
    // The workspace subscribes once in connectedCallback; the handler is the 3rd subscribe() arg.
    const handler = subscribe.mock.calls[0][2];
    return { element, handler };
}

function grid(element) {
    return element.shadowRoot.querySelector('c-dlm-quote-line-grid');
}

describe('c-dlm-term-workspace LMC → grid refresh', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    // Regression: adding the FIRST Term publishes `termSelected` (which mounts the grid via the shell
    // prop) BEFORE `termsChanged`. By the time `termsChanged` arrives the grid is already mounted and
    // the shell's selected-term-id prop is unchanged, so no re-render follows. The handler must refresh
    // the grid IMPERATIVELY here — a renderedCallback-latched refresh would never fire and the grid
    // would strand on the stale (pre-add) getQuoteLines cache until a full page reload.
    it('refreshes an already-mounted grid on termsChanged even when the selection prop is unchanged', async () => {
        const { element, handler } = await createPropDriven();
        expect(grid(element)).not.toBeNull();

        // Spy on the mounted grid's @api refresh.
        grid(element).refresh = jest.fn();

        // termsChanged carrying the SAME selectedTermId (prop-driven: the shell owns/keeps selection).
        handler({
            type: 'termsChanged',
            quoteId: QUOTE_ID,
            selectedTermId: TERM_ID,
            source: 'dlmTermsRail'
        });
        await flushPromises();

        expect(grid(element).refresh).toHaveBeenCalledTimes(1);
    });

    it('refreshes an already-mounted grid on linesChanged from another tile', async () => {
        const { element, handler } = await createPropDriven();
        grid(element).refresh = jest.fn();

        handler({
            type: 'linesChanged',
            quoteId: QUOTE_ID,
            source: 'dlmTermHeader'
        });
        await flushPromises();

        expect(grid(element).refresh).toHaveBeenCalledTimes(1);
    });

    it('ignores its own echoes (source guard)', async () => {
        const { element, handler } = await createPropDriven();
        grid(element).refresh = jest.fn();

        handler({
            type: 'linesChanged',
            quoteId: QUOTE_ID,
            source: 'dlmTermWorkspace'
        });
        await flushPromises();

        expect(grid(element).refresh).not.toHaveBeenCalled();
    });

    it('ignores messages for a different quote', async () => {
        const { element, handler } = await createPropDriven();
        grid(element).refresh = jest.fn();

        handler({
            type: 'termsChanged',
            quoteId: ' 0Q000000000000XXXX',
            selectedTermId: TERM_ID,
            source: 'dlmTermsRail'
        });
        await flushPromises();

        expect(grid(element).refresh).not.toHaveBeenCalled();
    });
});
