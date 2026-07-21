import { LightningElement, api } from "lwc";
import {
  METHOD_PRODUCT,
  METHOD_FARECLASS,
  computeUndiscounted,
  edrExisting,
  edrByRound,
  totalsSummary,
  clamp,
  round1,
  num,
  formatKpi,
  pct1
} from "c/dlDemoModel";

const METHOD_OPTIONS = [
  { label: "Product", value: METHOD_PRODUCT },
  { label: "Fare Class", value: METHOD_FARECLASS }
];

const STATUS_OPTIONS = ["Draft", "Sent", "Countered", "Recommended"];

/**
 * dlModelingGrid — the client-only negotiation modeling spreadsheet (demo stage ③).
 *
 * A controlled component: the orchestrator (c/dlTermBuilder) owns the per-(term, method) model cache
 * and hands this grid exactly ONE model to edit via @api model. The grid keeps a private working copy,
 * mutates it as the analyst edits, recomputes the derived columns (Undiscounted Existing spend mix,
 * per-round EDR) synchronously, and emits:
 *   - `modelchange` { termId, method, model, summary } — after any edit (coalesced to one per frame).
 *   - `methodchange` { termId, method } — when the discounting method toggle flips (the orchestrator
 *     swaps in the cached/seeded model for that method and passes it back down).
 *   - `expandtoggle` { expanded } — Expand-Workspace affordance (the orchestrator collapses the rail).
 *
 * Editing UX mirrors the proven c/dlQuoteLineGrid pattern (inline lightning-inputs + data-* datasets +
 * clamp). Product and Fare Class are genuinely different row sets (see c/dlDemoModel.buildRows), never
 * a relabel of one set. Rounds are explicit: the *view* round is the one shown/edited in the main grid;
 * the *current* round drives KPIs; the *final offer* round drives the proposal + apply handoff.
 */
export default class DlModelingGrid extends LightningElement {
  @api term;
  @api currencyCode = "USD";
  @api expanded = false;

  _model = null;
  _working = null;
  // Which round's Proposed column is shown/edited in the main grid. Distinct from the model's
  // currentRoundIndex (drives KPIs) and finalOfferRoundIndex (drives the proposal).
  _viewRoundIndex = 0;
  _emitScheduled = false;

