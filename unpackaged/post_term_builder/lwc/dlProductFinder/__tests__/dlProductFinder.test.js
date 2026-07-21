import { createElement } from 'lwc';
import DlProductFinder from 'c/dlProductFinder';
import getCatalogContext from '@salesforce/apex/RLM_DeltaCatalogController.getCatalogContext';
import searchProducts from '@salesforce/apex/RLM_DeltaCatalogController.searchProducts';
import addLinesToQuote from '@salesforce/apex/RLM_DeltaCatalogController.addLinesToQuote';

// Control the imperative Apex the finder calls. (getRecommendations is left as the default auto-mock.)
jest.mock(
    '@salesforce/apex/RLM_DeltaCatalogController.getCatalogContext',
    () => ({ default: jest.fn() }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DeltaCatalogController.searchProducts',
    () => ({ default: jest.fn() }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DeltaCatalogController.addLinesToQuote',
    () => ({ default: jest.fn() }),
    { virtual: true }
);

const RECORD_ID = '0Q0000000000001AAA';

// eslint-disable-next-line @lwc/lwc/no-async-operation
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

function createComponent() {
    const element = createElement('c-dl-product-finder', { is: DlProductFinder });
    element.recordId = RECORD_ID;
    document.body.appendChild(element);
    return element;
}

describe('c-dl-product-finder', () => {
    beforeEach(() => {
        getCatalogContext.mockResolvedValue(JSON.stringify({ isSuccess: true, pricebook2Id: 'pb1', catalogs: [] }));
        searchProducts.mockResolvedValue(
            JSON.stringify({
                isSuccess: true,
                fields: [],
                products: [{ productId: 'prod1', pbeId: 'pbe1', name: 'Widget', code: 'W-1', isBundle: false }],
                cursor: null
            })
        );
        addLinesToQuote.mockResolvedValue(
            JSON.stringify({
                isSuccess: true,
                addedLines: [{ id: 'line1', productId: 'prod1', productName: 'Widget' }],
                addedCount: 1,
                groupIds: []
            })
        );
    });

    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('calls addLinesToQuote with the {inputJson: JSON.stringify(...)} wrapper and a flat (no-group) payload', async () => {
        const element = createComponent();
        await flushPromises();

        const datatable = element.shadowRoot.querySelector('c-dl-catalog-datatable');
        expect(datatable).not.toBeNull();

        // Simulate the per-row Add button firing the datatable's composed rowaction event.
        datatable.dispatchEvent(
            new CustomEvent('rowaction', {
                detail: {
                    action: { name: 'add' },
                    row: { pbeId: 'pbe1', productId: 'prod1', instanceCount: 2, name: 'Widget' }
                }
            })
        );
        await flushPromises();

        expect(addLinesToQuote).toHaveBeenCalledTimes(1);
        const arg = addLinesToQuote.mock.calls[0][0];
        // Exactly one named param: inputJson (preserve the JSON-wrapper Apex contract).
        expect(Object.keys(arg)).toEqual(['inputJson']);
        const payload = JSON.parse(arg.inputJson);
        expect(payload).toEqual({
            quoteId: RECORD_ID,
            lines: [{ pbeId: 'pbe1', productId: 'prod1', instanceCount: 2 }],
            newGroupName: null
        });
    });

    it('dispatches a composed linesadded event with { quoteId, addedCount, groupIds }', async () => {
        const element = createComponent();
        await flushPromises();

        const handler = jest.fn();
        element.addEventListener('linesadded', handler);

        const datatable = element.shadowRoot.querySelector('c-dl-catalog-datatable');
        datatable.dispatchEvent(
            new CustomEvent('rowaction', {
                detail: { action: { name: 'add' }, row: { pbeId: 'pbe1', productId: 'prod1', instanceCount: 1 } }
            })
        );
        await flushPromises();

        expect(handler).toHaveBeenCalledTimes(1);
        const evt = handler.mock.calls[0][0];
        expect(evt.detail).toEqual({ quoteId: RECORD_ID, addedCount: 1, groupIds: [] });
        expect(evt.bubbles).toBe(true);
        expect(evt.composed).toBe(true);
    });

    it('does not render any add-to-group controls', async () => {
        const element = createComponent();
        await flushPromises();

        const comboboxes = element.shadowRoot.querySelectorAll('lightning-combobox');
        // Only the (optional) catalog combobox may exist; with no catalogs there are none, and there is
        // never an "Add to group" combobox.
        comboboxes.forEach((cb) => {
            expect(cb.label).not.toBe('Add to group');
        });
        const groupInput = Array.from(element.shadowRoot.querySelectorAll('lightning-input')).find(
            (i) => i.label && i.label.toLowerCase().includes('group')
        );
        expect(groupInput).toBeUndefined();
    });
});
