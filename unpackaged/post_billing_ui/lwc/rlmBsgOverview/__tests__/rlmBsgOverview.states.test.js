// Todo 509: the group and timeline wires answer in either order. The views are built only once both have
// answered for the current record, so a timeline that answers first (even with no segments) no longer
// leaves the Billing Schedules view empty; each wire's error is its own. Also: a monthly schedule that
// starts on the 29th-31st bills in every month, its day clamped to the month's length.
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

function bsgData(startDate, endDate, scheduleNumber = 'BS-0001') {
    return {
        totalBilledAmount: 0, totalPendingAmount: 300,
        billingSchedules: [{
            id: SCHEDULE_ID, scheduleNumber, status: 'Active', category: 'Original', startDate, endDate,
            billingTermUnit: 'Month', billingTerm: 1, billingPeriodAmount: 100, billedAmount: 0, quantity: 1
        }]
    };
}
function segments(startDate, endDate) {
    return [{
        periodNumber: 1, startDate, endDate, status: 'Active', netQuantity: 1, periodicBilling: 100, credits: 0,
        activeScheduleIds: [SCHEDULE_ID], activeScheduleNumbers: ['BS-0001']
    }];
}

function mount(recordId = '1Bg000000000001AAA') {
    const el = createElement('c-rlm-bsg-overview', { is: RlmBsgOverview });
    el.recordId = recordId;
    document.body.appendChild(el);
    return el;
}

async function showSchedules(el) {
    el.shadowRoot.querySelectorAll('lightning-button')
        .forEach((b) => { if (b.label === 'Billing Schedules') b.click(); });
    await flush();
}

const ganttLinks = (el) => el.shadowRoot.querySelectorAll('lightning-button.schedule-link').length;
// Each period row as [period, schedules].
const periodRows = (el) => [...el.shadowRoot.querySelectorAll('.segments-table tbody tr')]
    .map((tr) => [...tr.querySelectorAll('td')].map((td) => td.textContent.trim()))
    .map((cells) => [cells[0], cells[4]]);

describe('rlmBsgOverview wire order and record changes', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('charts the schedules when an empty timeline answers before the group', async () => {
        const el = mount();
        getConsolidatedTimeline.emit([]);
        await flush();
        getBillingScheduleGroupData.emit(bsgData('2026-01-01', '2026-03-31'));
        await flush();
        await showSchedules(el);
        expect(ganttLinks(el)).toBe(1);
    });

    it('keeps the group error when the timeline answers after it', async () => {
        const el = mount();
        getBillingScheduleGroupData.error({ message: 'Billing Schedule Group not found' });
        await flush();
        getConsolidatedTimeline.emit(segments('2026-01-01', '2026-03-31'));
        await flush();
        expect(el.shadowRoot.querySelector('.slds-text-color_error')).not.toBeNull();
    });

    it("does not chart the previous record's group with the next record's timeline", async () => {
        const el = mount();
        getBillingScheduleGroupData.emit(bsgData('2026-01-01', '2026-03-31'));
        getConsolidatedTimeline.emit(segments('2026-01-01', '2026-03-31'));
        await flush();
        expect(periodRows(el).length).toBe(3);
        el.recordId = '1Bg000000000002AAA';
        await flush();
        getConsolidatedTimeline.emit([]);
        await flush();
        expect(periodRows(el)).toEqual([]);
        expect(el.shadowRoot.querySelector('lightning-spinner')).not.toBeNull();
    });
});

describe('rlmBsgOverview month-end schedules', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    async function load(startDate, endDate) {
        const el = mount();
        getBillingScheduleGroupData.emit(bsgData(startDate, endDate));
        getConsolidatedTimeline.emit(segments(startDate, endDate));
        await flush();
        return el;
    }

    it('bills a schedule starting January 31 in February', async () => {
        const el = await load('2026-01-31', '2026-04-29');
        expect(periodRows(el)).toEqual([
            ["Jan '26", 'BS-0001'],
            ["Feb '26", 'BS-0001'],
            ["Mar '26", 'BS-0001'],
            ["Apr '26", '']
        ]);
    });

    it('counts each billing date from the start, so a clamped February does not move later months', async () => {
        // Billing dates Jan 31, Feb 28, Mar 31, Apr 30; May 31 is after the end, so May has none.
        const el = await load('2026-01-31', '2026-05-30');
        expect(periodRows(el).map((row) => row[1])).toEqual(['BS-0001', 'BS-0001', 'BS-0001', 'BS-0001', '']);
    });
});
