import { LightningElement, api, wire } from 'lwc';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { refreshApex } from '@salesforce/apex';
import saveTypedSignature from '@salesforce/apex/RLM_HomeServices_ContractSigningCtrl.saveTypedSignature';

import CONTRACT_START_DATE from '@salesforce/schema/Contract.StartDate';
import CONTRACT_ACCOUNT_ID from '@salesforce/schema/Contract.AccountId';
import CONTRACT_TYPED_SIG from '@salesforce/schema/Contract.RLM_HomeServices_TypedSignature__c';
import CONTRACT_SIGNED_AT from '@salesforce/schema/Contract.RLM_HomeServices_SignedDateTime__c';
import ACCOUNT_NAME from '@salesforce/schema/Contract.Account.Name';
import ACCOUNT_BILLING_STREET from '@salesforce/schema/Contract.Account.BillingStreet';
import ACCOUNT_BILLING_CITY from '@salesforce/schema/Contract.Account.BillingCity';
import ACCOUNT_BILLING_STATE from '@salesforce/schema/Contract.Account.BillingState';
import ACCOUNT_BILLING_POSTAL_CODE from '@salesforce/schema/Contract.Account.BillingPostalCode';
import ACCOUNT_BILLING_COUNTRY from '@salesforce/schema/Contract.Account.BillingCountry';

const IPAD_WIDTH = 768;
const IPAD_HEIGHT = 1024;
const MIN_SCALE = 0.8;

const FIELDS = [
    CONTRACT_START_DATE,
    CONTRACT_ACCOUNT_ID,
    CONTRACT_TYPED_SIG,
    CONTRACT_SIGNED_AT,
    ACCOUNT_NAME,
    ACCOUNT_BILLING_STREET,
    ACCOUNT_BILLING_CITY,
    ACCOUNT_BILLING_STATE,
    ACCOUNT_BILLING_POSTAL_CODE,
    ACCOUNT_BILLING_COUNTRY
];

export default class Rlm_contractSigning extends LightningElement {
    @api recordId;

    wiredRecord;
    typedName = '';
    acknowledged = false;
    saving = false;

    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    wiredContract(result) {
        this.wiredRecord = result;
    }

    get loading() {
        return this.wiredRecord?.loading === true;
    }

    get errorMessage() {
        const err = this.wiredRecord?.error;
        if (!err) {
            return null;
        }
        return err.body?.message || err.message || 'Unable to load contract.';
    }

    get hasRecord() {
        return this.wiredRecord?.data != null;
    }

    get formattedStartDate() {
        const data = this.wiredRecord?.data;
        if (!data) {
            return '—';
        }
        const v = getFieldValue(data, CONTRACT_START_DATE);
        if (!v) {
            return '—';
        }
        try {
            return new Intl.DateTimeFormat(undefined, {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).format(new Date(v));
        } catch (e) {
            return String(v);
        }
    }

    get customerName() {
        const data = this.wiredRecord?.data;
        if (!data) {
            return '—';
        }
        const name = getFieldValue(data, ACCOUNT_NAME);
        return name || '—';
    }

    get serviceAddress() {
        const data = this.wiredRecord?.data;
        if (!data) {
            return '—';
        }
        const parts = [
            getFieldValue(data, ACCOUNT_BILLING_STREET),
            getFieldValue(data, ACCOUNT_BILLING_CITY),
            getFieldValue(data, ACCOUNT_BILLING_STATE),
            getFieldValue(data, ACCOUNT_BILLING_POSTAL_CODE),
            getFieldValue(data, ACCOUNT_BILLING_COUNTRY)
        ].filter((p) => p != null && String(p).trim() !== '');
        return parts.length ? parts.join(', ') : '—';
    }

    get isSigned() {
        const data = this.wiredRecord?.data;
        if (!data) {
            return false;
        }
        const sig = getFieldValue(data, CONTRACT_TYPED_SIG);
        return Boolean(sig && String(sig).trim());
    }

    get signedDisplayName() {
        const data = this.wiredRecord?.data;
        if (!data) {
            return '';
        }
        return getFieldValue(data, CONTRACT_TYPED_SIG) || '';
    }

    get formattedSignedAt() {
        const data = this.wiredRecord?.data;
        if (!data) {
            return '';
        }
        const dt = getFieldValue(data, CONTRACT_SIGNED_AT);
        if (!dt) {
            return '';
        }
        try {
            return new Intl.DateTimeFormat(undefined, {
                dateStyle: 'medium',
                timeStyle: 'short'
            }).format(new Date(dt));
        } catch (e) {
            return String(dt);
        }
    }

    get signDisabled() {
        return (
            this.saving ||
            !this.acknowledged ||
            !String(this.typedName || '').trim() ||
            this.isSigned
        );
    }

    handleTypedNameChange(event) {
        this.typedName = event.target.value;
    }

    handleAckChange(event) {
        this.acknowledged = event.target.checked;
    }

    async handleSign() {
        if (this.signDisabled) {
            return;
        }
        this.saving = true;
        try {
            await saveTypedSignature({
                contractId: this.recordId,
                typedName: this.typedName.trim()
            });
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Agreement signed',
                    message: 'Your typed signature has been saved on this contract.',
                    variant: 'success'
                })
            );
            this.typedName = '';
            this.acknowledged = false;
            await refreshApex(this.wiredRecord);
        } catch (e) {
            const msg =
                e.body?.message || e.message || 'Could not save signature.';
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Error',
                    message: msg,
                    variant: 'error'
                })
            );
        } finally {
            this.saving = false;
        }
    }

    renderedCallback() {
        if (this._scaleSetup) {
            return;
        }
        this._scaleSetup = true;
        this.setupViewportScaling();
    }

    setupViewportScaling() {
        const viewport = this.template.querySelector('.contract-viewport');
        const wrapper = this.template.querySelector('.contract-wrapper');
        if (!viewport || !wrapper) {
            return;
        }

        const updateScale = () => {
            const rect = viewport.getBoundingClientRect();
            const availableWidth = Math.max(0, viewport.clientWidth);
            const availableHeight = Math.max(0, window.innerHeight - rect.top);
            const scaleX = availableWidth / IPAD_WIDTH;
            const scaleY = availableHeight / IPAD_HEIGHT;
            const scale = Math.max(MIN_SCALE, Math.min(1, scaleX, scaleY));

            wrapper.style.transform = `scale(${scale})`;
            wrapper.style.transformOrigin = 'top center';
        };

        updateScale();
        const observer = new ResizeObserver(updateScale);
        observer.observe(viewport);
        this._resizeObserver = observer;
        window.addEventListener('resize', updateScale);
        this._handleWindowResize = updateScale;
    }

    disconnectedCallback() {
        if (this._resizeObserver) {
            this._resizeObserver.disconnect();
            this._resizeObserver = null;
        }
        if (this._handleWindowResize) {
            window.removeEventListener('resize', this._handleWindowResize);
            this._handleWindowResize = null;
        }
    }
}