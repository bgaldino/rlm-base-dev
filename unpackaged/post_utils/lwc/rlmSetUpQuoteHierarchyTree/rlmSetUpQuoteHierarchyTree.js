import { LightningElement, api, track } from 'lwc';

const MAX_DEPTH = 5;

/**
 * Reusable hierarchy tree: gray connector lines, folder/file icons, +/− expand only.
 * Modes: manual (add + rename), CSV import (rename only, no add), confirm/review (read-only, same chrome).
 */
export default class RlmSetUpQuoteHierarchyTree extends LightningElement {
    @api hierarchyJson = '{"parents":[]}';
    @api productCountsJson = '{}';
    /** Loaded once in connectedCallback when building from CSV (optional). */
    @api initialHierarchyJson;
    /**
     * Legacy: when true, blocks adding parent/subgroups. Does not block rename unless allowRename is false.
     */
    @api readOnlyHierarchy = false;
    /** When false, hide "Parent groups" and per-row "Add subgroup". Omit attribute for default-on. */
    @api allowAddNodes;
    /** When false, double-click rename disabled. Omit attribute for default-on. */
    @api allowRename;
    /**
     * Review/confirm: tree reflects this JSON; updates when attribute changes.
     * When set, use with allowAddNodes=false, allowRename=false for read-only review.
     */
    @api
    get displayHierarchyJson() {
        return this._displayHierarchyJson;
    }
    set displayHierarchyJson(value) {
        this._displayHierarchyJson = value;
        this._applyDisplayHierarchy();
    }
    /** When true, show "× count" after each name (uses productCountsJson keyed by path). */
    @api showProductCounts = false;
    /** When true, do not write hierarchyJson/productCountsJson from internal changes (review local expand only). */
    @api suppressSync = false;
    /** Show inner title "Subgroups and nested groups". Omit for default-on; set false when parent supplies heading. */
    @api showSectionHeader;
    /** Set Up Quote modify: existing groups from server — hide top "Add parent", show line counts, delete icon, dispatch events. */
    @api modifyExistingMode = false;
    /** With modifyExistingMode: append "N line item(s)" after each node name (from node.lineItemCount). */
    @api showExistingLineItemCounts = false;
    /**
     * Product count step: fixed hierarchy from displayHierarchyJson; per-row number inputs.
     * Counts are keyed by sfId, tempId, or tree path (same keys wizard uses for _existingGroupCounts / _productCountsJson).
     */
    @api productCountsEditMode = false;
    /**
     * In productCountsEditMode, when set, replaces the subtree-only combined total with this line (e.g. full-quote preview from wizard).
     */
    @api productCountsExternalGrandSummary;

    /** Prefer this from the parent when the parent does not bind `hierarchy-json` (avoids stale default @api). */
    @api
    getLiveHierarchyJson() {
        try {
            return JSON.stringify(this._tree || { parents: [] });
        } catch (e) {
            return '{"parents":[]}';
        }
    }

    /** Prefer this for the same reason as getLiveHierarchyJson. */
    @api
    getLiveProductCountsJson() {
        try {
            return JSON.stringify(this._counts && typeof this._counts === 'object' ? this._counts : {});
        } catch (e) {
            return '{}';
        }
    }

    @track _tree = { parents: [] };
    @track _counts = {};
    @track _collapsedPaths = {};
    _displayHierarchyJson;

    @track selectedPath = null;
    @track editingPath = null;
    @track editingDraftName = '';

    _skipBlurCommit = false;

    connectedCallback() {
        if (this.initialHierarchyJson && !this._displayHierarchyJson) {
            try {
                const parsed =
                    typeof this.initialHierarchyJson === 'string'
                        ? JSON.parse(this.initialHierarchyJson)
                        : this.initialHierarchyJson;
                if (parsed && parsed.parents && Array.isArray(parsed.parents)) {
                    this._tree = parsed;
                }
            } catch (e) {
                /* ignore */
            }
        }
        this._applyDisplayHierarchy();
        if (this.productCountsEditMode) {
            this._counts = { ...this._pathCounts() };
        }
        this._syncOutputs();
    }

    get _readOnlyHierarchyEffective() {
        const v = this.readOnlyHierarchy;
        if (v === false || v === 'false') return false;
        return Boolean(v);
    }

