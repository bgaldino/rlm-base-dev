import { LightningElement, api } from "lwc";
import {
  METHOD_PRODUCT,
  METHOD_FARECLASS,
  edrExisting,
  edrProposed,
  totalsSummary,
  clamp,
  round1,
  pct1
} from "c/dlDemoModel";

const METHOD_OPTIONS = [
  { label: "Product", value: METHOD_PRODUCT },
  { label: "Fare Class", value: METHOD_FARECLASS }
];

/**
 * dlModelingGrid — the client-only negotiation modeling spreadsheet (demo stage ③).
 *
 * A controlled component: the shell (c/dlmWorkspaceShell) owns the per-(term, method) model cache and
 * hands this grid exactly ONE model to edit via @api model. The grid keeps a private working copy,
 * mutates it as the analyst edits, recomputes the derived columns synchronously, and emits:
 *   - `modelchange` { termId, method, model, summary } — after any edit (coalesced to one per frame).
 *   - `methodchange` { termId, method } — when the discounting method toggle flips (the shell swaps in
 *     the cached/seeded model for that method and passes it back down).
 *   - `expandtoggle` { expanded } — Expand-Workspace affordance (the shell collapses the rail).
 *
 * Editing UX mirrors the proven c/dlQuoteLineGrid pattern (inline lightning-inputs + data-* datasets +
 * clamp). Product and Fare Class are genuinely different row sets over the Term's REAL fares (see
 * c/dlDemoModel.buildRows), never a relabel of one set. The negotiation is a single proposed set: one
 * editable Proposed Disc % per fare drives the KPIs and the Apply-Final-Offer handoff — no rounds.
 */
export default class DlModelingGrid extends LightningElement {
  @api term;
  @api currencyCode = "USD";
  @api expanded = false;

  _model = null;
  _working = null;
  _emitScheduled = false;

  @api
  get model() {
    return this._model;
  }
  set model(value) {
    this._model = value || null;
    this._working = value ? this._clone(value) : null;
  }

  // ---------- method toggle ----------

  get methodOptions() {
    return METHOD_OPTIONS;
  }

  get method() {
    return this._working ? this._working.method : METHOD_PRODUCT;
  }

  get isProductMethod() {
    return this.method === METHOD_PRODUCT;
  }

  get valueColumnLabel() {
    return this.isProductMethod ? "Product" : "Fare Class";
  }

  handleMethodChange(event) {
    const method = event.detail.value;
    if (!this._working || method === this._working.method) {
      return;
    }
    this.dispatchEvent(
      new CustomEvent("methodchange", {
        detail: { termId: this._working.termId, method },
        bubbles: true,
        composed: true
      })
    );
  }

  // ---------- state ----------

  get hasModel() {
    return !!this._working && Array.isArray(this._working.rows);
  }

  // A model with no fares (Term has no lines yet) renders an empty-state instead of a headerless grid.
  get hasRows() {
    return this.hasModel && this._working.rows.length > 0;
  }

  // ---------- expand affordance ----------

  get expandLabel() {
    return this.expanded ? "Collapse Workspace" : "Expand Workspace";
  }

  get expandIcon() {
    return this.expanded ? "utility:contract_alt" : "utility:expand_alt";
  }

  handleToggleExpand() {
    this.dispatchEvent(
      new CustomEvent("expandtoggle", {
        detail: { expanded: !this.expanded },
        bubbles: true,
        composed: true
      })
    );
  }

  // ---------- rows ----------

  // Build the render rows: each fare's spend mix + existing/prior/proposed discounts. Prior Disc % is a
  // read-only reference column; the rest are inline-editable.
  get displayRows() {
    if (!this._working) {
      return [];
    }
    const rows = this._working.rows;
    return rows.map((r) => {
      // Read-only prior-cycle discount context (null unless the fare was enriched from getQuoteLines).
      const hasPrior = r.priorDiscountPct !== null && r.priorDiscountPct !== undefined;
      return {
        key: r.key,
        label: r.label,
        currentExistingPct: r.currentExistingPct,
        projectedPct: r.projectedPct,
        existingDiscountPct: r.existingDiscountPct,
        priorDiscountDisplay: hasPrior ? pct1(r.priorDiscountPct) : "—",
        proposedPct: r.proposedDiscountPct
      };
    });
  }

  // Sticky totals row: Spend % / Projected % sums + validity flags (per c/dlDemoModel.totalsSummary).
  get totals() {
    if (!this._working) {
      return null;
    }
    const t = totalsSummary(this._working.rows);
    return {
      ceTotal: `${round1(t.ceTotal).toFixed(1)}%`,
      projectedTotal: `${round1(t.projectedTotal).toFixed(1)}%`,
      ceValid: t.ceValid,
      projectedValid: t.projectedValid,
      ceClass: t.ceValid ? "dl-mg-total" : "dl-mg-total dl-mg-total_bad",
      projectedClass: t.projectedValid ? "dl-mg-total" : "dl-mg-total dl-mg-total_bad"
    };
  }

  get showTotalsWarning() {
    const t = this.totals;
    return t && (!t.ceValid || !t.projectedValid);
  }

  // Existing EDR + Proposed EDR for the summary line under the grid.
  get edrSummary() {
    if (!this._working) {
      return null;
    }
    return {
      existing: pct1(edrExisting(this._working.rows)),
      proposed: pct1(edrProposed(this._working.rows))
    };
  }

  // ---------- cell edits ----------

  _row(key) {
    return this._working && this._working.rows.find((r) => r.key === key);
  }

  handleCurrentExistingChange(event) {
    const r = this._row(event.target.dataset.key);
    if (r) {
      r.currentExistingPct = clamp(event.target.value, 0, 100);
      this._recomputeAndEmit();
    }
  }

  handleProjectedChange(event) {
    const r = this._row(event.target.dataset.key);
    if (r) {
      r.projectedPct = clamp(event.target.value, 0, 100);
      this._recomputeAndEmit();
    }
  }

  handleExistingDiscountChange(event) {
    const r = this._row(event.target.dataset.key);
    if (r) {
      r.existingDiscountPct = clamp(event.target.value, 0, 100);
      this._recomputeAndEmit();
    }
  }

  handleProposedChange(event) {
    const r = this._row(event.target.dataset.key);
    if (r) {
      r.proposedDiscountPct = clamp(event.target.value, 0, 100);
      this._recomputeAndEmit();
    }
  }

  // ---------- recompute + emit ----------

  // A recompute is just re-reading the getters (derived columns are pure functions of _working); the
  // reassignment nudges LWC reactivity for the nested-array mutations, and the emit is coalesced.
  _recomputeAndEmit() {
    this._working = { ...this._working };
    this._scheduleEmit();
  }

  _scheduleEmit() {
    if (this._emitScheduled) {
      return;
    }
    this._emitScheduled = true;
    Promise.resolve().then(() => {
      this._emitScheduled = false;
      this._emitModelChange();
    });
  }

  _emitModelChange() {
    if (!this._working) {
      return;
    }
    const m = this._working;
    const t = totalsSummary(m.rows);
    const summary = {
      edrExisting: edrExisting(m.rows),
      edrProposed: edrProposed(m.rows),
      totalsValid: t.ceValid && t.projectedValid
    };
    this.dispatchEvent(
      new CustomEvent("modelchange", {
        detail: { termId: m.termId, method: m.method, model: this._clone(m), summary },
        bubbles: true,
        composed: true
      })
    );
  }

  _clone(obj) {
    return JSON.parse(JSON.stringify(obj));
  }
}
