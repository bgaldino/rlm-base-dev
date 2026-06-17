import { LightningElement, api } from "lwc";
import getWaterfall from "@salesforce/apex/RLM_PricingWaterfallApiController.getWaterfall";

const QUOTE_LINE_ITEM_PREFIX = "0QL";
const ORDER_ITEM_PREFIX = "802";

export default class RlmPricingWaterfallApi extends LightningElement {
  @api recordId;
  @api usageType = "Pricing";

  _waterfallData = null;
  _error = null;
  _isLoading = false;
  _hasLoaded = false;
  _showDebug = false;
  _searchTerm = "";
  _copyLabel = "Copy JSON";

  connectedCallback() {
    this.loadWaterfall();
  }

  async loadWaterfall() {
    if (!this.recordId || this._isUnsupportedObject()) return;
    this._isLoading = true;
    this._error = null;

    try {
      this._waterfallData = await getWaterfall({
        lineItemId: this.recordId,
        usageType: this.usageType || null
      });
    } catch (err) {
      this._error = err.body?.message || err.message || "Failed to load waterfall.";
      this._waterfallData = null;
    } finally {
      this._isLoading = false;
      this._hasLoaded = true;
    }
  }

  handleRefresh() {
    this.loadWaterfall();
  }

  toggleDebug() {
    this._showDebug = !this._showDebug;
  }

  handleSearch(event) {
    this._searchTerm = event.target.value;
  }

  handleCopyJson() {
    const json = this.debugJson;
    if (!json) return;
    navigator.clipboard.writeText(json).then(() => {
      this._copyLabel = "Copied!";
      // eslint-disable-next-line @lwc/lwc/no-async-operation
      setTimeout(() => {
        this._copyLabel = "Copy JSON";
      }, 2000);
    });
  }

  get isLoading() {
    return this._isLoading;
  }

  get showDebug() {
    return this._showDebug;
  }

  get copyLabel() {
    return this._copyLabel;
  }

  get debugJson() {
    if (!this._waterfallData) return "";
    return JSON.stringify(this._waterfallData, null, 2);
  }

  get filteredDebugJson() {
    const json = this.debugJson;
    if (!this._searchTerm || !json) return json;
    const term = this._searchTerm.toLowerCase();
    const lines = json.split("\n");
    const filtered = lines.filter((line) => line.toLowerCase().includes(term));
    return filtered.length > 0 ? filtered.join("\n") : "No matches found.";
  }

  get debugButtonLabel() {
    return this._showDebug ? "Hide JSON" : "Show JSON";
  }

  get debugButtonIcon() {
    return this._showDebug ? "utility:collapse_all" : "utility:expand_all";
  }

  get searchTerm() {
    return this._searchTerm;
  }

  get error() {
    if (this._isUnsupportedObject()) {
      return "This component supports QuoteLineItem and OrderItem record pages only.";
    }
    return this._error;
  }

  get hasData() {
    return this._waterfallData?.waterfall != null;
  }

  get noWaterfall() {
    return this._hasLoaded && !this.hasData && !this._error;
  }

  get apiPath() {
    return this._waterfallData?._apiPath || "";
  }

  get outputFields() {
    const output = this._waterfallData?.output;
    if (!output) return [];
    return Object.entries(output).map(([key, value]) => ({
      key,
      label: this._humanize(key),
      value: value != null ? String(value) : ""
    }));
  }

  get waterfallSteps() {
    const steps = this._waterfallData?.waterfall;
    if (!Array.isArray(steps)) return [];
    const mapped = [...steps]
      .sort((a, b) => (a.sequence || 0) - (b.sequence || 0))
      .map((step, idx) => ({
        key: `step-${idx}`,
        sequence: step.sequence,
        name: step.pricingElement?.name || `Step ${step.sequence}`,
        elementType: step.pricingElement?.elementType || "",
        hasAdjustments:
          Array.isArray(step.pricingElement?.adjustments) &&
          step.pricingElement.adjustments.length > 0,
        adjustments: (step.pricingElement?.adjustments || []).map((adj, i) => ({
          key: `adj-${i}`,
          name: adj.name || "",
          value: adj.adjustmentValue != null ? String(adj.adjustmentValue) : ""
        })),
        outputParameters: this._mapToArray(step.outputParameters),
        hasOutputs:
          step.outputParameters != null &&
          Object.keys(step.outputParameters).length > 0
      }));

    if (!this._searchTerm) return mapped;

    const term = this._searchTerm.toLowerCase();
    return mapped.filter(
      (step) =>
        step.name.toLowerCase().includes(term) ||
        step.elementType.toLowerCase().includes(term) ||
        step.outputParameters.some(
          (p) => p.label.toLowerCase().includes(term) || p.value.toLowerCase().includes(term)
        ) ||
        step.adjustments.some(
          (a) => a.name.toLowerCase().includes(term) || a.value.toLowerCase().includes(term)
        )
    );
  }

  get stepCount() {
    const total = this._waterfallData?.waterfall?.length || 0;
    const shown = this.waterfallSteps.length;
    if (!this._searchTerm || shown === total) return `${total}`;
    return `${shown}/${total}`;
  }

  _isUnsupportedObject() {
    const prefix = this._getPrefix();
    return prefix !== QUOTE_LINE_ITEM_PREFIX && prefix !== ORDER_ITEM_PREFIX;
  }

  _getPrefix() {
    const id = this.recordId ? String(this.recordId) : "";
    return id.length >= 3 ? id.substring(0, 3).toUpperCase() : null;
  }

  _mapToArray(obj) {
    if (!obj) return [];
    return Object.entries(obj).map(([key, value]) => ({
      key,
      label: this._humanize(key),
      value: typeof value === "object" ? JSON.stringify(value) : String(value)
    }));
  }

  _humanize(camelCase) {
    if (!camelCase) return "";
    return camelCase
      .replace(/([A-Z])/g, " $1")
      .replace(/^./, (s) => s.toUpperCase())
      .trim();
  }
}