    get effectiveAllowAddNodes() {
        if (this._readOnlyHierarchyEffective) return false;
        return this.allowAddNodes !== false;
    }

    get effectiveAllowRename() {
        if (this.productCountsEditMode) return false;
        return this.allowRename !== false;
    }

    get effectiveShowSectionHeader() {
        return this.showSectionHeader !== false;
    }

    /** Hide "Parent groups" block when editing existing quote groups only. */
    get showParentAddSection() {
        if (this.productCountsEditMode) return false;
        return this.effectiveAllowAddNodes && !this.modifyExistingMode;
    }

    get hasParents() {
        return this._tree.parents && this._tree.parents.length > 0;
    }

    _pathCounts() {
        try {
            const c =
                typeof this.productCountsJson === 'string'
                    ? JSON.parse(this.productCountsJson || '{}')
                    : this.productCountsJson || {};
            return typeof c === 'object' && c !== null ? c : {};
        } catch (e) {
            return {};
        }
    }

    _applyDisplayHierarchy() {
        if (this._displayHierarchyJson == null || this._displayHierarchyJson === '') return;
        try {
            const parsed =
                typeof this._displayHierarchyJson === 'string'
                    ? JSON.parse(this._displayHierarchyJson)
                    : this._displayHierarchyJson;
            if (parsed && Array.isArray(parsed.parents)) {
                this._tree = parsed;
            }
        } catch (e) {
            /* ignore */
        }
    }

    /**
     * Per path: subgroup count, on-quote line items, entered demo count, row total, subtree roll-up (option A: row + sum(child roll-ups)).
     */
    _buildProductCountStepMetrics() {
        const pathCounts = this._pathCounts();
        const metrics = {};
        const walk = (nodes, basePath) => {
            if (!nodes) return;
            nodes.forEach((n, i) => {
                const path = basePath !== '' ? `${basePath}-${i}` : String(i);
                const countKey = n.sfId || n.tempId || path;
                const subgroupCount = (n.children && n.children.length) || 0;
                let onQuote = 0;
                if (n.lineItemCount != null && n.lineItemCount !== '') {
                    const oq = Number(n.lineItemCount);
                    onQuote = Number.isFinite(oq) && oq >= 0 ? oq : 0;
                }
                const fromCounts = this._counts[countKey];
                const fromProp = pathCounts[countKey];
                const mergedEntered =
                    fromCounts != null && fromCounts !== '' ? fromCounts : fromProp != null ? fromProp : 0;
                const ent = Number(mergedEntered);
                const enteredNum = Number.isFinite(ent) && ent >= 0 ? ent : 0;
                const rowTotal = onQuote + enteredNum;
                const childPaths = (n.children || []).map((_, j) => `${path}-${j}`);
                metrics[path] = { subgroupCount, onQuote, entered: enteredNum, rowTotal, childPaths };
                walk(n.children || [], path);
            });
        };
        walk(this._tree.parents || [], '');
        const roll = (path) => {
            const m = metrics[path];
            if (!m) return 0;
            let sumChild = 0;
            m.childPaths.forEach((cp) => {
                sumChild += roll(cp);
            });
            m.rollUp = m.rowTotal + sumChild;
            return m.rollUp;
        };
        (this._tree.parents || []).forEach((_, i) => roll(String(i)));
        return metrics;
    }

    /** Sum of each root’s subtree roll-up (disjoint trees → whole shown hierarchy). */
    get productCountsStepGrandRollupLabel() {
        if (!this.productCountsEditMode || !this.hasParents) return null;
        const m = this._buildProductCountStepMetrics();
        const parents = this._tree.parents || [];
        if (!parents.length) return null;
        let sum = 0;
        parents.forEach((_, i) => {
            const me = m[String(i)];
            if (me) sum += me.rollUp;
        });
        return `Combined total (on quote + entered, full tree): ${sum}`;
    }

