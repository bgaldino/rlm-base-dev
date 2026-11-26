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

describe('rlmBsgOverview schedule links without numbers', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.restoreAllMocks();
    });

    async function render(data) {
        const el = createElement('c-rlm-bsg-overview', { is: RlmBsgOverview });
        el.recordId = '1Bg000000000001AAA';
        document.body.appendChild(el);
        getBillingScheduleGroupData.emit(data);
        getConsolidatedTimeline.emit(segments(null));
        await flush();
        return el;
    }

    // Pack 452: a milestone-billed group links its schedule by number; a missing number shows a
    // dash, never the record Id.
    it('labels a milestone period\'s schedule link with a dash, not the Id, when the number is missing', async () => {
        const el = await render({
            totalBilledAmount: 0, totalPendingAmount: 100,
            billingSchedules: [{
                id: SCHEDULE_ID, scheduleNumber: null, startDate: '2026-01-01', endDate: '2026-03-31',
                billingTermUnit: 'BillingMilestonePlan', billingTerm: 1, billingPeriodAmount: 100, billedAmount: 0, quantity: 1
            }],
            milestoneItems: [{ id: 'm1', name: 'Kickoff', completionDate: '2026-02-01', amount: 100, status: 'Pending' }]
        });
        const labels = periodScheduleLabels(el);
        expect(labels).toEqual(['—']);
        expect(el.shadowRoot.textContent).not.toContain(SCHEDULE_ID);
    });

    // Two schedules without numbers active in one period: both links render, keyed by their ids
    // (a dash for both labels would otherwise give both the same key).
    it('renders a link per schedule when two schedules in one period have no number', async () => {
        const errors = jest.spyOn(console, 'error').mockImplementation(() => {});
        const schedule = (id) => ({
            id, scheduleNumber: null, startDate: '2026-01-01', endDate: '2026-01-31',
            billingTermUnit: 'Month', billingTerm: 1, billingPeriodAmount: 100, billedAmount: 0, quantity: 1
        });
        const el = await render({
            totalBilledAmount: 0, totalPendingAmount: 200,
            billingSchedules: [schedule('0iB000000000001AAA'), schedule('0iB000000000002AAA')]
        });
        const firstRowLinks = el.shadowRoot.querySelector('.segments-table tbody tr').querySelectorAll('.schedule-table-link');
        expect([...firstRowLinks].map((n) => n.textContent)).toEqual(['—', '—']);
        // LWC reports a repeated for:each key as '[LWC error]: Duplicated "key" attribute value ...'.
        const duplicateKeyErrors = errors.mock.calls.filter((call) => String(call[0]).includes('Duplicated "key"'));
        expect(duplicateKeyErrors).toEqual([]);
    });
});
