import { LightningElement,api } from 'lwc';
import { FlowAttributeChangeEvent } from 'lightning/flowSupport';
import getQuotableCountries from '@salesforce/apex/BillingInformationController.getQuotableCountries';
import validateCurrencySupport from '@salesforce/apex/BillingInformationController.validateCurrencySupport';
const QUOTABLE_COUNTRIES = 'QuotableCountries';

export default class CountryPicklistComponent extends LightningElement {
    _countryOptions;
    _userSelectedCountry;
    _countryComponent;

    //input parameters
    @api countryLabel;
    @api defaultCountry;
    @api countryHelpText;
    @api disableCountry = false;
    @api selectedCurrency;
    @api isCountryFieldRequired;
    @api isHelpTextDisabled;
    @api countryOptionsChoice;

    //output parameters
    @api selectedCountry;

    get countryOptions(){
        return this._countryOptions;
    }

    set countryOptions(option){
        this._countryOptions = option;
    }

    get selectedCountryValue(){
        let selectedCountry = this._userSelectedCountry ? this._userSelectedCountry : this.defaultCountry;
        this.dispatchEvent(new FlowAttributeChangeEvent('selectedCountry', selectedCountry));
        return selectedCountry;
    }

    get displayCountryHelpText(){
        if(!this.isHelpTextDisabled) return this.countryHelpText;
        return null;
    }

    connectedCallback() {
        this.populateCountries();
    }

    async populateCountries() {
        let result;
        if(this.countryOptionsChoice === QUOTABLE_COUNTRIES){
            result = await getQuotableCountries();
        }
        this.countryOptions = result?.map((item) => {
            return { value: item.isoCode, label: `${item.isoCode} - ${item.name}` };
        });
    }

    handleCountryChange(event) {
        this._userSelectedCountry = event.detail.value;
        this.handleCountryComponentValidation();
    }

    renderedCallback() {
        this._countryComponent = this.template.querySelector('[ data-id="countryId" ]');
        this.handleCountryComponentValidation();
    }

    handleCountryComponentValidation() {
        if (this._countryComponent && this.selectedCurrency !== undefined) {
            validateCurrencySupport({ billingCountry: this.selectedCountryValue, billingCurrency: this.selectedCurrency})
            .then(result => {
                if (result) {
                    this._countryComponent.setCustomValidity('');
                    this._countryComponent.reportValidity();
                } else {
                    this._countryComponent.setCustomValidity(`Not compatible with ${this.selectedCurrency}.`);
                    this._countryComponent.reportValidity();
                }
            })
        }
    }
}