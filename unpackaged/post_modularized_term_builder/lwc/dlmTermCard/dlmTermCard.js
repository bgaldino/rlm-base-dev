import { LightningElement, api } from "lwc";
import { scopeLabel, scopeTypeRank } from "c/dlDemoModel";

// Route-attribute codes the rail chip summarizes (must match the PC-DL-TERM attribute defs). The
// card only READS these off the term payload getBuilderState already returns; it never queries.
const ORIGIN_CODE = "DL_Origin";
const DESTINATION_CODE = "DL_Destination";
const DIRECTIONALITY_CODE = "DL_Directionality";
const MEASURE_CODE = "DL_Measure";
const REQUIREMENT_CODE = "DL_RequirementValue";
const SCOPE_TYPE_CODE = "DL_ScopeType";
const MARKET_GROUP_CODE = "DL_MarketGroup";

/**
 * Presentational rail chip for one Term in c/dlTermBuilder. Renders the Term's display name, its
 * fare-line count, and a one-line route/requirement summary derived from the route attributes the
 * builder-state payload already carries — so the rail renders with no extra server calls.
 *
 * Owns no data and does no I/O: it takes a `term` object (as shaped by
 * RLM_DeltaTermBuilderController.getBuilderState) plus a `selected` flag, and emits a composed
 * `termselect` event ({ termId }) when clicked or activated by keyboard.
 */
export default class DlmTermCard extends LightningElement {
  @api term;
  @api selected = false;

  // Transient, client-only scope operator (Includes | Excludes). Deliberately NOT a persisted
  // DL_* attribute (see the dl-termbuilder plan README): it lives on the card, defaults to
  // "Includes", is lost on reload, and only steers how this card renders its scope label. Changes
  // are emitted as `operatorchange` so a parent could use it for filtering later.
  _operator = "Includes";

  get displayName() {
    return (this.term && this.term.displayName) || "Untitled Term";
  }

  get fareCount() {
    return (this.term && Number(this.term.fareCount)) || 0;
  }

  get fareCountLabel() {
    const n = this.fareCount;
    return `${n} fare${n === 1 ? "" : "s"}`;
  }

  // Map the term's attribute list (code → display value) once for the summary getters.
  get attrMap() {
    const map = {};
    const attrs = (this.term && this.term.attributes) || [];
    attrs.forEach((a) => {
      if (a && a.code) {
        map[a.code] = a.value;
      }
    });
    return map;
  }

  // "ATL — Airport → LHR — Airport" (or "Between ATL … LHR" when directionality is set). Blank
  // until at least one endpoint is chosen.
  get routeLabel() {
    const m = this.attrMap;
    const origin = m[ORIGIN_CODE];
    const destination = m[DESTINATION_CODE];
    if (!origin && !destination) {
      return "";
    }
    const arrow = m[DIRECTIONALITY_CODE] === "Between" ? " ↔ " : " → ";
    return `${origin || "—"}${arrow}${destination || "—"}`;
  }

  // One-line geography summary ("Country · Includes GB, FR · Between"); blank when no scope attrs
  // set. The Includes/Excludes wording is driven by the transient card-local operator, not the term.
  get scopeLabel() {
    return scopeLabel(this.term, this._operator);
  }

  // The operator toggle only makes sense when the Term declares a market group to include/exclude;
  // a route-only or scope-type-only Term has nothing for the operator to act on, so hide it.
  get showOperatorToggle() {
    return !!this.attrMap[MARKET_GROUP_CODE];
  }

  get includesActive() {
    return this._operator !== "Excludes";
  }

  get excludesActive() {
    return this._operator === "Excludes";
  }

  get includesClass() {
    return this.includesActive
      ? "dl-term-card__op dl-term-card__op_active"
      : "dl-term-card__op";
  }

  get excludesClass() {
    return this.excludesActive
      ? "dl-term-card__op dl-term-card__op_active"
      : "dl-term-card__op";
  }

  // Specificity rank badge (the scope type doubles as the specificity indicator: a more specific
  // scope wins when a market fits multiple Terms). Present only when the Term declares a DL_ScopeType.
  get scopeRankBadge() {
    const scopeType = this.attrMap[SCOPE_TYPE_CODE];
    if (!scopeType) {
      return null;
    }
    return {
      label: scopeType,
      // 5 = airport (most specific) … 0 = custom; used only to tint the badge by strength.
      cls: `dl-term-card__rank dl-term-card__rank_${scopeTypeRank(scopeType)}`
    };
  }

  // "Share Gap 5.0 pts" style summary; blank when no measure captured.
  get requirementLabel() {
    const m = this.attrMap;
    const measure = m[MEASURE_CODE];
    if (!measure) {
      return "";
    }
    const value = m[REQUIREMENT_CODE];
    return value ? `${measure}: ${value}` : measure;
  }

  get hasSummary() {
    return !!this.routeLabel || !!this.scopeLabel || !!this.requirementLabel;
  }

  get cardClass() {
    return this.selected
      ? "dl-term-card dl-term-card_selected"
      : "dl-term-card";
  }

  get selectedStr() {
    return this.selected ? "true" : "false";
  }

  handleSelect() {
    this._emit();
  }

  // Flip the transient operator. Stops propagation so tapping the toggle doesn't also select the
  // card, and emits `operatorchange` ({ termId, operator }) for any parent that wants to filter.
  handleOperator(event) {
    event.stopPropagation();
    const operator = event.currentTarget.dataset.op;
    if (!operator || operator === this._operator) {
      return;
    }
    this._operator = operator;
    const termId = this.term && this.term.id;
    if (!termId) {
      return;
    }
    this.dispatchEvent(
      new CustomEvent("operatorchange", {
        detail: { termId, operator },
        bubbles: true,
        composed: true
      })
    );
  }

  // Space/Enter activate the chip (it is a role="button" div, so it needs its own key handling).
  // Ignore keys that originated on an inner control (e.g. the operator buttons) — those handle
  // their own activation and must not also select the card.
  handleKeydown(event) {
    if (event.target !== event.currentTarget) {
      return;
    }
    if (
      event.key === "Enter" ||
      event.key === " " ||
      event.key === "Spacebar"
    ) {
      event.preventDefault();
      this._emit();
    }
  }

  _emit() {
    const termId = this.term && this.term.id;
    if (!termId) {
      return;
    }
    this.dispatchEvent(
      new CustomEvent("termselect", {
        detail: { termId },
        bubbles: true,
        composed: true
      })
    );
  }
}
