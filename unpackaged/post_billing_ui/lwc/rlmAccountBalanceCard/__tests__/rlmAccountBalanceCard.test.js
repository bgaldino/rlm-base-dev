import { createElement } from 'lwc';
import RlmAccountBalanceCard from 'c/rlmAccountBalanceCard';
import getInvoiceSummary from '@salesforce/apex/RLM_InvoiceSummaryController.getInvoiceSummary';
import getBillingSummary from '@salesforce/apex/RLM_OnAccountBillingController.getBillingSummary';

jest.mock(
    '@salesforce/apex/RLM_InvoiceSummaryController.getInvoiceSummary',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_OnAccountBillingController.getBillingSummary',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);

const INVOICE = { totalInvoices: 2, totalDue: 100 };
const BILLING = { totalInvoices: 2, invoiceBalance: 100 };
const REFUSED = { message: 'Billing summary is unavailable.' };

const flush = () => Promise.resolve();
const errorText = (el) => el.shadowRoot.querySelector('.slds-text-color_error')?.textContent;

function mount() {
    const el = createElement('c-rlm-account-balance-card', { is: RlmAccountBalanceCard });
    el.recordId = '001000000000001AAA';
    document.body.appendChild(el);
    return el;
}

describe('rlmAccountBalanceCard wires', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows the error and no figures while the billing summary is refused', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.error(REFUSED);
        await flush();
        expect(errorText(el)).toBe(REFUSED.message);
        expect(el.shadowRoot.querySelector('.abc-card')).toBeNull();
    });

    it('clears the error and shows the figures when the billing wire then succeeds', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.error(REFUSED);
        await flush();
        getBillingSummary.emit(BILLING);
        await flush();
        expect(errorText(el)).toBeUndefined();
        expect(el.shadowRoot.querySelector('.abc-card')).not.toBeNull();
    });

    it('drops the previous result when the invoice wire then fails', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(BILLING);
        await flush();
        expect(el.shadowRoot.querySelector('.abc-card')).not.toBeNull();
        getInvoiceSummary.error({ message: 'Invoice summary is unavailable.' });
        await flush();
        expect(errorText(el)).toBe('Invoice summary is unavailable.');
        expect(el.shadowRoot.querySelector('.abc-card')).toBeNull();
    });

    it('clears the error and shows the figures when the invoice wire then succeeds', async () => {
        const el = mount();
        getBillingSummary.emit(BILLING);
        getInvoiceSummary.error({ message: 'Invoice summary is unavailable.' });
        await flush();
        getInvoiceSummary.emit(INVOICE);
        await flush();
        expect(errorText(el)).toBeUndefined();
        expect(el.shadowRoot.querySelector('.abc-card')).not.toBeNull();
    });

    it.each([
        ['invoice first', true],
        ['billing first', false]
    ])('shows the invoice error when both wires fail, %s', async (_order, invoiceFirst) => {
        const el = mount();
        const failInvoice = () => getInvoiceSummary.error({ message: 'Invoice summary is unavailable.' });
        const failBilling = () => getBillingSummary.error(REFUSED);
        if (invoiceFirst) { failInvoice(); failBilling(); } else { failBilling(); failInvoice(); }
        await flush();
        expect(errorText(el)).toBe('Invoice summary is unavailable.');
        expect(el.shadowRoot.querySelector('.abc-card')).toBeNull();
    });
});

// Pack 452: a balance the server could not read comes back null and shows as unavailable, never
// as $0.00; a wire is ready only on data or an error; a new recordId starts a new load.
const ALL_READ = {
    totalInvoices: 2, invoiceBalance: 100, debitMemoBalance: 20,
    creditMemoBalance: 5, paymentBalance: 30, refundBalance: 0, netAccountBalance: 85
};
const PAYMENTS_REFUSED = { ...ALL_READ, paymentBalance: null, netAccountBalance: null };
const spinner = (el) => el.shadowRoot.querySelector('lightning-spinner');
const metricTexts = (el) => [...el.shadowRoot.querySelectorAll('.abc-metric-value')].map((n) => n.textContent);

describe('rlmAccountBalanceCard unavailable balances and loading', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows the figures when every balance is read', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(el.shadowRoot.querySelector('.abc-net-amount').textContent).toBe('$85.00');
        expect(metricTexts(el)).toEqual(['$120.00', '$35.00']);
    });

    it('shows a refused balance, and every total that includes it, as unavailable, not $0.00', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(PAYMENTS_REFUSED);
        await flush();
        expect(el.shadowRoot.querySelector('.abc-net-amount').textContent).toBe('Unavailable');
        expect(metricTexts(el)).toEqual(['$120.00', 'Unavailable']);
        expect(el.shadowRoot.querySelector('.abc-pill').textContent).toBe('Balance Unavailable');
    });

    it('keeps the spinner through the empty first delivery and until both wires answer', async () => {
        const el = mount();
        await flush();
        expect(spinner(el)).not.toBeNull();
        getInvoiceSummary.emit(INVOICE);
        await flush();
        expect(spinner(el)).not.toBeNull();
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(spinner(el)).toBeNull();
    });

    it('stops the spinner on an error too', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.error(REFUSED);
        await flush();
        expect(spinner(el)).toBeNull();
    });

    it('hides the previous record and shows the spinner when the recordId changes', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(el.shadowRoot.querySelector('.abc-net-amount')).not.toBeNull();
        el.recordId = '001000000000002AAA';
        await flush();
        expect(spinner(el)).not.toBeNull();
        expect(el.shadowRoot.querySelector('.abc-net-amount')).toBeNull();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit({ ...ALL_READ, netAccountBalance: 10, invoiceBalance: 25, debitMemoBalance: 20 });
        await flush();
        expect(spinner(el)).toBeNull();
        expect(el.shadowRoot.querySelector('.abc-net-amount').textContent).toBe('$10.00');
    });
});