    get visibleRows() {
        const list = [];
        const isExpanded = (path) => !this._collapsedPaths[path];
        const pathCounts = this.showProductCounts || this.productCountsEditMode ? this._pathCounts() : {};
        const stepMetrics = this.productCountsEditMode ? this._buildProductCountStepMetrics() : null;

        const TRACK = 15;
        const ELBOW = 15;
        const TOGGLE = 18;
        const ICON = 22;
        const GAP = 6;
        /** Extra left offset per depth so nested rows cannot be mistaken for top-level (esp. single-root + thin guides). */
        const DEPTH_MARGIN = 18;

        const numRoots = (this._tree.parents && this._tree.parents.length) || 0;
        const multiRoot = numRoots > 1;

        const walk = (nodes, basePath, depth, continueVertical) => {
            if (!nodes) return;
            nodes.forEach((n, i, arr) => {
                const isLastSibling = i === arr.length - 1;
                const path = basePath !== '' ? `${basePath}-${i}` : String(i);
                const hasChildren = !!(n.children && n.children.length);
                const expanded = hasChildren ? isExpanded(path) : false;

                const guidePipes = [];
                for (let c = 0; c < depth - 1; c++) {
                    const pipeOn = continueVertical[c] === true;
                    guidePipes.push({
                        key: `${path}-pipe-${c}`,
                        on: pipeOn,
                        pipeClass: pipeOn ? 'tree-pipe tree-pipe-on' : 'tree-pipe'
                    });
                }

                const elbowNone = depth === 0 && !multiRoot;
                const elbowTee =
                    (depth === 0 && multiRoot && !isLastSibling) || (depth > 0 && !isLastSibling);
                const elbowCorner =
                    (depth === 0 && multiRoot && isLastSibling) || (depth > 0 && isLastSibling);

                const guidesInnerW =
                    guidePipes.length * TRACK + (elbowNone ? 0 : ELBOW) + TOGGLE + ICON + GAP;
                const guideMargin = depth * DEPTH_MARGIN;
                const guidesW = guideMargin + guidesInnerW;

                const cnt = pathCounts[path];
                const countSuffix =
                    !this.productCountsEditMode &&
                    this.showProductCounts &&
                    cnt != null &&
                    cnt !== ''
                        ? ` \u00d7 ${cnt}`
                        : '';
                let displayLabel;
                if (this.productCountsEditMode) {
                    displayLabel = (n.name || '');
                    if (n.tempId && !n.sfId) displayLabel += ' (new)';
                } else {
                    displayLabel = (n.name || '') + countSuffix;
                    if (this.modifyExistingMode && this.showExistingLineItemCounts && n.lineItemCount != null) {
                        displayLabel += `  ${n.lineItemCount} line item(s)`;
                    }
                    if (this.modifyExistingMode && n.tempId && !n.sfId) {
                        displayLabel += ' (new)';
                    }
                }

                const countKey = n.sfId || n.tempId || path;
                const fromCounts = this._counts[countKey];
                const fromProp = pathCounts[countKey];
                const mergedCount =
                    fromCounts != null && fromCounts !== '' ? fromCounts : fromProp != null ? fromProp : 0;
                const numCount = Number(mergedCount);
                const countEditValue = String(Number.isFinite(numCount) ? numCount : 0);

                const sm = stepMetrics && stepMetrics[path];
                const productStepSubgroupCount = sm ? sm.subgroupCount : 0;
                const productStepOnQuote = sm ? sm.onQuote : 0;
                const productStepRowTotal = sm ? sm.rowTotal : 0;
                const productStepRollUp = sm ? sm.rollUp : 0;
                const productStepShowRollUp = !!(this.productCountsEditMode && hasChildren);

                const isSelected = this.effectiveAllowRename && this.selectedPath === path;
                list.push({
                    path,
                    name: n.name,
                    displayLabel,
                    countKey,
                    countEditValue,
                    productStepSubgroupCount,
                    productStepOnQuote,
                    productStepRowTotal,
                    productStepRollUp,
                    productStepShowRollUp,
                    sfId: n.sfId,
                    tempId: n.tempId,
                    showDelete:
                        !this.productCountsEditMode && this.modifyExistingMode && !!(n.sfId || n.tempId),
                    depth,
                    /** First nested row under root(s): connector often reads darker; use lighter stroke. */
                    firstBranchGuides: depth === 1,
                    hasChildren,
                    branchExpanded: expanded,
                    toggleLabel: hasChildren ? (expanded ? '\u2212' : '+') : '',
                    toggleTitle: hasChildren ? (expanded ? 'Collapse' : 'Expand') : '',
                    ariaExpanded: hasChildren ? String(expanded) : null,
                    folderIcon: hasChildren ? (expanded ? 'utility:open_folder' : 'utility:folder') : 'utility:file',
                    iconAlt: hasChildren ? (expanded ? 'Expanded folder' : 'Folder') : 'File',
                    guidePipes,
                    elbowNone,
                    elbowTee,
                    elbowCorner,
                    canAddChild: !this.productCountsEditMode && depth < MAX_DEPTH - 1,
                    isEditing: this.editingPath === path,
                    isSelected,
                    rowClass:
                        'tree-row' +
                        (isSelected ? ' tree-row-selected' : '') +
                        (depth === 1 ? ' tree-row-first-branch' : ''),
                    rowCoreClass: 'tree-row-core' + (isSelected ? ' tree-row-core-selected' : ''),
                    guidesClass: 'tree-guides' + (depth === 1 ? ' tree-guides-depth1' : ''),
                    elbowClass: 'tree-elbow' + (elbowNone ? ' tree-elbow-none' : ''),
                    guideClusterStyle: `margin-left:${guideMargin}px`,
                    addChildStyle: `margin-left: ${guidesW}px`
                });

                if (hasChildren && expanded) {
                    const next = continueVertical.slice();
                    while (next.length <= depth) {
                        next.push(false);
                    }
                    next[depth] = !isLastSibling;
                    walk(n.children, path, depth + 1, next);
                }
            });
        };

        walk(this._tree.parents, '', 0, []);
        return list;
    }

