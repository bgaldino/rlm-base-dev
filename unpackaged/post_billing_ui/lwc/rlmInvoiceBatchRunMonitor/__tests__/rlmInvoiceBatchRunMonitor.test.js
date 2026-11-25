import { createElement } from 'lwc';
import RlmInvoiceBatchRunMonitor from 'c/rlmInvoiceBatchRunMonitor';
import { getRecord } from 'lightning/uiRecordApi';

// The user's Salesforce time zone.
jest.mock('@salesforce/i18n/timeZone', () => ({ default: 'Asia/Tokyo' }), { virtual: true });
jest.mock(
    '@salesforce/apex/RLM_InvoiceBatchRunMonitorController.getInvoiceStatusCounts',
    () => ({ default: jest.fn(() => Promise.resolve({ Draft: 0, Pending: 0, Posted: 1, Error: 0 })) }),
    { virtual: true }
);

const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

const field = (value) => ({ value });
const RUN = {
    fields: {
        InvoiceBatchRunNumber: field('IBR-000000001'),
        Status: field('Completed'),
        StatusSubtype: field('Completed'),
        // 09:42 and 09:47 UTC are 6:42 PM and 6:47 PM in Tokyo (UTC+9).
        StartTime: field('2026-11-25T09:42:00.000Z'),
        CompletionTime: field('2026-11-25T09:47:07.000Z'),
        TotalInvoicesGenerated: field(1),
        TotalPostedInvoices: field(1)
    }
};

const timingValues = (el) =>
    Array.from(el.shadowRoot.querySelectorAll('.timing-value')).map((n) => n.textContent);

describe('rlmInvoiceBatchRunMonitor times', () => {
    afterEach(() => {
        jest.restoreAllMocks();
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('formats start and completion times in the user time zone, not the browser zone', async () => {
        // Machine-independent check: the formatter must be told the user's zone. (The text check
        // below alone would pass without the fix on a machine that is itself in Tokyo.)
        const toLocaleString = jest.spyOn(Date.prototype, 'toLocaleString');
        const el = createElement('c-rlm-invoice-batch-run-monitor', { is: RlmInvoiceBatchRunMonitor });
        el.recordId = '5IRWt000002yvtVOAQ';
        document.body.appendChild(el);
        getRecord.emit(RUN);
        await flush();

        const zones = toLocaleString.mock.calls.map(([, options]) => options && options.timeZone);
        expect(zones.length).toBeGreaterThan(0);
        expect(zones.every((zone) => zone === 'Asia/Tokyo')).toBe(true);
        const values = timingValues(el);
        expect(values[0]).toBe('Nov 25, 2026, 6:42 PM');
        expect(values[1]).toBe('Nov 25, 2026, 6:47 PM');
    });
});
