import { LightningElement, api, wire } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import getQuoteLines from '@salesforce/apex/RLM_DeltaLineController.getQuoteLines';
import updateLineDiscountAndDates from '@salesforce/apex/RLM_DeltaLineController.updateLineDiscountAndDates';
import deleteLines from '@salesforce/apex/RLM_DeltaLineController.deleteLines';
import updateTermName from '@salesforce/apex/RLM_DeltaLineController.updateTermName';

const UNGROUPED_LABEL = '—';
// rem of indentation per bundle nesting level, applied as inline padding-left on the product name.
const INDENT_REM = 1.25;
// The DL_FareCodes__c multipicklist values (booking/fare classes). Value == label, so the
// dual-listbox options are the codes themselves. Stable catalog, so hardcoded rather than fetched.
const FARE_CODE_VALUES = [
    'J', 'C', 'D', 'I', 'Z', 'P', 'A', 'G', 'W', 'S', 'Y',
    'B', 'M', 'H', 'Q', 'K', 'L', 'U', 'T', 'X', 'V', 'E'
];
const FARE_CODE_OPTIONS = FARE_CODE_VALUES.map((c) => ({ label: c, value: c }));

/**
 * Custom expandable line grid for a Quote. Renders the persisted quote lines as an SLDS table with
 * inline Start / End date editing (the discount is negotiated in the Modeling tab, not here), and an
 * expander on each line that reveals the
 * reusable c/dlLineAttributePicker inline beneath the row (no modal). Lines are ordered by group
 * then by bundle hierarchy (parent immediately followed by its components, indented by depth).
 *
 * Refresh is driven explicitly through the @api refresh() method (→ refreshApex). A host that adds
 * lines elsewhere (e.g. c/dlProductFinder) must call refresh() — getRecordNotifyChange does NOT
 * refresh this grid because it only invalidates LDS getRecord caches, not the getQuoteLines wire.
 *
 * Reuses the same PST-backed Apex via the JSON-in/JSON-out contract (one `inputJson` string param
 * + a `_parse` helper).
 *
 * Term Builder additions (backward-compatible): `scopeRootLineId` narrows the grid to one Term root
 * plus its descendants, and a DL-TERM row's product name is inline-editable (CustomProductName).
 */
export default class DlmQuoteLineGrid extends LightningElement {
    @api recordId;
    @api attributeCodes; // optional CSV allowlist passed through to each attribute picker
    // Hide the leading Group column. Boolean @api props must default to false per LWC lint, so the
    // flag is expressed as "hide" rather than "show".
    @api hideGroupColumn = false;

    // When set, the grid shows only this Term root and its descendants (fares). Unset ⇒ full quote.
    // Backed by a setter so switching Terms re-scopes the already-loaded lines without a server call.
    _scopeRootLineId;
    @api
    get scopeRootLineId() {
        return this._scopeRootLineId;
    }
    set scopeRootLineId(value) {
        this._scopeRootLineId = value;
        if (this._lastParsed) {
            this.buildRows(this._lastParsed);
        }
    }

    displayRows = [];
    errorMessage = '';
    _saving = false;

    // Normalized, hierarchy-ordered lines from the server (the source for _composeRows()).
    _baseRows = [];
    // Per-line inline-edit drafts: { [lineId]: { startDate?, endDate?, fareCodes? } }.
    _drafts = {};
    // Per-line cell errors: { [lineId]: { endDate? } } (message strings).
    _errors = {};
    // Ids of lines whose attribute picker is expanded — preserved across refreshes.
    _expandedIds = new Set();
    // A querySelector run once after the next render to place focus (expander ↔ detail region).
    _focusTarget = null;
    _wired;
    // Last parsed server payload, so a scopeRootLineId change can re-scope without refetching.
    _lastParsed = null;
    // Per-Term inline name drafts: { [lineId]: string } while the rep types a new Term name.
    _nameDrafts = {};
    // Set when refresh() is called before the wire has provisioned (the host mounts this grid and
    // asks it to refresh in the same frame — e.g. the first Term added flips the workspace open).
    // The first delivery then forces one server round trip, so a stale cached getQuoteLines payload
    // (getQuoteLines is cacheable=true, and a host may have warmed the cache empty before the line
    // existed) can't strand the grid on pre-add data.
    _refreshPending = false;

