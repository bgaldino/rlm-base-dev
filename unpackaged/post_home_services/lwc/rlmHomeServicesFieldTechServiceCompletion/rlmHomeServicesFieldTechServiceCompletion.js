import { LightningElement, api, wire, track } from 'lwc';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import { getRelatedListRecords } from 'lightning/uiRelatedListApi';
import { CloseActionScreenEvent } from 'lightning/actions';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import ACCOUNT_NAME_FIELD from '@salesforce/schema/Account.Name';
import ACCOUNT_BILLING_STREET from '@salesforce/schema/Account.BillingStreet';
import ACCOUNT_BILLING_CITY from '@salesforce/schema/Account.BillingCity';
import ACCOUNT_BILLING_STATE from '@salesforce/schema/Account.BillingState';
import USER_NAME_FIELD from '@salesforce/schema/User.Name';
import Id from '@salesforce/user/Id';
import invokeServiceCompletion from '@salesforce/apex/RLM_HomeServices_FieldTechController.invokeServiceCompletion';

const ACCOUNT_FIELDS = [ACCOUNT_NAME_FIELD, ACCOUNT_BILLING_STREET, ACCOUNT_BILLING_CITY, ACCOUNT_BILLING_STATE];
const USER_FIELDS = [USER_NAME_FIELD];

const MONTH_OPTIONS = [
    { label: 'Month 1  — First Monthly Service', value: '1' },
    { label: 'Month 2  — Second Monthly Service', value: '2' },
    { label: 'Month 3  — Third Monthly Service', value: '3' },
    { label: 'Month 4  — Fourth Monthly Service', value: '4' },
    { label: 'Month 5  — Fifth Monthly Service', value: '5' },
    { label: 'Month 6  — Sixth Monthly Service', value: '6' },
    { label: 'Month 7  — Seventh Monthly Service', value: '7' },
    { label: 'Month 8  — Eighth Monthly Service', value: '8' },
    { label: 'Month 9  — Ninth Monthly Service', value: '9' },
    { label: 'Month 10 — Tenth Monthly Service', value: '10' },
    { label: 'Month 11 — Eleventh Monthly Service', value: '11' },
    { label: 'Month 12 — Twelfth Monthly Service', value: '12' }
];

export default class RlmHomeServicesFieldTechServiceCompletion extends LightningElement {
    @api recordId;

    @track selectedMonth = '';
    @track serviceDate = '';
    @track techNotes = '';
    @track isLoading = false;
    @track isSuccess = false;
    @track hasError = false;
    @track errorMessage = '';
    @track completionDateTime = '';
    @track currentScreen = 'overview';
    @track activeTab = 'overview';

    userId = Id;
    monthOptions = MONTH_OPTIONS;

    connectedCallback() {
        this.serviceDate = this._getDefaultServiceDate();
    }

    _getDefaultServiceDate() {
        return new Date().toISOString().split('T')[0];
    }

    @wire(getRecord, { recordId: '$recordId', fields: ACCOUNT_FIELDS })
    accountRecord;

    @wire(getRecord, { recordId: '$userId', fields: USER_FIELDS })
    userRecord;

    @wire(getRelatedListRecords, {
        parentRecordId: '$recordId',
        relatedListId: 'Assets',
        fields: ['Asset.Name', 'Asset.Product2.Name']
    })
    assetRecords;

    // ── Account / User getters ───────────────────────────────────────────────

    get accountName() {
        return getFieldValue(this.accountRecord.data, ACCOUNT_NAME_FIELD) || 'Loading...';
    }

    get serviceAddress() {
        const street = getFieldValue(this.accountRecord.data, ACCOUNT_BILLING_STREET) || '';
        const city   = getFieldValue(this.accountRecord.data, ACCOUNT_BILLING_CITY)   || '';
        const state  = getFieldValue(this.accountRecord.data, ACCOUNT_BILLING_STATE)  || '';
        if (city && state) return `${street ? street + ', ' : ''}${city}, ${state}`;
        return street || 'Address on file';
    }

    get technicianName() {
        return getFieldValue(this.userRecord.data, USER_NAME_FIELD) || 'Technician';
    }

    // ── Asset product name ───────────────────────────────────────────────────

    get assetProductName() {
        const records = this.assetRecords?.data?.records;
        if (records && records.length > 0) {
            const asset = records[0];
            const prod2Name = asset.fields?.Product2?.value?.fields?.Name?.value;
            const assetName = asset.fields?.Name?.value;
            return prod2Name || assetName || 'Service Plan';
        }
        return 'Service Plan';
    }

    // ── Map markers (built from billing address) ─────────────────────────────

