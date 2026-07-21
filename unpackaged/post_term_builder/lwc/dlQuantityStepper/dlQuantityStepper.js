import { LightningElement, api } from 'lwc';

/**
 * In-row instance-count field for the product cart's discovery datatable. Rendered as a custom
 * column type (see c/dlCatalogDatatable), it mirrors c/dlSellingModelPicker: a tiny child
 * component that dispatches a composed `quantitychange` event so it escapes the datatable's shadow
 * root and reaches the cart. The datatable rebinds `value` on every re-render, so this holds no
 * draft state of its own.
 *
 * `value` is the number of separate Quantity-1 QuoteLineItems the product will become on checkout
 * (instances), NOT a QuoteLineItem.Quantity. It is clamped to [1, max].
 */
const DEFAULT_MAX = 50;

export default class DlQuantityStepper extends LightningElement {
    @api rowKey; // the product row's key — echoed back so the cart maps the event to its row
    @api value = 1; // current instance count
    @api max = DEFAULT_MAX;

    get effectiveMax() {
        const m = Number(this.max);
        return Number.isFinite(m) && m > 0 ? m : DEFAULT_MAX;
    }

    get current() {
        return this._clamp(this.value);
    }

    // Stop the click from also toggling lightning-datatable's row selection.
    stopEvent(event) {
        event.stopPropagation();
    }

    handleChange(event) {
        // Native input carries the value on event.target.
        this._emit(Number(event.target.value));
    }

    _emit(next) {
        const value = this._clamp(next);
        this.dispatchEvent(
            new CustomEvent('quantitychange', {
                detail: { rowKey: this.rowKey, value },
                bubbles: true,
                composed: true
            })
        );
    }

    _clamp(raw) {
        const n = Math.floor(Number(raw));
        if (!Number.isFinite(n) || n < 1) {
            return 1;
        }
        return Math.min(n, this.effectiveMax);
    }
}
