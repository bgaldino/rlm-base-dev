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
    creditMemoBalance: 5, paymentBalance: 30, refundBalance: 1, netAccountBalance: 86
};
const spinner = (el) => el.shadowRoot.querySelector('lightning-spinner');
const metricTexts = (el) => [...el.shadowRoot.querySelectorAll('.metric-value')].map((n) => n.textContent);
const netText = (el) => el.shadowRoot.querySelector('.total-amount')?.textContent;

// The tooltip lines shown on hovering the metric of the given type.
async function tooltipLines(el, type) {
    el.shadowRoot.querySelector(`.metric[data-type="${type}"]`).dispatchEvent(new CustomEvent('mouseenter'));
    await flush();
    return [...el.shadowRoot.querySelectorAll('.tooltip-line')].map((n) => n.textContent);
}

async function loaded(billing) {
    const el = mount();
    getInvoiceSummary.emit(INVOICE);
    getBillingSummary.emit(billing);
    await flush();
    return el;
}

describe('rlmInvoiceSummaryBar unavailable balances', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows the figures when every balance is read', async () => {
        const el = await loaded(ALL_READ);
        expect(netText(el)).toBe('$86.00');
        expect(metricTexts(el)).toEqual(['$120.00', '$34.00']);
        expect(await tooltipLines(el, 'payables')).toEqual(['Payments: $30.00', 'Credits: $5.00', 'Refunds: -$1.00']);
    });

    // Each part in turn: the totals that include it, the net, its tooltip line and the pill show
    // Unavailable; the other total still shows its figure; nothing shows a number or "-Unavailable".
    it.each([
        ['invoiceBalance', 'receivables', 'Posted Invoices: Unavailable'],
        ['debitMemoBalance', 'receivables', 'Debit Memo Balance: Unavailable'],
        ['creditMemoBalance', 'payables', 'Credits: Unavailable'],
        ['paymentBalance', 'payables', 'Payments: Unavailable'],
        ['refundBalance', 'payables', 'Refunds: Unavailable']
    ])('shows %s, its total and the net as Unavailable when it is refused', async (part, group, line) => {
        const el = await loaded({ ...ALL_READ, [part]: null, netAccountBalance: null });
        expect(netText(el)).toBe('Unavailable');
        expect(metricTexts(el)).toEqual(group === 'receivables' ? ['Unavailable', '$34.00'] : ['$120.00', 'Unavailable']);
        const lines = await tooltipLines(el, group);
        expect(lines).toContain(line);
        lines.forEach((l) => expect(l).not.toContain('-Unavailable'));
        lines.forEach((l) => expect(l).not.toContain('$0.00'));
        expect(el.shadowRoot.querySelector('.status-pill').textContent).toBe('Balance Unavailable');
    });

    it('does not claim no billing activity when a balance could not be read', async () => {
        const el = await loaded({ ...ALL_READ, paymentBalance: null, netAccountBalance: null, totalInvoices: 0 });
        expect(el.shadowRoot.querySelector('.status-pill').textContent).toBe('Balance Unavailable');
    });
});

