import { LightningElement, api, wire } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { CloseActionScreenEvent } from 'lightning/actions';

import getAccountBillingInfo from '@salesforce/apex/RLM_BillingScheduleGroupService.getAccountBillingInfo';
import getLegalEntities from '@salesforce/apex/RLM_BillingScheduleGroupService.getLegalEntities';
import getTaxTreatments from '@salesforce/apex/RLM_BillingScheduleGroupService.getTaxTreatments';
import getProducts from '@salesforce/apex/RLM_BillingScheduleGroupService.getProducts';
import createBillingScheduleGroupAndScheduleViaAPI from '@salesforce/apex/RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI';

export default class RlmBillingScheduleGroupModal extends LightningElement {
    @api recordId; // Account Id

    accountName;
    billingAccountId;
    billingAccountName;
    billingCity;

    isLoading = true; // Start as loading while we fetch account data
    legalEntityOptions = [];
    taxTreatmentOptions = [];
    productOptions = [];

    billingTermUnitPicklist; // BillingScheduleGroup.BillingTermUnitPicklist
    billingTerm; // BillingScheduleGroup.BillingTerm (numeric; required for Month/Year)
    billingTypePicklistTiming;
    legalEntityId;

    quantity = 1; // BillingSchedule.Quantity - defaults to 1
    taxTreatmentId; // BillingSchedule.TaxTreatmentId
    currencyIsoCode = 'USD'; // CurrencyIsoCode__std - defaults to USD
    unitPrice = 0; // UnitPrice__std - defaults to 0
    totalPrice = 0; // TotalPrice__std - defaults to 0
    productId; // Product2 Id
    productName; // ProductName__std
    startDate; // StartDate__std (defaults to today)
    billingDayOfMonth; // BillingDayOfMonth__std (defaults to today's day)
    billingStartMonth; // BillingStartMonth__std (defaults to current month)
    chargeType; // "One Time" or "Recurring"
    termSetting = 'Evergreen'; // "Evergreen" or "Termed" - defaults to Evergreen
    termDuration = 1; // Number of periods for termed contracts - defaults to 1
    termDurationUnit = 'Year'; // Unit for term duration - defaults to Year
    endDate; // Calculated end date for termed contracts
    numberOfBillingPeriods = 0; // Calculated number of billing periods for termed contracts

    chargeTypeOptions = [
        { label: 'One Time', value: 'OneTime' },
        { label: 'Recurring', value: 'Recurring' }
    ];

    billingFrequencyOptions = [
        { label: 'Month', value: 'Month' },
        { label: 'Quarter', value: 'Quarter' },
        { label: 'Semi-Annual', value: 'Semi-Annual' },
        { label: 'Year', value: 'Year' }
    ];

    billingTimingOptions = [
        { label: 'Advance', value: 'Advance' },
        { label: 'Arrears', value: 'Arrears' }
    ];

    termSettingOptions = [
        { label: 'Evergreen', value: 'Evergreen' },
        { label: 'Termed', value: 'Termed' }
    ];

    termDurationUnitOptions = [
        { label: 'Month', value: 'Month' },
        { label: 'Quarter', value: 'Quarter' },
        { label: 'Semi-Annual', value: 'Semi-Annual' },
        { label: 'Year', value: 'Year' }
    ];

    currencyOptions = [
        { label: 'USD - US Dollar', value: 'USD' },
        { label: 'EUR - Euro', value: 'EUR' },
        { label: 'GBP - British Pound', value: 'GBP' },
        { label: 'CAD - Canadian Dollar', value: 'CAD' },
        { label: 'AUD - Australian Dollar', value: 'AUD' },
        { label: 'JPY - Japanese Yen', value: 'JPY' }
    ];

    get currencyFormatter() {
        const formatters = {
            USD: { currency: 'USD', symbol: '$', decimals: 2 },
            EUR: { currency: 'EUR', symbol: '\u20AC', decimals: 2 },
            GBP: { currency: 'GBP', symbol: '\u00A3', decimals: 2 },
            CAD: { currency: 'CAD', symbol: 'C$', decimals: 2 },
            AUD: { currency: 'AUD', symbol: 'A$', decimals: 2 },
            JPY: { currency: 'JPY', symbol: '\u00A5', decimals: 0 }
        };
        return formatters[this.currencyIsoCode] || formatters.USD;
    }

