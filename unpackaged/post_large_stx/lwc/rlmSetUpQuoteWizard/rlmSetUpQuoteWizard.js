import { LightningElement, api, track } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import { CloseActionScreenEvent } from 'lightning/actions';
import runSetUpQuoteFromLWC from '@salesforce/apex/RLM_SetUpQuoteInvocable.runSetUpQuoteFromLWC';
import getQuotesForModify from '@salesforce/apex/RLM_SetUpQuoteInvocable.getQuotesForModify';
import getQuoteHierarchy from '@salesforce/apex/RLM_SetUpQuoteInvocable.getQuoteHierarchy';
import getRecentQuotesForRepeatBuy from '@salesforce/apex/RLM_SetUpQuoteInvocable.getRecentQuotesForRepeatBuy';
import getAccountsForRepeatBuy from '@salesforce/apex/RLM_SetUpQuoteInvocable.getAccountsForRepeatBuy';
import getRepeatBuyLines from '@salesforce/apex/RLM_SetUpQuoteInvocable.getRepeatBuyLines';
import previewQuoteLineCounts from '@salesforce/apex/RLM_SetUpQuoteLinePreview.previewQuoteLineCounts';

const STEP_CREATE_OR_MODIFY = 1;
const STEP_QUOTE_INFO = 2;
const STEP_HIERARCHY = 3;
const STEP_ASSIGN_REPEAT = 4;
const STEP_PRODUCT_COUNTS = 5;
const STEP_LARGE_DEAL = 6;
const STEP_CONFIRM = 7;
const STEP_RESULT = 8;
const LARGE_DEAL_THRESHOLD = 500;

const CSV_HEADER = 'Group 1,Group 2,Group 3,Group 4,Group 5,Bundle Product,Product,Quantity';

export default class RlmSetUpQuoteWizard extends NavigationMixin(LightningElement) {
    @api recordId;
    @api objectApiName;

    @track step = STEP_CREATE_OR_MODIFY;
    @track isCreate = true;
    @track newQuoteName = '';
    @track quoteId = '';
    /** Raw list from getQuotesForModify: [{ value, label, isLargeDeal }] */
    @track quoteOptions = [];
    @track quoteOptionsLoading = false;
    @track largeDeal = false;
    @track largeDealRequiredByThreshold = false;
    @track result = null; // { quoteId, success, errorMessage }
    @track loading = false;
    @track _hierarchyJson = null;
    @track _productCountsJson = '{}';
    /** Modify only: existing quote hierarchy from getQuoteHierarchy. */
    @track existingHierarchy = null;
    @track existingHierarchyLoading = false;
    /** Modify only: QuoteLineGroup Ids the user chose to delete (and their line items). */
    @track groupsToDelete = [];
    /** Modify only: group Id -> new name (for rename). */
    @track groupRenames = {};
    /** Modify only: pending new subgroups under existing [{ parentGroupId, name, tempId }]. */
    @track newSubgroupsUnderExisting = [];
    /** Modify only: JSON for c-rlm-set-up-quote-hierarchy-tree (existing groups tree). */
    @track existingTreeDisplayJson = '{"parents":[]}';
    /** Modify only: QuoteLineGroup Id -> name from server when hierarchy was loaded. */
    originalGroupNamesById = {};
    /** Modify only: product counts for existing groups and new subgroups (groupId or tempId -> count). */
    @track _existingGroupCounts = {};
    /** Create only: 'manual' | 'csv' — how user adds groups. */
    @track importMethod = null;
    /** Create + CSV: { hierarchyJson, csvImportLineItemsJson } after parsing. */
    @track csvImportData = null;
    /** Create + CSV: error or validation message. */
    @track csvFileError = null;
    /** Create + CSV: summary { rowCount, groupCount, lineItemCount } for display. */
    @track csvSummary = null;
    /** Create + CSV: chosen file name for display. */
    @track csvFileName = null;
    /** Create mode lock for a run: SCRATCH | CSV | PREVIOUS_QUOTES */
    @track createMode = 'SCRATCH';
    /** Previous-quotes mode: account context and source quote selection. */
    @track repeatBuyAccountId = '';
    @track repeatBuyQuoteOptions = [];
    @track repeatBuyQuotesLoading = false;
    @track repeatBuyAccountOptions = [];
    @track repeatBuyAccountsLoading = false;
    @track repeatBuySelectedQuoteIds = [];
    @track repeatBuyPayload = [];
    @track repeatBuyLinesLoading = false;
    @track repeatBuyFilter = '';
    @track repeatBuyAssignments = [];
    @track repeatBuySelectedMasterKey = '';
    @track repeatBuyBulkTargetPath = '';
    @track repeatBuyLastActionMessage = '';
    @track repeatBuyDuplicateResolutionMode = 'MERGE';
    @track hierarchyValidationError = null;
    @track quoteInfoNextLocked = false;
    /** Modify, step 3: which master–detail pane is active — existing tree | manual new groups | CSV new groups. */
    @track modifyHierarchyRail = 'existing';
    /** Modify, step 4: product counts — existing groups | new manual tree (same style as hierarchy rail). */
    @track modifyProductCountsRail = 'existing';
    /** Step 4 / Confirm: QuoteLineItem count preview from Apex (no threshold enforcement). */
    @track quoteLinePreview = null;
    _quoteLinePreviewTimer;
    _quoteInfoNextLockTimer;
    _modalFocused = false;

    /** When modifying a quote that already has Large Deal set, we skip the Large Deal step (5-step flow). */
    get skipLargeDealStep() {
        if (this.isCreate) return false;
        if (!this.quoteId) return false;
        const opt = (this.quoteOptions || []).find((o) => o.value === this.quoteId);
        return opt && opt.isLargeDeal === 'true';
    }

    get quoteOptionsForCombobox() {
        const list = this.quoteOptions || [];
        return [{ label: '-- Select a quote --', value: '' }, ...list.map((o) => ({ label: o.label, value: o.value }))];
    }

    get stepTitle() {
        const titles = {
            [STEP_CREATE_OR_MODIFY]: 'Create or Modify',
            [STEP_QUOTE_INFO]: this.isCreate ? 'Quote details' : 'Select quote',
            [STEP_HIERARCHY]: 'Build group hierarchy',
            [STEP_ASSIGN_REPEAT]: 'Assign repeated lines to groups',
            [STEP_PRODUCT_COUNTS]: 'Product count per group',
            [STEP_LARGE_DEAL]: 'Large Deal',
            [STEP_CONFIRM]: 'Review and run',
            [STEP_RESULT]: 'Result'
        };
        return titles[this.step] || '';
    }

    /** Step indicator: 7 steps normally, 6 when Large Deal step is skipped. */
    get stepsList() {
        const steps = this.isCreatePreviousMode
            ? [
                  { id: 1, label: 'Create/Modify' },
                  { id: 2, label: 'Quote' },
                  { id: 3, label: 'Hierarchy' },
                  { id: 4, label: 'Assign repeat lines' },
                  { id: 5, label: 'Product counts' },
                  { id: 6, label: 'Large Deal' },
                  { id: 7, label: 'Confirm' },
                  { id: 8, label: 'Result' }
              ]
            : [
                  { id: 1, label: 'Create/Modify' },
                  { id: 2, label: 'Quote' },
                  { id: 3, label: 'Hierarchy' },
                  { id: 5, label: 'Product counts' },
                  { id: 6, label: 'Large Deal' },
                  { id: 7, label: 'Confirm' },
                  { id: 8, label: 'Result' }
              ];
        if (this.skipLargeDealStep) {
            const filtered = steps.filter((s) => s.id !== STEP_LARGE_DEAL);
            return filtered.map((s, idx) => {
                const isActive = this._stepIndexForIndicator === idx + 1;
                const isCompleted = this._stepIndexForIndicator > idx + 1;
                let stepClass = 'step-dot';
                if (isCompleted) stepClass += ' step-dot-done';
                else if (isActive) stepClass += ' step-dot-active';
                return { ...s, stepNum: idx + 1, totalSteps: filtered.length, isActive, isCompleted, stepClass, isLast: idx === filtered.length - 1 };
            });
        }
        return steps.map((s, idx) => {
            const isActive = this.step === s.id;
            const isCompleted = this.step > s.id;
            let stepClass = 'step-dot';
            if (isCompleted) stepClass += ' step-dot-done';
            else if (isActive) stepClass += ' step-dot-active';
            return { ...s, stepNum: idx + 1, totalSteps: steps.length, isActive, isCompleted, stepClass, isLast: idx === steps.length - 1 };
        });
    }

    /** For 6-step flow (skip Large Deal), map internal step to indicator index. */
    get _stepIndexForIndicator() {
        const steps = this.isCreatePreviousMode
            ? [1, 2, 3, 4, 5, 6, 7, 8]
            : [1, 2, 3, 5, 6, 7, 8];
        const filtered = this.skipLargeDealStep ? steps.filter((id) => id !== STEP_LARGE_DEAL) : steps;
        const idx = filtered.indexOf(this.step);
        return idx >= 0 ? idx + 1 : 1;
    }

    get showBack() {
        return this.step > STEP_CREATE_OR_MODIFY && this.step < STEP_RESULT;
    }

    get isCreatePreviousMode() {
        return this.isCreate && this.createMode === 'PREVIOUS_QUOTES';
    }

    get showCreateModeEntryControls() {
        if (!this.isCreate) return false;
        return !(this.isCreatePreviousMode && !!this.newQuoteName);
    }

    get repeatBuyHasQuoteSelection() {
        return this.repeatBuySelectedQuoteIds && this.repeatBuySelectedQuoteIds.length > 0;
    }

    get repeatBuyAssignmentsVisible() {
        return this.isCreatePreviousMode && this.repeatBuyAssignments && this.repeatBuyAssignments.length > 0;
    }

    get repeatBuyFilteredAssignments() {
        const q = (this.repeatBuyFilter || '').trim().toLowerCase();
        if (!q) return this.repeatBuyAssignments || [];
        return (this.repeatBuyAssignments || []).filter((r) => {
            const p = String(r.productName || '').toLowerCase();
            const c = String(r.productCode || '').toLowerCase();
            const g = String(r.historicalGroupName || '').toLowerCase();
            return p.includes(q) || c.includes(q) || g.includes(q);
        });
    }

