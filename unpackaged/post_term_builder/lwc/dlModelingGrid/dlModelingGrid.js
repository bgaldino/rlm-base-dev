import { LightningElement, api } from "lwc";
import {
  edrExisting,
  edrProposed,
  totalsSummary,
  clamp,
  round1,
  pct1
} from "c/dlDemoModel";

// Alliance Partner options — the DL_Carriers global value set (value == label, restricted picklist).
// Stable catalog, so hardcoded rather than fetched (matches the c/dlmQuoteLineGrid fare-code pattern).
const ALLIANCE_PARTNER_VALUES = [
  "Air France",
  "KLM Royal Dutch Airlines",
  "Virgin Atlantic",
  "Aeromexico",
  "Korean Air",
  "LATAM Airlines",
  "WestJet"
];
const ALLIANCE_PARTNER_OPTIONS = ALLIANCE_PARTNER_VALUES.map((c) => ({ label: c, value: c }));

/**
 * dlModelingGrid — the client-only negotiation modeling spreadsheet.
 *
 * A controlled component: the shell (c/dlmWorkspaceShell) owns the per-term model cache and hands this
 * grid exactly ONE model to edit via @api model. The grid keeps a private working copy, mutates it as
 * the analyst edits, recomputes the derived columns synchronously, and emits:
 *   - `modelchange` { termId, method, model, summary } — after any spend/discount edit (coalesced to
 *     one per frame).
 *   - `alliancechange` { backingFareId, alliancePartners } — when a row's Alliance Partner multiselect
 *     changes; the shell persists it to the backing QuoteLineItem immediately (each row independently).
 *
 * The grid is locked to the Product row set (one row per REAL fare, 1:1 with a QuoteLineItem via
 * `backingFareId`; see c/dlDemoModel.buildRows), with each row labeled by its product and fare codes,
 * e.g. `Delta One (J C)`. The negotiation is a single proposed set: one editable Proposed Disc % per
 * fare drives the KPIs and the Apply-Final-Offer handoff — no rounds, no method toggle.
 *
 * Editing UX mirrors the proven c/dlmQuoteLineGrid pattern (inline lightning-inputs + data-* datasets +
 * clamp; an expander per row reveals the Alliance Partner dual-listbox inline beneath it).
 */
export default class DlModelingGrid extends LightningElement {
  @api term;
  @api currencyCode = "USD";

  _model = null;
  _working = null;
  _emitScheduled = false;
  // Row keys whose Alliance Partner editor is expanded.
  _expandedKeys = new Set();
  // A querySelector run once after the next render to place focus (expander ↔ detail region).
  _focusTarget = null;

