import { createElement } from 'lwc';
import RlmBsgOverview from 'c/rlmBsgOverview';
import getBillingScheduleGroupData from '@salesforce/apex/RLM_BSGTimelineController.getBillingScheduleGroupData';
import getConsolidatedTimeline from '@salesforce/apex/RLM_BSGTimelineController.getConsolidatedTimeline';

jest.mock(
    '@salesforce/apex/RLM_BSGTimelineController.getBillingScheduleGroupData',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_BSGTimelineController.getConsolidatedTimeline',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);

const SCHEDULE_ID = '0iB000000000001AAA';
const flush = () => Promise.resolve();

// One monthly schedule over a quarter, with or without its schedule number.
function bsgData(scheduleNumber) {
    return {
        totalBilledAmount: 0, totalPendingAmount: 300,
        billingSchedules: [{
            id: SCHEDULE_ID, scheduleNumber, startDate: '2026-01-01', endDate: '2026-03-31',
            billingTermUnit: 'Month', billingTerm: 1, billingPeriodAmount: 100, billedAmount: 0, quantity: 1
        }]
    };
}
function segments(scheduleNumber) {
    return [{
        periodNumber: 1, startDate: '2026-01-01', endDate: '2026-03-31', status: 'Active',
        netQuantity: 1, periodicBilling: 100, credits: 0,
        activeScheduleIds: [SCHEDULE_ID], activeScheduleNumbers: [scheduleNumber]
    }];
}

async function load(scheduleNumber) {
    const el = createElement('c-rlm-bsg-overview', { is: RlmBsgOverview });
    el.recordId = '1Bg000000000001AAA';
    document.body.appendChild(el);
    getBillingScheduleGroupData.emit(bsgData(scheduleNumber));
    getConsolidatedTimeline.emit(segments(scheduleNumber));
    await flush();
    return el;
}

const periodScheduleLabels = (el) => [...el.shadowRoot.querySelectorAll('.schedule-table-link')].map((n) => n.textContent);

describe('rlmBsgOverview period table schedule links', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('lists the schedule number in each billing period', async () => {
        const el = await load('BS-0001');
        const labels = periodScheduleLabels(el);
        expect(labels.length).toBeGreaterThan(0);
        labels.forEach((label) => expect(label).toBe('BS-0001'));
    });

    // Pack 452: a missing schedule number shows a dash, never the record Id.
    it('lists a dash, not the record Id, when the schedule number is missing', async () => {
        const el = await load(null);
        const labels = periodScheduleLabels(el);
        expect(labels.length).toBeGreaterThan(0);
        labels.forEach((label) => expect(label).toBe('—'));
    });
});