    handleParentKeydown(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.handleAddParent();
        }
    }

    handleAddParent() {
        if (!this.effectiveAllowAddNodes) return;
        const nameInput = this.template.querySelector('lightning-input.parent-name-input');
        const name = nameInput && nameInput.value ? String(nameInput.value).trim() : '';
        if (!name) return;
        const path = String(this._tree.parents.length);
        const newParent = { name, path, children: [] };
        this._tree = { parents: [...(this._tree.parents || []), newParent] };
        if (nameInput) nameInput.value = '';
        this._syncOutputs();
    }

    handleAddChild(event) {
        if (!this.effectiveAllowAddNodes) return;
        const parentPath = event.currentTarget.dataset.parentPath;
        const input = this.template.querySelector(`lightning-input.child-name[data-parent-path="${parentPath}"]`);
        const name = input && input.value ? String(input.value).trim() : '';
        if (!name) return;
        const parent = this._getNodeByPath(this._tree.parents, parentPath);
        if (!parent) return;
        const depth = parentPath.split('-').length;
        if (depth >= MAX_DEPTH) return;
        const childPath = parentPath + '-' + (parent.children ? parent.children.length : 0);
        const newChild = this.modifyExistingMode
            ? {
                  name,
                  path: childPath,
                  children: [],
                  lineItemCount: 0,
                  tempId: 'new-' + Date.now() + '-' + Math.random().toString(36).slice(2, 9)
              }
            : { name, path: childPath, children: [] };
        this._tree = this._replaceNode(this._tree, parentPath, (node) => ({
            ...node,
            children: [...(node.children || []), newChild]
        }));
        if (input) input.value = '';
        this._syncOutputs();
        this._emitExistingMutated();
    }

    handleProductCountChange(event) {
        if (!this.productCountsEditMode) return;
        const key = event.currentTarget.dataset.countKey;
        if (key == null) return;
        const v = parseInt(event.target.value, 10);
        this._counts = { ...this._counts, [key]: Number.isFinite(v) && v >= 0 ? v : 0 };
        this._syncOutputs();
        this.dispatchEvent(new CustomEvent('quotelinepreviewsync', { bubbles: true, composed: true }));
    }

    handleRowSelect(event) {
        if (this.productCountsEditMode) return;
        if (!this.effectiveAllowRename) return;
        event.stopPropagation();
        const path = event.currentTarget.dataset.path;
        this.selectedPath = path;
    }

    handleToggleExpand(event) {
        event.stopPropagation();
        const path = event.currentTarget.dataset.path;
        const next = { ...this._collapsedPaths };
        if (next[path]) {
            delete next[path];
        } else {
            next[path] = true;
        }
        this._collapsedPaths = next;
    }

    handleLabelDblClick(event) {
        event.stopPropagation();
        if (!this.effectiveAllowRename) return;
        const path = event.currentTarget.dataset.path;
        this._beginRename(path);
    }

    _beginRename(path) {
        const node = this._getNodeByPath(this._tree.parents, path);
        if (!node) return;

        if (this.editingPath && this.editingPath !== path) {
            this._commitRename();
        }

        this.selectedPath = path;
        this.editingPath = path;
        this.editingDraftName = node.name || '';
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        requestAnimationFrame(() => {
            const input = this.template.querySelector(`lightning-input.tree-rename-input[data-path="${path}"]`);
            if (input) input.focus();
        });
    }

    handleDraftChange(event) {
        this.editingDraftName = event.target.value != null ? String(event.target.value) : '';
    }

    handleRenameKeydown(event) {
        if (event.key === 'Escape') {
            event.preventDefault();
            this._cancelRename();
        }
    }

    handleRenameBlur() {
        if (this._skipBlurCommit) return;
        this._commitRename();
    }

    _cancelRename() {
        this._skipBlurCommit = true;
        this.editingPath = null;
        this.editingDraftName = '';
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        Promise.resolve().then(() => {
            this._skipBlurCommit = false;
        });
    }

    _commitRename() {
        if (!this.editingPath) return;
        const path = this.editingPath;
        const node = this._getNodeByPath(this._tree.parents, path);
        const previous = node ? node.name : '';
        const nextName = String(this.editingDraftName != null ? this.editingDraftName : '').trim();

        this.editingPath = null;
        this.editingDraftName = '';

        if (!node) {
            this._syncOutputs();
            return;
        }
        if (!nextName) {
            this._syncOutputs();
            return;
        }
        if (nextName === previous) {
            this._syncOutputs();
            return;
        }

        this._tree = this._replaceNode(this._tree, path, (n) => ({
            ...n,
            name: nextName
        }));
        this._syncOutputs();
        this._emitExistingMutated();
    }

    _getNodeByPath(parents, path) {
        if (!path || !parents) return null;
        let arr = parents;
        let node = null;
        for (const idx of path.split('-').map(Number)) {
            if (!arr || arr[idx] == null) return null;
            node = arr[idx];
            arr = node.children || [];
        }
        return node;
    }

    _replaceNode(tree, targetPath, updater) {
        const parts = targetPath.split('-').map(Number);
        const replaceAt = (nodes, depth) => {
            if (!nodes) return nodes;
            const idx = parts[depth];
            if (depth === parts.length - 1) {
                const out = [...nodes];
                out[idx] = updater(out[idx]);
                return out;
            }
            const out = [...nodes];
            out[idx] = { ...out[idx], children: replaceAt(out[idx].children || [], depth + 1) };
            return out;
        };
        return { parents: replaceAt(tree.parents, 0) };
    }

    _syncOutputs() {
        if (this.suppressSync) return;
        this.hierarchyJson = JSON.stringify(this._tree);
        this.productCountsJson = JSON.stringify(this._counts);
    }

    _emitExistingMutated() {
        if (!this.modifyExistingMode || this.suppressSync) return;
        this.dispatchEvent(
            new CustomEvent('existingtreemutated', {
                detail: { hierarchyJson: this.hierarchyJson },
                bubbles: true,
                composed: true
            })
        );
    }

    handleDeleteModifyRow(event) {
        event.stopPropagation();
        if (!this.modifyExistingMode) return;
        const path = event.currentTarget.dataset.path;
        const node = this._getNodeByPath(this._tree.parents, path);
        if (!node) return;
        if (node.sfId) {
            this.dispatchEvent(
                new CustomEvent('existingtreegroupdelete', {
                    detail: { sfId: node.sfId },
                    bubbles: true,
                    composed: true
                })
            );
        } else if (node.tempId) {
            this.dispatchEvent(
                new CustomEvent('existingtreegroupdelete', {
                    detail: { tempId: node.tempId },
                    bubbles: true,
                    composed: true
                })
            );
        }
    }
}