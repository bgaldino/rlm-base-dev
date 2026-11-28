/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// Todo 510: a line's period dates are Salesforce Dates ('YYYY-MM-DD'). Read as midnight UTC they showed
// a day early in a browser behind UTC. Each case pins the browser's time zone (setBrowserTimeZone,
// from the environment above).
import { createElement } from 'lwc';
import RlmInvoiceProductSummary from 'c/rlmInvoiceProductSummary';
import getInvoiceProductSummary from '@salesforce/apex/RLM_InvoiceProductSummaryController.getInvoiceProductSummary';

jest.mock(
    '@salesforce/apex/RLM_InvoiceProductSummaryController.getInvoiceProductSummary',
    () => {
        const { createApexTestWireAdapter } = jest.requireActual('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_InvoiceProductSummaryController.saveLineAttributes',
    () => ({ default: jest.fn(() => Promise.resolve()) }),
    { virtual: true }
);

const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

const ZONES = ['America/Los_Angeles', 'America/New_York', 'Pacific/Honolulu', 'UTC', 'Asia/Tokyo'];

describe.each(ZONES)('rlmInvoiceProductSummary with the browser in %s', (timeZone) => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.restoreAllMocks();
    });

    it('shows a line period as stored', async () => {
        setBrowserTimeZone(timeZone);
        jest.spyOn(console, 'log').mockImplementation(() => {});
        const el = createElement('c-rlm-invoice-product-summary', { is: RlmInvoiceProductSummary });
        el.recordId = '3tt000000000001AAA';
        document.body.appendChild(el);
        getInvoiceProductSummary.emit({
            totalLines: 1, grandSubtotal: 100, grandTax: 0, grandTotal: 100,
            products: [{
                productId: '01t000000000001AAA', productName: 'Product', chargeType: 'Monthly', lineCount: 1,
                subtotal: 100, taxAmount: 0, totalWithTax: 100,
                lines: [{
                    lineId: '5TV000000000001AAA', name: 'Line 1', chargeAmount: 100, taxAmount: 0, totalWithTax: 100,
                    periodStartDate: '2026-01-01', periodEndDate: '2026-01-31'
                }]
            }]
        });
        await flush();
        el.shadowRoot.querySelector('[data-id="01t000000000001AAA"]').click();
        await flush();
        expect([...el.shadowRoot.querySelectorAll('.date-range')].map((n) => n.textContent))
            .toEqual(['Jan 1, 2026 → Jan 31, 2026']);
    });
});
