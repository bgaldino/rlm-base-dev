import { LightningElement, api, wire } from "lwc";
import { getRecord } from "lightning/uiRecordApi";
import { NavigationMixin } from "lightning/navigation";
import getAllPricingRuns from "@salesforce/apex/RLM_PricingWaterfallController.getAllPricingRuns";

const QLI_FIELDS = [
  "QuoteLineItem.PriceWaterfallIdentifier",
  "QuoteLineItem.LastModifiedDate",
  "QuoteLineItem.ListPrice",
  "QuoteLineItem.UnitPrice",
  "QuoteLineItem.Discount",
  "QuoteLineItem.TotalPrice",
  "QuoteLineItem.Quantity",
  "QuoteLineItem.CurrencyIsoCode"
];

const ORDER_ITEM_FIELDS = [
  "OrderItem.PriceWaterfallIdentifier",
  "OrderItem.LastModifiedDate",
  "OrderItem.ListPrice",
  "OrderItem.UnitPrice",
  "OrderItem.Discount",
  "OrderItem.TotalPrice",
  "OrderItem.Quantity",
  "OrderItem.CurrencyIsoCode"
];

const QUOTE_LINE_ITEM_PREFIX = "0QL";
const ORDER_ITEM_PREFIX = "802";

// Runs within this many milliseconds of each other are shown under the same group header
const GROUP_THRESHOLD_MS = 10_000;
const DEFAULT_HISTORY_PAGE_SIZE = 25;

// Returns classes for a status badge: slds-badge provides base layout,
// badge-* overrides the background/text color.
function statusBadgeClass(status) {
  if (status === "Success") return "slds-badge badge-success";
  if (status === "Failure") return "slds-badge badge-error";
  if (status) return "slds-badge badge-warning";
  return "";
}

function confidenceBadgeClass(confidenceBand) {
  if (confidenceBand === "Very High" || confidenceBand === "High") {
    return "slds-badge confidence-badge confidence-badge-high";
  }
  if (confidenceBand === "Medium") {
    return "slds-badge confidence-badge confidence-badge-medium";
  }
  if (confidenceBand === "Low") {
    return "slds-badge confidence-badge confidence-badge-low";
  }
  return "slds-badge confidence-badge";
}

export default class RlmPricingWaterfall extends NavigationMixin(LightningElement) {
  @api recordId;
  @api historyPageSize = DEFAULT_HISTORY_PAGE_SIZE;
  @api showPriceSummary;
  @api showCurrentExecution;
  _currentHistoryPage = 1;

  _recordData = null;
  _recordLoaded = false;
  _waterfallRunId = null; // current run id from PriceWaterfallIdentifier
  _waterfallRunIdCandidates = [];

  _runs = null;
  _runsError = null;
  _recordError = null;

  @wire(getRecord, { recordId: "$quoteLineRecordId", fields: QLI_FIELDS })
  wiredQuoteLineRecord({ error, data }) {
    if (!this.isQuoteLineItemContext) return;
    this._recordLoaded = true;
    this._handleRecordResult({ error, data });
  }

  @wire(getRecord, { recordId: "$orderItemRecordId", fields: ORDER_ITEM_FIELDS })
  wiredOrderItemRecord({ error, data }) {
    if (!this.isOrderItemContext) return;
    this._recordLoaded = true;
    this._handleRecordResult({ error, data });
  }