    get repeatBuyMasterNodes() {
        const rows = this.repeatBuyFilteredAssignments || [];
        const nodes = new Map();
        rows.forEach((r) => {
            const quoteKey = String(r.sourceQuoteKey || 'q0');
            const groupPath = String(r.sourcePath || '');
            const quoteLabel = r.quoteLabel || `Quote ${quoteKey}`;
            const groupLabel = r.historicalGroupName || 'Ungrouped';
            if (!nodes.has(`quote:${quoteKey}`)) {
                nodes.set(`quote:${quoteKey}`, { key: `quote:${quoteKey}`, label: quoteLabel, kind: 'quote', quoteKey, count: 0, selected: false, cssClass: '', depth: 0 });
            }
            nodes.get(`quote:${quoteKey}`).count += 1;
            const gk = `group:${quoteKey}:${groupPath}`;
            if (!nodes.has(gk)) {
                nodes.set(gk, { key: gk, label: groupLabel, kind: 'group', groupPath, quoteKey, count: 0, selected: false, cssClass: '', depth: 1 });
            }
            nodes.get(gk).count += 1;
        });
        const ordered = [];
        const seenQuoteKeys = new Set();
        const seenGroupKeys = new Set();
        rows.forEach((r) => {
            const quoteKey = String(r.sourceQuoteKey || 'q0');
            const quoteNodeKey = `quote:${quoteKey}`;
            const groupNodeKey = `group:${quoteKey}:${String(r.sourcePath || '')}`;
            if (!seenQuoteKeys.has(quoteNodeKey) && nodes.has(quoteNodeKey)) {
                seenQuoteKeys.add(quoteNodeKey);
                ordered.push(nodes.get(quoteNodeKey));
            }
            if (!seenGroupKeys.has(groupNodeKey) && nodes.has(groupNodeKey)) {
                seenGroupKeys.add(groupNodeKey);
                ordered.push(nodes.get(groupNodeKey));
            }
        });
        const selected = this.repeatBuySelectedMasterKey || (ordered[0] && ordered[0].key);
        return ordered.map((n) => {
            const isSel = selected === n.key;
            return {
                ...n,
                selected: isSel,
                cssClass: `repeat-master-node${isSel ? ' repeat-master-node_selected' : ''}${n.depth > 0 ? ' repeat-master-node_child' : ''}`
            };
        });
    }

    get repeatBuyDetailRows() {
        const key = this.repeatBuySelectedMasterKey;
        const rows = this.repeatBuyFilteredAssignments || [];
        const decorate = (arr) =>
            arr.map((r) => ({
                ...r,
                duplicateActionLabel: r.duplicateToTarget ? 'Undo duplicate' : 'Duplicate to target',
                removeActionLabel: r.removed ? 'Restore' : 'Remove from add',
                removeActionClass: r.removed ? 'repeat-action-btn repeat-action-btn_restore' : 'repeat-action-btn',
                duplicateActionIcon: r.duplicateToTarget ? 'utility:undo' : 'utility:copy',
                removeActionIcon: r.removed ? 'utility:refresh' : 'utility:delete'
            }));
        if (!key) return decorate(rows);
        if (key.startsWith('quote:')) {
            const quoteKey = key.replace('quote:', '');
            return decorate(rows.filter((r) => String(r.sourceQuoteKey || 'q0') === quoteKey));
        }
        if (key.startsWith('group:')) {
            const parts = key.split(':');
            const quoteKey = parts[1] || '';
            const gp = parts.slice(2).join(':');
            return decorate(rows.filter((r) => String(r.sourceQuoteKey || 'q0') === quoteKey && String(r.sourcePath || '') === gp));
        }
        return decorate(rows);
    }

    get repeatBuySelectedMasterLabel() {
        const key = this.repeatBuySelectedMasterKey;
        const node = (this.repeatBuyMasterNodes || []).find((n) => n.key === key);
        return node ? node.label : 'All repeated lines';
    }

    get hasRepeatBuyDetailRows() {
        return (this.repeatBuyDetailRows || []).length > 0;
    }

    get repeatBuySelectedCount() {
        return (this.repeatBuyAssignments || []).filter((r) => r.selected === true).length;
    }

    get hasRepeatBuySelection() {
        return this.repeatBuySelectedCount > 0;
    }

    get repeatBuyBulkActionsDisabled() {
        return !this.hasRepeatBuySelection;
    }

    get repeatBuyStats() {
        const rows = this.repeatBuyAssignments || [];
        let selected = 0;
        let removed = 0;
        let duplicated = 0;
        let moved = 0;
        let active = 0;
        let duplicateExtra = 0;
        rows.forEach((r) => {
            if (r.selected === true) selected++;
            const isRemoved = r.removed === true;
            const isDup = r.duplicateToTarget === true;
            const source = String(r.sourcePath || '');
            const target = String(r.targetPath || '');
            const movedToOther = !isRemoved && source && target && source !== target;
            if (isRemoved) removed++;
            if (isDup) duplicated++;
            if (movedToOther) moved++;
            if (!isRemoved) {
                active++;
                if (isDup && movedToOther) duplicateExtra++;
            }
        });
        return {
            totalRows: rows.length,
            selectedRows: selected,
            removedRows: removed,
            duplicatedRows: duplicated,
            movedRows: moved,
            activeRows: active,
            duplicateExtraRows: duplicateExtra,
            projectedRowsToAdd: active + duplicateExtra
        };
    }

    get repeatBuyStatusText() {
        const s = this.repeatBuyStats;
        return `Total ${s.totalRows} | Selected ${s.selectedRows} | Active ${s.activeRows} | Duplicate +${s.duplicateExtraRows} | Removed ${s.removedRows} | Projected add ${s.projectedRowsToAdd}`;
    }

    get repeatBuyTotalCount() {
        return (this.repeatBuyAssignments || []).length;
    }

    get repeatBuyAllSelectedGlobal() {
        const rows = this.repeatBuyAssignments || [];
        if (!rows.length) return false;
        return rows.every((r) => r.selected === true);
    }

    get assignmentTargetOptions() {
        const out = [];
        const flat = this.confirmHierarchyFlatList || [];
        flat.forEach((n) => out.push({ label: n.name, value: n.path }));
        return out;
    }

    get isCsvImport() {
        return this.importMethod === 'csv';
    }

    get repeatBuyDuplicateResolutionOptions() {
        return [
            { label: 'Merge duplicate names (recommended)', value: 'MERGE' },
            { label: 'Keep separate and auto-rename duplicates', value: 'RENAME' }
        ];
    }

    /** Create + CSV, or Modify + CSV with no existing groups to count → skip product-count step. */
    get skipProductCountsStepEntirely() {
        if (this.importMethod !== 'csv') return false;
        if (this.isCreate) return true;
        return !(this.existingHierarchyFlatList && this.existingHierarchyFlatList.length);
    }

    get showHierarchyTree() {
        if (!this.isCreate) return false;
        if (this.isCreatePreviousMode) return true;
        if (this.importMethod === 'csv') {
            return !!(this.csvImportData && this.csvImportData.hierarchyJson);
        }
        if (!this.importMethod) return false;
        return this.importMethod === 'manual';
    }
    /** When CSV: pass parsed hierarchy so the tree shows it (read-only). Create or Modify. */
    get csvHierarchyForTree() {
        if (this.isCreatePreviousMode && this._hierarchyJson) return this._hierarchyJson;
        if (this.importMethod !== 'csv' || !this.csvImportData || !this.csvImportData.hierarchyJson) return undefined;
        return this.csvImportData.hierarchyJson;
    }
    get isCsvImportReadOnlyHierarchy() {
        return this.importMethod === 'csv' && !!this.csvImportData;
    }

    /** Modify, CSV pane: show parsed preview tree. */
    get modifyCsvPreviewTreeVisible() {
        return !!(this.csvImportData && this.csvImportData.hierarchyJson);
    }

    get modifyRailExistingClass() {
        const base = 'modify-hierarchy-rail-btn';
        return this.modifyHierarchyRail === 'existing' ? `${base} modify-hierarchy-rail-btn_active` : base;
    }

    get modifyRailManualClass() {
        const base = 'modify-hierarchy-rail-btn';
        return this.modifyHierarchyRail === 'manual' ? `${base} modify-hierarchy-rail-btn_active` : base;
    }

    get modifyRailCsvClass() {
        const base = 'modify-hierarchy-rail-btn';
        return this.modifyHierarchyRail === 'csv' ? `${base} modify-hierarchy-rail-btn_active` : base;
    }

    get modifyPaneExistingClass() {
        let c = 'modify-hierarchy-pane-section';
        if (this.modifyHierarchyRail !== 'existing') c += ' slds-hide';
        return c;
    }

    get modifyPaneManualClass() {
        let c = 'modify-hierarchy-pane-section';
        if (this.modifyHierarchyRail !== 'manual') c += ' slds-hide';
        return c;
    }

    get modifyPaneCsvClass() {
        let c = 'modify-hierarchy-pane-section';
        if (this.modifyHierarchyRail !== 'csv') c += ' slds-hide';
        return c;
    }

    get modifyRailExistingAriaCurrent() {
        return this.modifyHierarchyRail === 'existing' ? 'page' : undefined;
    }

    get modifyRailManualAriaCurrent() {
        return this.modifyHierarchyRail === 'manual' ? 'page' : undefined;
    }

    get modifyRailCsvAriaCurrent() {
        return this.modifyHierarchyRail === 'csv' ? 'page' : undefined;
    }

    get modifyProductCountsRailExistingClass() {
        const base = 'modify-hierarchy-rail-btn';
        return this.modifyProductCountsRail === 'existing' ? `${base} modify-hierarchy-rail-btn_active` : base;
    }

    get modifyProductCountsRailManualClass() {
        const base = 'modify-hierarchy-rail-btn';
        return this.modifyProductCountsRail === 'manual' ? `${base} modify-hierarchy-rail-btn_active` : base;
    }

    get modifyProductCountsPaneExistingClass() {
        let c = 'modify-hierarchy-pane-section';
        if (this.modifyProductCountsRail !== 'existing') c += ' slds-hide';
        return c;
    }

    get modifyProductCountsPaneManualClass() {
        let c = 'modify-hierarchy-pane-section';
        if (this.modifyProductCountsRail !== 'manual') c += ' slds-hide';
        return c;
    }

    get existingGroupCountsJsonForTree() {
        try {
            return JSON.stringify(this._existingGroupCounts || {});
        } catch (e) {
            return '{}';
        }
    }

    get hasNewManualGroupsForProductCounts() {
        if (this.isCreate || this.importMethod === 'csv') return false;
        try {
            const h =
                typeof this._hierarchyJson === 'string'
                    ? JSON.parse(this._hierarchyJson || '{}')
                    : this._hierarchyJson || {};
            return (h.parents && h.parents.length) > 0;
        } catch (e) {
            return false;
        }
    }

    get hasProductCountsModifyExistingPane() {
        return !this.isCreate && (this.existingHierarchyFlatList || []).length > 0;
    }

    get productCountsTreeAllowAdd() {
        return false;
    }

    get productCountsTreeAllowRename() {
        return false;
    }

    get productCountsTreeShowSectionHeader() {
        return false;
    }

    /** Boolean bindings for existing-groups tree (do not use attribute="false" — LWC treats that as true). */
    get existingGroupsTreeShowSectionHeader() {
        return false;
    }

    /** Hierarchy step: manual + modify allow adds; CSV import does not. */
    get hierarchyEditAllowAddNodes() {
        return !this.isCsvImportReadOnlyHierarchy;
    }

    /** Confirm step tree: JSON string for c-rlm-set-up-quote-hierarchy-tree. */
    get confirmDisplayHierarchyJson() {
        const h = this._hierarchyJson;
        if (h == null || h === '') return '{"parents":[]}';
        if (typeof h === 'string') return h;
        try {
            return JSON.stringify(h);
        } catch (e) {
            return '{"parents":[]}';
        }
    }

    get hierarchyConfirmAllowAddNodes() {
        return false;
    }

    get hierarchyConfirmAllowRename() {
        return false;
    }

    get hierarchyConfirmShowSectionHeader() {
        return false;
    }

    get hierarchyConfirmShowProductCounts() {
        return true;
    }

    get hierarchyConfirmSuppressSync() {
        return true;
    }