    @wire(getQuoteLines, { quoteId: '$recordId' })
    wiredLines(result) {
        this._wired = result;
        if (result.data) {
            this._lastParsed = this._parse(result.data);
            this.buildRows(this._lastParsed);
            this.errorMessage = '';
        } else if (result.error) {
            this.errorMessage = this._errMessage(result.error);
        }
        // Honor a refresh() that arrived before this wire had a result to refresh.
        if (this._refreshPending && (result.data || result.error)) {
            this._refreshPending = false;
            refreshApex(this._wired);
        }
    }

    renderedCallback() {
        if (this._focusTarget) {
            const selector = this._focusTarget;
            this._focusTarget = null;
            const el = this.template.querySelector(selector);
            if (el) {
                el.focus();
            }
        }
    }

    buildRows(parsed) {
        if (parsed.isSuccess === false) {
            this.errorMessage = parsed.errorMessage || 'Unable to load quote lines.';
            this._baseRows = [];
            this.displayRows = [];
            this._emitState();
            return;
        }
        // Collect { line, groupPath } across groups + ungrouped, then order each bucket by bundle
        // hierarchy (parent line immediately followed by its components) with a computed indent depth.
        const entries = [];
        (parsed.groups || []).forEach((g) => this.collectGroup(g, '', entries));
        (parsed.ungrouped || []).forEach((l) => entries.push({ line: l, groupPath: UNGROUPED_LABEL }));
        const ordered = this.scopeToRoot(this.orderByHierarchy(entries));
        this._baseRows = ordered.map((e) => this.lineBase(e.line, e.groupPath, e.depth));

        // Preserve in-flight state across a refresh: an unsolicited wire emit (e.g. the finder adding
        // a line, or a post-save refresh) must not silently discard the user's unsaved drafts, cell
        // errors, or which rows they had expanded. Keep only entries whose line still exists; drop the
        // rest. Expansion is additionally pruned to lines that still have an expandable section
        // (editable attributes on a Term, or the fare-code editor on a fare row).
        const ids = new Set(this._baseRows.map((r) => r.id));
        const expandableIds = new Set(this._baseRows.filter((r) => this._isExpandable(r)).map((r) => r.id));
        this._drafts = this._pruneMap(this._drafts, ids);
        this._errors = this._pruneMap(this._errors, ids);
        this._nameDrafts = this._pruneMap(this._nameDrafts, ids);
        [...this._expandedIds].forEach((id) => {
            if (!expandableIds.has(id)) {
                this._expandedIds.delete(id);
            }
        });
        this._composeRows();
    }

    collectGroup(group, parentPath, entries) {
        const path = parentPath ? `${parentPath} / ${group.name}` : group.name;
        (group.lines || []).forEach((l) => entries.push({ line: l, groupPath: path }));
        (group.children || []).forEach((c) => this.collectGroup(c, path, entries));
    }

