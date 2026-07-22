import { LightningElement, api } from "lwc";

/**
 * dlDataContext — the compact read-only "Flown Data" strip for the Delta Term Builder.
 *
 * Tells the flown-data story ("12 months of ARC flown data for the customer + subsidiaries,
 * DL + JV partners"). It is deliberately distinct from the negotiation/contract default dates in
 * the header — those seed new line dates; this describes the analysis window the KPIs are derived
 * from.
 *
 * Purely presentational: it holds a small, sensible default context and lets the presenter toggle a
 * read-only detail popover. No backend, no persistence. A host may override any field via @api.
 */
export default class DlDataContext extends LightningElement {
  @api sourceSystem = "ARC"; // "ARC" | "PRISM"
  @api periodLabel = "FY25";
  @api months = 12;
  @api subsidiaries = 3;
  @api updatedLabel = "Jul 15";
  // Carriers included in the simulated dataset. Default: Delta + two JV partners.
  @api carriers = ["DL", "AF", "KL"];

  // Annualized defaults to true, so it is an internal property rather than an @api boolean (LWC
  // forbids a public boolean defaulting to true). Flip via the setter if a host ever needs to.
  _annualized = true;
  @api
  get annualized() {
    return this._annualized;
  }
  set annualized(value) {
    this._annualized = !!value;
  }

  _expanded = false;

  get carriersLabel() {
    const list = Array.isArray(this.carriers) ? this.carriers : [];
    if (list.length === 0) {
      return "DL";
    }
    const host = list[0];
    const partners = list.slice(1);
    return partners.length ? `${host} + ${partners.join("/")}` : host;
  }

  get annualizedLabel() {
    return this.annualized ? "Annualized" : "As-flown";
  }

  // The one-line summary chips shown in the collapsed strip.
  get summaryChips() {
    return [
      { key: "source", text: `${this.periodLabel} ${this.sourceSystem} flown data` },
      { key: "months", text: `${this.months} months` },
      { key: "subs", text: `${this.subsidiaries} subsidiaries` },
      { key: "carriers", text: this.carriersLabel },
      { key: "updated", text: `Updated ${this.updatedLabel}` }
    ];
  }

  // Detail rows for the expanded popover (read-only; the "controls" are illustrative only).
  get detailRows() {
    const list = Array.isArray(this.carriers) ? this.carriers : [];
    return [
      { key: "source", label: "Data source", value: this.sourceSystem },
      { key: "period", label: "Flown-data window", value: `${this.periodLabel} · ${this.months} months` },
      { key: "annualized", label: "Annualized", value: this.annualized ? "Yes" : "No" },
      { key: "subs", label: "Included subsidiaries", value: String(this.subsidiaries) },
      { key: "carriers", label: "Included carriers", value: list.join(", ") || "DL" },
      { key: "updated", label: "Last updated", value: this.updatedLabel }
    ];
  }

  get expanded() {
    return this._expanded;
  }

  get expandedStr() {
    return this._expanded ? "true" : "false";
  }

  get toggleIcon() {
    return this._expanded ? "utility:chevronup" : "utility:chevrondown";
  }

  get toggleTitle() {
    return this._expanded ? "Hide flown-data detail" : "Show flown-data detail";
  }

  handleToggle() {
    this._expanded = !this._expanded;
  }
}