    get step3NextDisabled() {
        if (this.loading) return true;
        if (!this.isCreate && this.modifyHierarchyRail === 'csv') {
            return !this.csvImportData;
        }
        if (this.isCreate && this.importMethod === 'csv' && !this.csvImportData) return true;
        return false;
    }

    get showNext() {
        return this.step < STEP_CONFIRM;
    }

    get step2NextDisabled() {
        return this.loading || this.quoteInfoNextLocked;
    }

    get showSubmit() {
        return this.step === STEP_CONFIRM;
    }

    get showDone() {
        return this.step === STEP_RESULT;
    }

    /**
     * Account context where this screen action is launched.
     * Use this to stamp created Quote.QuoteAccountId.
     */
    get launchAccountId() {
        if (this.objectApiName === 'Account' && this.recordId) {
            return this.recordId;
        }
        return null;
    }

    /** Step 4 list: when modify = existing + new subgroups + new tree; when create = new tree only. Modify + CSV: existing groups only (products for new tree come from CSV). */
    get productCountsFlatList() {
        if (this.isCreate) {
            if (this.importMethod === 'csv') return [];
            return (this.confirmHierarchyFlatList || []).map((n) => ({ ...n, groupKey: n.path, keyType: 'newTree' }));
        }
        const existingList = (this.existingHierarchyFlatList || []).map((n) => ({
            groupKey: n.tempId || n.id,
            keyType: 'existing',
            name: n.name,
            count: this._existingGroupCounts[n.tempId || n.id] != null ? this._existingGroupCounts[n.tempId || n.id] : 0,
            indentStyle: n.indentStyle
        }));
        if (this.importMethod === 'csv') {
            return existingList;
        }
        const newTreeList = (this.confirmHierarchyFlatList || []).map((n) => ({
            groupKey: n.path,
            keyType: 'newTree',
            name: n.name,
            count: (() => { try { const c = JSON.parse(this._productCountsJson || '{}'); return c[n.path] != null ? c[n.path] : 0; } catch (e) { return 0; } })(),
            indentStyle: n.indentStyle
        }));
        return [...existingList, ...newTreeList];
    }

    get hasProductCountsStep() {
        return this.productCountsFlatList.length > 0;
    }

    get step4EmptyHelperMessage() {
        if (!this.isCreate && this.importMethod === 'csv') {
            return 'No existing groups need demo product counts on this step. New groups use products from your CSV. Go back if you need to change the file.';
        }
        return 'No groups in hierarchy. Go back and add at least one group.';
    }

    /** Modify only: flat list of existing + pending new groups for step 3 display (excluding deleted). */
    get existingHierarchyFlatList() {
        const toDelete = this.groupsToDelete || [];
        const renames = this.groupRenames || {};
        const pending = this.newSubgroupsUnderExisting || [];
        const hideSet = new Set();
        const collectDescendantIds = (nodes) => {
            if (!nodes) return;
            (nodes || []).forEach((n) => {
                const id = n.id || n.Id;
                if (id) hideSet.add(id);
                if (n.children && n.children.length) collectDescendantIds(n.children);
            });
        };
        const parents = (this.existingHierarchy && this.existingHierarchy.parents) || [];
        toDelete.forEach((rootId) => {
            const findAndCollect = (nodes) => {
                if (!nodes) return false;
                for (const n of nodes || []) {
                    if ((n.id || n.Id) === rootId) { collectDescendantIds([n]); return true; }
                    if (findAndCollect(n.children)) return true;
                }
                return false;
            };
            findAndCollect(parents);
        });
        const list = [];
        const addPendingWithDescendants = (parentKey, baseDepth) => {
            pending.filter((p) => p.parentGroupId === parentKey).forEach((p) => {
                list.push({
                    uniqueKey: p.tempId,
                    id: null,
                    tempId: p.tempId,
                    name: p.name,
                    originalName: p.name,
                    lineItemCount: 0,
                    depth: baseDepth,
                    indentStyle: 'margin-left: ' + baseDepth * 20 + 'px',
                    canAddSubgroup: baseDepth < 4,
                    isPending: true
                });
                addPendingWithDescendants(p.tempId, baseDepth + 1);
            });
        };
        const walk = (nodes, depth) => {
            if (!nodes) return;
            (nodes || []).forEach((n) => {
                const id = n.id || n.Id;
                if (id && hideSet.has(id)) return;
                const originalName = n.name || ('Group ' + id);
                list.push({
                    uniqueKey: id,
                    id,
                    tempId: null,
                    name: renames[id] !== undefined ? renames[id] : originalName,
                    originalName,
                    lineItemCount: n.lineItemCount != null ? n.lineItemCount : 0,
                    depth,
                    indentStyle: 'margin-left: ' + depth * 20 + 'px',
                    canAddSubgroup: depth < 4,
                    isPending: false
                });
                pending.filter((p) => p.parentGroupId === id).forEach((p) => {
                    list.push({
                        uniqueKey: p.tempId,
                        id: null,
                        tempId: p.tempId,
                        name: p.name,
                        originalName: p.name,
                        lineItemCount: 0,
                        depth: depth + 1,
                        indentStyle: 'margin-left: ' + (depth + 1) * 20 + 'px',
                        canAddSubgroup: depth + 1 < 4,
                        isPending: true
                    });
                    addPendingWithDescendants(p.tempId, depth + 2);
                });
                if (n.children && n.children.length) walk(n.children, depth + 1);
            });
        };
        walk(parents, 0);
        return list;
    }

    get hasExistingGroupsToShow() {
        return !this.isCreate && this.existingHierarchyFlatList && this.existingHierarchyFlatList.length > 0;
    }

    get showCancel() {
        return this.step === STEP_CREATE_OR_MODIFY;
    }

    get isStep1() { return this.step === STEP_CREATE_OR_MODIFY; }
    get isStep2() { return this.step === STEP_QUOTE_INFO; }
    get isStep3() { return this.step === STEP_HIERARCHY; }
    get isStep4() { return this.step === STEP_ASSIGN_REPEAT; }
    get isStep5() { return this.step === STEP_PRODUCT_COUNTS; }
    get isStep6() { return this.step === STEP_LARGE_DEAL; }
    get isStep7() { return this.step === STEP_CONFIRM; }
    get isStep8() { return this.step === STEP_RESULT; }

    get confirmModeLabel() {
        if (!this.isCreate) return 'Modify';
        if (this.createMode === 'CSV') return 'Create from CSV';
        if (this.createMode === 'PREVIOUS_QUOTES') return 'Create from previous quotes';
        return 'Create from scratch';
    }
    get confirmQuoteLabel() { return this.isCreate ? this.newQuoteName : (this.quoteId || '—'); }
    get confirmGroupsToDeleteCount() { return !this.isCreate && this.groupsToDelete && this.groupsToDelete.length > 0 ? this.groupsToDelete.length : 0; }
    get confirmRenamesCount() {
        if (this.isCreate || !this.existingHierarchy) return 0;
        let count = 0;
        const renames = this.groupRenames || {};
        Object.keys(renames).forEach((id) => {
            const orig = this.originalGroupNamesById[id];
            const ren = String(renames[id] || '').trim();
            if (orig !== undefined && ren && ren !== orig) count++;
        });
        return count;
    }
    get confirmNewSubgroupsCount() { return !this.isCreate && this.newSubgroupsUnderExisting && this.newSubgroupsUnderExisting.length ? this.newSubgroupsUnderExisting.length : 0; }
    get confirmLargeDealLabel() {
        if (this.skipLargeDealStep) return 'Yes (already set on quote)';
        return this.effectiveLargeDeal ? 'Yes' : 'No';
    }

    get createModeScratchClass() {
        const base = 'choice-card';
        return this.createMode === 'SCRATCH' ? `${base} choice-card-selected` : base;
    }

    get createModeCsvClass() {
        const base = 'choice-card';
        return this.createMode === 'CSV' ? `${base} choice-card-selected` : base;
    }

    get createModePreviousClass() {
        const base = 'choice-card';
        return this.createMode === 'PREVIOUS_QUOTES' ? `${base} choice-card-selected` : base;
    }

    get modalCardClass() {
        const base = 'modal-card';
        if (this.step === STEP_HIERARCHY || this.step === STEP_ASSIGN_REPEAT || this.step === STEP_PRODUCT_COUNTS || this.step === STEP_CONFIRM) {
            let c = base + ' modal-card-wide';
            if (!this.isCreate && (this.step === STEP_HIERARCHY || this.step === STEP_PRODUCT_COUNTS)) {
                c += ' modal-card-modify-hierarchy';
            }
            if (this.step === STEP_ASSIGN_REPEAT) c += ' modal-card-repeat-assign';
            return c;
        }
        return base;
    }

    /** For Confirm step: flat list of { path, name, count } from _hierarchyJson + _productCountsJson (read-only summary without hierarchy component). */
    get confirmHierarchyFlatList() {
        let tree = { parents: [] };
        let counts = {};
        try {
            tree = typeof this._hierarchyJson === 'string' ? JSON.parse(this._hierarchyJson || '{}') : (this._hierarchyJson || {});
            if (!tree.parents) tree.parents = [];
        } catch (e) { /* ignore */ }
        try {
            counts = typeof this._productCountsJson === 'string' ? JSON.parse(this._productCountsJson || '{}') : (this._productCountsJson || {});
        } catch (e) { /* ignore */ }
        const list = [];
        const walk = (nodes, basePath) => {
            if (!nodes) return;
            nodes.forEach((n, i) => {
                const path = basePath !== '' ? `${basePath}-${i}` : String(i);
                list.push({ path, name: n.name || ('Group ' + path), depth: path.split('-').length - 1, count: counts[path] != null ? counts[path] : 0 });
                if (n.children && n.children.length) walk(n.children, path);
            });
        };
        walk(tree.parents, '');
        return list.map((n) => ({ ...n, indentStyle: 'margin-left: ' + n.depth * 20 + 'px' }));
    }

    get confirmHasHierarchy() {
        return this.confirmHierarchyFlatList && this.confirmHierarchyFlatList.length > 0;
    }

    get confirmEffectiveProductCountsJson() {
        if (!this.isCreatePreviousMode) return this._productCountsJson;
        const counts = {};
        try {
            const base = typeof this._productCountsJson === 'string' ? JSON.parse(this._productCountsJson || '{}') : (this._productCountsJson || {});
            Object.keys(base || {}).forEach((k) => {
                const n = parseInt(base[k], 10);
                counts[k] = Number.isFinite(n) && n > 0 ? n : 0;
            });
        } catch (e) {
            // keep empty map on parse error
        }
        (this.repeatBuyAssignments || []).forEach((r) => {
            if (r.removed === true) return;
            const source = String(r.sourcePath || '');
            const target = String(r.targetPath || '');
            if (target) counts[target] = (counts[target] || 0) + 1;
            if (r.duplicateToTarget === true && source && source !== target) {
                counts[source] = (counts[source] || 0) + 1;
            }
        });
        return JSON.stringify(counts);
    }

    handleCreate() {
        this.isCreate = true;
        this.largeDealRequiredByThreshold = false;
        this.modifyProductCountsRail = 'existing';
        this.importMethod = 'manual';
        this.createMode = 'SCRATCH';
        this.csvImportData = null;
        this.csvFileError = null;
        this.csvSummary = null;
        this.step = STEP_QUOTE_INFO;
    }

