import { LightningElement, api, wire } from "lwc";
import { getRecord, getFieldValue } from "lightning/uiRecordApi";
import { NavigationMixin } from "lightning/navigation";
import getAllPricingRuns from "@salesforce/apex/RLM_PricingWaterfallController.getAllPricingRuns";

const QLI_FIELDS = [
  "QuoteLineItem.PriceWaterfallIdentifier",
  "QuoteLineItem.ListPrice",
  "QuoteLineItem.UnitPrice",
  "QuoteLineItem.Discount",
  "QuoteLineItem.TotalPrice",
  "QuoteLineItem.Quantity",
  "QuoteLineItem.CurrencyIsoCode"
];

// Runs within this many milliseconds of each other are shown under the same group header
const GROUP_THRESHOLD_MS = 10_000;

// Returns classes for a status badge: slds-badge provides base layout,
// badge-* overrides the background/text color.
function statusBadgeClass(status) {
  if (status === "Success") return "slds-badge badge-success";
  if (status === "Failure") return "slds-badge badge-error";
  if (status) return "slds-badge badge-warning";
  return "";
}

export default class RlmPricingWaterfall extends NavigationMixin(LightningElement) {
  @api recordId;

  _recordData = null;
  _recordLoaded = false;
  _waterfallRunId = null; // current run id from PriceWaterfallIdentifier

  _runs = null;
  _runsError = null;
  _recordError = null;

  @wire(getRecord, { recordId: "$recordId", fields: QLI_FIELDS })
  wiredRecord({ error, data }) {
    this._recordLoaded = true;
    if (data) {
      this._recordData = data;
      this._recordError = null;
      const identifier = getFieldValue(data, "QuoteLineItem.PriceWaterfallIdentifier");
      if (identifier) {
        const colonIdx = identifier.indexOf(":");
        this._waterfallRunId = colonIdx !== -1 ? identifier.substring(colonIdx + 1) : null;
      } else {
        this._waterfallRunId = null;
      }
    } else if (error) {
      this._recordData = null;
      this._recordError = error?.body?.message ?? "Failed to load record fields.";
    }
  }

  @wire(getAllPricingRuns, { lineItemId: "$recordId" })
  wiredRuns({ error, data }) {
    if (data) {
      this._runs = data;
      this._runsError = null;
    } else if (error) {
      this._runs = null;
      this._runsError = error?.body?.message ?? "Failed to load pricing history.";
    }
  }

  handleOpenRecord(event) {
    // Ctrl/Cmd/Shift+click → let the browser open the href in a new tab/window
    if (event.ctrlKey || event.metaKey || event.shiftKey) return;
    event.preventDefault();
    const paeId = event.currentTarget.dataset.id;
    if (!paeId) return;
    this[NavigationMixin.Navigate]({
      type: "standard__recordPage",
      attributes: {
        recordId: paeId,
        objectApiName: "PricingApiExecution",
        actionName: "view"
      }
    });
  }

  // ── Getters ──────────────────────────────────────────────────────────

  get isLoading() {
    return !this._recordLoaded;
  }

  get isPricingNotRun() {
    return this._recordLoaded && !this._waterfallRunId && !this._recordError;
  }

  get listPrice() {
    return getFieldValue(this._recordData, "QuoteLineItem.ListPrice");
  }

  get unitPrice() {
    return getFieldValue(this._recordData, "QuoteLineItem.UnitPrice");
  }

  get discount() {
    return getFieldValue(this._recordData, "QuoteLineItem.Discount");
  }

  get totalPrice() {
    return getFieldValue(this._recordData, "QuoteLineItem.TotalPrice");
  }

  get quantity() {
    return getFieldValue(this._recordData, "QuoteLineItem.Quantity");
  }

  get currencyCode() {
    return getFieldValue(this._recordData, "QuoteLineItem.CurrencyIsoCode") ?? "USD";
  }

  get hasDiscount() {
    const d = this.discount;
    return d !== null && d !== undefined && d !== 0;
  }

