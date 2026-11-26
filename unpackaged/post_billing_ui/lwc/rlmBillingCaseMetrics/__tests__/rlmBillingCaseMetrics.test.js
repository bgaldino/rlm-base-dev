import { createElement } from 'lwc';
import RlmBillingCaseMetrics from 'c/rlmBillingCaseMetrics';
import getMetrics from '@salesforce/apex/RLM_BillingCaseMetricsController.getMetrics';

jest.mock(
    '@salesforce/apex/RLM_BillingCaseMetricsController.getMetrics',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);

const flush = () => Promise.resolve();
const ALL_READ = { openBillingCases: 3, openDisputes: 2, disputedInvoices: 1, totalDisputedAmount: 250 };

async function load(emitFn) {
    const el = createElement('c-rlm-billing-case-metrics', { is: RlmBillingCaseMetrics });
    document.body.appendChild(el);
    emitFn();
    await flush();
    return [...el.shadowRoot.querySelectorAll('.metric-value')].map((n) => n.textContent);
}

// Pack 452: a metric the server could not read comes back null and shows as unavailable, never 0;
// a failed call shows every metric as unavailable rather than as zeros.
describe('rlmBillingCaseMetrics', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows the metrics when every read runs', async () => {
        expect(await load(() => getMetrics.emit(ALL_READ))).toEqual(['3', '2', '1', '$250.00']);
    });

    it('shows real zeros as zeros', async () => {
        expect(await load(() => getMetrics.emit({ openBillingCases: 0, openDisputes: 0, disputedInvoices: 0, totalDisputedAmount: 0 })))
            .toEqual(['0', '0', '0', '$0.00']);
    });

    it('shows a refused case count as Unavailable', async () => {
        expect(await load(() => getMetrics.emit({ ...ALL_READ, openBillingCases: null })))
            .toEqual(['Unavailable', '2', '1', '$250.00']);
    });

    it('shows refused dispute metrics as Unavailable', async () => {
        expect(await load(() => getMetrics.emit({ ...ALL_READ, openDisputes: null, totalDisputedAmount: null, disputedInvoices: null })))
            .toEqual(['3', 'Unavailable', 'Unavailable', 'Unavailable']);
    });

    it('shows every metric as Unavailable, not zero, when the call fails', async () => {
        expect(await load(() => getMetrics.error({ message: 'failed' })))
            .toEqual(['Unavailable', 'Unavailable', 'Unavailable', 'Unavailable']);
    });
});
