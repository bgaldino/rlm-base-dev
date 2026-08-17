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
    { label: 'Account', fieldName: 'accountName', type: 'text' },
    { label: 'Serial Number', fieldName: 'serialNumber', type: 'text' },
    { label: 'Serialized Units', fieldName: 'serialUnitSummary', type: 'text' },
    { label: 'Product', fieldName: 'productName', type: 'text' },
    { label: 'Contract', fieldName: 'contractNumber', type: 'text' },
    { label: 'Qty', fieldName: 'currentQuantity', type: 'number', cellAttributes: { alignment: 'left' } },
    { label: 'Current MRR', fieldName: 'currentMrr', type: 'currency' },
    { label: 'Status', fieldName: 'status', type: 'text' },
    { label: 'ABO Status', fieldName: 'assetStatus', type: 'text' },
    { label: 'Billing Start', fieldName: 'billingStartDate', type: 'text' },
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

    // Flat list of every asset row (source of truth for filtering).
    @track allRows = [];
    // Hierarchical view (root/parent bundle items with nested _children) after
    // the current search filter is applied - this is what the tree-grid renders.
    @track treeRows = [];
    // Ids of expanded parent nodes (fully expanded by default).
    @track expandedRows = [];
    // Ids of rows that are children of another asset (Asset.ParentId points at a
    // row in this list). Child bundle components are NOT independently
    // selectable - the parent bundle is the unit of action.
    _childIds = new Set();
    searchTerm = '';
    accountId;
    accountName;
    totalAssetCount = 0;
    accountCount = 1;
    // When true, read assets from every account in the primary account's
    // hierarchy (parents + all descendants), not just the record's account.
    includeHierarchy = false;
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

    @wire(getConsole, {
        recordId: '$recordId',
        objectApiName: '$objectApiName',
        includeHierarchy: '$includeHierarchy'
    })
    wiredConsole(value) {
        this._wired = value;
        const { data, error } = value;
        if (data) {
            this.loadError = undefined;
            this.accountId = data.accountId;
            this.accountName = data.accountName;
            this.totalAssetCount = data.totalAssetCount;
            this.accountCount = data.accountCount;
            this.allRows = this.flatten(data.groups);
            const ids = new Set(this.allRows.map((r) => r.id));
            this._childIds = new Set(
                this.allRows.filter((r) => r.parentId && ids.has(r.parentId)).map((r) => r.id)
            );
            this.recomputeTree();
        } else if (error) {
            this.loadError = this.reduceError(error);
            this.allRows = [];
            this.treeRows = [];
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

    // ---- hierarchy + search ----
    // Rebuild the tree-grid data from allRows, honoring the current search term,
    // and expand every parent node so the bundle structure is visible.
    recomputeTree() {
        const filtered = this.filterRows(this.allRows, this.searchTerm);
        this.treeRows = this.buildTree(filtered);
        this.expandedRows = filtered
            .filter((r) => filtered.some((c) => c.parentId === r.id))
            .map((r) => r.id);
    }

    // Nest child bundle items under their parent (Asset.ParentId) so the
    // parent/child relationship is preserved and visualized in the tree-grid.
    buildTree(rows) {
        const byId = new Map();
        rows.forEach((r) => byId.set(r.id, { ...r, _children: [] }));
        const roots = [];
        byId.forEach((node) => {
            const pid = node.parentId;
            if (pid && byId.has(pid)) {
                byId.get(pid)._children.push(node);
            } else {
                roots.push(node);
            }
        });
        // Drop empty _children so leaf rows don't show an expand chevron.
        byId.forEach((node) => {
            if (node._children.length === 0) delete node._children;
        });
        return roots;
    }

    // Substring match on serial number, asset name, product, and contract.
    // Ancestors of a match are kept so a matched child stays in context.
    filterRows(rows, term) {
        const t = (term || '').trim().toLowerCase();
        if (!t) return rows;
        const byId = new Map(rows.map((r) => [r.id, r]));
        const keep = new Set();
        rows.forEach((r) => {
            const hay = [r.name, r.accountName, r.serialNumber, r.serialUnitSummary, r.productName, r.productCode, r.contractNumber]
                .filter(Boolean)
                .join(' ')
                .toLowerCase();
            if (hay.includes(t)) keep.add(r.id);
        });
        [...keep].forEach((id) => {
            let cur = byId.get(id);
            while (cur && cur.parentId && byId.has(cur.parentId)) {
                keep.add(cur.parentId);
                cur = byId.get(cur.parentId);
            }
        });
        return rows.filter((r) => keep.has(r.id));
    }

    handleSearch(event) {
        this.searchTerm = event.detail.value;
        this.recomputeTree();
    }
    handleHierarchyToggle(event) {
        // Re-runs the wire (reactive param), pulling assets from the whole tree.
        this.includeHierarchy = event.detail.checked;
    }
    handleToggle(event) {
        const { name, isExpanded } = event.detail;
        const set = new Set(this.expandedRows);
        if (isExpanded) set.add(name);
        else set.delete(name);
        this.expandedRows = [...set];
    }
    handleToggleAll(event) {
        this.expandedRows = event.detail.isExpanded
            ? this.allRows.filter((r) => this.allRows.some((c) => c.parentId === r.id)).map((r) => r.id)
            : [];
    }

    // ---- derived UI state ----
    get hasRows() {
        return this.allRows && this.allRows.length > 0;
    }
    get hasNoRows() {
        return !this.hasRows;
    }
    get hasVisibleRows() {
        return this.treeRows && this.treeRows.length > 0;
    }
    get noSearchMatches() {
        return this.hasRows && !this.hasVisibleRows;
    }
    get hierarchySummary() {
        if (!this.includeHierarchy) return '';
        return this.accountCount > 1
            ? `Showing assets across ${this.accountCount} related accounts`
            : 'No related accounts found in the hierarchy';
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
    // Only parent/top-level assets are selectable. Child bundle components are
    // stripped out and the tree-grid selection is re-bound so their checkboxes
    // clear immediately; the parent bundle carries its children into the action.
    handleRowSelection(event) {
        const selected = event.detail.selectedRows || [];
        const parents = selected.filter((r) => !this._childIds.has(r.id));
        const blocked = selected.length - parents.length;
        this.selectedAssetIds = parents.map((r) => r.id);
        if (blocked > 0) {
            this.toast(
                'Child items can’t be selected',
                'Select the parent bundle instead — its child components are included automatically.',
                'info'
            );
        }
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
