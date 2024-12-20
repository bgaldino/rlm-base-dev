import { createElement } from 'lwc';
import CountryPicklistComponent from 'c/countryPicklistComponent';
import getQuotableCountries from '@salesforce/apex/BillingInformationController.getQuotableCountries';
import validateCurrencySupport from '@salesforce/apex/BillingInformationController.validateCurrencySupport';

import quotableCountriesJSON from "./data/quotableCountries.json";

jest.mock(
    "@salesforce/apex/BillingInformationController.getQuotableCountries",
    () => ({
        default: jest.fn()
    }),
    { virtual: true }
);
jest.mock(
    "@salesforce/apex/BillingInformationController.validateCurrencySupport",
    () => ({
        default: jest.fn()
    }),
    { virtual: true }
);

const waitForDOMLifecycle = async () => Promise.resolve;

const createComponentUnderTest = async (setApiFields) => {
    const el = createElement('c-country-picklist-component', {
        is: CountryPicklistComponent
    });
    if (setApiFields) {
        setApiFields(el);
    }
    document.body.appendChild(el);
    await waitForDOMLifecycle();
    return el;
};


describe('c-country-picklist-component', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });


    it('ensure custom components are created', async () => {
        getQuotableCountries.mockResolvedValue(quotableCountriesJSON);
        validateCurrencySupport.mockResolvedValue(true);
        const component = await createComponentUnderTest((el) => {
            el.countryLabel = 'Billing Country';
            el.defaultCountry = 'US';
            el.countryHelpText = 'test';
            el.disableCountry = false;
            el.selectedCurrency = 'USD';
            el.isCountryFieldRequired = true;
            el.isHelpTextDisabled = false;
            el.countryOptionsChoice = 'QuotableCountries';
        });
        await waitForDOMLifecycle();
        expect(component).not.toBeNull();
        const countryField = component.shadowRoot.querySelector('[data-id="countryId"]');
        expect(countryField.value).toBe('US');
    });

    it('test onChange country event', async () => {
        getQuotableCountries.mockResolvedValue(quotableCountriesJSON);
        validateCurrencySupport.mockResolvedValue(true);
        const component = await createComponentUnderTest((el) => {
            el.countryLabel = 'Billing Country';
            el.defaultCountry = 'US';
            el.countryHelpText = 'test';
            el.disableCountry = false;
            el.selectedCurrency = 'USD';
            el.isCountryFieldRequired = true;
            el.isHelpTextDisabled = false;
            el.countryOptionsChoice = 'QuotableCountries';
        });
        await waitForDOMLifecycle();
        const countryField = component.shadowRoot.querySelector('[data-id="countryId"]');
        countryField.dispatchEvent(new CustomEvent('change',{detail:{
            "value" : 'AU'
        }}));
        await waitForDOMLifecycle();
        expect(countryField.value).toBe('AU');
    });

    it('test false validation for currency', async () => {
        getQuotableCountries.mockResolvedValue(quotableCountriesJSON);
        validateCurrencySupport.mockResolvedValue(false);
        const component = await createComponentUnderTest((el) => {
            el.countryLabel = 'Billing Country';
            el.defaultCountry = 'US';
            el.countryHelpText = 'test';
            el.disableCountry = false;
            el.selectedCurrency = 'USD1';
            el.isCountryFieldRequired = true;
            el.isHelpTextDisabled = false;
            el.countryOptionsChoice = 'QuotableCountries';
        });
        await waitForDOMLifecycle();
        const countryField = component.shadowRoot.querySelector('[data-id="countryId"]');
        await waitForDOMLifecycle();
        expect(countryField.value).toBe('US');
    });

});