    handleCreateModeChange(event) {
        const mode = event.currentTarget?.dataset?.mode;
        if (!mode) return;
        // Guard against duplicate click interactions on same card.
        if (mode === this.createMode) return;
        this.createMode = mode;
        this.importMethod = mode === 'CSV' ? 'csv' : mode === 'SCRATCH' ? 'manual' : null;
        this.repeatBuySelectedQuoteIds = [];
        this.repeatBuyPayload = [];
        this.repeatBuyAssignments = [];
        this.repeatBuySelectedMasterKey = '';
        this._hierarchyJson = null;
        this._productCountsJson = '{}';
        if (mode === 'PREVIOUS_QUOTES' && !this.repeatBuyAccountsLoading && (!this.repeatBuyAccountOptions || this.repeatBuyAccountOptions.length === 0)) {
            this.loadRepeatBuyAccounts();
        }
        // Prevent accidental click-through to Next after card rerender.
        this.quoteInfoNextLocked = true;
        window.clearTimeout(this._quoteInfoNextLockTimer);
        this._quoteInfoNextLockTimer = window.setTimeout(() => {
            this.quoteInfoNextLocked = false;
            this._quoteInfoNextLockTimer = null;
        }, 350);
    }

    async loadRepeatBuyAccounts() {
        this.repeatBuyAccountsLoading = true;
        this.repeatBuyAccountOptions = [];
        try {
            const rows = await getAccountsForRepeatBuy();
            this.repeatBuyAccountOptions = (rows || []).map((r) => ({ label: r.label, value: r.value }));
        } catch (e) {
            this.repeatBuyAccountOptions = [];
        }
        this.repeatBuyAccountsLoading = false;
    }

    handleRepeatBuyAccountChange(event) {
        this.repeatBuyAccountId = (event.detail?.value || '').trim();
        this.repeatBuyQuoteOptions = [];
        this.repeatBuySelectedQuoteIds = [];
        if (this.repeatBuyAccountId) {
            this.handleLoadRepeatBuyQuotes();
        }
    }

    async handleLoadRepeatBuyQuotes() {
        if (!this.repeatBuyAccountId) return;
        this.repeatBuyQuotesLoading = true;
        this.repeatBuyQuoteOptions = [];
        try {
            const rows = await getRecentQuotesForRepeatBuy({ accountId: this.repeatBuyAccountId });
            this.repeatBuyQuoteOptions = (rows || []).map((r) => ({ label: r.label, value: r.value }));
        } catch (e) {
            this.repeatBuyQuoteOptions = [];
        }
        this.repeatBuyQuotesLoading = false;
    }

    handleRepeatBuyQuotesSelect(event) {
        this.repeatBuySelectedQuoteIds = event.detail?.value || [];
    }

    handleRepeatBuyFilterChange(event) {
        this.repeatBuyFilter = event.detail?.value || '';
    }

    async loadRepeatBuyLinesAndSeedHierarchy() {
        if (!this.repeatBuyHasQuoteSelection) return;
        this.repeatBuyLinesLoading = true;
        this.repeatBuyPayload = [];
        this.repeatBuyAssignments = [];
        this.repeatBuySelectedMasterKey = '';
        try {
            const raw = await getRepeatBuyLines({ quoteIdsJson: JSON.stringify(this.repeatBuySelectedQuoteIds) });
            const payload = typeof raw === 'string' ? JSON.parse(raw || '[]') : raw || [];
            this.repeatBuyPayload = payload;
            this.seedHierarchyAndAssignmentsFromRepeatPayload(payload);
        } catch (e) {
            this.repeatBuyPayload = [];
            this.repeatBuyAssignments = [];
            this._hierarchyJson = '{"parents":[]}';
        }
        this.repeatBuyLinesLoading = false;
    }

    seedHierarchyAndAssignmentsFromRepeatPayload(payload) {
        const parents = [];
        const assignments = [];
        let rootIdx = 0;
        (payload || []).forEach((q, qi) => {
            const byGroup = {};
            (q.lines || []).forEach((line) => {
                const g = line.groupName || 'Ungrouped';
                if (!byGroup[g]) byGroup[g] = [];
                byGroup[g].push(line);
            });
            let gi = 0;
            const orderedGroups = Object.keys(byGroup).sort((a, b) => {
                const an = String(a || '').toLowerCase();
                const bn = String(b || '').toLowerCase();
                const rank = (n) => {
                    if (!n || n === 'ungrouped') return 3;
                    if (n.includes('parent')) return 0;
                    if (n.includes('child')) return 2;
                    return 1;
                };
                const ra = rank(an);
                const rb = rank(bn);
                if (ra !== rb) return ra - rb;
                return an.localeCompare(bn);
            });
            orderedGroups.forEach((gName) => {
                const groupPath = String(rootIdx++);
                gi++;
                parents.push({ name: gName, path: groupPath, children: [] });
                byGroup[gName].forEach((line, li) => {
                    assignments.push({
                        key: `${q.quoteId}-${groupPath}-${li}`,
                        selected: false,
                        sourceQuoteKey: String(qi),
                        sourcePath: groupPath,
                        targetPath: groupPath,
                        duplicateToTarget: false,
                        removed: false,
                        quoteLabel: q.quoteLabel,
                        historicalGroupName: gName,
                        productName: line.productName,
                        productCode: line.productCode,
                        quantity: line.editableQuantity != null ? line.editableQuantity : line.historicalQuantity,
                        historicalQuantity: line.historicalQuantity,
                        historicalUnitPrice: line.historicalUnitPrice,
                        historicalNetTotal: line.historicalNetTotal,
                        productIdentifier: line.productCode || line.productName
                    });
                });
            });
        });
        this._hierarchyJson = JSON.stringify({ parents: parents || [] });
        this._productCountsJson = '{}';
        this.repeatBuyAssignments = assignments;
        this.repeatBuySelectedMasterKey = assignments.length ? `quote:${assignments[0].sourceQuoteKey}` : '';
    }

    handleRepeatBuyMasterSelect(event) {
        this.repeatBuySelectedMasterKey = event.currentTarget?.dataset?.masterKey || '';
    }

