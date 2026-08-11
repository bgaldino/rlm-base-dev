import { LightningElement, api, wire, track } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { NavigationMixin } from 'lightning/navigation';
import getConsole from '@salesforce/apex/RLM_AssetConsoleController.getConsole';
import launchConsolidatedAction from '@salesforce/apex/RLM_AssetConsoleController.launchConsolidatedAction';
import suspendAssets from '@salesforce/apex/RLM_AssetConsoleController.suspendAssets';
import resumeAssets from '@salesforce/apex/RLM_AssetConsoleController.resumeAssets';

const COLUMNS = [
    { label: 'Asset', fieldName: 'name', type: 'text', wrapText: false },
    { label: 'Product', fieldName: 'productName', type: 'text' },
    { label: 'Contract', fieldName: 'contractNumber', type: 'text' },
    { label: 'Qty', fieldName: 'currentQuantity', type: 'number', cellAttributes: { alignment: 'left' } },
    { label: 'Current MRR', fieldName: 'currentMrr', type: 'currency' },
    { label: 'Status', fieldName: 'status', type: 'text' },
    { label: 'ABO Status', fieldName: 'assetStatus', type: 'text' },
    { label: 'Lifecycle End', fieldName: 'lifecycleEndDate', type: 'text' },
    { label: 'Eligibility', fieldName: 'eligibilityLabel', type: 'text' }
];

const ACTION_OPTIONS = [
    { label: 'Amend (change quantity / terms)', value: 'Amend' },
    { label: 'Upgrade', value: 'Upgrade' },
    { label: 'Downgrade', value: 'Downgrade' },
    { label: 'Renew', value: 'Renew' },
    { label: 'Cancel', value: 'Cancel' },
    { label: 'Suspend', value: 'Suspend' },
    { label: 'Resume', value: 'Resume' }
];

const OUTPUT_OPTIONS = [
    { label: 'Quote', value: 'Quote' },
    { label: 'Order', value: 'Order' }
];

export default class RlmAssetConsole extends NavigationMixin(LightningElement) {
    @api recordId;
    @api objectApiName;

    columns = COLUMNS;
    actionOptions = ACTION_OPTIONS;
    outputOptions = OUTPUT_OPTIONS;

    @track rows = [];
    accountId;
    accountName;
    totalAssetCount = 0;
    loadError;

    // action form state
    selectedAssetIds = [];
    actionType = 'Amend';
    outputType = 'Quote';
    effectiveDate;
    quantityChange;
    renewalEndDate;
    resumptionDate;
    skipPricing = false;

    // result state
    working = false;
    lastResult;

    _wired;

    @wire(getConsole, { recordId: '$recordId', objectApiName: '$objectApiName' })
    wiredConsole(value) {
        this._wired = value;
        const { data, error } = value;
        if (data) {
            this.loadError = undefined;
            this.accountId = data.accountId;
            this.accountName = data.accountName;
            this.totalAssetCount = data.totalAssetCount;
            this.rows = this.flatten(data.groups);
        } else if (error) {
            this.loadError = this.reduceError(error);
            this.rows = [];
        }
    }

    flatten(groups) {
        const out = [];
        (groups || []).forEach((g) => {
            (g.assets || []).forEach((a) => {
                const elig = [];
                if (a.canAmend) elig.push('Amend');
                if (a.canRenew) elig.push('Renew');
                if (a.canCancel) elig.push('Cancel');
                out.push({
                    ...a,
                    contractNumber: g.contractNumber,
                    contractId: g.contractId,
                    eligibilityLabel: a.ineligibleReason
                        ? a.ineligibleReason
                        : elig.join(' / ')
                });
            });
        });
        return out;
    }

