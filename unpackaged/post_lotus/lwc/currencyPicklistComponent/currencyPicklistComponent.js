import { LightningElement,api } from 'lwc';
import { FlowAttributeChangeEvent } from 'lightning/flowSupport';

export default class CurrencyPicklistComponent extends LightningElement {
    _userSelectedCurrency
    _currencyOptions;

    //input parameters
    @api defaultCurrency;
    @api currencyHelpText;
    @api disableCurrency;
    @api isCurrencyFieldRequired;
    @api isHelpTextDisabled;
    @api currencyLabel;
    
    //output parameters
    @api selectedCurrency;

    get currencyOptions(){
        return this._currencyOptions;
    }

    set currencyOptions(option){
        this._currencyOptions = option;
    }

    get selectedCurrencyValue(){
        let selectedCurrency = this._userSelectedCurrency ? this._userSelectedCurrency : this.defaultCurrency;
        this.dispatchEvent(new FlowAttributeChangeEvent('selectedCurrency', selectedCurrency));
        return selectedCurrency;
    }

    get displayCurrencyHelpText(){
        if(!this.isHelpTextDisabled) return this.currencyHelpText;
        return null;
    }

    connectedCallback(){
        this.loadDataCurrencyData();
    }

    loadDataCurrencyData(){
        this.currencyOptions = [
            { label: 'AUD - Australian Dollar', value: 'AUD' },
            { label: 'CAD - Canadian Dollar', value: 'CAD' },
            { label: 'EUR - Euro', value: 'EUR' },
            { label: 'GBP - British Pound', value: 'GBP' },
            { label: 'USD - U.S. Dollar', value: 'USD' }
        ];
    }

    handleCurrencyChange(event) {
        this._userSelectedCurrency = event.target.value;
    }
}