    get currencyStep() {
        const formatter = this.currencyFormatter;
        return formatter.decimals === 0 ? '1' : '0.01';
    }

    get currencySymbol() {
        return this.currencyFormatter.symbol;
    }

    get unitPriceLabel() {
        return `Unit Price (${this.currencySymbol})`;
    }

    get totalPriceLabel() {
        return `Total Price (${this.currencySymbol})`;
    }

    get formattedUnitPrice() {
        if (this.unitPrice === undefined || this.unitPrice === null) return this.unitPrice;
        const formatter = this.currencyFormatter;
        return Number(this.unitPrice.toFixed(formatter.decimals));
    }

    get formattedTotalPrice() {
        if (this.totalPrice === undefined || this.totalPrice === null) return this.totalPrice;
        const formatter = this.currencyFormatter;
        return Number(this.totalPrice.toFixed(formatter.decimals));
    }

    connectedCallback() {
        // Set default values for date fields
        const today = new Date();
        this.startDate = today.toISOString().split('T')[0]; // YYYY-MM-DD format
        this.billingDayOfMonth = today.getDate();
        this.billingStartMonth = today.getMonth() + 1; // JavaScript months are 0-indexed
        // Calculate initial end date with defaults
        this.calculateEndDate();
    }

    @wire(getAccountBillingInfo, { accountId: '$recordId' })
    wiredAccountInfo({ error, data }) {
        if (data) {
            this.accountName = data.accountName;
            this.billingAccountId = data.billingAccountId;
            this.billingAccountName = data.billingAccountName;
            this.billingCity = data.billingCity;

            if (!this.billingAccountId) {
                this.dispatchEvent(
                    new ShowToastEvent({
                        title: 'No Billing Account',
                        message: 'This Account does not have an associated Billing Account.',
                        variant: 'warning'
                    })
                );
            }
            this.isLoading = false;
        } else if (error) {
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Error loading Account',
                    message: this.reduceError(error),
                    variant: 'error'
                })
            );
            this.isLoading = false;
        }
    }

    @wire(getLegalEntities)
    wiredLegalEntities({ error, data }) {
        if (data) {
            this.legalEntityOptions = data.map((le) => ({
                label: le.name,
                value: le.id
            }));
        } else if (error) {
            this.legalEntityOptions = [];
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Error loading Legal Entities',
                    message: this.reduceError(error),
                    variant: 'error'
                })
            );
        }
    }

    @wire(getTaxTreatments)
    wiredTaxTreatments({ error, data }) {
        if (data) {
            this.taxTreatmentOptions = data.map((tt) => ({
                label: tt.name,
                value: tt.id
            }));
        } else if (error) {
            this.taxTreatmentOptions = [];
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Error loading Tax Treatments',
                    message: this.reduceError(error),
                    variant: 'error'
                })
            );
        }
    }

    @wire(getProducts)
    wiredProducts({ error, data }) {
        if (data) {
            this.productOptions = data.map((prod) => ({
                label: prod.name,
                value: prod.id
            }));
        } else if (error) {
            this.productOptions = [];
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Error loading Products',
                    message: this.reduceError(error),
                    variant: 'error'
                })
            );
        }
    }

    get isCreateDisabled() {
        return (
            !this.billingAccountId ||
            !this.chargeType ||
            (this.isRecurring && !this.billingTermUnitPicklist) ||
            (this.isRecurring && !this.billingTypePicklistTiming) ||
            (this.isTermed && !this.isValidBillingFrequency) ||
            this.quantity === undefined ||
            this.quantity === null ||
            !this.legalEntityId ||
            !this.taxTreatmentId ||
            !this.currencyIsoCode ||
            this.unitPrice === undefined ||
            this.unitPrice === null ||
            !this.productId ||
            !this.startDate ||
            !this.billingDayOfMonth ||
            !this.billingStartMonth
        );
    }

    get isRecurring() {
        return this.chargeType === 'Recurring';
    }

    get isTermed() {
        return this.termSetting === 'Termed' && this.isRecurring;
    }

    get isValidBillingFrequency() {
        if (!this.isTermed || !this.billingTermUnitPicklist || !this.termDurationUnit) {
            return true;
        }

        // Get months for each period type
        const periodMonths = {
            Month: 1,
            Quarter: 3,
            'Semi-Annual': 6,
            Year: 12
        };

        const billingMonths = periodMonths[this.billingTermUnitPicklist] || 0;
        const termMonths = periodMonths[this.termDurationUnit] || 0;

        // Billing frequency cannot be larger than term duration
        return billingMonths <= termMonths;
    }

    get billingFrequencyErrorMessage() {
        if (!this.isValidBillingFrequency) {
            return `Billing Frequency cannot be larger than Term Duration Period (${this.termDurationUnit})`;
        }
        return '';
    }

    handleChargeTypeChange(event) {
        this.chargeType = event.detail.value;
        if (this.chargeType === 'OneTime') {
            this.billingTermUnitPicklist = 'OneTime';
        } else {
            this.billingTermUnitPicklist = undefined;
        }
    }

    handleBillingFrequencyChange(event) {
        this.billingTermUnitPicklist = event.detail.value;
        // Recalculate number of billing periods when frequency changes
        this.calculateEndDate();
    }

    handleTermSettingChange(event) {
        this.termSetting = event.detail.value;
        // Recalculate end date when term setting changes
        this.calculateEndDate();
    }

    handleTermDurationChange(event) {
        const raw = event.detail.value;
        const parsed = raw === '' || raw === null || raw === undefined ? undefined : Number(raw);
        this.termDuration = Number.isFinite(parsed) ? parsed : undefined;
        this.calculateEndDate();
    }

    handleTermDurationUnitChange(event) {
        this.termDurationUnit = event.detail.value;
        this.calculateEndDate();
    }

    calculateEndDate() {
        if (!this.startDate || !this.termDuration || !this.termDurationUnit || !this.isTermed) {
            this.endDate = null;
            this.numberOfBillingPeriods = 0;
            return;
        }

        const start = new Date(this.startDate + 'T00:00:00');
        let monthsToAdd = 0;

        switch (this.termDurationUnit) {
            case 'Month':
                monthsToAdd = this.termDuration;
                break;
            case 'Quarter':
                monthsToAdd = this.termDuration * 3;
                break;
            case 'Semi-Annual':
                monthsToAdd = this.termDuration * 6;
                break;
            case 'Year':
                monthsToAdd = this.termDuration * 12;
                break;
            default:
                monthsToAdd = 0;
        }

        const end = new Date(start);
        end.setMonth(end.getMonth() + monthsToAdd);
        // Subtract one day to get the last day of the term
        end.setDate(end.getDate() - 1);

        this.endDate = end.toISOString().split('T')[0];

        // Calculate number of billing periods
        this.calculateNumberOfBillingPeriods(monthsToAdd);
    }

    calculateNumberOfBillingPeriods(totalMonths) {
        if (!this.isTermed || !this.billingTermUnitPicklist) {
            this.numberOfBillingPeriods = 0;
            return;
        }

        const periodMonths = {
            Month: 1,
            Quarter: 3,
            'Semi-Annual': 6,
            Year: 12
        };

        const billingPeriodMonths = periodMonths[this.billingTermUnitPicklist] || 1;
        this.numberOfBillingPeriods = Math.floor(totalMonths / billingPeriodMonths);

        // Recalculate total price with the new number of billing periods
        this.recalculatePrices();
    }

    recalculatePrices() {
        if (this.isTermed && this.numberOfBillingPeriods > 0 && this.quantity && this.unitPrice !== undefined) {
            this.totalPrice = this.quantity * this.unitPrice * this.numberOfBillingPeriods;
        }
    }

    handleQuantityChange(event) {
        const raw = event.detail.value;
        const parsed = raw === '' || raw === null || raw === undefined ? undefined : Number(raw);
        this.quantity = Number.isFinite(parsed) ? parsed : undefined;
        // Recalculate total price when quantity changes
        if (this.quantity && this.unitPrice !== undefined) {
            if (this.isTermed && this.numberOfBillingPeriods > 0) {
                this.totalPrice = this.quantity * this.unitPrice * this.numberOfBillingPeriods;
            } else {
                this.totalPrice = this.quantity * this.unitPrice;
            }
        }
    }

    handleUnitPriceChange(event) {
        const raw = event.detail.value;
        const parsed = raw === '' || raw === null || raw === undefined ? undefined : Number(raw);
        this.unitPrice = Number.isFinite(parsed) ? parsed : undefined;
        // Recalculate total price when unit price changes
        if (this.quantity && this.unitPrice !== undefined) {
            if (this.isTermed && this.numberOfBillingPeriods > 0) {
                this.totalPrice = this.quantity * this.unitPrice * this.numberOfBillingPeriods;
            } else {
                this.totalPrice = this.quantity * this.unitPrice;
            }
        }
    }

    handleTotalPriceChange(event) {
        const raw = event.detail.value;
        const parsed = raw === '' || raw === null || raw === undefined ? undefined : Number(raw);
        this.totalPrice = Number.isFinite(parsed) ? parsed : undefined;
        // Recalculate unit price when total price changes
        if (this.totalPrice !== undefined && this.quantity && this.quantity !== 0) {
            if (this.isTermed && this.numberOfBillingPeriods > 0) {
                this.unitPrice = this.totalPrice / (this.numberOfBillingPeriods * this.quantity);
            } else {
                this.unitPrice = this.totalPrice / this.quantity;
            }
        }
    }

    handleBillingTimingChange(event) {
        this.billingTypePicklistTiming = event.detail.value;
    }

    handleLegalEntityChange(event) {
        this.legalEntityId = event.detail.value;
    }

    handleTaxTreatmentChange(event) {
        this.taxTreatmentId = event.detail.value;
    }

    handleCurrencyChange(event) {
        this.currencyIsoCode = event.detail.value;
        // Round prices to correct decimal places when currency changes
        const formatter = this.currencyFormatter;
        if (this.unitPrice !== undefined && this.unitPrice !== null) {
            this.unitPrice = Number(this.unitPrice.toFixed(formatter.decimals));
        }
        if (this.totalPrice !== undefined && this.totalPrice !== null) {
            this.totalPrice = Number(this.totalPrice.toFixed(formatter.decimals));
        }
    }

    handleProductChange(event) {
        this.productId = event.detail.value;
        // Find the selected product name
        const selectedProduct = this.productOptions.find((opt) => opt.value === this.productId);
        this.productName = selectedProduct ? selectedProduct.label : '';
    }

    handleStartDateChange(event) {
        this.startDate = event.detail.value;
        // Update billing day and month based on start date
        if (this.startDate) {
            const selectedDate = new Date(this.startDate + 'T00:00:00');
            this.billingDayOfMonth = selectedDate.getDate();
            this.billingStartMonth = selectedDate.getMonth() + 1; // JavaScript months are 0-indexed
        }
        // Recalculate end date when start date changes
        this.calculateEndDate();
    }

    handleCancel() {
        this.dispatchEvent(new CloseActionScreenEvent());
    }

    async handleCreate() {
        this.isLoading = true;
        try {
            // Invoke the standard Create Standalone Billing Schedules action natively (async).
            const result = await createBillingScheduleGroupAndScheduleViaAPI({
                billingAccountId: this.billingAccountId,
                billingTermUnitPicklist: this.billingTermUnitPicklist,
                billingTerm: this.billingTerm,
                billingTypePicklistTiming: this.billingTypePicklistTiming,
                quantity: this.quantity,
                legalEntityId: this.legalEntityId,
                taxTreatmentId: this.taxTreatmentId,
                currencyIsoCode: this.currencyIsoCode,
                unitPrice: this.unitPrice,
                totalPrice: this.totalPrice,
                billingCity: this.billingCity,
                productId: this.productId,
                productName: this.productName,
                startDate: this.startDate,
                billingDayOfMonth: this.billingDayOfMonth,
                billingStartMonth: this.billingStartMonth,
                termSetting: this.termSetting,
                endDate: this.endDate
            });

            const reference = result && result.requestId ? ` (request ${result.requestId})` : '';
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Billing Schedule Generation Submitted',
                    message: `Billing schedule generation was submitted for processing${reference}.`,
                    variant: 'success'
                })
            );

            this.dispatchEvent(new CloseActionScreenEvent());
        } catch (e) {
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Error creating Billing Schedule Group',
                    message: this.reduceError(e),
                    variant: 'error'
                })
            );
        } finally {
            this.isLoading = false;
        }
    }

    reduceError(error) {
        // Best-effort error message parsing across common Salesforce/LWC error shapes.
        if (!error) return 'Unknown error';
        if (Array.isArray(error.body)) return error.body.map((x) => x.message).join(', ');
        if (error.body && typeof error.body.message === 'string') return error.body.message;
        if (typeof error.message === 'string') return error.message;
        return JSON.stringify(error);
    }
}
