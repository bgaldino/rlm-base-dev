/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// Todo 510: the invoice date is a Salesforce Date ('YYYY-MM-DD'). Read as midnight UTC it showed a day
// early in a browser behind UTC. Each case pins the browser's time zone (setBrowserTimeZone, from the
// environment above).
import { createElement } from 'lwc';
import RlmSplitInvoicesCards from 'c/rlmSplitInvoicesCards';
import { graphql } from 'lightning/graphql';
import getRelatedNames from '@salesforce/apex/RLM_SplitInvoicesController.getRelatedNames';

jest.mock(
    '@salesforce/apex/RLM_SplitInvoicesController.getRelatedNames',
    () => ({ default: jest.fn() }),
    { virtual: true }
);

const CURRENT_ID = '3tt000000000001AAA';
const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

const ZONES = ['America/Los_Angeles', 'America/New_York', 'Pacific/Honolulu', 'UTC', 'Asia/Tokyo'];

describe.each(ZONES)('rlmSplitInvoicesCards with the browser in %s', (timeZone) => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    it('shows the invoice date as stored', async () => {
        setBrowserTimeZone(timeZone);
        getRelatedNames.mockResolvedValue({});
        const el = createElement('c-rlm-split-invoices-cards', { is: RlmSplitInvoicesCards });
        el.recordId = CURRENT_ID;
        document.body.appendChild(el);
        // One payload answers both graphql wires; it is sent twice because the list wire reads only
        // once the current invoice has given it the correlation id.
        const payload = { uiapi: { query: {
            Invoice: { edges: [{ node: { Id: CURRENT_ID, CorrelationIdentifier: { value: 'CORR-1' } } }] },
            InvoiceByCorrelation: { edges: [{ node: {
                Id: '3tt000000000002AAA', DocumentNumber: { value: 'INV-0002' }, InvoiceDate: { value: '2026-01-01' },
                TotalAmountWithTax: { value: 50 }, Status: { value: 'Posted' }, CorrelationIdentifier: { value: 'CORR-1' },
                BillingAccountId: { value: null }, BillingProfileId: { value: null }, BillToContactId: { value: null },
                SettlementStatus: { value: 'Not Settled' }
            } }] }
        } } };
        graphql.emit(payload);
        await flush();
        graphql.emit(payload);
        await flush();
        expect([...el.shadowRoot.querySelectorAll('.card-date')].map((n) => n.textContent)).toEqual(['Jan 1, 2026']);
    });
});
