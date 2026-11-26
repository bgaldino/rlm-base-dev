import { createElement } from 'lwc';
import RlmOnAccountBilling from 'c/rlmOnAccountBilling';
import getBillingSummary from '@salesforce/apex/RLM_OnAccountBillingController.getBillingSummary';

jest.mock(
    '@salesforce/apex/RLM_OnAccountBillingController.getBillingSummary',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);

// Pack 452: a balance the server could not read comes back null and shows as unavailable, never
// as $0.00; the wire is ready only on data or an error; a new recordId starts a new load.
const ALL_READ = {
    currencyIsoCode: 'USD', isMultiCurrency: false, totalInvoices: 2,
    invoiceBalance: 100, debitMemoBalance: 20, creditMemoBalance: 5,
    paymentBalance: 30, refundBalance: 1, netAccountBalance: 86
};
const REFUNDS_REFUSED = { ...ALL_READ, refundBalance: null, netAccountBalance: null };

const flush = () => Promise.resolve();
const spinner = (el) => el.shadowRoot.querySelector('lightning-spinner');
const boxAmounts = (el) => [...el.shadowRoot.querySelectorAll('.box-amount')].map((n) => n.textContent);
const net = (el) => el.shadowRoot.querySelector('.net-amount')?.textContent;
const popoverValues = (el) => [...el.shadowRoot.querySelectorAll('.popover-value')].map((n) => n.textContent);

function mount() {
    const el = createElement('c-rlm-on-account-billing', { is: RlmOnAccountBilling });
    el.recordId = '001000000000001AAA';
    document.body.appendChild(el);
    return el;
}

describe('rlmOnAccountBilling', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows the figures when every balance is read', async () => {
        const el = mount();
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(boxAmounts(el)).toEqual(['$120.00', '$34.00']);
        expect(net(el)).toBe('$86.00');
        expect(popoverValues(el)).toEqual(['$100.00', '$20.00', '$30.00', '$5.00', '-$1.00']);
    });

    it('shows a refused balance, and every total that includes it, as unavailable, not $0.00', async () => {
        const el = mount();
        getBillingSummary.emit(REFUNDS_REFUSED);
        await flush();
        expect(boxAmounts(el)).toEqual(['$120.00', 'Unavailable']);
        expect(net(el)).toBe('Unavailable');
        expect(popoverValues(el)[4]).toBe('Unavailable');
        expect(el.shadowRoot.querySelector('.status-pill').textContent).toBe('Balance Unavailable');
    });

    it('shows the server error and no figures when the summary fails', async () => {
        const el = mount();
        getBillingSummary.error({ message: 'Unable to read this account\'s invoices.' });
        await flush();
        expect(el.shadowRoot.querySelector('.error-container').textContent).toContain('Unable to read this account\'s invoices.');
        expect(el.shadowRoot.querySelector('.summary-strip')).toBeNull();
        expect(spinner(el)).toBeNull();
    });

    it('keeps the spinner through the empty first delivery', async () => {
        const el = mount();
        await flush();
        expect(spinner(el)).not.toBeNull();
        expect(el.shadowRoot.querySelector('.empty-state')).toBeNull();
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(spinner(el)).toBeNull();
    });

    it('hides the previous record and shows the spinner when the recordId changes', async () => {
        const el = mount();
        getBillingSummary.emit(ALL_READ);
        await flush();
        el.recordId = '001000000000002AAA';
        await flush();
        expect(spinner(el)).not.toBeNull();
        expect(el.shadowRoot.querySelector('.summary-strip')).toBeNull();
        getBillingSummary.emit({ ...ALL_READ, netAccountBalance: 7 });
        await flush();
        expect(spinner(el)).toBeNull();
        expect(net(el)).toBe('$7.00');
    });
});
