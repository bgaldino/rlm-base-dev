import { LightningElement, api } from 'lwc';

/**
 * In-row selling-model selector for the Contracted Pricing catalog datatable. Rendered as a custom
 * column type: a product with multiple selling models shows a combobox; a single-model product
 * shows its model as plain text (no needless control). Selecting a model dispatches a `modelchange`
 * event carrying the chosen { pbeId, productSellingModelId, sellingModelType } so the parent can
 * retarget add/configure to that PBE. The datatable rebinds value/options on every re-render, so
 * this component holds no draft state of its own.
 */
export default class DlSellingModelPicker extends LightningElement {
    @api rowKey; // the product row's key — echoed back so the parent maps the event to its row
    @api selectedPbeId; // currently selected PBE (the row's effective pbeId)
    @api sellingModels = []; // [{ pbeId, productSellingModelId, sellingModelType, label }]

    get hasChoice() {
        return Array.isArray(this.sellingModels) && this.sellingModels.length > 1;
    }

    // Label for the single-model case; blank if somehow model-less (the row wouldn't render then).
    get singleLabel() {
        const models = this.sellingModels || [];
        return models.length ? this._labelFor(models[0]) : '';
    }

    // A native <select> reflects selection via each option's `selected` attribute (not a `value`
    // prop), so mark the option whose pbeId matches the row's current selection.
    get options() {
        return (this.sellingModels || []).map((m) => ({
            label: this._labelFor(m),
            value: m.pbeId,
            selected: m.pbeId === this.selectedPbeId
        }));
    }

    // Stop the click from also reaching lightning-datatable's row-selection handler.
    stopEvent(event) {
        event.stopPropagation();
    }

    handleChange(event) {
        // Native <select> carries the chosen value on event.target, not event.detail.
        const pbeId = event.target.value;
        const model = (this.sellingModels || []).find((m) => m.pbeId === pbeId);
        if (!model) {
            return;
        }
        this.dispatchEvent(
            new CustomEvent('modelchange', {
                detail: {
                    rowKey: this.rowKey,
                    pbeId: model.pbeId,
                    productSellingModelId: model.productSellingModelId,
                    sellingModelType: model.sellingModelType
                },
                bubbles: true,
                composed: true
            })
        );
    }

    // Prefer the server-provided PSM Name (e.g. "Term Based - Semi-Annual" — what distinguishes two
    // TermDefined models); fall back to a humanized enum (TermDefined → "Term Defined") if absent.
    _labelFor(model) {
        if (model && model.label) {
            return model.label;
        }
        const type = model && model.sellingModelType;
        return type ? String(type).replace(/([a-z])([A-Z])/g, '$1 $2') : '';
    }
}
