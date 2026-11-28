/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// Todo 510: schedule dates are Salesforce Dates ('YYYY-MM-DD'). Read as midnight UTC, a schedule
// starting on January 1 gained a December month label in a browser behind UTC, and its dates showed a
// day early. Each case pins the browser's time zone (setBrowserTimeZone, from the environment above).
import { createElement } from 'lwc';
import RlmBsgSchedulesTimeline from 'c/rlmBsgSchedulesTimeline';
import getBillingScheduleGroupData from '@salesforce/apex/RLM_BSGTimelineController.getBillingScheduleGroupData';

jest.mock(
    '@salesforce/apex/RLM_BSGTimelineController.getBillingScheduleGroupData',
    () => {
        const { createApexTestWireAdapter } = jest.requireActual('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);

const SCHEDULE_ID = '0iB000000000001AAA';
const flush = () => Promise.resolve();

const ZONES = ['America/Los_Angeles', 'America/New_York', 'Pacific/Honolulu', 'UTC', 'Asia/Tokyo'];

describe.each(ZONES)('rlmBsgSchedulesTimeline with the browser in %s', (timeZone) => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('labels the schedule months and shows its dates as stored', async () => {
        setBrowserTimeZone(timeZone);
        const el = createElement('c-rlm-bsg-schedules-timeline', { is: RlmBsgSchedulesTimeline });
        el.recordId = '1Bg000000000001AAA';
        document.body.appendChild(el);
        getBillingScheduleGroupData.emit({
            billingSchedules: [{
                id: SCHEDULE_ID, scheduleNumber: 'BS-0001', status: 'Active', category: 'Original',
                startDate: '2026-01-01', endDate: '2026-03-31', nextBillingDate: '2026-02-01',
                billingTermUnit: 'Month', billingPeriodAmount: 100, totalAmount: 300, billedAmount: 0, quantity: 1
            }]
        });
        await flush();

        const months = [...el.shadowRoot.querySelectorAll('.month-label')].map((n) => n.textContent.trim());
        expect(months).toEqual(['Jan 26', 'Feb 26', 'Mar 26']);

        el.shadowRoot.querySelector('lightning-button.schedule-link').click();
        await flush();
        const text = el.shadowRoot.textContent;
        expect(text).toContain('Jan 1, 2026');
        expect(text).toContain('Mar 31, 2026');
        expect(text).toContain('Feb 1, 2026');
    });
});