    // Reorder each group bucket depth-first by ParentQuoteLineItemId so a bundle parent is immediately
    // followed by its components (and their components), and record each line's nesting depth for
    // indentation. A line whose parent isn't in the same bucket is treated as a root (depth 0), so
    // grouping and bundle nesting stay independent. Sibling order is preserved (server already sorted).
    orderByHierarchy(entries) {
        // Preserve first-seen bucket order.
        const bucketOrder = [];
        const byBucket = new Map();
        entries.forEach((e) => {
            if (!byBucket.has(e.groupPath)) {
                byBucket.set(e.groupPath, []);
                bucketOrder.push(e.groupPath);
            }
            byBucket.get(e.groupPath).push(e);
        });

        const result = [];
        bucketOrder.forEach((bucket) => {
            const bucketEntries = byBucket.get(bucket);
            const ids = new Set(bucketEntries.map((e) => e.line.id));
            const childrenByParent = new Map();
            const roots = [];
            bucketEntries.forEach((e) => {
                const parentId = e.line.parentLineId;
                if (parentId && ids.has(parentId)) {
                    if (!childrenByParent.has(parentId)) {
                        childrenByParent.set(parentId, []);
                    }
                    childrenByParent.get(parentId).push(e);
                } else {
                    roots.push(e);
                }
            });
            // Iterative DFS (guarded against cycles) preserving sibling order.
            const seen = new Set();
            const visit = (entry, depth) => {
                if (seen.has(entry.line.id)) {
                    return;
                }
                seen.add(entry.line.id);
                result.push({ line: entry.line, groupPath: entry.groupPath, depth });
                (childrenByParent.get(entry.line.id) || []).forEach((child) => visit(child, depth + 1));
            };
            roots.forEach((r) => visit(r, 0));
            // Safety net: any entry not reached (e.g. a parent cycle) still gets emitted at depth 0.
            bucketEntries.forEach((e) => {
                if (!seen.has(e.line.id)) {
                    seen.add(e.line.id);
                    result.push({ line: e.line, groupPath: e.groupPath, depth: 0 });
                }
            });
        });
        return result;
    }

    // When scopeRootLineId is set, keep only the scope-root line and its descendants (fares under a
    // Term), and re-base their depth so the root renders at depth 0 with its fares indented one level.
    // Unset ⇒ pass through unchanged (full-quote behavior). A scope id that isn't present ⇒ empty grid.
    scopeToRoot(ordered) {
        const rootId = this.scopeRootLineId;
        if (!rootId) {
            return ordered;
        }
        const byId = new Map(ordered.map((e) => [e.line.id, e]));
        if (!byId.has(rootId)) {
            return [];
        }
        // Walk parentLineId chains: a line is in scope iff the chain reaches the scope root.
        const inScope = new Set([rootId]);
        ordered.forEach((e) => {
            let cursor = e.line.id;
            const path = [];
            // Guard against cycles with the visited-path set.
            while (cursor && !inScope.has(cursor) && !path.includes(cursor)) {
                path.push(cursor);
                const parent = byId.get(cursor);
                cursor = parent ? parent.line.parentLineId : null;
            }
            if (cursor && inScope.has(cursor)) {
                path.forEach((id) => inScope.add(id));
            }
        });
        const rootDepth = byId.get(rootId).depth || 0;
        return ordered
            .filter((e) => inScope.has(e.line.id))
            .map((e) => ({ ...e, depth: Math.max(0, (e.depth || 0) - rootDepth) }));
    }

    // Normalize a server line into a base row. Unlike the datatable editor, the custom table carries
    // the real `hasEditableAttributes` boolean (drives the expander), a stable `detailRegionId` (for
    // aria-controls), and an inline indent style rather than encoding either as a CSS class string.
    lineBase(line, groupPath, depth) {
        return {
            id: line.id,
            groupPath,
            productName: line.productName || '',
            // Catalog name fallback shown when a Term's custom name is cleared.
            catalogProductName: line.catalogProductName || line.productName || '',
            customProductName: line.customProductName || '',
            isTerm: !!line.isTerm,
            indentStyle: depth ? `padding-left:${depth * INDENT_REM}rem` : '',
            productCode: line.productCode,
            // Frozen prior-contract discount (renewal lines only; null otherwise). Read-only — shown
            // in its own column for reference, never bound to an input or draft. The live/proposed
            // discount is edited in the Modeling tab, not in this grid.
            priorDiscount: line.priorDiscount,
            startDate: line.startDate,
            endDate: line.endDate,
            hasEditableAttributes: !!line.hasEditableAttributes,
            // A fare row is a non-Term bundle child (a fare class under a Term). Fare rows expose the
            // fare-code editor in their own expandable section; Term rows expose route attributes.
            // Gating on a resolved parent keeps a root-level non-Term product (which isn't a fare)
            // out of the fare-code UI.
            isFareRow: !line.isTerm && !!line.parentLineId,
            // Per-line fare codes (fare rows only). Server sends a list; keep as an array for the
            // dual-listbox value binding.
            fareCodes: Array.isArray(line.fareCodes) ? line.fareCodes : [],
            detailRegionId: `rlm-line-detail-${line.id}`
        };
    }

