/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// Todo 510: schedule and segment dates are Salesforce Dates ('YYYY-MM-DD'). Read as midnight UTC, a
// schedule starting on January 1 charted from December in a browser behind UTC, and segment dates
// showed a day early. Each case pins the browser's time zone (setBrowserTimeZone, from the
// environment above); the repo's Jest config otherwise runs every suite in UTC.
import { createElement } from 'lwc';
import RlmBsgConsolidatedTimeline from 'c/rlmBsgConsolidatedTimeline';
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

async function load(timeZone) {
    setBrowserTimeZone(timeZone);
    const el = createElement('c-rlm-bsg-consolidated-timeline', { is: RlmBsgConsolidatedTimeline });
    el.recordId = '1Bg000000000001AAA';
    document.body.appendChild(el);
    getBillingScheduleGroupData.emit({
        totalBilledAmount: 0, totalPendingAmount: 300,
        billingSchedules: [{
            id: SCHEDULE_ID, scheduleNumber: 'BS-0001', startDate: '2026-01-01', endDate: '2026-03-31',
            billingTermUnit: 'Month', billingTerm: 1, billingPeriodAmount: 100, billedAmount: 0, quantity: 1
        }]
    });
    getConsolidatedTimeline.emit([{
        periodNumber: 1, startDate: '2026-01-01', endDate: '2026-03-31', status: 'Active',
        netQuantity: 1, periodicBilling: 100, credits: 0,
        activeScheduleIds: [SCHEDULE_ID], activeScheduleNumbers: ['BS-0001']
    }]);
    await flush();
    return el;
}

const ZONES = ['America/Los_Angeles', 'America/New_York', 'Pacific/Honolulu', 'UTC', 'Asia/Tokyo'];

describe.each(ZONES)('rlmBsgConsolidatedTimeline with the browser in %s', (timeZone) => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('charts the schedule months and shows the segment dates as stored', async () => {
        const el = await load(timeZone);
        const labels = [...el.shadowRoot.querySelectorAll('.x-axis-label')].map((n) => n.textContent.trim());
        expect(labels).toEqual(["Jan '26", "Feb '26", "Mar '26"]);
        const bars = [...el.shadowRoot.querySelectorAll('.bar-label')].map((n) => n.textContent.trim());
        expect(bars).toEqual(['$100.00', '$100.00', '$100.00']);
        const text = el.shadowRoot.textContent;
        expect(text).toContain('Jan 1, 2026');
        expect(text).toContain('Mar 31, 2026');
    });
});
