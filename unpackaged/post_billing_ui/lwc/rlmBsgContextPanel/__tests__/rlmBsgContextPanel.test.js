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

describe('rlmBsgContextPanel billing arrangement account names', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows "Not available" for a name that could not be read, and a dash only with no account', async () => {
        const el = createElement('c-rlm-bsg-context-panel', { is: RlmBsgContextPanel });
        el.recordId = '1Bg000000000001AAA';
        document.body.appendChild(el);
        getBSGContext.emit({
            viewType: 'standard',
            arrangement: {
                status: 'Active',
                lines: [
                    { lineId: 'L1', accountName: 'Acme', accountNameUnavailable: false, billingPercentage: 50 },
                    { lineId: 'L2', accountName: '—', accountNameUnavailable: true, billingPercentage: 30 },
                    { lineId: 'L3', accountName: '—', accountNameUnavailable: false, billingPercentage: 20 }
                ]
            }
        });
        await flush();

        const accounts = [...el.shadowRoot.querySelectorAll('.arr-info-text > span b:nth-of-type(2)')]
            .map((b) => b.textContent);
        expect(accounts).toEqual(['Acme', 'Not available', '—']);
    });
});