    get fareCodeOptions() {
        return FARE_CODE_OPTIONS;
    }

    // Build the flat render list: each base row emits a data row, and each expanded row additionally
    // emits a detail row (the inline attribute picker) immediately after it. Both current draft values
    // and cell errors are merged in here so the template stays declarative.
    _composeRows() {
        const rows = [];
        this._baseRows.forEach((b) => {
            const draft = this._drafts[b.id] || {};
            const cellErr = this._errors[b.id] || {};
            const expanded = this._expandedIds.has(b.id);
            const nameDraft = this._nameDrafts[b.id];
            rows.push({
                key: b.id,
                isDetail: false,
                id: b.id,
                groupPath: b.groupPath,
                productName: b.productName,
                // Term rows render an inline name input; all others render static text.
                isTerm: b.isTerm,
                termNameValue: nameDraft !== undefined ? nameDraft : b.customProductName,
                termNamePlaceholder: b.catalogProductName,
                indentStyle: b.indentStyle,
                productCode: b.productCode,
                // Read-only prior-contract discount shown in its own column; independent of drafts.
                // Em dash when there is no prior value (non-renewal lines).
                priorDiscountDisplay: this._priorDiscountDisplay(b.priorDiscount),
                startDateValue: 'startDate' in draft ? draft.startDate : b.startDate,
                endDateValue: 'endDate' in draft ? draft.endDate : b.endDate,
                // Fare-code editing has moved off the row into the expandable detail section; the row
                // shows a compact read-only summary of the currently-selected codes on fare rows.
                showFareSummary: b.isFareRow,
                fareSummary: this._fareSummary('fareCodes' in draft ? draft.fareCodes : b.fareCodes),
                // An expander shows when the row has an expandable section: route attributes on a Term,
                // or the fare-code editor on a fare row. The label differs so the a11y text is accurate.
                expandable: this._isExpandable(b),
                expanded,
                expandedStr: expanded ? 'true' : 'false',
                expanderIcon: expanded ? 'utility:chevrondown' : 'utility:chevronright',
                expanderTitle: this._expanderTitle(b, expanded),
                detailRegionId: b.detailRegionId,
                startDateError: cellErr.startDate,
                endDateError: cellErr.endDate,
                endDateClass: cellErr.endDate ? 'slds-has-error' : ''
            });
            if (expanded) {
                rows.push({
                    key: `${b.id}-detail`,
                    isDetail: true,
                    // A fare row's detail hosts the fare-code dual-listbox; a Term's hosts the
                    // attribute picker. Exactly one is true per detail row.
                    isFareDetail: b.isFareRow,
                    id: b.id,
                    detailRegionId: b.detailRegionId,
                    detailLabel: b.isFareRow ? `Fare codes for ${b.productName}` : `Attributes for ${b.productName}`,
                    fareCodesValue: 'fareCodes' in draft ? draft.fareCodes : b.fareCodes,
                    colspan: this.detailColspan
                });
            }
        });
        this.displayRows = rows;
        this._emitState();
    }

    // A row is expandable when it has a section to reveal: a Term with editable route attributes, or
    // a fare row (which always exposes the fare-code editor).
    _isExpandable(b) {
        return b.isFareRow || b.hasEditableAttributes;
    }

    _expanderTitle(b, expanded) {
        const noun = b.isFareRow ? 'fare codes' : 'attributes';
        return expanded ? `Collapse ${noun}` : `Expand ${noun}`;
    }