    handleAssignmentQuantityChange(event) {
        const key = event.currentTarget?.dataset?.key;
        const v = parseInt(event.detail?.value, 10);
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.key === key ? { ...r, quantity: Number.isFinite(v) && v > 0 ? v : 1 } : r
        );
    }

    handleAssignmentSelectChange(event) {
        const key = event.currentTarget?.dataset?.key;
        const checked = event.detail?.checked === true;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.key === key ? { ...r, selected: checked } : r
        );
    }

    handleAssignmentTargetChange(event) {
        const key = event.currentTarget?.dataset?.key;
        const targetPath = event.detail?.value;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.key === key ? { ...r, targetPath } : r
        );
    }

    handleRepeatBuyBulkTargetChange(event) {
        this.repeatBuyBulkTargetPath = event.detail?.value || '';
    }

    handleSelectAllRowsGlobal(event) {
        const checked = event.detail?.checked === true;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) => ({ ...r, selected: checked }));
    }

    handleApplyTargetToSelected() {
        const targetPath = this.repeatBuyBulkTargetPath;
        if (!targetPath) return;
        const selectedCount = this.repeatBuySelectedCount;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.selected === true ? { ...r, targetPath } : r
        );
        this.repeatBuyLastActionMessage = `${selectedCount} selected row(s) updated with target group.`;
    }

    handleBulkDuplicateSelected() {
        const selectedCount = this.repeatBuySelectedCount;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.selected === true ? { ...r, duplicateToTarget: true } : r
        );
        this.repeatBuyLastActionMessage = `${selectedCount} selected row(s) marked as Duplicate to target.`;
    }

    handleBulkRemoveSelected() {
        const selectedCount = this.repeatBuySelectedCount;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.selected === true ? { ...r, removed: true } : r
        );
        this.repeatBuyLastActionMessage = `${selectedCount} selected row(s) marked as Remove from add.`;
    }

    handleBulkRestoreSelected() {
        const selectedCount = this.repeatBuySelectedCount;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.selected === true ? { ...r, removed: false } : r
        );
        this.repeatBuyLastActionMessage = `${selectedCount} selected row(s) restored.`;
    }

    handleAssignmentDuplicateChange(event) {
        const key = event.currentTarget?.dataset?.key;
        const checked = event.detail?.checked === true;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.key === key ? { ...r, duplicateToTarget: checked } : r
        );
    }

    handleAssignmentRemoveChange(event) {
        const key = event.currentTarget?.dataset?.key;
        const checked = event.detail?.checked === true;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.key === key ? { ...r, removed: checked } : r
        );
    }

    handleAssignmentDuplicateAction(event) {
        const key = event.currentTarget?.dataset?.key;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.key === key ? { ...r, duplicateToTarget: !(r.duplicateToTarget === true) } : r
        );
        const row = (this.repeatBuyAssignments || []).find((r) => r.key === key);
        this.repeatBuyLastActionMessage = row && row.duplicateToTarget
            ? '1 row marked as duplicate to target.'
            : '1 row unmarked from duplicate.';
    }

    handleAssignmentRemoveAction(event) {
        const key = event.currentTarget?.dataset?.key;
        this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) =>
            r.key === key ? { ...r, removed: !(r.removed === true) } : r
        );
        const row = (this.repeatBuyAssignments || []).find((r) => r.key === key);
        this.repeatBuyLastActionMessage = row && row.removed
            ? '1 row marked as remove from add.'
            : '1 row restored.';
    }

    async handleModify() {
        this.isCreate = false;
        this.largeDealRequiredByThreshold = false;
        this.quoteId = '';
        this.modifyHierarchyRail = 'existing';
        this.modifyProductCountsRail = 'existing';
        this.importMethod = 'manual';
        this.csvImportData = null;
        this.csvFileError = null;
        this.csvSummary = null;
        this.csvFileName = null;
        this.step = STEP_QUOTE_INFO;
        await this.loadQuoteOptions();
    }

    async loadQuoteOptions() {
        this.quoteOptionsLoading = true;
        this.quoteOptions = [];
        try {
            const list = await getQuotesForModify();
            this.quoteOptions = (list || []).map((o) => ({
                value: o.value,
                label: o.label,
                isLargeDeal: o.isLargeDeal === 'true' ? 'true' : 'false'
            }));
        } catch (e) {
            this.quoteOptions = [];
        }
        this.quoteOptionsLoading = false;
    }

    handleQuoteSelect(event) {
        this.quoteId = event.detail.value || '';
    }

    handleNewQuoteNameChange(event) {
        this.newQuoteName = (event.detail?.value || '').trim();
    }

    handleNewQuoteNameInput(event) {
        this.newQuoteName = (event.detail?.value || '').trim();
    }

    handleQuoteNameKeydown(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            event.stopPropagation();
        }
    }

    /** Split CSV text into rows; newlines inside double-quoted fields are not treated as row breaks. */
    _splitCsvLines(str) {
        const result = [];
        let i = 0;
        let inQuote = false;
        let start = 0;
        while (i < str.length) {
            const c = str[i];
            if (c === '"') {
                if (inQuote && i + 1 < str.length && str[i + 1] === '"') {
                    i += 2;
                    continue;
                }
                inQuote = !inQuote;
                i++;
                continue;
            }
            if (!inQuote && (c === '\n' || c === '\r')) {
                const line = str.slice(start, i).trim();
                if (line.length) result.push(line);
                if (c === '\r' && i + 1 < str.length && str[i + 1] === '\n') i += 2;
                else i += 1;
                start = i;
                continue;
            }
            i++;
        }
        const line = str.slice(start).trim();
        if (line.length) result.push(line);
        return result;
    }

    /** Parse CSV and build hierarchy + line items. Returns { hierarchyJson, csvImportLineItemsJson, summary, error }. */
    parseCsvToImportData(csvText) {
        const out = { hierarchyJson: null, csvImportLineItemsJson: null, summary: { rowCount: 0, groupCount: 0, lineItemCount: 0 }, error: null };
        if (!csvText || typeof csvText !== 'string') {
            out.error = 'No file content';
            return out;
        }
        const text = csvText.replace(/^\uFEFF/, '');
        const lines = this._splitCsvLines(text);
        if (lines.length < 2) {
            out.error = 'CSV must have header and at least one data row';
            return out;
        }
        const parseRow = (line) => {
            const result = [];
            let i = 0;
            while (i < line.length) {
                if (line[i] === '"') {
                    i++;
                    let cell = '';
                    while (i < line.length) {
                        if (line[i] === '"' && line[i + 1] === '"') {
                            cell += '"';
                            i += 2;
                        } else if (line[i] === '"') {
                            i++;
                            break;
                        } else {
                            cell += line[i];
                            i++;
                        }
                    }
                    result.push(cell);
                    if (i < line.length && line[i] === ',') i++;
                } else {
                    let cell = '';
                    while (i < line.length && line[i] !== ',') cell += line[i++];
                    result.push(cell.trim());
                    if (i < line.length && line[i] === ',') i++;
                }
            }
            if (line.length > 0 && line[line.length - 1] === ',') result.push('');
            return result;
        };
        const expectedCols = ['Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5', 'Bundle Product', 'Product', 'Quantity'];
        const rawFirstLine = lines[0];
        let headerCells = parseRow(rawFirstLine).map((c) => (c || '').trim());
        // Workaround: some CSVs (e.g. Excel with quoted "Bundle Product\t") produce 9 columns with empty [6]; accept and normalize
        let normalizeNineCols = false;
        if (headerCells.length === 9 && headerCells[6] === '' && headerCells[7] === 'Product' && headerCells[8] === 'Quantity') {
            headerCells = headerCells.slice(0, 6).concat(headerCells.slice(7));
            normalizeNineCols = true;
        }
        const headerOk = headerCells.length >= 8 && !expectedCols.some((name, idx) => headerCells[idx] !== name);
        if (!headerOk) {
            // Log full debug details to console for developer diagnosis; show only an actionable message in the UI.
            const cellRepr = (s) => {
                if (s == null) return 'null';
                const codes = [];
                for (let k = 0; k < Math.min(s.length, 20); k++) codes.push(s.charCodeAt(k));
                return JSON.stringify(s) + ' (len=' + s.length + ' codes=' + codes.join(',') + ')';
            };
            const charCodes = [];
            for (let k = 0; k < Math.min(rawFirstLine.length, 15); k++) charCodes.push(rawFirstLine.charCodeAt(k));
            let debugInfo = '[CSV header mismatch]\n';
            debugInfo += 'Raw first line length: ' + rawFirstLine.length + ', first 15 char codes: ' + charCodes.join(',') + '\n';
            debugInfo += 'Raw first line (JSON): ' + JSON.stringify(rawFirstLine) + '\n';
            debugInfo += 'Parsed column count: ' + headerCells.length + '\n';
            expectedCols.forEach((name, idx) => {
                const match = headerCells[idx] === name;
                debugInfo += '  [' + idx + '] expected ' + JSON.stringify(name) + ' => ' + (match ? 'OK' : 'MISMATCH (got ' + cellRepr(headerCells[idx]) + ')') + '\n';
            });
            // eslint-disable-next-line no-console
            console.error(debugInfo);
            out.error = 'Invalid CSV header. Expected: ' + CSV_HEADER + '. Check that the file was exported from the correct template and has not been modified.';
            return out;
        }
        const norm = (s) => (s || '').trim().replace(/\s+/g, '');
        const pathKey = (g1, g2, g3, g4, g5) => [g1 || '', g2 || '', g3 || '', g4 || '', g5 || ''].join('|');
        const pathKeyNorm = (g1, g2, g3, g4, g5) => [norm(g1), norm(g2), norm(g3), norm(g4), norm(g5)].join('|');
        const pathOrder = [];
        const pathToPathIndex = new Map();
        /** First spelling seen for each normalized Group 1 — keeps one root label when CSV varies spacing (e.g. Fire Bizz Case vs FireBizz Case). */
        const canonicalG1ByNorm = new Map();
        const lineItems = [];
        let rowCount = 0;
        for (let r = 1; r < lines.length; r++) {
            let cells = parseRow(lines[r]);
            if (normalizeNineCols && cells.length === 9) cells = cells.slice(0, 6).concat(cells.slice(7));
            if (cells.length < 8) continue;
            const g1 = (cells[0] || '').trim();
            const g2 = (cells[1] || '').trim();
            const g3 = (cells[2] || '').trim();
            const g4 = (cells[3] || '').trim();
            const g5 = (cells[4] || '').trim();
            const bundleProduct = (cells[5] || '').trim();
            const product = (cells[6] || '').trim();
            const qtyStr = (cells[7] || '').trim();
            if (bundleProduct && product) continue;
            if (g1) {
                const n1 = norm(g1);
                if (!canonicalG1ByNorm.has(n1)) {
                    canonicalG1ByNorm.set(n1, g1);
                }
            }
            const key = pathKeyNorm(g1, g2, g3, g4, g5);
            if (!pathToPathIndex.has(key)) {
                pathToPathIndex.set(key, pathOrder.length);
                const g1Stable = g1 ? canonicalG1ByNorm.get(norm(g1)) : g1;
                pathOrder.push({ g1: g1Stable || g1, g2, g3, g4, g5 });
            }
            rowCount++;
        }
        const keyToPath = new Map();
        const buildTree = () => {
            const keyToNode = new Map();
            const getOrCreate = (k, name) => {
                if (keyToNode.has(k)) return keyToNode.get(k);
                const node = { name: name || k.split('|').find(Boolean) || 'Group', path: '', children: [] };
                keyToNode.set(k, node);
                return node;
            };
            pathOrder.forEach((po) => {
                const k1 = pathKeyNorm(po.g1, '', '', '', '');
                const k2 = pathKeyNorm(po.g1, po.g2, '', '', '');
                const k3 = pathKeyNorm(po.g1, po.g2, po.g3, '', '');
                const k4 = pathKeyNorm(po.g1, po.g2, po.g3, po.g4, '');
                const k5 = pathKeyNorm(po.g1, po.g2, po.g3, po.g4, po.g5);
                const name5 = [po.g5, po.g4, po.g3, po.g2, po.g1].find(Boolean) || 'Group';
                getOrCreate(k1, po.g1 || 'Group 1');
                getOrCreate(k2, po.g2 || null);
                getOrCreate(k3, po.g3 || null);
                getOrCreate(k4, po.g4 || null);
                const leaf = getOrCreate(k5, name5);
                const parent4 = po.g4 ? getOrCreate(k4, po.g4) : null;
                const parent3 = po.g3 ? getOrCreate(k3, po.g3) : null;
                const parent2 = po.g2 ? getOrCreate(k2, po.g2) : null;
                const parent1 = getOrCreate(k1, po.g1 || 'Group 1');
                if (leaf === parent1) return;
                const g2 = (po.g2 || '').trim();
                const g3 = (po.g3 || '').trim();
                const g4 = (po.g4 || '').trim();
                const g5 = (po.g5 || '').trim();
                const p4 = g5 && parent4;
                const p3 = g4 && parent3;
                const p2 = g3 && parent2;
                const p1 = g2 && parent1;
                if (p4 && p4.children.indexOf(leaf) < 0) p4.children.push(leaf);
                else if (p3 && p3.children.indexOf(leaf) < 0) p3.children.push(leaf);
                else if (p2 && p2.children.indexOf(leaf) < 0) p2.children.push(leaf);
                else if (p1 && p1.children.indexOf(leaf) < 0) p1.children.push(leaf);
                else if (parent1 && parent1.children.indexOf(leaf) < 0) parent1.children.push(leaf);
            });
            const assignPaths = (nodes, prefix) => {
                nodes.forEach((n, i) => {
                    n.path = prefix !== '' ? prefix + '-' + i : String(i);
                    if (n.children && n.children.length) assignPaths(n.children, n.path);
                });
            };
            const roots = [];
            const seen = new Set();
            pathOrder.forEach((po) => {
                const k1 = pathKeyNorm(po.g1, '', '', '', '');
                if (!seen.has(k1)) {
                    seen.add(k1);
                    roots.push(keyToNode.get(k1));
                }
            });
            assignPaths(roots, '');
            keyToNode.forEach((node, k) => {
                if (node.children.length === 0 && node.path) keyToPath.set(k, node.path);
            });
            return { parents: roots };
        };
        const tree = buildTree();
        const lineItemsWithPath = [];
        for (let r = 1; r < lines.length; r++) {
            let cells = parseRow(lines[r]);
            if (normalizeNineCols && cells.length === 9) cells = cells.slice(0, 6).concat(cells.slice(7));
            if (cells.length < 8) continue;
            const bundleProduct = (cells[5] || '').trim();
            const product = (cells[6] || '').trim();
            if (bundleProduct && product) continue;
            let productIdentifier = bundleProduct || product;
            if (!productIdentifier) continue;
            const key = pathKeyNorm((cells[0] || '').trim(), (cells[1] || '').trim(), (cells[2] || '').trim(), (cells[3] || '').trim(), (cells[4] || '').trim());
            const path = keyToPath.get(key);
            if (path === undefined) continue;
            // Rule: if no quantity is provided, treat quantity as 1
            let qty = 1;
            const qtyStr = (cells[7] || '').trim();
            if (qtyStr && !isNaN(Number(qtyStr))) qty = Math.max(1, Math.floor(Number(qtyStr)));
            // Strip erroneous trailing ",N" from product cell (e.g. "QB-NETSECURE-10G,2" → "QB-NETSECURE-10G"); quantity always from Quantity column
            if (productIdentifier.includes(',')) {
                const lastComma = productIdentifier.lastIndexOf(',');
                const after = productIdentifier.slice(lastComma + 1).trim();
                const num = parseInt(after, 10);
                if (after !== '' && !isNaN(num) && num >= 0 && String(num) === after) {
                    productIdentifier = productIdentifier.slice(0, lastComma).trim();
                }
            }
            lineItemsWithPath.push({ path, productIdentifier, quantity: qty });
        }
        out.hierarchyJson = JSON.stringify(tree);
        out.csvImportLineItemsJson = JSON.stringify(lineItemsWithPath);
        out.summary = { rowCount, groupCount: pathOrder.length, lineItemCount: lineItemsWithPath.length };
        return out;
    }

    handleImportMethodChoice(event) {
        const choice = event.currentTarget.dataset.choice;
        this.importMethod = choice === 'csv' ? 'csv' : 'manual';
        this.csvImportData = null;
        this.csvFileError = null;
        this.csvSummary = null;
        this.csvFileName = null;
    }

    handleCsvFileChange(event) {
        const file = event.target.files && event.target.files[0];
        this.csvFileError = null;
        this.csvSummary = null;
        this.csvImportData = null;
        this.csvFileName = file ? file.name : null;
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
            const text = reader.result || '';
            const result = this.parseCsvToImportData(text);
            if (result.error) {
                this.csvFileError = result.error;
                return;
            }
            this.csvImportData = { hierarchyJson: result.hierarchyJson, csvImportLineItemsJson: result.csvImportLineItemsJson };
            this.csvSummary = result.summary;
        };
        reader.readAsText(file);
    }

    handleHierarchyNextForCsv() {
        if (!this.csvImportData || !this.csvImportData.hierarchyJson) return;
        this._hierarchyJson = this.csvImportData.hierarchyJson;
        this._productCountsJson = '{}';
        if (this.isCreate) {
            this.step = STEP_LARGE_DEAL;
            return;
        }
        const hasExisting = (this.existingHierarchyFlatList || []).length > 0;
        if (hasExisting) {
            this.step = STEP_PRODUCT_COUNTS;
        } else if (this.skipLargeDealStep) {
            this.largeDeal = true;
            this.step = STEP_CONFIRM;
        } else {
            this.step = STEP_LARGE_DEAL;
        }
    }

    async handleQuoteInfoNext() {
        if (this.isCreate) {
            const el = this.template.querySelector('lightning-input[data-step="quote-name"]');
            if (el) {
                this.newQuoteName = (el.value || '').trim();
            } else {
                this.newQuoteName = (this.newQuoteName || '').trim();
            }
            if (!this.newQuoteName) {
                if (el) {
                    el.setCustomValidity('New quote name is required.');
                    el.reportValidity();
                }
                return;
            }
            if (el) {
                el.setCustomValidity('');
                el.reportValidity();
            }
            if (this.createMode === 'PREVIOUS_QUOTES') {
                const quotesEl = this.template.querySelector('lightning-dual-listbox[name="repeatbuy-quotes"]');
                if (!this.repeatBuyHasQuoteSelection) {
                    if (quotesEl) {
                        quotesEl.setCustomValidity('Select at least one source quote.');
                        quotesEl.reportValidity();
                    }
                    return;
                }
                if (quotesEl) {
                    quotesEl.setCustomValidity('');
                    quotesEl.reportValidity();
                }
                await this.loadRepeatBuyLinesAndSeedHierarchy();
            }
            if (!this.isCreatePreviousMode) {
                // Keep Step 3 source in sync with the Step 2 create mode selection.
                this.importMethod = this.createMode === 'CSV' ? 'csv' : 'manual';
            }
        } else {
            if (!this.quoteId || !this.quoteId.trim()) return;
            this.existingHierarchyLoading = true;
            this.existingHierarchy = null;
            this.groupsToDelete = [];
            this.groupRenames = {};
            this.newSubgroupsUnderExisting = [];
            this._existingGroupCounts = {};
            try {
                const raw = await getQuoteHierarchy({ quoteId: this.quoteId });
                const parsed = typeof raw === 'string' ? JSON.parse(raw || '{}') : (raw || {});
                this.existingHierarchy = parsed;
            } catch (e) {
                this.existingHierarchy = { parents: [] };
            }
            this.captureOriginalGroupNamesFromHierarchy();
            this.existingTreeDisplayJson = this.buildExistingGroupsTreeJson();
            this.existingHierarchyLoading = false;
            this.importMethod = 'manual';
            this.modifyHierarchyRail = 'existing';
            this.modifyProductCountsRail = 'existing';
            this.csvImportData = null;
            this.csvFileError = null;
            this.csvSummary = null;
            this.csvFileName = null;
        }
        this.step = STEP_HIERARCHY;
    }

    captureOriginalGroupNamesFromHierarchy() {
        this.originalGroupNamesById = {};
        const walk = (nodes) => {
            (nodes || []).forEach((n) => {
                const id = n.id || n.Id;
                if (id) {
                    const nm = (n.name || '').trim();
                    this.originalGroupNamesById[id] = nm || 'Group ' + id;
                }
                walk(n.children || []);
            });
        };
        walk((this.existingHierarchy && this.existingHierarchy.parents) || []);
    }

    buildExistingGroupsTreeJson() {
        const parents = (this.existingHierarchy && this.existingHierarchy.parents) || [];
        const toDelete = this.groupsToDelete || [];
        const pending = this.newSubgroupsUnderExisting || [];
        const renames = this.groupRenames || {};
        const hideSet = new Set();
        const collectDescendantIds = (nodes) => {
            (nodes || []).forEach((n) => {
                const id = n.id || n.Id;
                if (id) hideSet.add(id);
                collectDescendantIds(n.children || []);
            });
        };
        toDelete.forEach((rootId) => {
            const findAndCollect = (nodes) => {
                if (!nodes) return false;
                for (const n of nodes) {
                    if ((n.id || n.Id) === rootId) {
                        collectDescendantIds([n]);
                        return true;
                    }
                    if (findAndCollect(n.children)) return true;
                }
                return false;
            };
            findAndCollect(parents);
        });

        const mapPendingSubtree = (parentKey) =>
            pending
                .filter((p) => p.parentGroupId === parentKey)
                .map((p) => ({
                    name: p.name,
                    tempId: p.tempId,
                    lineItemCount: 0,
                    children: mapPendingSubtree(p.tempId)
                }));

        const mapServerNode = (n) => {
            const id = n.id || n.Id;
            if (!id || hideSet.has(id)) return null;
            const originalName = n.name || 'Group ' + id;
            const name = renames[id] !== undefined ? renames[id] : originalName;
            const serverChildren = (n.children || []).map(mapServerNode).filter(Boolean);
            const pendingChildren = mapPendingSubtree(id);
            return {
                name,
                sfId: id,
                lineItemCount: n.lineItemCount != null ? n.lineItemCount : 0,
                children: [...serverChildren, ...pendingChildren]
            };
        };

        const roots = parents.map(mapServerNode).filter(Boolean);
        return JSON.stringify({ parents: roots });
    }

    removePendingSubgroupBranch(tempId) {
        const pending = this.newSubgroupsUnderExisting || [];
        const toRemove = new Set([tempId]);
        let changed = true;
        while (changed) {
            changed = false;
            for (const p of pending) {
                if (toRemove.has(p.parentGroupId) && !toRemove.has(p.tempId)) {
                    toRemove.add(p.tempId);
                    changed = true;
                }
            }
        }
        this.newSubgroupsUnderExisting = pending.filter((p) => !toRemove.has(p.tempId));
    }

    extractPendingSubgroupsFromTree(nodes) {
        const out = [];
        const walk = (arr, parentKey) => {
            (arr || []).forEach((n) => {
                if (n.tempId && !n.sfId) {
                    out.push({ parentGroupId: parentKey, name: n.name, tempId: n.tempId });
                }
                walk(n.children || [], n.sfId || n.tempId);
            });
        };
        walk(nodes, null);
        return out;
    }

    applyExistingTreeStateFromJson(jsonStr) {
        if (!jsonStr || typeof jsonStr !== 'string') return;
        let tree;
        try {
            tree = JSON.parse(jsonStr);
        } catch (e) {
            return;
        }
        const nextRenames = {};
        const walkR = (nodes) => {
            (nodes || []).forEach((n) => {
                if (n.sfId && this.originalGroupNamesById[n.sfId] !== undefined) {
                    const orig = this.originalGroupNamesById[n.sfId];
                    const nm = String(n.name || '').trim();
                    if (nm && nm !== orig) nextRenames[n.sfId] = nm;
                }
                walkR(n.children || []);
            });
        };
        walkR(tree.parents || []);
        this.groupRenames = nextRenames;
        this.newSubgroupsUnderExisting = this.extractPendingSubgroupsFromTree(tree.parents || []);
    }

    syncExistingTreeFromChild() {
        const el = this.template.querySelector('c-rlm-set-up-quote-hierarchy-tree[data-step="existing-hierarchy-tree"]');
        if (!el || this.isCreate) return;
        const json = el.hierarchyJson;
        if (json) this.applyExistingTreeStateFromJson(json);
    }

    handleExistingTreeMutated(event) {
        const json = event.detail && event.detail.hierarchyJson;
        if (json) this.applyExistingTreeStateFromJson(json);
    }

    handleExistingTreeGroupDelete(event) {
        const d = event.detail || {};
        if (d.sfId) {
            const id = d.sfId;
            if (!(this.groupsToDelete || []).includes(id)) {
                this.groupsToDelete = [...(this.groupsToDelete || []), id];
            }
        } else if (d.tempId) {
            this.removePendingSubgroupBranch(d.tempId);
        }
        this.existingTreeDisplayJson = this.buildExistingGroupsTreeJson();
    }

    _clearModifyCsvFileState() {
        this.csvImportData = null;
        this.csvFileError = null;
        this.csvSummary = null;
        this.csvFileName = null;
    }

    _readHierarchyEditSnapshot() {
        const el = this.template.querySelector('c-rlm-set-up-quote-hierarchy-tree[data-step="hierarchy-edit"]');
        if (!el) {
            return { tree: '{"parents":[]}', counts: '{}' };
        }
        const tree =
            typeof el.getLiveHierarchyJson === 'function'
                ? el.getLiveHierarchyJson()
                : el.hierarchyJson || '{"parents":[]}';
        const counts =
            typeof el.getLiveProductCountsJson === 'function'
                ? el.getLiveProductCountsJson()
                : el.productCountsJson || '{}';
        return {
            tree: tree != null && tree !== '' ? tree : '{"parents":[]}',
            counts: counts != null && counts !== '' ? counts : '{}'
        };
    }

    handleModifyRailSelect(event) {
        const rail = event.currentTarget && event.currentTarget.dataset ? event.currentTarget.dataset.rail : null;
        if (!rail) return;
        const prev = this.modifyHierarchyRail;
        if (prev === 'manual' && rail !== 'manual') {
            const { tree } = this._readHierarchyEditSnapshot();
            this._hierarchyJson = tree;
        }
        if (rail === 'manual') {
            if (prev === 'csv') this._clearModifyCsvFileState();
            this.importMethod = 'manual';
        } else if (rail === 'csv') {
            if (prev === 'manual') this._clearModifyCsvFileState();
            this.importMethod = 'csv';
        }
        this.modifyHierarchyRail = rail;
    }

    handleHierarchyNext() {
        if (!this.isCreate) {
            this.syncExistingTreeFromChild();
        }
        if (this.importMethod === 'csv') {
            this.handleHierarchyNextForCsv();
            return;
        }
        const { tree, counts } = this._readHierarchyEditSnapshot();
        const parents = (() => { try { return JSON.parse(tree).parents || []; } catch (e) { return []; } })();
        if (this.isCreate && !parents.length) return;
        let resolvedTree = tree;
        if (this.isCreatePreviousMode) {
            if (this.repeatBuyDuplicateResolutionMode === 'MERGE') {
                resolvedTree = this.mergeDuplicateTopLevelGroups(resolvedTree);
            } else if (this.repeatBuyDuplicateResolutionMode === 'RENAME') {
                resolvedTree = this.renameDuplicateGroups(resolvedTree);
            }
        }
        const dup = this.findDuplicateGroupName(resolvedTree);
        if (dup) {
            this.hierarchyValidationError = `Duplicate group name is not allowed: ${dup}`;
            return;
        }
        this.hierarchyValidationError = null;
        this._hierarchyJson = resolvedTree;
        this._productCountsJson = counts;
        this.step = this.isCreatePreviousMode ? STEP_ASSIGN_REPEAT : STEP_PRODUCT_COUNTS;
    }

    handleRepeatBuyDuplicateResolutionChange(event) {
        this.repeatBuyDuplicateResolutionMode = event.detail?.value || 'MERGE';
    }

    findDuplicateGroupName(treeJson) {
        try {
            const tree = typeof treeJson === 'string' ? JSON.parse(treeJson || '{}') : treeJson || {};
            const seen = new Set();
            let dup = null;
            const walk = (nodes) => {
                (nodes || []).forEach((n) => {
                    const nm = String(n.name || '').trim().toLowerCase();
                    if (nm) {
                        if (seen.has(nm) && dup == null) dup = n.name;
                        seen.add(nm);
                    }
                    walk(n.children || []);
                });
            };
            walk(tree.parents || []);
            return dup;
        } catch (e) {
            return null;
        }
    }

    renameDuplicateGroups(treeJson) {
        try {
            const tree = typeof treeJson === 'string' ? JSON.parse(treeJson || '{}') : (treeJson || {});
            const seen = new Map();
            const walk = (nodes) => {
                (nodes || []).forEach((n) => {
                    const raw = String(n.name || '').trim();
                    const key = raw.toLowerCase();
                    if (key) {
                        const c = seen.get(key) || 0;
                        if (c > 0) n.name = `${raw} (${c + 1})`;
                        seen.set(key, c + 1);
                    }
                    walk(n.children || []);
                });
            };
            walk(tree.parents || []);
            return JSON.stringify(tree);
        } catch (e) {
            return treeJson;
        }
    }

    mergeDuplicateTopLevelGroups(treeJson) {
        try {
            const tree = typeof treeJson === 'string' ? JSON.parse(treeJson || '{}') : (treeJson || {});
            const parents = tree.parents || [];
            const merged = [];
            const byName = new Map();
            const remap = new Map();
            parents.forEach((p, idx) => {
                const nm = String(p.name || '').trim();
                const key = nm.toLowerCase();
                if (!byName.has(key)) {
                    const clone = { ...p, children: [...(p.children || [])] };
                    byName.set(key, merged.length);
                    merged.push(clone);
                } else {
                    const keepIdx = byName.get(key);
                    const keep = merged[keepIdx];
                    keep.children = [...(keep.children || []), ...(p.children || [])];
                }
                remap.set(String(idx), String(byName.get(key)));
            });
            tree.parents = merged;
            const remapPath = (path) => {
                const s = String(path || '');
                if (!s) return s;
                const parts = s.split('-');
                const first = remap.get(parts[0]);
                if (first == null) return s;
                parts[0] = first;
                return parts.join('-');
            };
            this.repeatBuyAssignments = (this.repeatBuyAssignments || []).map((r) => ({
                ...r,
                sourcePath: remapPath(r.sourcePath),
                targetPath: remapPath(r.targetPath)
            }));
            return JSON.stringify(tree);
        } catch (e) {
            return treeJson;
        }
    }

    handleModifyProductCountsRailSelect(event) {
        const rail = event.currentTarget && event.currentTarget.dataset ? event.currentTarget.dataset.rail : null;
        if (rail === 'existing' || rail === 'manual') this.modifyProductCountsRail = rail;
        this.scheduleQuoteLinePreviewRefresh();
    }

    get showQuoteLinePreviewBanner() {
        return (this.step === STEP_PRODUCT_COUNTS || this.step === STEP_CONFIRM) && !this.loading;
    }

    /** Loading / error only; success uses the four-line simplified summary below. */
    get quoteLinePreviewShowStatusLine() {
        const p = this.quoteLinePreview;
        return !p || !!p.error;
    }

    get quoteLinePreviewStatusLine() {
        const p = this.quoteLinePreview;
        if (!p) {
            return 'Calculating quote line estimate…';
        }
        if (p.error) {
            return p.error;
        }
        return '';
    }

    get quoteLinePreviewBreakdownVisible() {
        const p = this.quoteLinePreview;
        return !!(p && !p.error);
    }

    get quoteLinePreviewCurrentTotal() {
        const p = this.quoteLinePreview;
        return p && !p.error ? p.currentTotal : 0;
    }

    get quoteLinePreviewProjectedTotal() {
        const p = this.quoteLinePreview;
        const base = p && !p.error ? p.projectedTotal : 0;
        if (!this.isCreatePreviousMode) return base;
        return base + this.quoteLinePreviewRepeatAdds;
    }

    get isLargeDealRequired() {
        return this.largeDealRequiredByThreshold;
    }

    get estimatedProjectedTotalForLargeDealRequirement() {
        const p = this.quoteLinePreview;
        if (p && !p.error) {
            return this.quoteLinePreviewProjectedTotal;
        }
        // Fallback while preview is still loading, primarily for create flows.
        if (this.isCreate) {
            let newGroups = 0;
            try {
                const counts =
                    typeof this._productCountsJson === 'string'
                        ? JSON.parse(this._productCountsJson || '{}')
                        : this._productCountsJson || {};
                newGroups = this._sumDemoCountsMap(counts);
            } catch (e) {
                newGroups = 0;
            }
            const repeatAdds = this.isCreatePreviousMode ? this.quoteLinePreviewRepeatAdds : 0;
            return newGroups + repeatAdds;
        }
        return 0;
    }

    get effectiveLargeDeal() {
        return this.largeDeal || this.isLargeDealRequired || this.skipLargeDealStep;
    }

    get largeDealRequirementHelpText() {
        if (!this.isLargeDealRequired) return null;
        return `Estimated total is ${this.estimatedProjectedTotalForLargeDealRequirement}. Large Deal is required at ${LARGE_DEAL_THRESHOLD}+ lines and has been selected automatically.`;
    }

    get quoteLinePreviewNewGroupsAdds() {
        const p = this.quoteLinePreview;
        return p && !p.error ? p.newLinesFromHierarchy : 0;
    }

    get quoteLinePreviewRepeatAdds() {
        if (!this.isCreatePreviousMode) return 0;
        return this.repeatBuyStats.projectedRowsToAdd;
    }

    /** Sum of demo counts entered on the Existing groups tab (additive view; not net vs on-quote). */
    get quoteLinePreviewExistingAddsSum() {
        return this._sumDemoCountsMap(this._existingGroupCounts);
    }

    _sumDemoCountsMap(obj) {
        if (!obj || typeof obj !== 'object') {
            return 0;
        }
        let sum = 0;
        Object.keys(obj).forEach((k) => {
            const v = obj[k];
            const n = typeof v === 'number' ? v : parseInt(v, 10);
            if (Number.isFinite(n) && n >= 0) {
                sum += n;
            }
        });
        return sum;
    }

    get quoteLinePreviewSimplifiedFootnote() {
        const p = this.quoteLinePreview;
        let base =
            'Estimated total after Run is the authoritative number. It follows Set Up Quote rules (line replacement on existing groups, deleted groups, CSV, etc.) and may not equal the sum of the three lines above. Tree roll-up is not a quote total.';
        if (p && !p.error && p.linesRemovedFromDeletes > 0) {
            base +=
                ' About ~' +
                p.linesRemovedFromDeletes +
                ' row(s) are removed because groups are marked for delete.';
        }
        return base;
    }

    get quoteLinePreviewBannerClass() {
        const p = this.quoteLinePreview;
        if (p && p.error) return 'quote-line-preview-banner quote-line-preview-banner_error';
        return 'quote-line-preview-banner';
    }

    /** Footer under product-count trees (modify): entire quote, not subtree-only roll-up. */
    get quoteLinePreviewTreeGrandSummary() {
        if (this.isCreate) {
            return undefined;
        }
        if (this.step !== STEP_PRODUCT_COUNTS && this.step !== STEP_CONFIRM) {
            return undefined;
        }
        const p = this.quoteLinePreview;
        if (!p) {
            return 'Combined total (entire quote): calculating…';
        }
        if (p.error) {
            return 'Combined total (entire quote): ' + p.error;
        }
        return (
            'Full quote (same as gray box): ' +
            p.currentTotal +
            ' rows now → ' +
            p.projectedTotal +
            ' estimated after Run. Tree roll-up is only for this section’s hierarchy, not total quote lines.'
        );
    }

    renderedCallback() {
        if (!this._modalFocused) {
            this._modalFocused = true;
            const card = this.template.querySelector('.modal-card');
            if (card) {
                card.focus();
            }
        }
        if (this.step === STEP_PRODUCT_COUNTS || this.step === STEP_CONFIRM) {
            this.scheduleQuoteLinePreviewRefresh();
        }
    }

    handleModalKeydown(event) {
        if (event.key === 'Escape') {
            event.stopPropagation();
            this.handleClose();
            return;
        }
        if (event.key !== 'Tab') return;
        const FOCUSABLE_SELECTOR = [
            'a[href]',
            'button:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            '[tabindex]:not([tabindex="-1"])',
            'lightning-button:not([disabled])',
            'lightning-button-icon:not([disabled])',
            'lightning-input:not([disabled])',
            'lightning-combobox:not([disabled])',
            'lightning-textarea:not([disabled])'
        ].join(', ');
        const focusable = [...this.template.querySelectorAll(FOCUSABLE_SELECTOR)].filter(
            (el) => el.offsetParent !== null
        );
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const active = this.template.activeElement;
        if (event.shiftKey) {
            if (active === first) {
                event.preventDefault();
                last.focus();
            }
        } else {
            if (active === last) {
                event.preventDefault();
                first.focus();
            }
        }
    }

    scheduleQuoteLinePreviewRefresh() {
        if (this.step !== STEP_PRODUCT_COUNTS && this.step !== STEP_CONFIRM) {
            return;
        }
        window.clearTimeout(this._quoteLinePreviewTimer);
        this._quoteLinePreviewTimer = window.setTimeout(() => {
            this._quoteLinePreviewTimer = null;
            this.refreshQuoteLinePreview();
        }, 320);
    }

    handleQuoteLinePreviewSync() {
        this.syncWizardCountsForLinePreview();
        this.scheduleQuoteLinePreviewRefresh();
    }

    handleCreateProductCountChange() {
        this.syncWizardCountsForLinePreview();
        this.scheduleQuoteLinePreviewRefresh();
    }

    syncWizardCountsForLinePreview() {
        if (this.step === STEP_PRODUCT_COUNTS && !this.isCreate && this.hasProductCountsStep) {
            const existingEl = this.template.querySelector('c-rlm-set-up-quote-hierarchy-tree[data-step="product-counts-existing"]');
            const newEl = this.template.querySelector('c-rlm-set-up-quote-hierarchy-tree[data-step="product-counts-new-manual"]');
            if (existingEl && existingEl.productCountsJson) {
                try {
                    this._existingGroupCounts = JSON.parse(existingEl.productCountsJson);
                } catch (e) {
                    /* keep */
                }
            }
            if (this.importMethod !== 'csv' && newEl && newEl.productCountsJson) {
                try {
                    this._productCountsJson = newEl.productCountsJson;
                } catch (e) {
                    /* keep */
                }
            }
        }
        if (this.step === STEP_PRODUCT_COUNTS && this.isCreate && this.hasProductCountsStep) {
            const pathCounts = {};
            this.template.querySelectorAll('lightning-input[data-step="product-count"]').forEach((input) => {
                const key = input.dataset.groupKey;
                const keyType = input.dataset.keyType;
                const val = parseInt(input.value, 10);
                const count = isNaN(val) ? 0 : val;
                if (key == null) return;
                if (keyType === 'newTree') {
                    pathCounts[key] = count;
                }
            });
            this._productCountsJson = JSON.stringify(pathCounts);
        }
    }

    buildQuoteLinePreviewPayload() {
        let existingGroupCountsJson = null;
        if (!this.isCreate) {
            this.syncExistingTreeFromChild();
            const counts = this._existingGroupCounts || {};
            if (Object.keys(counts).length) {
                existingGroupCountsJson = JSON.stringify(counts);
            }
        }
        return {
            isCreate: this.isCreate,
            quoteId: this.isCreate ? null : this.quoteId,
            groupsToDeleteJson:
                this.isCreate || !(this.groupsToDelete && this.groupsToDelete.length)
                    ? null
                    : JSON.stringify(this.groupsToDelete),
            existingGroupCountsJson,
            hierarchyJson: this._hierarchyJson || null,
            productCountsJson: this._productCountsJson || '{}',
            csvImportLineItemsJson:
                this.csvImportData && this.csvImportData.csvImportLineItemsJson
                    ? this.csvImportData.csvImportLineItemsJson
                    : null
        };
    }

    async refreshQuoteLinePreview() {
        if (this.step !== STEP_PRODUCT_COUNTS && this.step !== STEP_CONFIRM) {
            return;
        }
        if (!this.isCreate && (!this.quoteId || !String(this.quoteId).trim())) {
            this.quoteLinePreview = null;
            return;
        }
        try {
            this.syncWizardCountsForLinePreview();
            const payload = this.buildQuoteLinePreviewPayload();
            const res = await previewQuoteLineCounts({ previewJson: JSON.stringify(payload) });
            const o = typeof res === 'string' ? JSON.parse(res) : res;
            this.quoteLinePreview = {
                currentTotal: o.currentTotal != null ? o.currentTotal : 0,
                projectedTotal: o.projectedTotal != null ? o.projectedTotal : 0,
                linesRemovedFromDeletes: o.linesRemovedFromDeletes != null ? o.linesRemovedFromDeletes : 0,
                netExistingGroupDelta: o.netExistingGroupDelta != null ? o.netExistingGroupDelta : 0,
                newLinesFromHierarchy: o.newLinesFromHierarchy != null ? o.newLinesFromHierarchy : 0,
                error: o.error || null
            };
        } catch (e) {
            this.quoteLinePreview = {
                currentTotal: 0,
                projectedTotal: 0,
                linesRemovedFromDeletes: 0,
                netExistingGroupDelta: 0,
                newLinesFromHierarchy: 0,
                error: e.body && e.body.message ? e.body.message : e.message || 'Quote line preview failed'
            };
        }
    }

    handleProductCountsNext() {
        let existingCounts = {};
        let pathCounts = {};
        if (!this.isCreate) {
            const existingEl = this.template.querySelector('c-rlm-set-up-quote-hierarchy-tree[data-step="product-counts-existing"]');
            const newEl = this.template.querySelector('c-rlm-set-up-quote-hierarchy-tree[data-step="product-counts-new-manual"]');
            if (existingEl) {
                try {
                    existingCounts = JSON.parse(existingEl.productCountsJson || '{}');
                } catch (e) {
                    existingCounts = {};
                }
            } else {
                existingCounts = { ...(this._existingGroupCounts || {}) };
            }
            if (this.importMethod !== 'csv' && newEl) {
                try {
                    pathCounts = JSON.parse(newEl.productCountsJson || '{}');
                } catch (e) {
                    pathCounts = {};
                }
            } else {
                pathCounts = {};
            }
        } else {
            this.template.querySelectorAll('lightning-input[data-step="product-count"]').forEach((input) => {
                const key = input.dataset.groupKey;
                const keyType = input.dataset.keyType;
                const val = parseInt(input.value, 10);
                const count = isNaN(val) ? 0 : val;
                if (key == null) return;
                if (keyType === 'existing') existingCounts[key] = count;
                else pathCounts[key] = count;
            });
        }
        this._existingGroupCounts = existingCounts;
        this._productCountsJson = JSON.stringify(pathCounts);
        // Re-evaluate from current Step 5 input snapshot (avoid stale async preview state).
        this.largeDealRequiredByThreshold = this.computeLargeDealRequiredSnapshot(existingCounts, pathCounts);
        // >= threshold => force checked; below threshold => clear.
        this.largeDeal = this.largeDealRequiredByThreshold;
        if (this.skipLargeDealStep) {
            this.largeDeal = true;
            this.step = STEP_CONFIRM;
        } else {
            this.step = STEP_LARGE_DEAL;
        }
    }

    handleAssignRepeatNext() {
        this.step = STEP_PRODUCT_COUNTS;
    }

    handleLargeDealNext() {
        const el = this.template.querySelector('lightning-input[data-step="large-deal"]');
        this.largeDeal = this.isLargeDealRequired ? true : el ? el.checked : false;
        this.step = STEP_CONFIRM;
    }

    computeLargeDealRequiredSnapshot(existingCounts, pathCounts) {
        // Create mode uses entered group counts (plus repeated-line adds) as immediate source of truth.
        if (this.isCreate) {
            const newGroups = this._sumDemoCountsMap(pathCounts);
            const repeatAdds = this.isCreatePreviousMode ? this.quoteLinePreviewRepeatAdds : 0;
            return newGroups + repeatAdds >= LARGE_DEAL_THRESHOLD;
        }
        // Modify mode: prefer latest preview when available.
        if (this.quoteLinePreview && !this.quoteLinePreview.error) {
            return this.quoteLinePreviewProjectedTotal >= LARGE_DEAL_THRESHOLD;
        }
        // Fallback estimate if preview is unavailable.
        const existingRows = this.quoteLinePreviewCurrentTotal || 0;
        const addsExisting = this._sumDemoCountsMap(existingCounts);
        const addsNew = this._sumDemoCountsMap(pathCounts);
        const repeatAdds = this.isCreatePreviousMode ? this.quoteLinePreviewRepeatAdds : 0;
        return existingRows + addsExisting + addsNew + repeatAdds >= LARGE_DEAL_THRESHOLD;
    }

    handleBack() {
        if (this.step === STEP_CONFIRM) {
            if (this.skipLargeDealStep) {
                this.step = this.skipProductCountsStepEntirely ? STEP_HIERARCHY : (this.isCreatePreviousMode ? STEP_PRODUCT_COUNTS : STEP_PRODUCT_COUNTS);
            } else {
                this.step = STEP_LARGE_DEAL;
            }
        } else if (this.step === STEP_LARGE_DEAL) {
            this.step = this.skipProductCountsStepEntirely ? STEP_HIERARCHY : STEP_PRODUCT_COUNTS;
        } else if (this.step === STEP_PRODUCT_COUNTS) {
            this.step = this.isCreatePreviousMode ? STEP_ASSIGN_REPEAT : STEP_HIERARCHY;
        } else if (this.step === STEP_ASSIGN_REPEAT) {
            this.step = STEP_HIERARCHY;
        } else if (this.step > STEP_CREATE_OR_MODIFY) {
            this.step--;
        }
    }

    handleCancel() {
        this.handleClose();
    }

    async handleSubmit() {
        this.loading = true;
        this.result = null;
        try {
            let groupRenamesJson = null;
            let newSubgroupsJson = null;
            let existingGroupCountsJson = null;
            if (!this.isCreate) {
                this.syncExistingTreeFromChild();
                const renamesToSend = {};
                const walk = (nodes) => {
                    (nodes || []).forEach((n) => {
                        const id = n.id || n.Id;
                        const orig = n.name || ('Group ' + id);
                        if (id && this.groupRenames[id] !== undefined && String(this.groupRenames[id]).trim() !== orig) renamesToSend[id] = String(this.groupRenames[id]).trim();
                        if (n.children && n.children.length) walk(n.children);
                    });
                };
                walk((this.existingHierarchy && this.existingHierarchy.parents) || []);
                if (Object.keys(renamesToSend).length) groupRenamesJson = JSON.stringify(renamesToSend);
                if (this.newSubgroupsUnderExisting && this.newSubgroupsUnderExisting.length) {
                    newSubgroupsJson = JSON.stringify(this.newSubgroupsUnderExisting.map((p) => ({ parentGroupId: p.parentGroupId, name: p.name, tempId: p.tempId })));
                }
                const counts = this._existingGroupCounts || {};
                if (Object.keys(counts).length) existingGroupCountsJson = JSON.stringify(counts);
            }
            const payload = {
                isCreate: this.isCreate,
                quoteId: this.isCreate ? null : this.quoteId,
                newQuoteName: this.isCreate ? this.newQuoteName : null,
                largeDeal: this.effectiveLargeDeal,
                quoteAccountId: this.isCreate ? this.launchAccountId : null,
                parentGroupNames: null,
                subgroupNamesPerParent: null,
                productCountsPerParent: null,
                hierarchyJson: this._hierarchyJson || null,
                productCountsJson: this._productCountsJson || '{}',
                csvImportLineItemsJson: this.csvImportData && this.csvImportData.csvImportLineItemsJson ? this.csvImportData.csvImportLineItemsJson : null,
                groupsToDeleteJson: this.isCreate ? null : (this.groupsToDelete && this.groupsToDelete.length ? JSON.stringify(this.groupsToDelete) : null),
                groupRenamesJson: groupRenamesJson || null,
                newSubgroupsJson: newSubgroupsJson || null,
                existingGroupCountsJson: existingGroupCountsJson || null,
                repeatBuyAccountId: this.isCreatePreviousMode ? (this.repeatBuyAccountId || null) : null,
                repeatBuyAssignmentsJson:
                    this.isCreatePreviousMode && this.repeatBuyAssignments && this.repeatBuyAssignments.length
                        ? JSON.stringify(this.repeatBuyAssignments.map((r) => ({
                              sourcePath: r.sourcePath,
                              targetPath: r.targetPath,
                              duplicateToTarget: r.duplicateToTarget === true,
                              removed: r.removed === true,
                              productIdentifier: r.productIdentifier,
                              quantity: r.quantity
                          })))
                        : null
            };
            const res = await runSetUpQuoteFromLWC({ inputJson: JSON.stringify(payload) });
            this.result = typeof res === 'string' ? JSON.parse(res) : res;
        } catch (e) {
            this.result = { quoteId: null, success: false, errorMessage: e.body?.message || e.message || String(e) };
        }
        this.loading = false;
        this.step = STEP_RESULT;
    }

    handleClose() {
        this.dispatchEvent(new CloseActionScreenEvent());
        this[NavigationMixin.Navigate]({
            type: 'standard__objectPage',
            attributes: { objectApiName: 'Quote', actionName: 'list' }
        });
    }

    handleDone() {
        // After creating a quote, navigate to the new quote record so it appears in the quote viewer
        if (this.result?.success && this.result?.quoteId) {
            this.dispatchEvent(new CloseActionScreenEvent());
            this[NavigationMixin.Navigate]({
                type: 'standard__recordPage',
                attributes: {
                    recordId: this.result.quoteId,
                    objectApiName: 'Quote',
                    actionName: 'view'
                }
            });
        } else {
            this.handleClose();
        }
    }
}