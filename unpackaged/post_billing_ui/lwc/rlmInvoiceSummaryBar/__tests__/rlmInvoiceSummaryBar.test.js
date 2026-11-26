import { createElement } from 'lwc';
import RlmInvoiceSummaryBar from 'c/rlmInvoiceSummaryBar';
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
    const el = createElement('c-rlm-invoice-summary-bar', { is: RlmInvoiceSummaryBar });
    el.recordId = '001000000000001AAA';
    document.body.appendChild(el);
    return el;
}

describe('rlmInvoiceSummaryBar wires', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows the error and no figures while the billing summary is refused', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.error(REFUSED);
        await flush();
        expect(errorText(el)).toBe(REFUSED.message);
        expect(el.shadowRoot.querySelector('.summary-container')).toBeNull();
    });

    it('clears the error and shows the figures when the billing wire then succeeds', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.error(REFUSED);
        await flush();
        getBillingSummary.emit(BILLING);
        await flush();
        expect(errorText(el)).toBeUndefined();
        expect(el.shadowRoot.querySelector('.summary-container')).not.toBeNull();
    });

    it('drops the previous result when the invoice wire then fails', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(BILLING);
        await flush();
        expect(el.shadowRoot.querySelector('.summary-container')).not.toBeNull();
        getInvoiceSummary.error({ message: 'Invoice summary is unavailable.' });
        await flush();
        expect(errorText(el)).toBe('Invoice summary is unavailable.');
        expect(el.shadowRoot.querySelector('.summary-container')).toBeNull();
    });

    it('clears the error and shows the figures when the invoice wire then succeeds', async () => {
        const el = mount();
        getBillingSummary.emit(BILLING);
        getInvoiceSummary.error({ message: 'Invoice summary is unavailable.' });
        await flush();
        getInvoiceSummary.emit(INVOICE);
        await flush();
        expect(errorText(el)).toBeUndefined();
        expect(el.shadowRoot.querySelector('.summary-container')).not.toBeNull();
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
        expect(el.shadowRoot.querySelector('.summary-container')).toBeNull();
    });
});

// Pack 452: a balance the server could not read comes back null and shows as unavailable, never
// as $0.00; a wire is ready only on data or an error; a new recordId starts a new load.
const ALL_READ = {
    totalInvoices: 2, invoiceBalance: 100, debitMemoBalance: 20,
    overdueCount: 0, delinquentCount: 0, partiallyPaidOverdueCount: 0, openWithBalance: 1,
    writtenOffCount: 0, disputeCount: 0, inCollections: false,
    creditMemoBalance: 5, paymentBalance: 30, refundBalance: 0, netAccountBalance: 85
};
const PAYMENTS_REFUSED = { ...ALL_READ, paymentBalance: null, netAccountBalance: null };
const spinner = (el) => el.shadowRoot.querySelector('lightning-spinner');
const metricTexts = (el) => [...el.shadowRoot.querySelectorAll('.metric-value')].map((n) => n.textContent);

describe('rlmInvoiceSummaryBar unavailable balances and loading', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows the figures when every balance is read', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(el.shadowRoot.querySelector('.total-amount').textContent).toBe('$85.00');
        expect(metricTexts(el)).toEqual(['$120.00', '$35.00']);
    });

    it('shows a refused balance, and every total that includes it, as unavailable, not $0.00', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(PAYMENTS_REFUSED);
        await flush();
        expect(el.shadowRoot.querySelector('.total-amount').textContent).toBe('Unavailable');
        expect(metricTexts(el)).toEqual(['$120.00', 'Unavailable']);
        expect(el.shadowRoot.querySelector('.status-pill').textContent).toBe('Balance Unavailable');
    });

    it('does not claim no billing activity when a balance could not be read', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit({ ...PAYMENTS_REFUSED, totalInvoices: 0 });
        await flush();
        expect(el.shadowRoot.querySelector('.status-pill').textContent).toBe('Balance Unavailable');
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
        expect(el.shadowRoot.querySelector('.total-amount')).not.toBeNull();
        el.recordId = '001000000000002AAA';
        await flush();
        expect(spinner(el)).not.toBeNull();
        expect(el.shadowRoot.querySelector('.total-amount')).toBeNull();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit({ ...ALL_READ, netAccountBalance: 10, invoiceBalance: 25, debitMemoBalance: 20 });
        await flush();
        expect(spinner(el)).toBeNull();
        expect(el.shadowRoot.querySelector('.total-amount').textContent).toBe('$10.00');
    });
});

// Pack 452: a status count the server could not read comes back null. The pill cannot decide the
// standing past that check, so it says so instead of treating the count as zero or false.
describe('status pill with an unavailable count', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    const pillFor = async (billing) => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(billing);
        await flush();
        return el.shadowRoot.querySelector('.status-pill').textContent;
    };

    it('reads the standing when every count is known', async () => {
        expect(await pillFor(ALL_READ)).toBe('Good Standing');
    });

    it.each(['inCollections', 'writtenOffCount', 'disputeCount', 'partiallyPaidOverdueCount'])(
        'shows Status Unavailable, not a standing, when %s is unavailable', async (key) => {
            expect(await pillFor({ ...ALL_READ, [key]: null })).toBe('Status Unavailable');
        }
    );

    it('still shows a known earlier status ahead of an unavailable later count', async () => {
        expect(await pillFor({ ...ALL_READ, inCollections: true, disputeCount: null })).toBe('In Collections');
        expect(await pillFor({ ...ALL_READ, delinquentCount: 1, disputeCount: null })).toBe('Delinquent');
    });

    it('does not claim no billing activity when collections are unavailable', async () => {
        expect(await pillFor({ ...ALL_READ, totalInvoices: 0, inCollections: null })).toBe('Status Unavailable');
    });
});

// Pack 452: a segment whose read was refused comes back null and is not drawn; the card says
// which could not be read instead of letting the gap read as "none".
describe('unavailable invoice segments', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    const READ = { totalInvoices: 2, totalDue: 100, currentAmount: 100, currentCount: 2, disputeAmount: 0, disputeCount: 0,
        promiseToPayAmount: 0, promiseToPayCount: 0 };
    const noteFor = async (invoice) => {
        const el = mount();
        getInvoiceSummary.emit(invoice);
        getBillingSummary.emit(ALL_READ);
        await flush();
        return el.shadowRoot.querySelector('.unavailable-note')?.textContent;
    };

    it('shows no note when every segment is read', async () => {
        expect(await noteFor(READ)).toBeUndefined();
    });

    it('names refused disputes', async () => {
        expect(await noteFor({ ...READ, disputeAmount: null, disputeCount: null }))
            .toBe('Disputes could not be read and are not shown.');
    });

    it('names refused promises to pay', async () => {
        expect(await noteFor({ ...READ, promiseToPayAmount: null, promiseToPayCount: null }))
            .toBe('Promises to pay could not be read and are not shown.');
    });

    it('names both when both are refused', async () => {
        expect(await noteFor({ ...READ, disputeAmount: null, promiseToPayAmount: null }))
            .toBe('Disputes and promises to pay could not be read and are not shown.');
    });
});