    // Compact, comma-free summary of selected fare codes for the always-visible cell (e.g. "W S J").
    // Empty selection reads as an em dash so the column isn't blank/ambiguous.
    _fareSummary(codes) {
        return Array.isArray(codes) && codes.length ? codes.join(' ') : '—';
    }

    // Prior-contract discount for its own column, e.g. "15%". Em dash when there is no prior value
    // (non-renewal lines); 0 is a real prior discount and renders as "0%". Number() trims trailing
    // zeros (15.00 → 15) to match how the live discount input shows the figure.
    _priorDiscountDisplay(prior) {
        if (prior === null || prior === undefined || prior === '') {
            return '—';
        }
        const n = Number(prior);
        return Number.isNaN(n) ? '—' : `${n}%`;
    }

    get detailColspan() {
        // expander + product + fare codes + prior discount + start + end + actions = 7,
        // plus the optional group column.
        return this.hideGroupColumn ? 7 : 8;
    }

    get showGroupColumn() {
        return !this.hideGroupColumn;
    }

    get hasRows() {
        return this._baseRows.length > 0;
    }

    get isDirty() {
        return this._dirtyLines().length > 0;
    }

    // `saving` is a getter over a private field so every mutation also re-emits grid state to the host
    // (which renders the header-level Cancel/Save buttons — see _emitState). All internal writes go
    // through the setter (`this.saving = …`); the template binds the getter.
    get saving() {
        return this._saving;
    }
    set saving(value) {
        this._saving = value;
        this._emitState();
    }

    get saveDisabled() {
        return this.saving || !this.isDirty;
    }

    // Notify the host of the grid's action state so it can render Save/Cancel controls aligned with its
    // own card title (c/dlmTermWorkspace). Fired whenever rows rebuild (dirty state may change) and
    // whenever a save/delete/rename toggles `saving`.
    _emitState() {
        this.dispatchEvent(new CustomEvent('statechange', {
            detail: {
                hasRows: this.hasRows,
                saveDisabled: this.saveDisabled,
                saving: this._saving
            },
            bubbles: true,
            composed: true
        }));
    }

    // Host-facing controls so a parent can drive Save/Cancel from buttons it renders in its own card
    // header. They delegate to the same handlers the in-grid buttons use.
    @api
    save() {
        return this.handleSave();
    }

    @api
    cancel() {
        this.handleCancel();
    }

    // Toggle a row's inline attribute picker. On expand, move focus into the detail region; on
    // collapse, return focus to the triggering expander. (Native <button> gives Enter/Space for free.)
    handleToggleExpand(event) {
        const id = event.currentTarget.dataset.id;
        if (this._expandedIds.has(id)) {
            this._expandedIds.delete(id);
            this._focusTarget = `[data-expander="${id}"]`;
        } else {
            this._expandedIds.add(id);
            this._focusTarget = `[data-detail="${id}"]`;
        }
        this._composeRows();
    }

    handleStartDateChange(event) {
        this._setDraft(event.target.dataset.id, 'startDate', event.target.value);
    }

    handleEndDateChange(event) {
        this._setDraft(event.target.dataset.id, 'endDate', event.target.value);
    }

    // Fare-code multiselect (dual-listbox) → array of selected codes. Copy the array so a later
    // mutation can't alias the draft.
    handleFareCodesChange(event) {
        const selected = Array.isArray(event.detail.value) ? [...event.detail.value] : [];
        this._setDraft(event.target.dataset.id, 'fareCodes', selected);
    }

    _setDraft(id, field, value) {
        const draft = { ...(this._drafts[id] || {}) };
        draft[field] = value;
        this._drafts = { ...this._drafts, [id]: draft };
        // Clear this cell's error as the user edits it.
        if (this._errors[id] && this._errors[id][field]) {
            const next = { ...this._errors[id] };
            delete next[field];
            this._errors = { ...this._errors, [id]: next };
        }
        this._composeRows();
    }

