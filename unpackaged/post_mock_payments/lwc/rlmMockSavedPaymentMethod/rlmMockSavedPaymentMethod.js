import { LightningElement, api, wire } from 'lwc';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import createMockPaymentMethod from '@salesforce/apex/RLM_MockSavedPaymentMethodController.createMockPaymentMethod';

import ACCOUNT_NAME from '@salesforce/schema/Account.Name';
import BILLING_STREET from '@salesforce/schema/Account.BillingStreet';
import BILLING_CITY from '@salesforce/schema/Account.BillingCity';
import BILLING_STATE from '@salesforce/schema/Account.BillingState';
import BILLING_POSTAL_CODE from '@salesforce/schema/Account.BillingPostalCode';
import BILLING_COUNTRY from '@salesforce/schema/Account.BillingCountry';

const ACCOUNT_FIELDS = [
    ACCOUNT_NAME,
    BILLING_STREET,
    BILLING_CITY,
    BILLING_STATE,
    BILLING_POSTAL_CODE,
    BILLING_COUNTRY
];

export default class RlmMockSavedPaymentMethod extends LightningElement {
    @api recordId;
    @api paymentGatewayId;
    @api paymentGatewayName;
    @api componentTitle = 'Add Payment Method';
    @api submitButtonLabel = 'Save Payment Method';
    @api defaultScenario = 'SUCCESS';
    @api defaultPaymentType = 'CARD';
    @api showPaymentTypeSwitcher = false;
    @api showOutcomeSelector = false;
    @api autoFillBillingAddress = false;

    scenario;
    paymentMethodType = 'CARD';
    accountHolderName = '';
    accountHolderEmail = '';
    saveAsDefault = false;
    cardNumber = '4242424242424242';
    cvv = '123';
    expiryMonth = 12;
    expiryYear = new Date().getFullYear() + 3;
    bankAccountNumber = '000123456789';
    bankRoutingNumber = '000000000';
    bankAccountType = 'Checking';
    bankAccountHolderType = 'Individual';
    billingStreet = '';
    billingCity = '';
    billingState = '';
    billingPostalCode = '';
    billingCountry = 'US';
    isSaving = false;
    accountDefaults = {
        accountHolderName: '',
        billingStreet: '',
        billingCity: '',
        billingState: '',
        billingPostalCode: '',
        billingCountry: 'US'
    };

    scenarioOptions = [
        { label: 'Success', value: 'SUCCESS' },
        { label: 'Decline', value: 'DECLINE' },
        { label: 'Invalid payment method', value: 'INVALID' },
        { label: 'Payment processing error', value: 'ERROR' }
    ];

    paymentMethodTypeOptions = [
        { label: 'Card', value: 'CARD' },
        { label: 'ACH Bank Account', value: 'ACH' }
    ];

    bankAccountTypeOptions = [
        { label: 'Checking', value: 'Checking' },
        { label: 'Savings', value: 'Savings' }
    ];

    bankAccountHolderTypeOptions = [
        { label: 'Individual', value: 'Individual' },
        { label: 'Business', value: 'Business' }
    ];

    get isCard() {
        return this.paymentMethodType === 'CARD';
    }

    get isAch() {
        return this.paymentMethodType === 'ACH';
    }

    get accountHolderNameLabel() {
        return this.isAch ? 'Bank account holder name' : 'Name on card';
    }

    @wire(getRecord, { recordId: '$recordId', fields: ACCOUNT_FIELDS })
    loadAccount({ data }) {
        if (!data || !this.autoFillBillingAddress) return;
        const accountName = getFieldValue(data, ACCOUNT_NAME) || '';
        // Seeded setup accounts often have internal names that should not appear
        // as cardholder-facing data in the payment form.
        const isInternalSeedName = /\b(mock|test|demo)\b/i.test(accountName);
        this.accountDefaults = {
            accountHolderName: isInternalSeedName ? '' : accountName,
            billingStreet: getFieldValue(data, BILLING_STREET) || '',
            billingCity: getFieldValue(data, BILLING_CITY) || '',
            billingState: getFieldValue(data, BILLING_STATE) || '',
            billingPostalCode: getFieldValue(data, BILLING_POSTAL_CODE) || '',
            billingCountry: getFieldValue(data, BILLING_COUNTRY) || 'US'
        };
        Object.keys(this.accountDefaults).forEach((field) => {
            if (!this[field]) this[field] = this.accountDefaults[field];
        });
    }

