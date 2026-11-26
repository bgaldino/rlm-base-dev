import { createElement } from 'lwc';
import RlmBillingScheduleGroupHierarchy from 'c/rlmBillingScheduleGroupHierarchy';
import getBillingScheduleGroups from '@salesforce/apex/RLM_BillingScheduleGroupController.getBillingScheduleGroups';

jest.mock(
    '@salesforce/apex/RLM_BillingScheduleGroupController.getBillingScheduleGroups',
    () => ({ default: jest.fn() }),
    { virtual: true }
);

const REFERENCE_ID = '802000000000001AAA';
const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

async function load(productName) {
    getBillingScheduleGroups.mockResolvedValue([{
        bsg: {
            Id: '1Bg000000000001AAA', ProductName: productName, ReferenceEntityId: REFERENCE_ID,
            BillingTermUnit: 'Month', BillingMethod: 'Recurring', StartDate: '2026-01-01', EndDate: '2026-12-31',
            TotalBilledAmount: 0, TotalPendingAmount: 100, CurrencyIsoCode: 'USD'
        },
        relationships: []
    }]);
    const el = createElement('c-rlm-billing-schedule-group-hierarchy', { is: RlmBillingScheduleGroupHierarchy });
    el.recordId = '001000000000001AAA';
    el.objectApiName = 'Account';
    document.body.appendChild(el);
    await flush();
    return el;
}

const names = (el) => [...el.shadowRoot.querySelectorAll('.bsg-name')].map((n) => n.textContent.trim());

describe('rlmBillingScheduleGroupHierarchy names', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    it('names a group by its product', async () => {
        const el = await load('Widget');
        expect(names(el)).toEqual(['Widget']);
    });

    // Pack 452: a missing product name shows a dash, never the referenced record's Id.
    it('names a group with a dash, not the referenced record Id, when the product name is missing', async () => {
        const el = await load(null);
        expect(names(el)).toEqual(['—']);
    });
});