    // Only lines whose drafted field actually differs from the server value, with just the changed
    // fields — mirrors the editor's "send only edited fields".
    _dirtyLines() {
        const baseById = new Map(this._baseRows.map((b) => [b.id, b]));
        const out = [];
        Object.keys(this._drafts).forEach((id) => {
            const b = baseById.get(id);
            if (!b) {
                return;
            }
            const draft = this._drafts[id];
            const payload = { id };
            let changed = false;
            if ('startDate' in draft && (draft.startDate || '') !== (b.startDate || '')) {
                payload.startDate = draft.startDate || null;
                changed = true;
            }
            if ('endDate' in draft && (draft.endDate || '') !== (b.endDate || '')) {
                payload.endDate = draft.endDate || null;
                changed = true;
            }
            if ('fareCodes' in draft && !this._eqCodes(draft.fareCodes, b.fareCodes)) {
                payload.fareCodes = Array.isArray(draft.fareCodes) ? draft.fareCodes : [];
                changed = true;
            }
            if (changed) {
                out.push(payload);
            }
        });
        return out;
    }

    async handleSave() {
        const dirty = this._dirtyLines();
        if (dirty.length === 0) {
            return;
        }
        // Validate each dirty line against its merged (draft + original) values before any save.
        const baseById = new Map(this._baseRows.map((b) => [b.id, b]));
        const errors = {};
        let hasError = false;
        dirty.forEach((p) => {
            const b = baseById.get(p.id) || {};
            const draft = this._drafts[p.id] || {};
            const startDate = 'startDate' in draft ? draft.startDate || '' : b.startDate || '';
            const endDate = 'endDate' in draft ? draft.endDate || '' : b.endDate || '';
            const cell = {};
            if (startDate && endDate && endDate < startDate) {
                cell.endDate = 'End must be ≥ start';
            }
            if (Object.keys(cell).length) {
                errors[p.id] = cell;
                hasError = true;
            }
        });
        if (hasError) {
            this._errors = errors;
            this.errorMessage = 'Fix the highlighted cells and save again.';
            this._composeRows();
            return;
        }

        this.saving = true;
        this._errors = {};
        this.errorMessage = '';
        try {
            const res = this._parse(
                await updateLineDiscountAndDates({
                    inputJson: JSON.stringify({ quoteId: this.recordId, lines: dirty })
                })
            );
            if (res.isSuccess === false) {
                this.errorMessage = res.errorMessage || 'Unable to save changes.';
                this._composeRows();
                return;
            }
            this._drafts = {};
            this._toast('Saved', `${res.updatedCount} line(s) updated.`, 'success');
            // Keep focus in the grid region rather than dropping to <body> when the Save button
            // disappears after the refresh clears the dirty state.
            this._focusTarget = '[data-grid-region]';
            await refreshApex(this._wired);
            this.dispatchEvent(new CustomEvent('linesupdated', { bubbles: true, composed: true }));
        } catch (e) {
            this.errorMessage = this._errMessage(e);
            this._composeRows();
        } finally {
            this.saving = false;
        }
    }

    handleCancel() {
        this._drafts = {};
        this._errors = {};
        this.errorMessage = '';
        this._composeRows();
    }

    // Remove a single line immediately (not part of the draft/save flow — the line is deleted on
    // the server right away, then the wire refreshes).
    async handleRemoveLine(event) {
        const id = event.currentTarget.dataset.id;
        this.errorMessage = '';
        this.saving = true;
        try {
            const res = this._parse(
                await deleteLines({
                    inputJson: JSON.stringify({ quoteId: this.recordId, lineIds: [id] })
                })
            );
            if (res.isSuccess === false) {
                this.errorMessage = res.errorMessage || 'Unable to remove line.';
                return;
            }
            this._expandedIds.delete(id);
            delete this._drafts[id];
            delete this._errors[id];
            this._focusTarget = '[data-grid-region]';
            await refreshApex(this._wired);
            this.dispatchEvent(new CustomEvent('linesupdated', { bubbles: true, composed: true }));
        } catch (e) {
            this.errorMessage = this._errMessage(e);
        } finally {
            this.saving = false;
        }
    }