  @api
  get model() {
    return this._model;
  }
  set model(value) {
    this._model = value || null;
    this._working = value ? this._clone(value) : null;
    if (this._working) {
      // Default the view round to whatever currently drives KPIs so the grid opens on the "live" round.
      this._viewRoundIndex = this._working.currentRoundIndex;
    }
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

  // ---------- rounds ----------

  get hasModel() {
    return !!this._working && Array.isArray(this._working.rows);
  }

  // Round selector chips. Marks which round is being viewed, which drives KPIs (current), and which is
  // the selected final offer.
  get roundChips() {
    if (!this._working) {
      return [];
    }
    const labels = this._working.roundLabels || [];
    const edrs = edrByRound(this._working.rows, labels.length);
    return labels.map((label, i) => {
      const isView = i === this._viewRoundIndex;
      const isCurrent = i === this._working.currentRoundIndex;
      const isFinal = i === this._working.finalOfferRoundIndex;
      const badges = [];
      if (isCurrent) {
        badges.push("Current");
      }
      if (isFinal) {
        badges.push("Final Offer");
      }
      let cls = "dl-mg-round";
      if (isView) {
        cls += " dl-mg-round_view";
      }
      if (isCurrent) {
        cls += " dl-mg-round_current";
      }
      return {
        index: i,
        label,
        edr: pct1(edrs[i]),
        badgeText: badges.join(" · "),
        hasBadge: badges.length > 0,
        status: (this._working.roundStatuses || [])[i] || "Draft",
        cls,
        ariaPressed: isView ? "true" : "false"
      };
    });
  }

  get viewRoundLabel() {
    const labels = (this._working && this._working.roundLabels) || [];
    return labels[this._viewRoundIndex] || "Round";
  }

  get proposedColumnLabel() {
    return `Proposed · ${this.viewRoundLabel}`;
  }

  get copyPreviousDisabled() {
    return this._viewRoundIndex === 0;
  }

  get isViewCurrentRound() {
    return this._working && this._viewRoundIndex === this._working.currentRoundIndex;
  }

  // Emphasize "Set as Current Round" (brand) when the viewed round isn't yet driving KPIs — the demo's
  // headline action. Once it is current, drop to neutral (also disabled).
  get setCurrentVariant() {
    return this.isViewCurrentRound ? "neutral" : "brand";
  }

  get isViewFinalOffer() {
    return this._working && this._viewRoundIndex === this._working.finalOfferRoundIndex;
  }

  get statusOptions() {
    return STATUS_OPTIONS.map((s) => ({ label: s, value: s }));
  }

  get viewRoundStatus() {
    return ((this._working && this._working.roundStatuses) || [])[this._viewRoundIndex] || "Draft";
  }

  handleRoundSelect(event) {
    const index = parseInt(event.currentTarget.dataset.index, 10);
    if (!Number.isNaN(index)) {
      this._viewRoundIndex = index;
    }
  }

  handleCopyPrevious() {
    if (this._viewRoundIndex === 0 || !this._working) {
      return;
    }
    const from = this._viewRoundIndex - 1;
    const to = this._viewRoundIndex;
    this._working.rows.forEach((r) => {
      r.rounds[to] = r.rounds[from];
    });
    this._recomputeAndEmit();
  }

  handleSetCurrentRound() {
    if (!this._working) {
      return;
    }
    this._working.currentRoundIndex = this._viewRoundIndex;
    this._recomputeAndEmit();
  }

  handleSetFinalOffer() {
    if (!this._working) {
      return;
    }
    this._working.finalOfferRoundIndex = this._viewRoundIndex;
    this._recomputeAndEmit();
  }

  handleStatusChange(event) {
    if (!this._working) {
      return;
    }
    const statuses = [...(this._working.roundStatuses || [])];
    statuses[this._viewRoundIndex] = event.detail.value;
    this._working.roundStatuses = statuses;
    this._recomputeAndEmit();
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

  // Build the render rows: each model row plus its derived Undiscounted Existing % and the active view
  // round's Proposed value. Cell error flags mark out-of-range distribution entries.
  get displayRows() {
    if (!this._working) {
      return [];
    }
    const rows = this._working.rows;
    const ue = computeUndiscounted(rows);
    const view = this._viewRoundIndex;
    return rows.map((r, i) => {
      const rowClass =
        "dl-mg-row" +
        (r.zeroSpend ? " dl-mg-row_zero" : "") +
        (r.isPartner ? " dl-mg-row_partner" : "");
      return {
        key: r.key,
        label: r.label,
        carrier: r.carrier,
        isPartner: r.isPartner,
        zeroSpend: r.zeroSpend,
        isLaneFare: r.isLaneFare,
        rowClass,
        currentExistingPct: r.currentExistingPct,
        undiscountedPct: ue[i],
        projectedPct: r.projectedPct,
        existingDiscountPct: r.existingDiscountPct,
        proposedPct: r.rounds[view],
        compareFare: r.isLaneFare ? r.compareFare : null,
        compareDisplay: r.isLaneFare ? r.compareFare : "—",
        notes: r.notes
      };
    });
  }

  // Sticky totals row: CE / UE / Projected sums + validity flags (per c/dlDemoModel.totalsSummary).
  get totals() {
    if (!this._working) {
      return null;
    }
    const t = totalsSummary(this._working.rows);
    return {
      ceTotal: `${round1(t.ceTotal).toFixed(1)}%`,
      ueTotal: `${round1(t.ueTotal).toFixed(1)}%`,
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

  // Existing EDR + view-round EDR for the summary line under the grid.
  get edrSummary() {
    if (!this._working) {
      return null;
    }
    const existing = edrExisting(this._working.rows);
    const edrs = edrByRound(this._working.rows, (this._working.roundLabels || []).length);
    return {
      existing: pct1(existing),
      viewRound: pct1(edrs[this._viewRoundIndex]),
      current: pct1(edrs[this._working.currentRoundIndex]),
      finalOffer: pct1(edrs[this._working.finalOfferRoundIndex]),
      viewLabel: this.viewRoundLabel
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
      r.rounds[this._viewRoundIndex] = clamp(event.target.value, 0, 100);
      this._recomputeAndEmit();
    }
  }

  handleCompareFareChange(event) {
    const r = this._row(event.target.dataset.key);
    if (r) {
      r.compareFare = Math.max(0, num(event.target.value));
      this._recomputeAndEmit();
    }
  }

  handleNotesChange(event) {
    const r = this._row(event.target.dataset.key);
    if (r) {
      r.notes = event.target.value;
      // Notes don't affect KPIs; still emit so the model stays in sync for the proposal/export.
      this._scheduleEmit();
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
    const edrs = edrByRound(m.rows, (m.roundLabels || []).length);
    const t = totalsSummary(m.rows);
    const summary = {
      edrExisting: edrExisting(m.rows),
      edrByRound: edrs,
      edrCurrentRound: edrs[m.currentRoundIndex],
      currentRoundIndex: m.currentRoundIndex,
      finalOfferRoundIndex: m.finalOfferRoundIndex,
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

  // Formatting passthroughs for the template.
  formatCurrency(value) {
    return formatKpi(value, "currency", this.currencyCode);
  }

  _clone(obj) {
    return JSON.parse(JSON.stringify(obj));
  }
}
