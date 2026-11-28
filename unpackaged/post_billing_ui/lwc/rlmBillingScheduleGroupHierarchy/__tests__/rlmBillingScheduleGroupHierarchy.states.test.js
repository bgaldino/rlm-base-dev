// Todo 509: refused reads and record changes. The Order's account (Order pages) and the groups are each
// loading until their own reply, then ready or unavailable; a refused read shows only its fixed sentence,
// never the platform's text; a record change starts over and drops every reply for an earlier request.
// getRecord.emit() and .error() are the sfdx-lwc-jest test adapter's API, not wire calls in a component.
/* eslint-disable @lwc/lwc/no-unexpected-wire-adapter-usages */
import { createElement } from 'lwc';
import RlmBillingScheduleGroupHierarchy from 'c/rlmBillingScheduleGroupHierarchy';
import getBillingScheduleGroups from '@salesforce/apex/RLM_BillingScheduleGroupController.getBillingScheduleGroups';
import { getRecord } from 'lightning/uiRecordApi';

jest.mock(
    '@salesforce/apex/RLM_BillingScheduleGroupController.getBillingScheduleGroups',
    () => ({ default: jest.fn() }),
    { virtual: true }
);

const ORDER_SENTENCE = 'Unable to read this order, so its billing schedule groups are not shown. Contact your administrator.';
const GROUPS_SENTENCE = 'Unable to show the billing schedule groups. Contact your administrator.';
const RAW = 'Insufficient access rights on cross-reference id';
const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

const group = (name, currency = 'USD') => ({ bsg: {
    Id: '1Bg000000000001AAA', ProductName: name, BillingTermUnit: 'Month', BillingMethod: 'Recurring',
    StartDate: '2026-01-01', EndDate: '2026-12-31', TotalBilledAmount: 0, TotalPendingAmount: 100, CurrencyIsoCode: currency
}, relationships: [] });
const orderRecord = (id, accountId) => ({ apiName: 'Order', id, fields: { AccountId: { value: accountId } } });

// Each groups request held until the test answers it, in call order.
function holdGroups() {
    const pending = [];
    getBillingScheduleGroups.mockImplementation(() => new Promise((resolve, reject) => pending.push({ resolve, reject })));
    return pending;
}

function mount(objectApiName, recordId) {
    const el = createElement('c-rlm-billing-schedule-group-hierarchy', { is: RlmBillingScheduleGroupHierarchy });
    el.recordId = recordId;
    el.objectApiName = objectApiName;
    document.body.appendChild(el);
    return el;
}

const alertText = (el) => el.shadowRoot.querySelector('.slds-alert_error h2')?.textContent;
const names = (el) => [...el.shadowRoot.querySelectorAll('.bsg-name')].map((n) => n.textContent.trim());
const spinner = (el) => !!el.shadowRoot.querySelector('lightning-spinner');
const text = (el) => el.shadowRoot.textContent;
const summary = (el) => el.shadowRoot.querySelector('.header-summary').textContent;