  get error() {
    return this._recordError || this._runsError;
  }

  get currentRun() {
    if (!this._runs || !this._waterfallRunId) return null;
    return this._runs.find((r) => r.waterfallRunId === this._waterfallRunId) ?? null;
  }

  // Line-level status is more meaningful for this QLI than the batch-level PAE status
  get currentLineStatus() {
    return this.currentRun?.lineStatus ?? null;
  }

  get currentOverallStatus() {
    return this.currentRun?.overallStatus ?? null;
  }

  get currentLineStatusBadgeClass() {
    return statusBadgeClass(this.currentLineStatus);
  }

  get currentOverallStatusBadgeClass() {
    return statusBadgeClass(this.currentOverallStatus);
  }

  get currentLineCount() {
    return this.currentRun?.lineCount ?? null;
  }

  get currentTriggeredBy() {
    return this.currentRun?.triggeredByName ?? null;
  }

  get hasPricingHistory() {
    return Array.isArray(this._runs) && this._runs.length > 0;
  }

  /**
   * Returns a flat list of separator rows and data rows for the pricing history
   * table, grouped by runs that happened within GROUP_THRESHOLD_MS of each other.
   *
   * Each item has `isSeparator: true|false` so the template can branch rendering.
   */
  get pricingHistory() {
    if (!Array.isArray(this._runs)) return null;

    // Newest first
    const sorted = [...this._runs].reverse();
    const items = [];
    let prevTime = null;
    let groupIdx = 0;

    sorted.forEach((run, idx) => {
      const runTime = run.createdDate ? new Date(run.createdDate).getTime() : null;

      // Start a new group when the gap to the previous run exceeds the threshold
      const isNewGroup =
        prevTime === null ||
        (runTime !== null && Math.abs(prevTime - runTime) > GROUP_THRESHOLD_MS);

      if (isNewGroup) {
        items.push({
          key: `sep-${groupIdx++}`,
          isSeparator: true,
          label: run.createdDate
            ? this._formatGroupLabel(new Date(run.createdDate))
            : "Unknown time",
          // Non-separator fields kept undefined — template guards on isSeparator
        });
        prevTime = runTime;
      }

      const isCurrent = run.waterfallRunId === this._waterfallRunId;
      const paeId = run.pricingApiExecutionId;
      items.push({
        key: run.waterfallRunId ?? `run-${idx}`,
        isSeparator: false,
        waterfallRunId: run.waterfallRunId,
        pricingApiExecutionId: paeId,
        paeUrl: paeId ? `/lightning/r/PricingApiExecution/${paeId}/view` : null,
        paeName: run.paeName,
        overallStatus: run.overallStatus,
        lineStatus: run.lineStatus,
        createdDate: run.createdDate,
        lineCount: run.lineCount,
        triggeredByName: run.triggeredByName,
        isCurrent,
        rowClass: isCurrent ? "current-run-row" : "",
        overallStatusBadgeClass: statusBadgeClass(run.overallStatus),
        lineStatusBadgeClass: statusBadgeClass(run.lineStatus)
      });
    });

    return items;
  }

  /** Human-readable label for a group header, e.g. "Jun 2, 2026 · 1:19:35 PM" */
  _formatGroupLabel(d) {
    const pad = (n) => String(n).padStart(2, "0");
    const months = [
      "Jan","Feb","Mar","Apr","May","Jun",
      "Jul","Aug","Sep","Oct","Nov","Dec"
    ];
    // Display in local time
    const month = months[d.getMonth()];
    const day   = d.getDate();
    const year  = d.getFullYear();
    const h     = d.getHours();
    const m     = d.getMinutes();
    const s     = d.getSeconds();
    const ampm  = h >= 12 ? "PM" : "AM";
    const h12   = ((h % 12) || 12);
    return `${month} ${day}, ${year} · ${h12}:${pad(m)}:${pad(s)} ${ampm}`;
  }
}