    get mapMarkers() {
        const street = getFieldValue(this.accountRecord.data, ACCOUNT_BILLING_STREET) || '';
        const city   = getFieldValue(this.accountRecord.data, ACCOUNT_BILLING_CITY)   || '';
        const state  = getFieldValue(this.accountRecord.data, ACCOUNT_BILLING_STATE)  || '';
        if (!city && !street) return [];
        return [{
            location: { Street: street, City: city, State: state, Country: 'US' },
            title: this.accountName
        }];
    }

    get hasMapMarkers() {
        return this.mapMarkers.length > 0;
    }

    // ── Date / time getters ──────────────────────────────────────────────────

    get appointmentTimeRange() {
        const now = new Date();
        const end = new Date(now.getTime() + 75 * 60 * 1000);
        const fmt = (d) => d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
        return `${fmt(now)} \u2013 ${fmt(end)}`;
    }

    get todayFormatted() {
        return new Date().toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    get currentTime() {
        return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }

    // ── Screen & tab state ───────────────────────────────────────────────────

    get isOverviewScreen()    { return this.currentScreen === 'overview'; }
    get isServiceFormScreen() { return this.currentScreen === 'serviceForm'; }

    get isTabOverview()  { return this.activeTab === 'overview'; }
    get isTabProducts()  { return this.activeTab === 'products'; }
    get isTabDetails()   { return this.activeTab === 'details';  }

    get overviewTabClass() { return `tab-item${this.activeTab === 'overview' ? ' tab-active' : ''}`; }
    get productsTabClass() { return `tab-item${this.activeTab === 'products' ? ' tab-active' : ''}`; }
    get detailsTabClass()  { return `tab-item${this.activeTab === 'details'  ? ' tab-active' : ''}`; }

    // ── Form state ───────────────────────────────────────────────────────────

    get isSubmitDisabled() {
        return !this.selectedMonth || !this.serviceDate;
    }

    get selectedMonthLabel() {
        const option = MONTH_OPTIONS.find(o => o.value === this.selectedMonth);
        return option ? option.label.split('—')[0].trim() : '';
    }

    // ── Handlers ─────────────────────────────────────────────────────────────

    handleTabClick(event) {
        this.activeTab = event.currentTarget.dataset.tab;
    }

    handleBackNav() {
        if (this.currentScreen === 'serviceForm') {
            this.currentScreen = 'overview';
            this.hasError = false;
        } else {
            this.dispatchEvent(new CloseActionScreenEvent());
        }
    }

    handleCompleteWorkOrder() {
        this.currentScreen = 'serviceForm';
    }

    handleRunningLate() {
        this.dispatchEvent(new ShowToastEvent({
            title: 'Customer Notified',
            message: 'Your customer has been notified that you\'re running late.',
            variant: 'info'
        }));
    }

    handleMonthChange(event) {
        this.selectedMonth = event.detail.value;
        this.hasError = false;
    }

    handleServiceDateChange(event) {
        this.serviceDate = event.target.value;
        this.hasError = false;
    }

    handleNotesChange(event) {
        this.techNotes = event.target.value;
    }

    handleCancel() {
        this.currentScreen = 'overview';
        this.hasError = false;
    }

    handleClose() {
        this.dispatchEvent(new CloseActionScreenEvent());
    }

    async handleSubmit() {
        if (!this.selectedMonth) {
            this.hasError = true;
            this.errorMessage = 'Please select a service month before submitting.';
            return;
        }
        if (!this.serviceDate) {
            this.hasError = true;
            this.errorMessage = 'Please enter a service date before submitting.';
            return;
        }

        this.isLoading = true;
        this.hasError = false;

        try {
            await invokeServiceCompletion({
                accountId: this.recordId,
                serviceMonth: parseInt(this.selectedMonth, 10),
                techNotes: this.techNotes,
                serviceDate: this.serviceDate
            });

            this.completionDateTime = new Date().toLocaleString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            this.isLoading = false;
            this.isSuccess = true;

            this.dispatchEvent(new ShowToastEvent({
                title: 'Service Recorded',
                message: `${this.selectedMonthLabel} service has been marked complete. Invoice generation is in progress.`,
                variant: 'success',
                mode: 'sticky'
            }));

        } catch (error) {
            this.isLoading = false;
            this.hasError = true;
            this.errorMessage = error?.body?.message || error?.message || 'An unexpected error occurred. Please try again.';

            this.dispatchEvent(new ShowToastEvent({
                title: 'Service Completion Failed',
                message: this.errorMessage,
                variant: 'error'
            }));
        }
    }
}