describe('rlmBillingScheduleGroupHierarchy refused reads and record changes', () => {
    beforeEach(() => jest.spyOn(console, 'error').mockImplementation(() => {}));
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.clearAllMocks();
    });

    it('shows the fixed sentence, not the platform text, when the groups read is refused', async () => {
        const pending = holdGroups();
        const el = mount('Account', '001000000000001AAA');
        await flush();
        pending[0].reject({ body: { message: RAW } });
        await flush();
        expect(alertText(el)).toBe(GROUPS_SENTENCE);
        expect(text(el)).not.toContain(RAW);
        expect(summary(el)).toBe('');
    });

    it('shows the fixed sentence, not the error text, when the groups cannot be processed', async () => {
        const pending = holdGroups();
        const el = mount('Account', '001000000000001AAA');
        await flush();
        pending[0].resolve({ notAList: true });
        await flush();
        expect(alertText(el)).toBe(GROUPS_SENTENCE);
        expect(text(el)).not.toContain('forEach');
    });

    it('shows the fixed sentence, not the platform text, when the order read is refused', async () => {
        holdGroups();
        const el = mount('Order', '801000000000001AAA');
        await flush();
        getRecord.error({ message: RAW });
        await flush();
        expect(alertText(el)).toBe(ORDER_SENTENCE);
        expect(text(el)).not.toContain('Error loading record');
    });

    it('keeps the order sentence when a groups reply in flight arrives after the order read fails', async () => {
        const pending = holdGroups();
        const el = mount('Order', '801000000000001AAA');
        getRecord.emit(orderRecord('801000000000001AAA', '001000000000001AAA'));
        await flush();
        getRecord.error({ message: RAW });
        await flush();
        pending[0].resolve([group('Widget')]);
        await flush();
        expect(alertText(el)).toBe(ORDER_SENTENCE);
        expect(names(el)).toEqual([]);
    });

    it('clears the order sentence as soon as the order reads again, with the spinner until the groups return', async () => {
        holdGroups();
        const el = mount('Order', '801000000000001AAA');
        getRecord.error({ message: RAW });
        await flush();
        getRecord.emit(orderRecord('801000000000001AAA', '001000000000001AAA'));
        await flush();
        expect(alertText(el)).toBeUndefined();
        expect(spinner(el)).toBe(true);
    });

    it('reads the groups again when the order recovers after a failure that dropped their reply', async () => {
        const pending = holdGroups();
        const el = mount('Order', '801000000000001AAA');
        getRecord.emit(orderRecord('801000000000001AAA', '001000000000001AAA'));
        await flush();
        getRecord.error({ message: RAW });
        await flush();
        getRecord.emit(orderRecord('801000000000001AAA', '001000000000001AAA'));
        await flush();
        expect(getBillingScheduleGroups).toHaveBeenCalledTimes(2);
        pending[0].resolve([group('Dropped')]);
        pending[1].resolve([group('Widget')]);
        await flush();
        expect(names(el)).toEqual(['Widget']);
    });

    it('reads the new account after an account change, with the spinner only', async () => {
        const pending = holdGroups();
        const el = mount('Account', '001000000000001AAA');
        await flush();
        pending[0].resolve([group('Old')]);
        await flush();
        expect(names(el)).toEqual(['Old']);
        el.recordId = '001000000000002AAA';
        await flush();
        expect(getBillingScheduleGroups).toHaveBeenLastCalledWith({ accountId: '001000000000002AAA' });
        expect(names(el)).toEqual([]);
        expect(el.shadowRoot.querySelector('.charge-type-tabs')).toBeNull();
        expect(spinner(el)).toBe(true);
    });

    it('clears the previous account\'s sentence on an account change', async () => {
        const pending = holdGroups();
        const el = mount('Account', '001000000000001AAA');
        await flush();
        pending[0].reject({ body: { message: RAW } });
        await flush();
        expect(alertText(el)).toBe(GROUPS_SENTENCE);
        el.recordId = '001000000000002AAA';
        await flush();
        expect(alertText(el)).toBeUndefined();
    });

    it('drops a success or a failure for the previous account', async () => {
        const pending = holdGroups();
        const el = mount('Account', '001000000000001AAA');
        await flush();
        el.recordId = '001000000000002AAA';
        await flush();
        pending[1].resolve([group('New')]);
        await flush();
        pending[0].resolve([group('Old')]);
        await flush();
        expect(names(el)).toEqual(['New']);
        pending[0].reject({ body: { message: RAW } });
        await flush();
        expect(alertText(el)).toBeUndefined();
    });

    it('drops a failure for the previous order of the same account', async () => {
        const pending = holdGroups();
        const el = mount('Order', '801000000000001AAA');
        getRecord.emit(orderRecord('801000000000001AAA', '001000000000001AAA'));
        await flush();
        el.recordId = '801000000000002AAA';
        await flush();
        getRecord.emit(orderRecord('801000000000002AAA', '001000000000001AAA'));
        await flush();
        pending[1].resolve([group('New')]);
        await flush();
        pending[0].reject({ body: { message: RAW } });
        await flush();
        expect(alertText(el)).toBeUndefined();
        expect(names(el)).toEqual(['New']);
    });

    it('shows the spinner, not "No Billing Schedule Groups", after an order change', async () => {
        const pending = holdGroups();
        const el = mount('Order', '801000000000001AAA');
        getRecord.emit(orderRecord('801000000000001AAA', '001000000000001AAA'));
        await flush();
        pending[0].resolve([group('Done')]);
        await flush();
        el.recordId = '801000000000002AAA';
        await flush();
        expect(text(el)).not.toContain('No Billing Schedule Groups');
        expect(names(el)).toEqual([]);
        expect(spinner(el)).toBe(true);
    });

    it("shows the new account's currency after an account change", async () => {
        const pending = holdGroups();
        const el = mount('Account', '001000000000001AAA');
        await flush();
        pending[0].resolve([group('Euro', 'EUR')]);
        await flush();
        expect(summary(el)).toContain('€');
        el.recordId = '001000000000002AAA';
        await flush();
        pending[1].resolve([group('Dollar', 'USD')]);
        await flush();
        expect(summary(el)).toContain('$');
        expect(summary(el)).not.toContain('€');
    });
});
