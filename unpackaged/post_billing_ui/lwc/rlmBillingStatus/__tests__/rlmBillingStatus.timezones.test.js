/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// Todo 510: the suspension and resumption dates are Salesforce Dates ('YYYY-MM-DD'). Read as midnight
// UTC they showed a day early in a browser behind UTC. Each case pins the browser's time zone
// (setBrowserTimeZone, from the environment above) and the current instant.
import { createElement } from 'lwc';
import RlmBillingStatus from 'c/rlmBillingStatus';
import { graphql } from 'lightning/graphql';

const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

const ZONES = ['America/Los_Angeles', 'America/New_York', 'Pacific/Honolulu', 'UTC', 'Asia/Tokyo'];

describe.each(ZONES)('rlmBillingStatus with the browser in %s', (timeZone) => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.useRealTimers();
    });

    it('shows the suspension dates as stored', async () => {
        setBrowserTimeZone(timeZone);
        jest.useFakeTimers({ now: new Date(2026, 0, 20, 12), doNotFake: ['nextTick', 'queueMicrotask', 'setTimeout', 'clearTimeout'] });
        const el = createElement('c-rlm-billing-status', { is: RlmBillingStatus });
        el.recordId = '001000000000001AAA';
        document.body.appendChild(el);
        graphql.emit({ uiapi: { query: { BillingAccount: { edges: [{ node: {
            Id: '15i000000000001AAA',
            BillingSuspensionDate: { value: '2026-01-01' }, BillingResumptionDate: { value: '2026-02-01' }
        } }] } } } });
        await flush();
        expect(el.shadowRoot.querySelector('.pill-dates').textContent).toBe('Jan 1, 2026 – Feb 1, 2026');
    });
});
