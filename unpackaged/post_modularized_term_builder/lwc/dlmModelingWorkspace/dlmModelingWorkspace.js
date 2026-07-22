import { LightningElement, api } from "lwc";
import { termScopeChips, routeLabel } from "c/dlDemoModel";

/**
 * Modularized Delta Term Builder — the "modeling workspace" tab body.
 *
 * A CONTROLLED PRESENTATIONAL WRAPPER (props down, events up). It holds NO model cache and does no
 * I/O — the always-mounted c/dlmWorkspaceShell owns the per-Term demo model cache and hands this
 * component exactly one active model to display + edit. This mirrors the monolith c/dlTermBuilder
 * orchestrator's relationship to c/dlModelingGrid, just split across the modularized shell/tab
 * boundary.
 *
 * It composes:
 *   - an "Apply Final Offer to Quote" action (the write-back is performed by the shell);
 *   - the reused c/dlModelingGrid, handed `selectedTerm` + `model`.
 *
 * Events up: c/dlModelingGrid dispatches `modelchange` / `methodchange` as composed + bubbling
 * events, so they propagate through this wrapper to the shell's listeners with no re-dispatch
 * here. This wrapper ORIGINATES `applyofferrequest` from its own Apply button; the shell
 * runs the actual updateLineDiscountAndDates write-back and broadcasts linesChanged.
 */
export default class DlmModelingWorkspace extends LightningElement {
  @api selectedTerm;
  @api model;
  @api currencyCode = "USD";
  // Latched by the shell while a Final-Offer write-back is in flight (and when there's no model).
  @api applyDisabled = false;
  // Participating (partner) carriers captured in the Configure Data Set panel and surfaced by the shell.
  // Context only — chips above the grid, never grid rows. Accepts an array or a ';'-delimited string.
  @api carriers = [];

  get hasModel() {
    return !!this.model;
  }

  // Participating-carrier chips shown above the grid. Normalizes the multiselect value (array or the
  // ';'-delimited picklist string) into [{ key, label }]; empty when no carriers were selected.
  get carrierChips() {
    const raw = this.carriers;
    const names = Array.isArray(raw)
      ? raw
      : `${raw || ""}`.split(";");
    return names
      .map((n) => `${n || ""}`.trim())
      .filter(Boolean)
      .map((name, i) => ({ key: `${i}:${name}`, label: name }));
  }

  get hasCarriers() {
    return this.carrierChips.length > 0;
  }

  // Term scope banner: the Term-level geography (Origin / Destination / Directionality / Market / …)
  // surfaced ONCE above the grid, never per-row. Derived from selectedTerm.attributes.
  get scopeChips() {
    return this.selectedTerm ? termScopeChips(this.selectedTerm) : [];
  }

  get hasScope() {
    return this.scopeChips.length > 0;
  }

  get scopeRouteLabel() {
    return this.selectedTerm ? routeLabel(this.selectedTerm) : "";
  }

  get scopeTermName() {
    return (this.selectedTerm && this.selectedTerm.displayName) || "Term";
  }

  handleApplyOffer() {
    if (this.applyDisabled) {
      return;
    }
    // The shell owns the Apex write-back + LMC broadcast; this wrapper just requests it.
    this.dispatchEvent(
      new CustomEvent("applyofferrequest", { bubbles: true, composed: true })
    );
  }
}