    // ---- derived UI state ----
    get hasRows() {
        return this.rows && this.rows.length > 0;
    }
    get hasNoRows() {
        return !this.hasRows;
    }
    get showQuantityChange() {
        return ['Amend', 'Upgrade', 'Downgrade'].includes(this.actionType);
    }
    get showRenewalEndDate() {
        return this.actionType === 'Renew';
    }
    get isSuspend() {
        return this.actionType === 'Suspend';
    }
    get isResume() {
        return this.actionType === 'Resume';
    }
    get showResumptionDate() {
        return this.actionType === 'Suspend';
    }
    get showEffectiveDate() {
        return this.actionType !== 'Resume';
    }
    get showOutput() {
        return !['Suspend', 'Resume'].includes(this.actionType);
    }
    get effectiveDateLabel() {
        return this.actionType === 'Suspend' ? 'Suspension Date' : 'Effective Date';
    }
    get launchDisabled() {
        return this.working || !this.selectedAssetIds.length;
    }
    get selectionSummary() {
        const n = this.selectedAssetIds.length;
        return n === 1 ? '1 asset selected' : `${n} assets selected`;
    }
    get hasResult() {
        return !!this.lastResult;
    }
    get resultOutputId() {
        return this.lastResult ? this.lastResult.outputRecordId : null;
    }

    // ---- handlers ----
    handleRowSelection(event) {
        const selected = event.detail.selectedRows || [];
        this.selectedAssetIds = selected.map((r) => r.id);
    }
    handleActionChange(e) {
        this.actionType = e.detail.value;
    }
    handleOutputChange(e) {
        this.outputType = e.detail.value;
    }
    handleEffectiveDate(e) {
        this.effectiveDate = e.detail.value;
    }
    handleQuantityChange(e) {
        this.quantityChange = e.detail.value;
    }
    handleRenewalEndDate(e) {
        this.renewalEndDate = e.detail.value;
    }
    handleResumptionDate(e) {
        this.resumptionDate = e.detail.value;
    }
    handleSkipPricing(e) {
        this.skipPricing = e.detail.checked;
    }

    async handleLaunch() {
        if (this.isSuspend) {
            return this.runSuspend();
        }
        if (this.isResume) {
            return this.runResume();
        }
        this.working = true;
        this.lastResult = undefined;
        try {
            const result = await launchConsolidatedAction({
                assetIds: this.selectedAssetIds,
                actionType: this.actionType,
                outputType: this.outputType,
                effectiveDate: this.effectiveDate,
                quantityChange: this.quantityChange ? Number(this.quantityChange) : null,
                renewalEndDate: this.renewalEndDate,
                skipPricing: this.skipPricing
            });
            this.lastResult = result;
            if (result.isSuccess) {
                this.toast(
                    'Consolidated ' + this.actionType + ' created',
                    'A single ' + result.outputType + ' was produced from ' + this.selectionSummary + '.',
                    'success'
                );
                await refreshApex(this._wired);
            } else {
                this.toast(
                    this.actionType + ' failed',
                    (result.messages || []).join(' ') || 'The lifecycle action did not complete.',
                    'error'
                );
            }
        } catch (e) {
            this.toast('Error', this.reduceError(e), 'error');
        } finally {
            this.working = false;
        }
    }

    async runSuspend() {
        this.working = true;
        try {
            const res = await suspendAssets({
                assetIds: this.selectedAssetIds,
                suspensionDate: this.effectiveDate,
                resumptionDate: this.resumptionDate
            });
            if (res.isSuccess) {
                this.toast('Assets suspended', res.assetsUpdated + ' asset(s) suspended; billing paused with a scheduled resume.', 'success');
                await refreshApex(this._wired);
            } else {
                this.toast('Suspend failed', (res.messages || []).join(' '), 'error');
            }
        } catch (e) {
            this.toast('Error', this.reduceError(e), 'error');
        } finally {
            this.working = false;
        }
    }

    async runResume() {
        this.working = true;
        try {
            const res = await resumeAssets({ assetIds: this.selectedAssetIds });
            if (res.isSuccess) {
                this.toast('Assets resumed', res.assetsUpdated + ' asset(s) set back to Active.', 'success');
                await refreshApex(this._wired);
            } else {
                this.toast('Resume failed', (res.messages || []).join(' '), 'error');
            }
        } catch (e) {
            this.toast('Error', this.reduceError(e), 'error');
        } finally {
            this.working = false;
        }
    }

    handleOpenResult() {
        if (!this.resultOutputId) return;
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: { recordId: this.resultOutputId, actionName: 'view' }
        });
    }

    // ---- helpers ----
    toast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
    reduceError(error) {
        if (!error) return 'Unknown error';
        if (Array.isArray(error.body)) return error.body.map((e) => e.message).join(', ');
        if (error.body && error.body.message) return error.body.message;
        if (typeof error.message === 'string') return error.message;
        return JSON.stringify(error);
    }
}
