import { createElement } from 'lwc';
import RlmBsgConsolidatedTimeline from 'c/rlmBsgConsolidatedTimeline';
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
    const el = createElement('c-rlm-bsg-consolidated-timeline', { is: RlmBsgConsolidatedTimeline });
    el.recordId = '1Bg000000000001AAA';
    document.body.appendChild(el);
    getBillingScheduleGroupData.emit(bsgData(scheduleNumber));
    getConsolidatedTimeline.emit(segments(scheduleNumber));
    await flush();
    return el;
}

const scheduleLabels = (el) => [...el.shadowRoot.querySelectorAll('lightning-button.schedule-badge-link')].map((b) => b.label);

describe('rlmBsgConsolidatedTimeline schedule links', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('labels a schedule link with its schedule number', async () => {
        const el = await load('BS-0001');
        expect(scheduleLabels(el)).toEqual(['BS-0001']);
    });

    // Pack 452: a missing schedule number shows a dash, never the record Id.
    it('labels a schedule link with a dash, not the record Id, when the number is missing', async () => {
        const el = await load(null);
        expect(scheduleLabels(el)).toEqual(['—']);
    });
});
