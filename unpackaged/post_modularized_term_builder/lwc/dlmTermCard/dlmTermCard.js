import { LightningElement, api } from "lwc";

// Route-attribute codes the rail chip summarizes (must match the PC-DL-TERM attribute defs). The
// card only READS these off the term payload getBuilderState already returns; it never queries.
const ORIGIN_CODE = "DL_Origin";
const DESTINATION_CODE = "DL_Destination";
const DIRECTIONALITY_CODE = "DL_Directionality";
const MEASURE_CODE = "DL_Measure";
const REQUIREMENT_CODE = "DL_RequirementValue";

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
    return !!this.routeLabel || !!this.requirementLabel;
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

  // Space/Enter activate the chip (it is a role="button" div, so it needs its own key handling).
  handleKeydown(event) {
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
