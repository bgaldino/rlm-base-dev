import { createElement } from 'lwc';
import RlmCollectionsConsole from 'c/rlmCollectionsConsole';
import getHighValueDelinquents from '@salesforce/apex/RLM_CollectionsConsoleController.getHighValueDelinquents';

jest.mock(
    '@salesforce/apex/RLM_CollectionsConsoleController.getHighValueDelinquents',
    () => {
        const { createApexTestWireAdapter } = jest.requireActual('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);

const flush = () => Promise.resolve();

describe('rlmCollectionsConsole high value delinquents account names', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows "Not available" for a name that could not be read, and a dash only with no account', async () => {
        const el = createElement('c-rlm-collections-console', { is: RlmCollectionsConsole });
        document.body.appendChild(el);
        getHighValueDelinquents.emit([
            { Id: '3tt000000000001AAA', accountId: '001000000000001AAA', businessAccount: 'Acme', accountNameUnavailable: false },
            { Id: '3tt000000000002AAA', accountId: '001000000000002AAA', businessAccount: '—', accountNameUnavailable: true },
            { Id: '3tt000000000003AAA', accountId: null, businessAccount: '—', accountNameUnavailable: false }
        ]);
        el.shadowRoot.querySelector('#tab-highvalue, [id^="tab-highvalue"]').click();
        await flush();

        const table = [...el.shadowRoot.querySelectorAll('lightning-datatable')]
            .find((t) => t.columns.some((c) => c.label === 'Business Account'));
        const rows = table.data.map((r) => [r.businessAccount, r.accountUrl]);
        expect(rows).toEqual([
            ['Acme', '/001000000000001AAA'],
            ['Not available', '/001000000000002AAA'],
            ['—', '#']
        ]);
    });
});
