/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// Todo 510: a milestone's accomplishment date is a Salesforce Date ('YYYY-MM-DD'). Read as midnight UTC
// it showed a day early in a browser behind UTC. Each case pins the browser's time zone
// (setBrowserTimeZone, from the environment above).
import { createElement } from 'lwc';
import RlmBsgContextPanel from 'c/rlmBsgContextPanel';
import getBSGContext from '@salesforce/apex/RLM_BSGContextController.getBSGContext';

jest.mock(
    '@salesforce/apex/RLM_BSGContextController.getBSGContext',
    () => {
        const { createApexTestWireAdapter } = jest.requireActual('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);

const flush = () => Promise.resolve();

const ZONES = ['America/Los_Angeles', 'America/New_York', 'Pacific/Honolulu', 'UTC', 'Asia/Tokyo'];

describe.each(ZONES)('rlmBsgContextPanel with the browser in %s', (timeZone) => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows a milestone accomplishment date as stored', async () => {
        setBrowserTimeZone(timeZone);
        const el = createElement('c-rlm-bsg-context-panel', { is: RlmBsgContextPanel });
        el.recordId = '1Bg000000000001AAA';
        document.body.appendChild(el);
        getBSGContext.emit({
            viewType: 'milestone',
            groupBilledAmount: 100, groupPendingAmount: 0,
            milestonePlan: {
                items: [{
                    id: 'm1', name: 'Kickoff', itemType: 'Amount', milestoneAmount: 100, flatAmount: 100,
                    isAccomplished: true, status: 'Invoiced', accomplishmentDate: '2026-01-01'
                }]
            }
        });
        await flush();
        expect([...el.shadowRoot.querySelectorAll('.ms-th-date')].map((n) => n.textContent.trim()))
            .toContain('Jan 1, 2026');
    });
});
