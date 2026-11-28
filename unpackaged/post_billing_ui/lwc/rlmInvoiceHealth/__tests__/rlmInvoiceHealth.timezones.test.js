/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// Todo 510: the due, settlement and dispute received dates are Salesforce Dates ('YYYY-MM-DD'). Read
// as midnight UTC they were the day before in a browser behind UTC: the countdown said "Due today" a
// day early and the dates showed a day early. Each case pins the browser's time zone
// (setBrowserTimeZone, from the environment above) and the current instant.
import { createElement } from 'lwc';
import RlmInvoiceHealth from 'c/rlmInvoiceHealth';
import { graphql } from 'lightning/graphql';

const INVOICE_ID = '3tt000000000001AAA';
const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

// One payload answers the component's three graphql wires (the stub adapter does not tell them apart).
function payload(dueDate) {
    return { uiapi: { query: {
        Invoice: { edges: [{ node: {
            Id: INVOICE_ID,
            Status: { value: 'Posted' }, DaysInvoiceOpen: { value: 3 }, DueDate: { value: dueDate },
            TotalChargeAmount: { value: 100 }, TotalTaxAmount: { value: 0 }, TotalAmountWithTax: { value: 100 },
            Balance: { value: 0 }, SettlementStatus: { value: 'Settled' }, FullSettlementDate: { value: '2026-01-15' }
        } }] },
        InvoiceLine: { edges: [] },
        Dispute: { edges: [{ node: {
            Id: '0dp000000000001AAA', Name: { value: 'DSP-1' }, DisputedAmount: { value: 10 }, ApprovedAmount: { value: 0 },
            ReceivedDate: { value: '2026-01-20' }, Case: null
        } }] }
    } } };
}

// Opens the invoice on local noon of `today` (a 'YYYY-MM-DD' in the browser's zone).
async function open(timeZone, today, dueDate) {
    setBrowserTimeZone(timeZone);
    const [y, m, d] = today.split('-').map(Number);
    jest.useFakeTimers({ now: new Date(y, m - 1, d, 12), doNotFake: ['nextTick', 'queueMicrotask', 'setTimeout', 'clearTimeout'] });
    const el = createElement('c-rlm-invoice-health', { is: RlmInvoiceHealth });
    el.recordId = INVOICE_ID;
    document.body.appendChild(el);
    graphql.emit(payload(dueDate));
    await flush();
    return el;
}

const ZONES = ['America/Los_Angeles', 'America/New_York', 'Pacific/Honolulu', 'UTC', 'Asia/Tokyo'];

describe.each(ZONES)('rlmInvoiceHealth with the browser in %s', (timeZone) => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.useRealTimers();
    });

    it('counts the days to the due date as calendar days', async () => {
        let el = await open(timeZone, '2026-01-14', '2026-01-15');
        expect(el.shadowRoot.textContent).toContain('1 days until due');
        document.body.removeChild(el);

        el = await open(timeZone, '2026-01-15', '2026-01-15');
        expect(el.shadowRoot.textContent).toContain('Due today');
        document.body.removeChild(el);

        // Across the US change back to standard time (November 1, 2026) the local midnights are 25 hours apart.
        el = await open(timeZone, '2026-10-30', '2026-11-09');
        expect(el.shadowRoot.textContent).toContain('10 days until due');
    });

    it('shows the settlement and dispute dates as stored', async () => {
        const el = await open(timeZone, '2026-01-20', '2026-01-15');
        expect(el.shadowRoot.textContent).toContain('on Jan 15, 2026');
        el.shadowRoot.querySelector('button[data-tab="disputes"]').click();
        await flush();
        expect(el.shadowRoot.textContent).toContain('Received: Jan 20, 2026');
    });
});
