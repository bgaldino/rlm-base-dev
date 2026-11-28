/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// Todo 510: schedule dates are Salesforce Dates ('YYYY-MM-DD'), calendar dates with no time zone. Read
// as midnight UTC, a schedule starting on January 1 became December 31 in a browser behind UTC: the
// period table gained an empty "Dec '25" row with no schedule link, and dates showed a day early. Each
// case pins the browser's time zone (setBrowserTimeZone, from the environment above); the repo's Jest
// config otherwise runs every suite in UTC, where the defect does not show.
import { createElement } from 'lwc';
import RlmBsgOverview from 'c/rlmBsgOverview';
import getBillingScheduleGroupData from '@salesforce/apex/RLM_BSGTimelineController.getBillingScheduleGroupData';
import getConsolidatedTimeline from '@salesforce/apex/RLM_BSGTimelineController.getConsolidatedTimeline';

jest.mock(
    '@salesforce/apex/RLM_BSGTimelineController.getBillingScheduleGroupData',
    () => {
        const { createApexTestWireAdapter } = jest.requireActual('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_BSGTimelineController.getConsolidatedTimeline',
    () => {
        const { createApexTestWireAdapter } = jest.requireActual('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);

const SCHEDULE_ID = '0iB000000000001AAA';
const flush = () => Promise.resolve();

// One monthly schedule of $100 over the first quarter of 2026, in a group that ends with it.
const BSG = {
    endDate: '2026-03-31',
    totalBilledAmount: 0, totalPendingAmount: 300,
    billingSchedules: [{
        id: SCHEDULE_ID, scheduleNumber: 'BS-0001', status: 'Active', category: 'Original',
        startDate: '2026-01-01', endDate: '2026-03-31', nextBillingDate: '2026-01-01',
        billingTermUnit: 'Month', billingTerm: 1, billingPeriodAmount: 100, billedAmount: 0, quantity: 1
    }]
};
const SEGMENTS = [{
    periodNumber: 1, startDate: '2026-01-01', endDate: '2026-03-31', status: 'Active',
    netQuantity: 1, periodicBilling: 100, credits: 0,
    activeScheduleIds: [SCHEDULE_ID], activeScheduleNumbers: ['BS-0001']
}];

async function load(timeZone) {
    setBrowserTimeZone(timeZone);
    const el = createElement('c-rlm-bsg-overview', { is: RlmBsgOverview });
    el.recordId = '1Bg000000000001AAA';
    document.body.appendChild(el);
    getBillingScheduleGroupData.emit(BSG);
    getConsolidatedTimeline.emit(SEGMENTS);
    await flush();
    return el;
}

// Each period row as [period, net qty, billing, credits, schedules, status].
const periodRows = (el) => [...el.shadowRoot.querySelectorAll('.segments-table tbody tr')]
    .map((tr) => [...tr.querySelectorAll('td')].map((td) => td.textContent.trim()));

const ZONES = ['America/Los_Angeles', 'America/New_York', 'Pacific/Honolulu', 'UTC', 'Asia/Tokyo'];

describe.each(ZONES)('rlmBsgOverview with the browser in %s', (timeZone) => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('puts each month of the schedule in its own period, linked to the schedule', async () => {
        const el = await load(timeZone);
        expect(periodRows(el)).toEqual([
            ["Jan '26", '1', '$100.00', '--', 'BS-0001', 'Pending'],
            ["Feb '26", '1', '$100.00', '--', 'BS-0001', 'Pending'],
            ["Mar '26", '1', '$100.00', '--', 'BS-0001', 'Pending']
        ]);
    });

    it('shows the group end date and the schedule dates as stored', async () => {
        const el = await load(timeZone);
        expect(el.shadowRoot.textContent).toContain('End: Mar 31, 2026');

        el.shadowRoot.querySelectorAll('lightning-button')
            .forEach((b) => { if (b.label === 'Billing Schedules') b.click(); });
        await flush();
        el.shadowRoot.querySelector('lightning-button.schedule-link').click();
        await flush();
        const text = el.shadowRoot.textContent;
        expect(text).toContain('Jan 1, 2026');
        expect(text).toContain('Mar 31, 2026');
        expect(text).not.toContain('Dec 31, 2025');
    });
});
