import { LightningElement, api, track } from 'lwc';
import { FlowNavigationNextEvent } from 'lightning/flowSupport';

import deleteUsageAndBindings from '@salesforce/apex/RLM_Utils_AccountResetController.deleteUsageAndBindings';
import deleteBillingOnly from '@salesforce/apex/RLM_Utils_AccountResetController.deleteBillingOnly';
import deleteFulfillment from '@salesforce/apex/RLM_Utils_AccountResetController.deleteFulfillment';
import deleteOrders from '@salesforce/apex/RLM_Utils_AccountResetController.deleteOrders';
import deleteContractsOnly from '@salesforce/apex/RLM_Utils_AccountResetController.deleteContractsOnly';
import deleteAssets from '@salesforce/apex/RLM_Utils_AccountResetController.deleteAssets';
import deleteQuotesOnly from '@salesforce/apex/RLM_Utils_AccountResetController.deleteQuotesOnly';
import deleteOpportunitiesOnly from '@salesforce/apex/RLM_Utils_AccountResetController.deleteOpportunitiesOnly';

const SELECTION_GROUPS = [
    {
        key: 'transactional',
        label: 'Transactional Data',
        toggleKey: 'deleteTransactional',
        toggleLabel: 'Delete Transactional (select/deselect section)',
        items: [
            { key: 'deleteUsageAndBindings', label: 'Delete Usage & Bindings' },
            { key: 'deleteFulfillment', label: 'Delete Fulfillment' },
            { key: 'deleteOrders', label: 'Delete Orders' },
            { key: 'deleteBilling', label: 'Delete Billing (Draft Invoices + Billing Schedule Groups)' },
            { key: 'deleteContracts', label: 'Delete Contracts' },
            { key: 'deleteAssets', label: 'Delete Assets' }
        ]
    },
    {
        key: 'crm',
        label: 'CRM Data',
        toggleKey: 'deleteCrm',
        toggleLabel: 'Delete CRM (select/deselect section)',
        items: [
            { key: 'deleteQuotes', label: 'Delete Quotes' },
            { key: 'deleteOpportunities', label: 'Delete Opportunities' }
        ]
    }
];

const PROGRESS_ROWS = [
    { type: 'header', key: 'hdr-tx', label: 'Transactional Data' },
    { type: 'step', key: 'usage', label: 'Delete Usage & Bindings', selectionKey: 'deleteUsageAndBindings', groupKey: 'deleteTransactional' },
    { type: 'step', key: 'fulfillment', label: 'Fulfillment', selectionKey: 'deleteFulfillment', groupKey: 'deleteTransactional' },
    { type: 'step', key: 'orders', label: 'Orders', selectionKey: 'deleteOrders', groupKey: 'deleteTransactional' },
    { type: 'step', key: 'billing', label: 'Billing (Draft Invoices + Billing Schedule Groups)', selectionKey: 'deleteBilling', groupKey: 'deleteTransactional' },
    { type: 'step', key: 'contracts', label: 'Contracts', selectionKey: 'deleteContracts', groupKey: 'deleteTransactional' },
    { type: 'step', key: 'assets', label: 'Assets', selectionKey: 'deleteAssets', groupKey: 'deleteTransactional' },
    { type: 'header', key: 'hdr-crm', label: 'CRM Data' },
    { type: 'step', key: 'quotes', label: 'Quotes', selectionKey: 'deleteQuotes', groupKey: 'deleteCrm' },
    { type: 'step', key: 'opportunities', label: 'Opportunities', selectionKey: 'deleteOpportunities', groupKey: 'deleteCrm' }
];

export default class RlmAccountResetProgress extends LightningElement {
    @api accountId;
    @api availableActions = [];

    @track rows = [];

    hasStarted = false;
    isComplete = false;
    completionMessage = '';

    selections = {
        deleteTransactional: true,
        deleteUsageAndBindings: true,
        deleteFulfillment: true,
        deleteOrders: true,
        deleteBilling: true,
        deleteContracts: true,
        deleteAssets: true,
        deleteCrm: true,
        deleteQuotes: true,
        deleteOpportunities: true
    };

    connectedCallback() {
        this.rows = PROGRESS_ROWS.map((row) =>
            row.type === 'header'
                ? { ...row }
                : {
                    ...row,
                    status: 'pending',
                    statusLabel: 'Pending',
                    details: '',
                    errorMessage: '',
                    isRunning: false,
                    itemClass: 'slds-progress__item',
                    markerClass: 'slds-progress__marker',
                    markerIconName: null,
                    inlineText: 'Pending',
                    inlineClass: 'slds-text-body_small slds-text-color_weak step-inline'
                }
        );
    }

    get selectionGroups() {
        return SELECTION_GROUPS.map((group) => ({
            ...group,
            toggleChecked: this.selections[group.toggleKey],
            items: group.items.map((item) => ({
                ...item,
                checked: this.selections[item.key],
                disabled: this.hasStarted
            })),
            disabled: this.hasStarted
        }));
    }

    get progressRows() {
        return this.rows.map((row) => ({
            ...row,
            typeHeader: row.type === 'header',
            typeStep: row.type === 'step'
        }));
    }

    get canNavigateNext() {
        return Array.isArray(this.availableActions) && this.availableActions.includes('NEXT');
    }

    get isResetDisabled() {
        return this.hasStarted;
    }

    handleToggleChange(event) {
        const key = event.target.dataset.key;
        this.selections = { ...this.selections, [key]: event.target.checked };
    }

