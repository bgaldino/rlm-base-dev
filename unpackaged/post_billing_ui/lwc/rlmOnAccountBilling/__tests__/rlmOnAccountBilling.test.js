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
    overdueCount: 0, delinquentCount: 0, partiallyPaidOverdueCount: 0, openWithBalance: 1,
    writtenOffCount: 0, disputeCount: 0, inCollections: false,
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

    // Each part in turn: its popover value, the box total that includes it, the net and the pill
    // show Unavailable; the other box still shows its figure; nothing shows "-Unavailable" or $0.00,
    // and the net is not styled as a credit.
    it.each([
        ['invoiceBalance', 0, 0],
        ['debitMemoBalance', 1, 0],
        ['paymentBalance', 2, 1],
        ['creditMemoBalance', 3, 1],
        ['refundBalance', 4, 1]
    ])('shows %s, its total and the net as Unavailable when it is refused', async (part, popoverIndex, boxIndex) => {
        const el = mount();
        getBillingSummary.emit({ ...ALL_READ, [part]: null, netAccountBalance: null });
        await flush();
        const boxes = boxAmounts(el);
        expect(boxes[boxIndex]).toBe('Unavailable');
        expect(boxes[1 - boxIndex]).toBe(boxIndex === 0 ? '$34.00' : '$120.00');
        const values = popoverValues(el);
        expect(values[popoverIndex]).toBe('Unavailable');
        values.forEach((v) => expect(v).not.toContain('-Unavailable'));
        values.forEach((v) => expect(v).not.toContain('$0.00'));
        expect(net(el)).toBe('Unavailable');
        expect(el.shadowRoot.querySelector('.net-amount').className).not.toContain('net-positive');
        expect(el.shadowRoot.querySelector('.status-pill').textContent).toBe('Balance Unavailable');
    });

    it('does not claim no billing activity when a balance could not be read', async () => {
        const el = mount();
        getBillingSummary.emit({ ...REFUNDS_REFUSED, totalInvoices: 0 });
        await flush();
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

    // The empty {data, error} delivery a wire can make before the first server result, sent here
    // after the component is connected with a recordId: it must not stop the spinner.
    it('keeps the spinner through an empty delivery after connecting', async () => {
        const el = mount();
        await flush();
        getBillingSummary.emit(undefined);
        await flush();
        expect(spinner(el)).not.toBeNull();
        expect(el.shadowRoot.querySelector('.empty-state')).toBeNull();
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(spinner(el)).toBeNull();
    });

    it('hides the previous record, its status pill and spinner state when the recordId changes', async () => {
        const el = mount();
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(el.shadowRoot.querySelector('.status-pill')).not.toBeNull();
        el.recordId = '001000000000002AAA';
        await flush();
        expect(spinner(el)).not.toBeNull();
        expect(el.shadowRoot.querySelector('.summary-strip')).toBeNull();
        expect(el.shadowRoot.querySelector('.status-pill')).toBeNull();
        getBillingSummary.emit(undefined);
        await flush();
        expect(spinner(el)).not.toBeNull();
        getBillingSummary.emit({ ...ALL_READ, netAccountBalance: 7 });
        await flush();
        expect(spinner(el)).toBeNull();
        expect(net(el)).toBe('$7.00');
    });

    it('clears the previous record\'s error when the recordId changes', async () => {
        const el = mount();
        getBillingSummary.error({ message: 'Unable to read this account\'s invoices.' });
        await flush();
        expect(el.shadowRoot.querySelector('.error-container')).not.toBeNull();
        el.recordId = '001000000000002AAA';
        await flush();
        expect(el.shadowRoot.querySelector('.error-container')).toBeNull();
        expect(spinner(el)).not.toBeNull();
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
        getBillingSummary.emit(billing);
        await flush();
        return el.shadowRoot.querySelector('.status-pill').textContent;
    };

    it('reads the standing when every count is known', async () => {
        expect(await pillFor(ALL_READ)).toBe('Good Standing');
    });

    it.each(['inCollections', 'writtenOffCount', 'disputeCount'])(
        'shows Status Unavailable, not a standing, when %s is unavailable', async (key) => {
            expect(await pillFor({ ...ALL_READ, [key]: null })).toBe('Status Unavailable');
        }
    );

    // Partially paid invoices are a subset of the overdue ones.
    it('treats an unavailable partially-paid count as a real zero when nothing is overdue', async () => {
        expect(await pillFor({ ...ALL_READ, partiallyPaidOverdueCount: null })).toBe('Good Standing');
    });

    it('shows Status Unavailable for an unavailable partially-paid count when invoices are overdue', async () => {
        expect(await pillFor({ ...ALL_READ, overdueCount: 1, partiallyPaidOverdueCount: null })).toBe('Status Unavailable');
    });

    it('still shows a known earlier status ahead of an unavailable later count', async () => {
        expect(await pillFor({ ...ALL_READ, inCollections: true, disputeCount: null })).toBe('In Collections');
        expect(await pillFor({ ...ALL_READ, delinquentCount: 1, disputeCount: null })).toBe('Delinquent');
    });

    it.each(['inCollections', 'writtenOffCount', 'disputeCount'])(
        'does not claim no billing activity when %s is unavailable', async (key) => {
            expect(await pillFor({ ...ALL_READ, totalInvoices: 0, [key]: null })).toBe('Status Unavailable');
        }
    );

    const NO_INVOICES = { ...ALL_READ, totalInvoices: 0, openWithBalance: 0, netAccountBalance: 0,
        invoiceBalance: 0, debitMemoBalance: 0, creditMemoBalance: 0, paymentBalance: 0, refundBalance: 0 };

    it('claims no billing activity only when everything it covers is known to be none', async () => {
        expect(await pillFor(NO_INVOICES)).toBe('No Billing Activity');
    });

    it.each([
        ['only written-off invoices', { writtenOffCount: 1 }, 'Written Off'],
        ['an unapplied payment', { paymentBalance: 500, netAccountBalance: -500 }, 'Credit Balance'],
        ['an open dispute', { disputeCount: 1 }, 'In Dispute'],
        ['a collection plan', { inCollections: true }, 'In Collections'],
        ['a debit memo balance', { debitMemoBalance: 40, netAccountBalance: 40 }, 'Good Standing'],
        ['a debit memo offset by an unapplied payment', { debitMemoBalance: 50, paymentBalance: 50 }, 'Fully Settled'],
        ['a credit memo offset by a refund', { creditMemoBalance: 30, refundBalance: 30 }, 'Fully Settled'],
        ['a single credit memo', { creditMemoBalance: 30, netAccountBalance: -30 }, 'Credit Balance']
    ])('does not claim no billing activity for an account with %s', async (_label, change, expected) => {
        expect(await pillFor({ ...NO_INVOICES, ...change })).toBe(expected);
    });

    // Each balance part on its own unread (null) with the rest zero, the net kept at 0 so only the
    // per-part check stands between the account and "No Billing Activity".
    it.each(['invoiceBalance', 'debitMemoBalance', 'creditMemoBalance', 'paymentBalance', 'refundBalance'])(
        'does not claim no billing activity when %s is unavailable', async (part) => {
            expect(await pillFor({ ...NO_INVOICES, [part]: null })).not.toBe('No Billing Activity');
        }
    );
});
