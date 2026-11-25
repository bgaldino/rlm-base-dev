import { createElement } from 'lwc';
import RlmAccountBalanceCard from 'c/rlmAccountBalanceCard';
import getInvoiceSummary from '@salesforce/apex/RLM_InvoiceSummaryController.getInvoiceSummary';
import getBillingSummary from '@salesforce/apex/RLM_OnAccountBillingController.getBillingSummary';

jest.mock(
    '@salesforce/apex/RLM_InvoiceSummaryController.getInvoiceSummary',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);
jest.mock(
    '@salesforce/apex/RLM_OnAccountBillingController.getBillingSummary',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);

const INVOICE = { totalInvoices: 2, totalDue: 100 };
const BILLING = { totalInvoices: 2, invoiceBalance: 100 };
const REFUSED = { message: 'Billing summary is unavailable.' };

const flush = () => Promise.resolve();
const errorText = (el) => el.shadowRoot.querySelector('.slds-text-color_error')?.textContent;

function mount() {
    const el = createElement('c-rlm-account-balance-card', { is: RlmAccountBalanceCard });
    el.recordId = '001000000000001AAA';
    document.body.appendChild(el);
    return el;
}

describe('rlmAccountBalanceCard wires', () => {
    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
    });

    it('shows the error and no figures while the billing summary is refused', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.error(REFUSED);
        await flush();
        expect(errorText(el)).toBe(REFUSED.message);
        expect(el.shadowRoot.querySelector('.abc-card')).toBeNull();
    });

    it('clears the error and shows the figures when the billing wire then succeeds', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.error(REFUSED);
        await flush();
        getBillingSummary.emit(BILLING);
        await flush();
        expect(errorText(el)).toBeUndefined();
        expect(el.shadowRoot.querySelector('.abc-card')).not.toBeNull();
    });

    it('drops the previous result when the invoice wire then fails', async () => {
        const el = mount();
        getInvoiceSummary.emit(INVOICE);
        getBillingSummary.emit(BILLING);
        await flush();
        expect(el.shadowRoot.querySelector('.abc-card')).not.toBeNull();
        getInvoiceSummary.error({ message: 'Invoice summary is unavailable.' });
        await flush();
        expect(errorText(el)).toBe('Invoice summary is unavailable.');
        expect(el.shadowRoot.querySelector('.abc-card')).toBeNull();
    });
});