    handleGroupToggle(event) {
        const groupKey = event.target.dataset.group;
        const group = SELECTION_GROUPS.find((g) => g.key === groupKey);
        if (!group) return;

        const checked = event.target.checked;
        const next = { ...this.selections, [group.toggleKey]: checked };
        group.items.forEach((item) => {
            next[item.key] = checked;
        });
        this.selections = next;
    }

    isStepEnabled(step) {
        const groupEnabled = step.groupKey ? this.selections[step.groupKey] : true;
        return groupEnabled && this.selections[step.selectionKey];
    }

    async startReset() {
        this.hasStarted = true;
        this.isComplete = false;
        this.completionMessage = '';

        await this.runStep('usage', () => deleteUsageAndBindings({ accountId: this.accountId }));
        await this.runStep('fulfillment', () => deleteFulfillment({ accountId: this.accountId, deleteFulfillment: this.isStepEnabled(this.getStep('fulfillment')) }));
        await this.runStep('orders', () => deleteOrders({ accountId: this.accountId, deleteOrders: this.isStepEnabled(this.getStep('orders')) }));
        await this.runStep('billing', () => deleteBillingOnly({ accountId: this.accountId, deleteBilling: this.isStepEnabled(this.getStep('billing')) }));
        await this.runStep('contracts', () => deleteContractsOnly({ accountId: this.accountId, deleteContracts: this.isStepEnabled(this.getStep('contracts')) }));
        await this.runStep('assets', () => deleteAssets({ accountId: this.accountId, deleteAssets: this.isStepEnabled(this.getStep('assets')) }));
        await this.runStep('quotes', () => deleteQuotesOnly({ accountId: this.accountId, deleteQuotes: this.isStepEnabled(this.getStep('quotes')) }));
        await this.runStep('opportunities', () => deleteOpportunitiesOnly({ accountId: this.accountId, deleteOpps: this.isStepEnabled(this.getStep('opportunities')) }));

        this.isComplete = true;
        if (this.canNavigateNext) {
            this.dispatchEvent(new FlowNavigationNextEvent());
        } else {
            this.completionMessage = 'Reset complete. You may close this dialog.';
        }
    }

    getStep(stepKey) {
        return this.rows.find((row) => row.type === 'step' && row.key === stepKey);
    }

    async runStep(stepKey, runner) {
        const step = this.getStep(stepKey);
        const isEnabled = this.isStepEnabled(step);

        this.updateStep(stepKey, {
            status: isEnabled ? 'running' : 'skipped',
            statusLabel: isEnabled ? 'Running' : 'Skipped',
            details: isEnabled ? '' : 'Step not selected.',
            errorMessage: '',
            isRunning: isEnabled,
            itemClass: this.toItemClass(isEnabled ? 'running' : 'skipped'),
            markerClass: this.toMarkerClass(isEnabled ? 'running' : 'skipped'),
            markerIconName: this.toMarkerIcon(isEnabled ? 'running' : 'skipped')
        });

        if (!isEnabled) {
            return;
        }

        const result = await this.executeStep(runner);
        const status = result?.status || 'success';
        this.updateStep(stepKey, {
            status,
            statusLabel: this.toStatusLabel(status),
            details: result?.details || '',
            errorMessage: result?.errors?.length ? result.errors.join('; ') : '',
            isRunning: false,
            itemClass: this.toItemClass(status),
            markerClass: this.toMarkerClass(status),
            markerIconName: this.toMarkerIcon(status)
        });
    }

    async executeStep(runner) {
        try {
            return await runner();
        } catch (e) {
            return {
                status: 'error',
                details: '',
                errors: [e?.body?.message || e?.message || 'Unknown error']
            };
        }
    }

    updateStep(stepKey, patch) {
        this.rows = this.rows.map((row) => {
            if (row.type !== 'step' || row.key !== stepKey) return row;
            const merged = { ...row, ...patch };
            merged.inlineText = this.toInlineText(merged);
            merged.inlineClass = this.toInlineClass(merged);
            return merged;
        });
    }

    toItemClass(status) {
        if (status === 'success') return 'slds-progress__item slds-is-completed';
        if (status === 'partial' || status === 'error') return 'slds-progress__item slds-has-error';
        if (status === 'running') return 'slds-progress__item slds-is-active';
        return 'slds-progress__item';
    }

    toMarkerClass(status) {
        if (status === 'success' || status === 'partial' || status === 'error') {
            return 'slds-progress__marker slds-progress__marker_icon';
        }
        return 'slds-progress__marker';
    }

    toMarkerIcon(status) {
        if (status === 'success') return 'utility:success';
        if (status === 'partial' || status === 'error') return 'utility:error';
        return null;
    }

    toStatusLabel(status) {
        if (status === 'success') return 'Complete';
        if (status === 'skipped') return 'Skipped';
        if (status === 'partial') return 'Completed with warnings';
        if (status === 'error') return 'Error';
        if (status === 'running') return 'Running';
        return 'Pending';
    }

    toInlineText(step) {
        const detail = step.errorMessage || step.details;
        return detail ? `${step.statusLabel} — ${detail}` : step.statusLabel;
    }

    toInlineClass(step) {
        if (step.errorMessage || step.status === 'error' || step.status === 'partial') {
            return 'slds-text-body_small slds-text-color_error step-inline';
        }
        return 'slds-text-body_small slds-text-color_weak step-inline';
    }

    handleDone() {
        if (this.canNavigateNext) {
            this.dispatchEvent(new FlowNavigationNextEvent());
        }
    }
}
