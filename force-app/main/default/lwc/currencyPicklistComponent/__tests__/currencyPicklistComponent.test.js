import { createElement } from 'lwc';
import CurrencyPicklistComponent from 'c/currencyPicklistComponent';


const waitForDOMLifecycle = async () => Promise.resolve;

const createComponentUnderTest = async (setApiFields) => {
    const el = createElement('c-currency-picklist-component', {
        is: CurrencyPicklistComponent
    });
    if (setApiFields) {
        setApiFields(el);
    }
    document.body.appendChild(el);
    await waitForDOMLifecycle();
    return el;
};


describe('c-currency-picklist-component', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });


    it('ensure custom components are created', async () => {
        const component = await createComponentUnderTest((el) => {
            el.currencyLabel = 'Billing Currency';
            el.defaultCurrency = 'US';
            el.currencyHelpText = 'test';
            el.disableCurrency = false;
            el.selectedCurrency = 'USD';
            el.isCurrencyFieldRequired = true;
            el.isHelpTextDisabled = false;
        });
        await waitForDOMLifecycle();
        expect(component).not.toBeNull();
        const countryField = component.shadowRoot.querySelector('[data-id="currencyId"]');
        expect(countryField.value).toBe('US');
    });

});
