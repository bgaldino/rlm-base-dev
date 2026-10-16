import { LightningElement, api, wire } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import getSavedPaymentMethods from '@salesforce/apex/RLM_MockPaymentSaleController.getSavedPaymentMethods';
import createPaymentSale from '@salesforce/apex/RLM_MockPaymentSaleController.createPaymentSale';

export default class RlmMockPaymentSale extends LightningElement {
    @api recordId;
    @api paymentGatewayId;
    @api paymentGatewayName;
    @api componentTitle = 'Payment Sale';
    @api submitButtonLabel = 'Create Payment';
    @api defaultPaymentType = 'CARD';
    @api showPaymentTypeSwitcher = false;
    @api defaultAmount = '1.00';

    allMethods = [];
    selectedMethodId;
    amount = '1.00';
    paymentTypeFilter = 'CARD';
    currencyIsoCode;
    loadError;
    saleError;
    saleResult;
    isLoadingMethods = true;
    isSubmitting = false;
    wiredMethodsResult;

    paymentTypeOptions = [
        { label: 'Card', value: 'CARD' },
        { label: 'ACH Bank Account', value: 'ACH' }
    ];

    @wire(getSavedPaymentMethods, {
        accountId: '$recordId',
        paymentGatewayId: '$configuredPaymentGateway'
    })
    wiredMethods(result) {
        this.wiredMethodsResult = result;
        this.isLoadingMethods = false;
        if (result.data) {
            this.allMethods = result.data.map((method) => ({
                label: method.label,
                value: method.id,
                paymentType: method.paymentType === 'us_bank_account' ? 'ACH' : 'CARD'
            }));
            this.currencyIsoCode = result.data[0]?.currencyIsoCode;
            this.selectAvailableMethod();
            this.loadError = undefined;
        } else if (result.error) {
            this.allMethods = [];
            this.loadError = this.reduceError(result.error);
        }
    }

    connectedCallback() {
        this.paymentTypeFilter = this.defaultPaymentType === 'ACH' ? 'ACH' : 'CARD';
        this.amount = this.defaultAmount || '1.00';
    }

    get methodOptions() {
        return this.allMethods
            .filter((method) => method.paymentType === this.paymentTypeFilter)
            .map(({ label, value }) => ({ label, value }));
    }

    get hasMethods() {
        return this.methodOptions.length > 0;
    }

    get isSaleDisabled() {
        return this.isSubmitting || !this.selectedMethodId || !this.amount || Number(this.amount) <= 0;
    }

    get needsGatewayConfiguration() {
        return !this.configuredPaymentGateway;
    }

    get configuredPaymentGateway() {
        return this.paymentGatewayId || this.paymentGatewayName;
    }

    get paymentTypeLabel() {
        return this.paymentTypeFilter === 'ACH' ? 'ACH bank account' : 'card';
    }

    get buttonLabel() {
        return this.isSubmitting ? 'Submitting payment…' : this.submitButtonLabel;
    }

    get paymentUrl() {
        return this.saleResult?.paymentId ? `/${this.saleResult.paymentId}` : undefined;
    }

    get saleResultClass() {
        const outcomeClass = this.saleResult?.status === 'Processed'
            ? 'slds-alert_success'
            : 'slds-alert_warning';
        return `slds-notify slds-notify_alert ${outcomeClass} slds-var-m-top_medium`;
    }

    handleMethodChange(event) {
        this.selectedMethodId = event.detail.value;
        this.saleResult = undefined;
        this.saleError = undefined;
    }

    handlePaymentTypeChange(event) {
        this.paymentTypeFilter = event.detail.value;
        this.selectAvailableMethod();
        this.saleResult = undefined;
        this.saleError = undefined;
    }

    selectAvailableMethod() {
        const currentIsAvailable = this.methodOptions.some(
            (option) => option.value === this.selectedMethodId
        );
        if (!currentIsAvailable) {
            this.selectedMethodId = this.methodOptions[0]?.value;
        }
    }

    handleAmountChange(event) {
        this.amount = event.detail.value;
        this.saleResult = undefined;
        this.saleError = undefined;
    }

    async handleSale() {
        this.isSubmitting = true;
        this.saleError = undefined;
        this.saleResult = undefined;
        try {
            this.saleResult = await createPaymentSale({
                accountId: this.recordId,
                paymentGatewayId: this.configuredPaymentGateway,
                savedPaymentMethodId: this.selectedMethodId,
                amount: Number(this.amount)
            });
            this.dispatchEvent(
                new ShowToastEvent({
                    title: this.saleResult.status === 'Processed'
                        ? 'Payment processed'
                        : 'Payment created',
                    message: `${this.saleResult.paymentNumber} · ${this.saleResult.status}`,
                    variant: this.saleResult.status === 'Processed' ? 'success' : 'warning'
                })
            );
            await refreshApex(this.wiredMethodsResult);
        } catch (error) {
            this.saleError = this.reduceError(error);
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Payment sale failed',
                    message: this.saleError,
                    variant: 'error'
                })
            );
        } finally {
            this.isSubmitting = false;
        }
    }

    reduceError(error) {
        if (Array.isArray(error?.body)) {
            return error.body.map((item) => item.message).join(', ');
        }
        return error?.body?.message || error?.message || 'An unexpected error occurred.';
    }
}
