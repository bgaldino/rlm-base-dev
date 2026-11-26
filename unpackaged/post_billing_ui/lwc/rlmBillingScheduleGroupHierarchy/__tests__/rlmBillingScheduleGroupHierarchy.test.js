import { createElement } from 'lwc';
import RlmBillingScheduleGroupHierarchy from 'c/rlmBillingScheduleGroupHierarchy';
import getBillingScheduleGroups from '@salesforce/apex/RLM_BillingScheduleGroupController.getBillingScheduleGroups';
import { getRecord } from 'lightning/uiRecordApi';

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

// Pack 452: UI API and script errors show a fixed sentence, never their own text.
describe('rlmBillingScheduleGroupHierarchy errors', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    const alertText = (el) => el.shadowRoot.querySelector('.slds-alert_error h2')?.textContent;

    it('shows a fixed sentence when the order read fails', async () => {
        jest.spyOn(console, 'error').mockImplementation(() => {});
        const el = createElement('c-rlm-billing-schedule-group-hierarchy', { is: RlmBillingScheduleGroupHierarchy });
        el.recordId = '801000000000001AAA';
        el.objectApiName = 'Order';
        document.body.appendChild(el);
        getRecord.error({ message: "The requested resource does not exist: field 'AccountId' on 'Order'" });
        await flush();
        expect(alertText(el)).toBe('Unable to read this order\'s account, so its billing schedule groups are not shown. Contact your administrator.');
    });

    it('shows a fixed sentence when the groups cannot be processed', async () => {
        jest.spyOn(console, 'error').mockImplementation(() => {});
        getBillingScheduleGroups.mockResolvedValue({ notAList: true });
        const el = createElement('c-rlm-billing-schedule-group-hierarchy', { is: RlmBillingScheduleGroupHierarchy });
        el.recordId = '001000000000001AAA';
        el.objectApiName = 'Account';
        document.body.appendChild(el);
        await flush();
        expect(alertText(el)).toBe('Unable to show the billing schedule groups. Contact your administrator.');
    });
});