describe('rlmInvoiceSummaryBar loading', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    // The empty {data, error} delivery a wire can make before the first server result, sent here
    // after the component is connected with a recordId: it must not stop the spinner.
    it('keeps the spinner through empty deliveries after connecting', async () => {
        const el = mount();
        await flush();
        getInvoiceSummary.emit(undefined);
        getBillingSummary.emit(undefined);
        await flush();
        expect(spinner(el)).not.toBeNull();
        expect(el.shadowRoot.querySelector('.summary-container')).toBeNull();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(spinner(el)).toBeNull();
    });

    it('keeps the spinner when the invoice wire delivers empty and the billing wire delivers data', async () => {
        const el = mount();
        await flush();
        getInvoiceSummary.emit(undefined);
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(spinner(el)).not.toBeNull();
    });

    it('keeps the spinner when the billing wire delivers empty and the invoice wire delivers data', async () => {
        const el = mount();
        await flush();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(undefined);
        await flush();
        expect(spinner(el)).not.toBeNull();
    });

    it('stops the spinner when the invoice wire fails and the billing wire answers', async () => {
        const el = mount();
        getInvoiceSummary.error({ message: 'Invoice summary is unavailable.' });
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(spinner(el)).toBeNull();
        expect(errorText(el)).toBe('Invoice summary is unavailable.');
    });

    it('stops the spinner on an error too', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.error(REFUSED);
        await flush();
        expect(spinner(el)).toBeNull();
    });

    it('keeps the spinner between the two wires after a recordId change', async () => {
        const el = await loaded(ALL_READ);
        el.recordId = '001000000000002AAA';
        await flush();
        expect(spinner(el)).not.toBeNull();
        expect(el.shadowRoot.querySelector('.summary-container')).toBeNull();
        getInvoiceSummary.emit(INVOICE);
        await flush();
        expect(spinner(el)).not.toBeNull();
        expect(el.shadowRoot.querySelector('.summary-container')).toBeNull();
        getBillingSummary.emit({ ...ALL_READ, invoiceBalance: 15 });
        await flush();
        expect(spinner(el)).toBeNull();
        expect(netText(el)).toBe('$1.00');
    });

    it('keeps the spinner when only the billing wire answers after a recordId change', async () => {
        const el = await loaded(ALL_READ);
        el.recordId = '001000000000002AAA';
        await flush();
        getBillingSummary.emit({ ...ALL_READ, invoiceBalance: 15 });
        await flush();
        expect(spinner(el)).not.toBeNull();
        getInvoiceSummary.emit(INVOICE);
        await flush();
        expect(spinner(el)).toBeNull();
        expect(netText(el)).toBe('$1.00');
    });

    it('clears the previous record\'s error when the recordId changes', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.error(REFUSED);
        await flush();
        expect(errorText(el)).toBe(REFUSED.message);
        el.recordId = '001000000000002AAA';
        await flush();
        expect(errorText(el)).toBeUndefined();
        expect(spinner(el)).not.toBeNull();
    });

    it('clears the previous record\'s invoice error when the recordId changes', async () => {
        const el = mount();
        getInvoiceSummary.error({ message: 'Invoice summary is unavailable.' });
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(errorText(el)).toBe('Invoice summary is unavailable.');
        el.recordId = '001000000000002AAA';
        await flush();
        expect(errorText(el)).toBeUndefined();
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

// Pack 452: a segment whose read was refused comes back null and is not drawn; the card says
// which could not be read instead of letting the gap read as "none".
describe('unavailable invoice segments', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    const READ = { totalInvoices: 2, totalDue: 100, currentAmount: 100, currentCount: 2, debitAmount: 0, debitCount: 0,
        disputeAmount: 0, disputeCount: 0, promiseToPayAmount: 0, promiseToPayCount: 0, paidAmount: 0, paidCount: 0 };
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

    it('names refused debit memos', async () => {
        expect(await noteFor({ ...READ, debitAmount: null, debitCount: null, totalDue: null }))
            .toBe('Debit memos could not be read and are not shown.');
    });

    it('names all three when all are refused', async () => {
        expect(await noteFor({ ...READ, debitAmount: null, disputeAmount: null, promiseToPayAmount: null }))
            .toBe('Debit memos, disputes and promises to pay could not be read and are not shown.');
    });

    it('names refused paid invoices', async () => {
        expect(await noteFor({ ...READ, paidAmount: null, paidCount: null }))
            .toBe('Paid invoices could not be read and are not shown.');
    });

    // The live persona with only Account and Invoice read: every part it cannot read is named.
    it('names every refused part for a user who reads only invoices', async () => {
        expect(await noteFor({ ...READ, debitAmount: null, disputeAmount: null, promiseToPayAmount: null }))
            .toBe('Debit memos, disputes and promises to pay could not be read and are not shown.');
    });

    it('never shows a refused paid amount as a segment', async () => {
        const el = mount();
        getInvoiceSummary.emit({ ...READ, paidAmount: null, paidCount: null });
        getBillingSummary.emit(ALL_READ);
        await flush();
        expect(el.shadowRoot.textContent).not.toContain('-Unavailable');
        const segmentLabels = [...el.shadowRoot.querySelectorAll('.arrow-label')].map((n) => n.textContent);
        expect(segmentLabels.some((label) => label.startsWith('Paid'))).toBe(false);
        expect(segmentLabels).toContain('Current');
    });

    it('names both when both are refused', async () => {
        expect(await noteFor({ ...READ, disputeAmount: null, promiseToPayAmount: null }))
            .toBe('Disputes and promises to pay could not be read and are not shown.');
    });
});