  @wire(getAllPricingRuns, { lineItemId: "$pricingLineRecordId" })
  wiredRuns({ error, data }) {
    if (data) {
      this._runs = data;
      this._runsError = null;
      this._currentHistoryPage = 1;
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
    if (this.isUnsupportedObject) return false;
    return !this._recordLoaded;
  }

  get isUnsupportedObject() {
    return !this.isQuoteLineItemContext && !this.isOrderItemContext;
  }

  get quoteLineRecordId() {
    return this.isQuoteLineItemContext ? this.recordId : null;
  }

  get orderItemRecordId() {
    return this.isOrderItemContext ? this.recordId : null;
  }

  get pricingLineRecordId() {
    return this.isUnsupportedObject ? null : this.recordId;
  }

  get isQuoteLineItemContext() {
    return this._getRecordIdPrefix() === QUOTE_LINE_ITEM_PREFIX;
  }

  get isOrderItemContext() {
    return this._getRecordIdPrefix() === ORDER_ITEM_PREFIX;
  }

  get isPricingNotRun() {
    return (
      this._recordLoaded &&
      !this._waterfallRunId &&
      !this._recordError &&
      !this.hasPricingHistory
    );
  }

  get listPrice() {
    return this._getRecordFieldValue("ListPrice");
  }

  get unitPrice() {
    return this._getRecordFieldValue("UnitPrice");
  }

  get discount() {
    return this._getRecordFieldValue("Discount");
  }

  get totalPrice() {
    return this._getRecordFieldValue("TotalPrice");
  }

  get quantity() {
    return this._getRecordFieldValue("Quantity");
  }

  get currencyCode() {
    return this._getRecordFieldValue("CurrencyIsoCode") ?? "USD";
  }

  get hasDiscount() {
    const d = this.discount;
    return d !== null && d !== undefined && d !== 0;
  }

  get error() {
    if (this.isUnsupportedObject) {
      return "RLM Pricing Waterfall supports QuoteLineItem and OrderItem record pages.";
    }
    return this._recordError || this._runsError;
  }

  get currentRun() {
    if (!Array.isArray(this._runs) || this._runs.length === 0) return null;

    const matchedByIdentifier =
      this._waterfallRunIdCandidates.length > 0
        ? (
            this._runs.find((r) =>
              this._waterfallRunIdCandidates.includes(r.waterfallRunId) ||
              this._waterfallRunIdCandidates.includes(r.paeName)
            ) ?? null
          )
        : null;

    const latestRun = this._latestRun;
    if (!latestRun) return matchedByIdentifier;

    // Primary behavior: when identifier matches, use it.
    // Fallback: if identifier is stale and line was modified after a newer run,
    // prefer latest run so "Current" reflects the line's active pricing.
    if (!matchedByIdentifier) {
      return this._wasLineTouchedAfterRun(latestRun) ? latestRun : null;
    }

    if (matchedByIdentifier === latestRun) {
      return matchedByIdentifier;
    }

    if (this._wasLineTouchedAfterRun(latestRun)) {
      return latestRun;
    }

    return matchedByIdentifier;
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

  get currentMatchSource() {
    return this._sanitizeDisplayValue(this.currentRun?.matchSource);
  }

  get currentMatchRole() {
    const role = this._sanitizeDisplayValue(this.currentRun?.matchRelationshipRole);
    return role && role !== this.currentMatchSource ? role : null;
  }

  get currentMatchedLineItemId() {
    return this._sanitizeDisplayValue(this.currentRun?.matchedLineItemId);
  }

  get currentMatchedExecutionToken() {
    const token = this._sanitizeDisplayValue(this.currentRun?.matchedExecutionToken);
    return token && token !== this.currentMatchedLineItemId ? token : null;
  }

  get currentMatchedRecordType() {
    return this._sanitizeDisplayValue(this.currentRun?.matchedRecordType);
  }

  get currentMatchConfidenceText() {
    return this._formatConfidenceText(this.currentRun);
  }

  get currentMatchConfidenceReason() {
    return this._sanitizeDisplayValue(this.currentRun?.matchConfidenceReason);
  }

  get currentMatchConfidenceBadgeClass() {
    return confidenceBadgeClass(this.currentRun?.matchConfidenceBand);
  }

  get hasPricingHistory() {
    return Array.isArray(this._runs) && this._runs.length > 0;
  }

  get configuredHistoryPageSize() {
    const parsed = Number(this.historyPageSize);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      return DEFAULT_HISTORY_PAGE_SIZE;
    }
    return Math.floor(parsed);
  }

  get isPriceSummaryVisible() {
    return this._coerceBoolean(this.showPriceSummary, true);
  }

  get isCurrentExecutionVisible() {
    return this._coerceBoolean(this.showCurrentExecution, true);
  }

  get totalHistoryRows() {
    return Array.isArray(this._runs) ? this._runs.length : 0;
  }

  get totalHistoryPages() {
    if (this.totalHistoryRows === 0) return 1;
    return Math.ceil(this.totalHistoryRows / this.configuredHistoryPageSize);
  }

  get hasPagination() {
    return this.totalHistoryPages > 1;
  }

  get currentHistoryPage() {
    return Math.min(Math.max(this._currentHistoryPage, 1), this.totalHistoryPages);
  }

  get isPreviousPageDisabled() {
    return this.currentHistoryPage <= 1;
  }

  get isNextPageDisabled() {
    return this.currentHistoryPage >= this.totalHistoryPages;
  }

  handlePreviousPage() {
    if (this.isPreviousPageDisabled) return;
    this._currentHistoryPage -= 1;
  }

  handleNextPage() {
    if (this.isNextPageDisabled) return;
    this._currentHistoryPage += 1;
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
    const startIdx = (this.currentHistoryPage - 1) * this.configuredHistoryPageSize;
    const endIdx = startIdx + this.configuredHistoryPageSize;
    const pagedRuns = sorted.slice(startIdx, endIdx);
    const items = [];
    let prevTime = null;
    let groupIdx = 0;

    pagedRuns.forEach((run, idx) => {
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

      const isCurrent = this._isCurrentRun(run);
      const paeId = run.pricingApiExecutionId;
      const matchSource = this._sanitizeDisplayValue(run.matchSource);
      const matchRelationshipRole = this._sanitizeDisplayValue(run.matchRelationshipRole);
      const matchedLineItemId = this._sanitizeDisplayValue(run.matchedLineItemId);
      const matchedExecutionToken = this._sanitizeDisplayValue(run.matchedExecutionToken);
      const matchedRecordType = this._sanitizeDisplayValue(run.matchedRecordType);
      const matchConfidenceReason = this._sanitizeDisplayValue(run.matchConfidenceReason);
      const matchedLineItemDisplay = this._compactIdentifier(matchedLineItemId);
      const matchedExecutionTokenDisplay = this._compactIdentifier(matchedExecutionToken);
      items.push({
        key: run.waterfallRunId ?? `run-${startIdx + idx}`,
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
        matchSource,
        matchRelationshipRole:
          matchRelationshipRole && matchRelationshipRole !== matchSource
            ? matchRelationshipRole
            : null,
        matchedLineItemId,
        matchedExecutionToken:
          matchedExecutionToken && matchedExecutionToken !== matchedLineItemId
            ? matchedExecutionToken
            : null,
        matchedRecordType,
        matchConfidenceText: this._formatConfidenceText(run),
        matchConfidenceBadgeClass: confidenceBadgeClass(run.matchConfidenceBand),
        matchConfidenceReason,
        matchedLineItemDisplay,
        matchedExecutionTokenDisplay,
        isCurrent,
        rowClass: isCurrent ? "current-run-row" : "",
        overallStatusBadgeClass: statusBadgeClass(run.overallStatus),
        lineStatusBadgeClass: statusBadgeClass(run.lineStatus)
      });
    });

    return items;
  }

  get _latestRun() {
    if (!Array.isArray(this._runs) || this._runs.length === 0) return null;
    return [...this._runs].sort((a, b) => {
      const aTs = a.createdDate ? new Date(a.createdDate).getTime() : 0;
      const bTs = b.createdDate ? new Date(b.createdDate).getTime() : 0;
      return bTs - aTs;
    })[0];
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

  /**
   * PriceWaterfallIdentifier formats are not fully consistent across org/runtime
   * paths. Build multiple candidates so "current run" marking still works.
   *
   * Examples observed:
   * - "{prefix}:{runId}"
   * - "{runId}"
   * - values where the execution name (PAE auto-number) is persisted
   */
  _extractRunIdCandidates(identifier) {
    if (!identifier) return [];

    const raw = String(identifier).trim();
    if (!raw) return [];

    const candidates = new Set([raw]);

    if (raw.includes(":")) {
      const firstSplit = raw.split(":")[1]?.trim();
      const lastSplit = raw.split(":").pop()?.trim();
      if (firstSplit) candidates.add(firstSplit);
      if (lastSplit) candidates.add(lastSplit);
    }

    // Some values include URL-like separators or accidental whitespace wrappers.
    const slashSplit = raw.split("/").pop()?.trim();
    if (slashSplit) candidates.add(slashSplit);

    return [...candidates].filter(Boolean);
  }

  _extractPrimaryRunId(identifier, candidates) {
    if (!identifier) return null;
    const raw = String(identifier).trim();
    if (!raw) return null;

    if (raw.includes(":")) {
      return raw.split(":").pop()?.trim() || (candidates[0] ?? null);
    }
    return candidates[0] ?? null;
  }

  _wasLineTouchedAfterRun(run) {
    const lineLastModified = this._getRecordFieldValue("LastModifiedDate");
    if (!lineLastModified || !run?.createdDate) return false;

    const lineTs = new Date(lineLastModified).getTime();
    const runTs = new Date(run.createdDate).getTime();
    return Number.isFinite(lineTs) && Number.isFinite(runTs) && lineTs >= runTs;
  }

  _isCurrentRun(run) {
    const current = this.currentRun;
    if (!current || !run) return false;

    if (current.pricingApiExecutionId && run.pricingApiExecutionId) {
      return current.pricingApiExecutionId === run.pricingApiExecutionId;
    }

    if (current.waterfallRunId && run.waterfallRunId) {
      return current.waterfallRunId === run.waterfallRunId;
    }

    return false;
  }

  _sanitizeDisplayValue(value) {
    if (value === null || value === undefined) return null;

    const uniqueParts = [];
    String(value)
      .split(/\r?\n/)
      .map((part) => part.trim())
      .filter(Boolean)
      .forEach((part) => {
        if (!uniqueParts.includes(part)) {
          uniqueParts.push(part);
        }
      });

    if (uniqueParts.length === 0) return null;
    return uniqueParts.join(" | ");
  }

  _coerceBoolean(value, defaultValue) {
    if (value === null || value === undefined) return defaultValue;
    if (typeof value === "boolean") return value;
    if (typeof value === "string") {
      const normalized = value.trim().toLowerCase();
      if (normalized === "true") return true;
      if (normalized === "false") return false;
    }
    return defaultValue;
  }

  _handleRecordResult({ error, data }) {
    if (data) {
      this._recordData = data;
      this._recordError = null;
      const identifier = this._getRecordFieldValue("PriceWaterfallIdentifier");
      const candidates = this._extractRunIdCandidates(identifier);
      this._waterfallRunIdCandidates = candidates;
      this._waterfallRunId = this._extractPrimaryRunId(identifier, candidates);
    } else if (error) {
      this._recordData = null;
      this._waterfallRunIdCandidates = [];
      this._waterfallRunId = null;
      this._recordError = error?.body?.message ?? "Failed to load record fields.";
    }
  }

  _getRecordFieldValue(fieldName) {
    return this._recordData?.fields?.[fieldName]?.value ?? null;
  }

  _getRecordIdPrefix() {
    const id = this.recordId ? String(this.recordId) : "";
    if (id.length < 3) return null;
    return id.substring(0, 3).toUpperCase();
  }

  _formatConfidenceText(run) {
    if (!run?.matchConfidenceBand) return null;
    if (run.matchConfidenceScore === null || run.matchConfidenceScore === undefined) {
      return run.matchConfidenceBand;
    }
    return `${run.matchConfidenceBand} (${run.matchConfidenceScore}%)`;
  }

  _compactIdentifier(value, maxLength = 18) {
    if (!value) return null;
    const raw = String(value);
    if (raw.length <= maxLength) return raw;
    const start = raw.slice(0, 8);
    const end = raw.slice(-6);
    return `${start}...${end}`;
  }
}
