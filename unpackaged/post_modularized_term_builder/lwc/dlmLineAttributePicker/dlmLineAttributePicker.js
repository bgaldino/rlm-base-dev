import { LightningElement, api, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import getLineAttributes from '@salesforce/apex/RLM_DeltaCatalogController.getLineAttributes';
import saveLineAttributes from '@salesforce/apex/RLM_DeltaCatalogController.saveLineAttributes';

/**
 * Reusable, configurable inline attribute picker for ONE persisted quote line. Given a
 * quoteLineItemId it discovers the line's informational (non-price-impacting) attributes server-side,
 * renders one control per attribute (chosen from its DataType / picklist), prefills current values,
 * and on Save persists only the changed ones through the controller's PST-backed saveLineAttributes.
 * On a successful save it emits a composed `attributessaved` event so a host (the cart list or the
 * modal wrapper) can react.
 *
 * Public API:
 *   @api quoteLineItemId  (required) — the persisted line to edit.
 *   @api attributeCodes   (optional) — CSV allowlist of AttributeDefinition.Code; narrows + orders.
 *   @api readOnly         (optional) — render all controls disabled (view only).
 * Product is resolved from the line server-side, so no productId is needed.
 */
export default class DlmLineAttributePicker extends LightningElement {
    @api attributeCodes;
    @api readOnly = false;
    // Hide this picker's own "Save Attributes" button — set by a host that drives saving centrally
    // (e.g. the cart's "Save All"). The public save() method still works when hidden.
    @api hideSave = false;

    @track attributes = [];
    loading = false;
    saving = false;
    errorMessage = '';
    _loadedForId; // guard so a re-render doesn't reload the same line repeatedly

    _quoteLineItemId;

    @api
    get quoteLineItemId() {
        return this._quoteLineItemId;
    }
    set quoteLineItemId(value) {
        this._quoteLineItemId = value;
        // Load whenever the target line changes (also covers the initial set on insertion).
        if (value && value !== this._loadedForId) {
            this.load();
        }
    }

    connectedCallback() {
        if (this._quoteLineItemId && this._quoteLineItemId !== this._loadedForId) {
            this.load();
        }
    }

    get hasAttributes() {
        return this.attributes.length > 0;
    }

    get showEmpty() {
        return !this.loading && !this.errorMessage && this.attributes.length === 0;
    }

    // Save is available only when something actually changed (and not while a save is in flight).
    get saveDisabled() {
        return this.saving || this.readOnly || !this.isDirty;
    }

    // Whether this picker has unsaved changes — read by a host driving a consolidated "Save All".
    @api
    get isDirty() {
        return this.attributes.some((a) => a.dirty);
    }

    get showOwnSaveButton() {
        return !this.readOnly && !this.hideSave;
    }

    async load() {
        this._loadedForId = this._quoteLineItemId;
        this.loading = true;
        this.errorMessage = '';
        try {
            const res = this._parse(
                await getLineAttributes({
                    inputJson: JSON.stringify({
                        quoteLineItemId: this._quoteLineItemId,
                        attributeCodes: this.attributeCodes || null
                    })
                })
            );
            if (res.isSuccess === false) {
                this.errorMessage = res.errorMessage || 'Unable to load attributes.';
                this.attributes = [];
                return;
            }
            this.attributes = (res.attributes || []).map((a) => this._toViewModel(a));
        } catch (e) {
            this.errorMessage = this._errMessage(e);
            this.attributes = [];
        } finally {
            this.loading = false;
        }
    }

    // Build a render-ready view model from a server attribute descriptor: choose a control kind from
    // the DataType, seed the current value, and remember the original for change detection.
    _toViewModel(a) {
        const dataType = (a.dataType || '').toLowerCase();
        const isPicklist = !!a.picklistId;
        const isCheckbox = !isPicklist && (dataType === 'checkbox' || dataType === 'boolean');
        const isNumber =
            !isPicklist &&
            !isCheckbox &&
            (dataType === 'number' || dataType === 'currency' || dataType === 'percent' || dataType === 'integer' || dataType === 'double');
        const isDate = !isPicklist && !isCheckbox && (dataType === 'date' || dataType === 'datetime');

        const options = isPicklist
            ? [{ label: '— None —', value: '' }].concat((a.picklistValues || []).map((v) => ({ label: v.label, value: v.id })))
            : [];

        // Keep the server (original) value distinct from the displayed value: for an unset picklist we
        // seed the platform default below, which must read as a change so a Save persists it.
        let origValue = '';
        let value = '';
        let checked = false;
        if (isPicklist) {
            origValue = a.currentPicklistValueId || '';
            // With no saved value, pre-select the picklist's default (AttributePicklistValue.IsDefault)
            // so attributes like Directionality → "Between" and Measure → "No Requirement" come up set.
            const defaultOption = origValue ? null : (a.picklistValues || []).find((v) => v.isDefault === true);
            value = origValue || (defaultOption ? defaultOption.id : '');
        } else if (isCheckbox) {
            checked = String(a.currentValue).toLowerCase() === 'true';
        } else {
            value = a.currentValue != null ? String(a.currentValue) : '';
            origValue = value;
        }

        const inputType = isCheckbox ? 'checkbox' : isNumber ? 'number' : isDate ? (dataType === 'datetime' ? 'datetime' : 'date') : 'text';

        return {
            key: a.attributeDefinitionId,
            attributeDefinitionId: a.attributeDefinitionId,
            label: a.label,
            code: a.code,
            required: !!a.isRequired,
            disabled: this.readOnly || !!a.isReadOnly,
            isPicklist,
            isCheckbox,
            isTextlike: !isPicklist && !isCheckbox,
            inputType,
            options,
            value,
            checked,
            // Originals for change detection (server state, not the seeded default).
            _origValue: origValue,
            _origChecked: checked,
            // A seeded default (value differs from the empty server value) starts dirty so Save persists it.
            dirty: value !== origValue
        };
    }

    handlePicklistChange(event) {
        this._update(event.target.dataset.id, { value: event.detail.value });
    }

    handleInputChange(event) {
        this._update(event.target.dataset.id, { value: event.target.value });
    }

    handleCheckboxChange(event) {
        this._update(event.target.dataset.id, { checked: event.target.checked });
    }

    _update(id, patch) {
        this.attributes = this.attributes.map((a) => {
            if (a.attributeDefinitionId !== id) {
                return a;
            }
            const next = { ...a, ...patch };
            next.dirty = next.isCheckbox ? next.checked !== next._origChecked : next.value !== next._origValue;
            return next;
        });
    }

    handleSave() {
        this.save();
    }

    /**
     * Persist this line's changed attributes. Public so a host (e.g. the cart's "Save All") can drive
     * saving across many pickers. Resolves to a plain result the caller can aggregate:
     *   { status: 'saved' | 'noop' | 'invalid' | 'error', savedCount, errorMessage }
     * Never rejects. `silent` suppresses the per-line success toast (the host shows one summary toast).
     */
    @api
    async save({ silent = false } = {}) {
        if (this.saving || this.readOnly || !this.isDirty) {
            return { status: 'noop', savedCount: 0 };
        }
        // Client-side required check (the server re-validates fail-closed).
        const missing = this.attributes.filter((a) => a.required && this._isBlank(a));
        if (missing.length) {
            this.errorMessage = `Required: ${missing.map((a) => a.label).join(', ')}.`;
            return { status: 'invalid', savedCount: 0, errorMessage: this.errorMessage };
        }
        const payload = this.attributes.filter((a) => a.dirty).map((a) => this._toPayload(a));
        if (payload.length === 0) {
            return { status: 'noop', savedCount: 0 };
        }
        this.saving = true;
        this.errorMessage = '';
        try {
            const res = this._parse(
                await saveLineAttributes({
                    inputJson: JSON.stringify({ quoteLineItemId: this._quoteLineItemId, attributes: payload })
                })
            );
            if (res.isSuccess === false) {
                this.errorMessage = res.errorMessage || 'Unable to save attributes.';
                return { status: 'error', savedCount: 0, errorMessage: this.errorMessage };
            }
            if (!silent) {
                this._toast('Attributes saved', `${res.savedCount} attribute(s) updated.`, 'success');
            }
            // Reload to reflect persisted state (new PATCH-vs-POST baseline, cleared dirty flags).
            this._loadedForId = null;
            await this.load();
            this.dispatchEvent(
                new CustomEvent('attributessaved', {
                    detail: { quoteLineItemId: this._quoteLineItemId, savedCount: res.savedCount },
                    bubbles: true,
                    composed: true
                })
            );
            return { status: 'saved', savedCount: res.savedCount };
        } catch (e) {
            this.errorMessage = this._errMessage(e);
            return { status: 'error', savedCount: 0, errorMessage: this.errorMessage };
        } finally {
            this.saving = false;
        }
    }

    // A changed attribute → the save payload. A blank value clears (server DELETEs the existing row).
    _toPayload(a) {
        if (a.isPicklist) {
            return { attributeDefinitionId: a.attributeDefinitionId, attributePicklistValueId: a.value || null };
        }
        if (a.isCheckbox) {
            return { attributeDefinitionId: a.attributeDefinitionId, attributeValue: a.checked ? 'true' : 'false' };
        }
        const v = a.value != null ? String(a.value).trim() : '';
        return { attributeDefinitionId: a.attributeDefinitionId, attributeValue: v || null };
    }

    _isBlank(a) {
        if (a.isCheckbox) {
            return false; // a checkbox always has a value (true/false)
        }
        return a.value == null || String(a.value).trim() === '';
    }

    _parse(json) {
        try {
            return json ? JSON.parse(json) : {};
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