  @api
  get model() {
    return this._model;
  }
  set model(value) {
    this._model = value || null;
    this._working = value ? this._clone(value) : null;
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

  // ---------- alliance partner options ----------

  get alliancePartnerOptions() {
    return ALLIANCE_PARTNER_OPTIONS;
  }

  // ---------- state ----------

  get hasModel() {
    return !!this._working && Array.isArray(this._working.rows);
  }

  // A model with no fares (Term has no lines yet) renders an empty-state instead of a headerless grid.
  get hasRows() {
    return this.hasModel && this._working.rows.length > 0;
  }

  // ---------- rows ----------

  // Build the flat render list: each fare emits a base data row (spend mix + prior/proposed discounts,
  // labeled with its fare codes), and each expanded row additionally emits a detail row hosting the
  // Alliance Partner dual-listbox. Prior Disc % is a read-only reference column; the spend/discount
  // cells are inline-editable.
  get displayRows() {
    if (!this._working) {
      return [];
    }
    const out = [];
    this._working.rows.forEach((r) => {
      // Read-only prior-cycle discount context (null unless the fare was enriched from getQuoteLines).
      const hasPrior = r.priorDiscountPct !== null && r.priorDiscountPct !== undefined;
      const fareCodes = Array.isArray(r.fareCodes) ? r.fareCodes : [];
      const alliancePartners = Array.isArray(r.alliancePartners) ? r.alliancePartners : [];
      const expanded = this._expandedKeys.has(r.key);
      out.push({
        key: r.key,
        isDetail: false,
        // Label the row as the product with its fare codes in parentheses, e.g. "Delta One (J C)".
        label: fareCodes.length ? `${r.label} (${fareCodes.join(" ")})` : r.label,
        currentExistingPct: r.currentExistingPct,
        projectedPct: r.projectedPct,
        priorDiscountDisplay: hasPrior ? pct1(r.priorDiscountPct) : "—",
        proposedPct: r.proposedDiscountPct,
        // Alliance Partner per-row editor. The backing QuoteLineItem id drives independent persistence;
        // a row without one (no backing fare) can't be persisted, so it isn't expandable.
        backingFareId: r.backingFareId || null,
        allianceSummary: alliancePartners.length ? alliancePartners.join(" · ") : "—",
        expandable: !!r.backingFareId,
        expanded,
        expandedStr: expanded ? "true" : "false",
        expanderIcon: expanded ? "utility:chevrondown" : "utility:chevronright",
        expanderTitle: expanded ? "Collapse alliance partners" : "Expand alliance partners",
        detailRegionId: this._detailRegionId(r.key)
      });
      if (expanded) {
        out.push({
          key: `${r.key}-detail`,
          isDetail: true,
          rowKey: r.key,
          backingFareId: r.backingFareId || null,
          detailRegionId: this._detailRegionId(r.key),
          detailLabel: `Alliance partners for ${r.label}`,
          alliancePartnersValue: alliancePartners,
          // value + Spend % + Projected % + Prior Disc % + Proposed Disc % (the expander shares the
          // value column, so the detail row spans all five columns).
          colspan: 5
        });
      }
    });
    return out;
  }

  _detailRegionId(key) {
    return `dl-mg-detail-${String(key).replace(/[^a-zA-Z0-9_-]/g, "_")}`;
  }

  // Spend % / Projected % sums + validity flags (per c/dlDemoModel.totalsSummary). Drives the
  // provisional-KPI warning banner when the spend distribution doesn't total 100%.
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

  handleProposedChange(event) {
    const r = this._row(event.target.dataset.key);
    if (r) {
      r.proposedDiscountPct = clamp(event.target.value, 0, 100);
      this._recomputeAndEmit();
    }
  }

  // ---------- alliance partner (per-row) ----------

  // Toggle a row's Alliance Partner editor. On expand, move focus into the detail region; on collapse,
  // return focus to the triggering expander. (Native <button> gives Enter/Space for free.)
  handleToggleExpand(event) {
    const key = event.currentTarget.dataset.key;
    if (this._expandedKeys.has(key)) {
      this._expandedKeys.delete(key);
      this._focusTarget = `[data-expander="${key}"]`;
    } else {
      this._expandedKeys.add(key);
      this._focusTarget = `[data-detail="${key}"]`;
    }
    // The Set mutation isn't reactive on its own; reassigning _working re-renders displayRows.
    this._working = { ...this._working };
  }

  // Alliance Partner multiselect (dual-listbox) → array of selected partners. Updates the working row
  // and emits `alliancechange` up to the shell, which persists it to the backing QuoteLineItem
  // independently (no draft/Save — each row changes on its own, mirroring the header carriers concept).
  handleAllianceChange(event) {
    const r = this._row(event.target.dataset.key);
    if (!r) {
      return;
    }
    const selected = Array.isArray(event.detail.value) ? [...event.detail.value] : [];
    r.alliancePartners = selected;
    this._working = { ...this._working };
    this.dispatchEvent(
      new CustomEvent("alliancechange", {
        detail: { backingFareId: r.backingFareId || null, alliancePartners: selected },
        bubbles: true,
        composed: true
      })
    );
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