    // Track the Term-name input as the rep types (no server call until blur / Enter).
    handleTermNameChange(event) {
        const id = event.target.dataset.id;
        this._nameDrafts = { ...this._nameDrafts, [id]: event.target.value };
    }

    // Commit a Term-name edit on blur or Enter. Only fires when the value actually changed from the
    // server value, so tabbing through a Term row is a no-op. Reverts the draft on error.
    async handleTermNameCommit(event) {
        const id = event.target.dataset.id;
        if (event.type === 'keydown') {
            if (event.key !== 'Enter') {
                return;
            }
            event.preventDefault();
        }
        if (!(id in this._nameDrafts)) {
            return;
        }
        const base = this._baseRows.find((b) => b.id === id);
        if (!base || !base.isTerm) {
            return;
        }
        const draft = (this._nameDrafts[id] || '').trim();
        if (draft === (base.customProductName || '')) {
            // No real change — drop the draft so the row shows the server value.
            const next = { ...this._nameDrafts };
            delete next[id];
            this._nameDrafts = next;
            return;
        }
        this.saving = true;
        this.errorMessage = '';
        try {
            const res = this._parse(
                await updateTermName({
                    inputJson: JSON.stringify({ quoteId: this.recordId, lineId: id, customProductName: draft })
                })
            );
            if (res.isSuccess === false) {
                this.errorMessage = res.errorMessage || 'Unable to rename the Term.';
                return;
            }
            const next = { ...this._nameDrafts };
            delete next[id];
            this._nameDrafts = next;
            await refreshApex(this._wired);
            this.dispatchEvent(new CustomEvent('termrenamed', {
                detail: { lineId: id, customProductName: res.customProductName },
                bubbles: true,
                composed: true
            }));
        } catch (e) {
            this.errorMessage = this._errMessage(e);
        } finally {
            this.saving = false;
        }
    }

    // A line's inline picker saved: PST may recalc net price, so refresh. Expansion + other rows'
    // drafts are preserved by buildRows (they key off still-existing line ids). Also notify the host
    // (via linesupdated) so it re-fetches builder state: a Term's route attributes feed the rail
    // chip's route/requirement summary, which comes from getBuilderState — the grid's own wire only
    // covers the line grid, so without this the side rail stays stale after a bare attribute save.
    handleAttributesSaved() {
        this.refresh();
        this.dispatchEvent(new CustomEvent('linesupdated', { bubbles: true, composed: true }));
    }

    @api
    async refresh() {
        // Force a fresh server round trip only once the wire has SETTLED (emitted real data or an
        // error). On provision an Apex wire first emits {data: undefined, error: undefined}, and
        // refreshApex against that un-fetched result is unreliable (it can no-op). The host mounts this
        // grid and calls refresh() in the same frame the first Term flips the workspace open — before
        // the wire's first real delivery — so latch and let wiredLines force the round trip when data
        // (even a stale cached empty payload) arrives.
        if (this._wired && (this._wired.data || this._wired.error)) {
            await refreshApex(this._wired);
        } else {
            this._refreshPending = true;
        }
    }

    _pruneMap(map, keepIds) {
        const next = {};
        Object.keys(map).forEach((id) => {
            if (keepIds.has(id)) {
                next[id] = map[id];
            }
        });
        return next;
    }

    // Order-insensitive equality of two fare-code lists (the dual-listbox can reorder selections).
    _eqCodes(a, b) {
        const sa = Array.isArray(a) ? [...a].sort() : [];
        const sb = Array.isArray(b) ? [...b].sort() : [];
        return sa.length === sb.length && sa.every((v, i) => v === sb[i]);
    }

    _parse(data) {
        try {
            return data ? JSON.parse(data) : {};
        } catch {
            return { isSuccess: false, errorMessage: 'Unexpected response from server.' };
        }
    }

    _errMessage(e) {
        return (e && e.body && e.body.message) || (e && e.message) || 'Unexpected error.';
    }

    _toast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
}
