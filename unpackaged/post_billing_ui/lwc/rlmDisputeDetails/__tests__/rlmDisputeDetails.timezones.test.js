/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// Todo 510: the received date and the invoice line's period are Salesforce Dates ('YYYY-MM-DD'). Read
// as midnight UTC they showed a day early in a browser behind UTC. Each case pins the browser's time
// zone (setBrowserTimeZone, from the environment above).
import { createElement } from 'lwc';
import RlmDisputeDetails from 'c/rlmDisputeDetails';
import { graphql } from 'lightning/graphql';
import getRelatedNames from '@salesforce/apex/RLM_DisputeDetailsController.getRelatedNames';

jest.mock(
    '@salesforce/apex/RLM_DisputeDetailsController.getRelatedNames',
    () => ({ default: jest.fn() }),
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_DisputeDetailsController.saveApprovedAmounts',
    () => ({ default: jest.fn() }),
    { virtual: true }
);

const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

const ZONES = ['America/Los_Angeles', 'America/New_York', 'Pacific/Honolulu', 'UTC', 'Asia/Tokyo'];

describe.each(ZONES)('rlmDisputeDetails with the browser in %s', (timeZone) => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    it('shows the received date and the line period as stored', async () => {
        setBrowserTimeZone(timeZone);
        getRelatedNames.mockResolvedValue({ invoiceNames: {}, lineNames: {}, lineBalances: {} });
        const el = createElement('c-rlm-dispute-details', { is: RlmDisputeDetails });
        el.recordId = '500000000000001AAA';
        document.body.appendChild(el);
        // One payload answers both graphql wires (the stub adapter does not tell them apart).
        graphql.emit({ uiapi: { query: {
            Dispute: { edges: [{ node: {
                Id: '0Xd000000000001AAA', Name: { value: 'D-0001' }, InvoiceId: { value: '3tt000000000001AAA' },
                DisputedAmount: { value: 10 }, ReceivedDate: { value: '2026-01-20' }
            } }] },
            DisputeItem: { edges: [{ node: {
                Id: 'a00000000000001AAA', InvoiceLineId: { value: '5TV000000000001AAA' },
                DisputedAmount: { value: 10 }, ApprovedAmount: { value: 0 },
                InvoiceLine: {
                    Name: { value: 'Line 1' }, Balance: { value: 10 },
                    InvoiceLineStartDate: { value: '2026-01-01' }, InvoiceLineEndDate: { value: '2026-01-31' }
                }
            } }] }
        } } });
        await flush();
        const text = el.shadowRoot.textContent;
        expect(text).toContain('Jan 20, 2026');
        expect(text).toContain('Jan 1, 2026 – Jan 31, 2026');
    });
});