    get minimumExpiryYear() {
        return new Date().getFullYear();
    }

    get isDisabled() {
        return this.isSaving || !this.recordId || !this.configuredPaymentGateway;
    }

    get needsGatewayConfiguration() {
        return !this.configuredPaymentGateway;
    }

    get configuredPaymentGateway() {
        return this.paymentGatewayId || this.paymentGatewayName;
    }

    connectedCallback() {
        this.scenario = this.defaultScenario || 'SUCCESS';
        this.paymentMethodType = this.defaultPaymentType === 'ACH' ? 'ACH' : 'CARD';
    }

    handleChange(event) {
        const { name, value } = event.target;
        if (event.target.type === 'checkbox') {
            this[name] = event.target.checked;
            return;
        }
        if (name === 'paymentMethodType') {
            this.paymentMethodType = value;
            return;
        }
        this[name] = name === 'expiryMonth' || name === 'expiryYear' ? Number(value) : value;
    }

    handleReset() {
        this.scenario = this.defaultScenario || 'SUCCESS';
        this.paymentMethodType = this.defaultPaymentType === 'ACH' ? 'ACH' : 'CARD';
        this.accountHolderEmail = '';
        this.saveAsDefault = false;
        this.cardNumber = '4242424242424242';
        this.cvv = '123';
        this.expiryMonth = 12;
        this.expiryYear = new Date().getFullYear() + 3;
        this.bankAccountNumber = '000123456789';
        this.bankRoutingNumber = '000000000';
        this.bankAccountType = 'Checking';
        this.bankAccountHolderType = 'Individual';
        this.accountHolderName = this.accountDefaults.accountHolderName;
        this.billingStreet = this.accountDefaults.billingStreet;
        this.billingCity = this.accountDefaults.billingCity;
        this.billingState = this.accountDefaults.billingState;
        this.billingPostalCode = this.accountDefaults.billingPostalCode;
        this.billingCountry = this.accountDefaults.billingCountry || 'US';
    }

    async handleCreate() {
        const inputs = [...this.template.querySelectorAll('lightning-input, lightning-combobox')];
        if (!inputs.reduce((valid, input) => input.reportValidity() && valid, true)) return;

        this.isSaving = true;
        try {
            const methodId = await createMockPaymentMethod({
                accountId: this.recordId,
                paymentGatewayId: this.configuredPaymentGateway,
                paymentMethodType: this.paymentMethodType,
                scenario: this.scenario,
                accountHolderName: this.accountHolderName,
                accountHolderEmail: this.accountHolderEmail,
                saveAsDefault: this.saveAsDefault,
                cardNumber: this.cardNumber,
                cvv: this.cvv,
                expiryMonth: this.expiryMonth,
                expiryYear: this.expiryYear,
                bankAccountNumber: this.bankAccountNumber,
                bankRoutingNumber: this.bankRoutingNumber,
                bankAccountType: this.bankAccountType,
                bankAccountHolderType: this.bankAccountHolderType,
                billingStreet: this.billingStreet,
                billingCity: this.billingCity,
                billingState: this.billingState,
                billingPostalCode: this.billingPostalCode,
                billingCountry: this.billingCountry
            });
            this.dispatchEvent(new ShowToastEvent({
                title: 'Payment method saved',
                message: 'The saved payment method is ready to use.',
                variant: 'success'
            }));
            this.dispatchEvent(new CustomEvent('saved', { detail: { recordId: methodId } }));
        } catch (error) {
            this.dispatchEvent(new ShowToastEvent({
                title: 'Could not create payment method',
                message: error?.body?.message || error.message || 'Unexpected error.',
                variant: 'error'
            }));
        } finally {
            this.cardNumber = '';
            this.cvv = '';
            this.isSaving = false;
        }
    }

    get buttonLabel() {
        return this.isSaving ? 'Saving payment method…' : this.submitButtonLabel;
    }
}
