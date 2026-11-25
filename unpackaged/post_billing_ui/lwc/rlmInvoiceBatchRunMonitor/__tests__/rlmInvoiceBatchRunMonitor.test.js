import { createElement } from 'lwc';
import RlmInvoiceBatchRunMonitor from 'c/rlmInvoiceBatchRunMonitor';
import { getRecord } from 'lightning/uiRecordApi';

// The user's Salesforce time zone. UTC+14 matches no realistic machine or CI zone, so the test fails
// if the component formats in the browser's zone instead.
jest.mock('@salesforce/i18n/timeZone', () => ({ default: 'Pacific/Kiritimati' }), { virtual: true });
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
        // 09:42 and 09:47 UTC are 11:42 PM and 11:47 PM in the user's zone (UTC+14).
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
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows start and completion times in the user time zone, not the browser zone', async () => {
        const el = createElement('c-rlm-invoice-batch-run-monitor', { is: RlmInvoiceBatchRunMonitor });
        el.recordId = '5IRWt000002yvtVOAQ';
        document.body.appendChild(el);
        getRecord.emit(RUN);
        await flush();
        const values = timingValues(el);
        expect(values[0]).toBe('Nov 25, 2026, 11:42 PM');
        expect(values[1]).toBe('Nov 25, 2026, 11:47 PM');
    });
});
