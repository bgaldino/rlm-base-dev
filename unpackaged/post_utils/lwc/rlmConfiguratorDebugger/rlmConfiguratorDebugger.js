import { LightningElement, api, wire } from "lwc";
import {
  subscribe,
  unsubscribe,
  MessageContext,
  APPLICATION_SCOPE,
  publish,
} from "lightning/messageService";
import CONFIGR_CHANNEL from "@salesforce/messageChannel/lightning__productConfigurator_notification";

/**
 * LMS event names as emitted by the Configurator Data Manager.
 * Used for filtering / labelling incoming log entries.
 */
const LMS_EVENTS = Object.freeze({
  VALUE_CHANGE: "valueChanged",
  NAVIGATE: "navigate",
  CLOSE_PREVIEW: "closePreview",
  TOGGLE_INSTANT_PRICING: "toggleInstantPricing",
  TOGGLE_RULES_VALIDATION: "toggleRulesValidation",
  TOGGLE_COMPACT_LAYOUT: "toggleCompactLayout",
  UPDATE_PRICES: "updatePrices",
  VALIDATE_PRODUCT: "validateProduct",
  CLONE_ITEMS: "cloneItems",
});

/**
 * Starter payload skeleton shown when the Edit tab is first opened or reset.
 * Matches the `valueChanged` LMS envelope expected by the Data Manager.
 */
const PAYLOAD_SKELETON = JSON.stringify(
  { action: LMS_EVENTS.VALUE_CHANGE, data: [] },
  null,
  2
);

/**
 * Documented LMS input payload for toggling instant pricing.
 *
 * {
 *   "action": "toggleInstantPricing",
 *   "value": true
 * }
 */
const TOGGLE_INSTANT_PRICING_PAYLOAD = Object.freeze({
  action: LMS_EVENTS.TOGGLE_INSTANT_PRICING,
  value: true,
});

/**
 * Documented LMS input payload for toggling compact layout.
 *
 * {
 *   "action": "toggleCompactLayout",
 *   "value": true
 * }
 */
const TOGGLE_COMPACT_LAYOUT_PAYLOAD = Object.freeze({
  action: LMS_EVENTS.TOGGLE_COMPACT_LAYOUT,
  value: true,
});

/**
 * Documented LMS input payload for toggling product/rules validation.
 *
 * {
 *   "action": "toggleRulesValidation",
 *   "value": false
 * }
 */
const TOGGLE_RULES_VALIDATION_PAYLOAD = Object.freeze({
  action: LMS_EVENTS.TOGGLE_RULES_VALIDATION,
  value: false,
});

/**
 * Documented LMS input payload for explicit product validation.
 * Available only when rules validation is false.
 *
 * {
 *   "action": "validateProduct"
 * }
 */
const VALIDATE_PRODUCT_PAYLOAD = Object.freeze({
  action: LMS_EVENTS.VALIDATE_PRODUCT,
});

/**
 * Documented LMS input payload for manual price updates.
 * Available only when instant pricing is false.
 *
 * {
 *   "action": "updatePrices"
 * }
 */
const UPDATE_PRICES_PAYLOAD = Object.freeze({
  action: LMS_EVENTS.UPDATE_PRICES,
});

const MAX_LOG_ENTRIES = 50;
const MAX_API_TIMINGS = 20;
const API_TIMING_TICK_MS = 250;
const STATE_SEARCH_DEBOUNCE_MS = 250;
const AUTO_INSTANT_PRICING_RETRY_MS = 150;
const MAX_AUTO_INSTANT_PRICING_RETRIES = 5;

/**
 * Configurator Debugger — third-party Flow Screen component
 *
 * Attaches to the same `lightning__productConfigurator_notification` LMS channel
 * the Data Manager uses so it can:
 *   1. Display a live, formatted snapshot of all @api Flow variables.
 *   2. Log every inbound LMS event from the Data Manager.
 *   3. Publish hand-crafted `valueChanged` payloads back to the Data Manager.
 *
 * Race-condition guard: the optionGroups setter is used as a "ready" signal.
 * When the user clicks Apply, we queue the publish and wait for the Data Manager
 * to echo back an optionGroups update before we fire, avoiding state collisions.
 *
 * @see https://help.salesforce.com/s/articleView?id=ind.product_configurator_third_party_configurator.htm&type=5
 */
export default class RlmConfiguratorDebugger extends LightningElement {
  // ── @api: String IDs ─────────────────────────────────────────────────────
  // Default Flow mapping: {!S_01_DataManager.transactionId}
  @api transactionId;
  // Default Flow mapping: {!S_01_DataManager.transactionLineId}
  @api transactionLineId;
  // Default Flow mapping: {!S_01_DataManager.currentTransactionLineId}
  @api currentTransactionLineId;
  // Default Flow mapping: {!S_01_DataManager.parentName}
  @api parentName;
  // Default Flow mapping: {!S_01_DataManager.origin}
  @api origin;
  // Default Flow mapping: {!S_01_DataManager.headerTitle}
  @api headerTitle;
  // Default Flow mapping: {!S_01_DataManager.currencyCode}
  @api currencyCode;
  // Default Flow mapping: {!S_01_DataManager.searchResultOptionId}
  @api searchResultOptionId;
  // Optional Flow mapping: {!S_01_DataManager.favoriteData}
  @api
  set favoriteData(value) {
    this._favoriteData = value;
    this._favoriteDataDeserialized = this._deserializeJsonString(
      value,
      "favoriteData"
    );
  }
  get favoriteData() {
    return this._favoriteData;
  }
  // Optional Flow mapping: {!S_01_DataManager.contextMetadata}
  @api
  set contextMetadata(value) {
    this._contextMetadata = value;
    this._contextMetadataDeserialized = this._deserializeJsonString(
      value,
      "contextMetadata"
    );
  }
  get contextMetadata() {
    return this._contextMetadata;
  }

  // ── @api: Complex objects (Apex-typed via Flow bindings) ──────────────────
  // Reserved for future Flow binding; not exposed in current metadata.
  @api header;
  // Default Flow mapping: {!S_01_DataManager.messages}
  @api messages;
  // Default Flow mapping: {!S_01_DataManager.summary}
  @api summary;
  // Default Flow mapping: {!S_01_DataManager.attributeCategories}
  @api attributeCategories;
  // Reserved for future Flow binding; not exposed in current metadata.
  @api navigationRoute;
  // Reserved for future Flow binding; not exposed in current metadata.
  @api searchInfo;
  // Default Flow mapping: {!S_01_DataManager.transactionRecord}
  @api transactionRecord;
  // Optional Flow mapping: {!S_01_DataManager.navigationInformation}
  @api navigationInformation;
  // Default Flow mapping: {!S_01_DataManager.addedNodes} (SalesTransactionItem[])
  @api addedNodes;
  // Default Flow mapping: {!S_01_DataManager.salesTransactionItems}
  @api salesTransactionItems;
  // Reserved for future Flow binding; not exposed in current metadata.
  @api tabs;

  // ── @api: Booleans ────────────────────────────────────────────────────────
  // Default Flow mapping: {!S_01_DataManager.isDesignTime}
  @api isDesignTime;
  // Default Flow mapping: {!S_01_DataManager.isClassContext}
  @api isClassContext;
  // Default Flow mapping: {!S_01_DataManager.isInstantPricingToggleEnabled}
  @api isInstantPricingToggleEnabled;
  // Default Flow mapping: {!S_01_DataManager.isCompactLayoutEnabled}
  @api isCompactLayoutEnabled;
  // Default Flow mapping: {!S_01_DataManager.isInstantPricingEnabled}
  @api
  set isInstantPricingEnabled(value) {
    this._isInstantPricingEnabled = this._coerceBoolean(value);
    this._isInstantPricingStateKnown = true;
    this._maybeAutoEnableInstantPricing();
  }

  get isInstantPricingEnabled() {
    return this._isInstantPricingEnabled;
  }
  // Default Flow mapping: {!S_01_DataManager.isProductValidationEnabled}
  @api isProductValidationEnabled;
  // Default Flow mapping: {!S_01_DataManager.showPrices}
  @api showPrices;
  // Default Flow mapping: {!S_01_DataManager.isConfiguratorDisabled}
  @api isConfiguratorDisabled;
  // Default Flow mapping: {!S_01_DataManager.isPriceRampEnabled}
  @api isPriceRampEnabled;
  // Optional Flow input: if true, auto-enables instant pricing once after LMS is ready.
  @api automaticInstantPricing = false;

  // ── optionGroups — custom setter used as the race-condition gate ──────────
  _optionGroups;
  _waitingForDataManager = false;
  _pendingPublish = null;

  @api
  set optionGroups(value) {
    this._optionGroups = value;
    if (this._waitingForDataManager && this._pendingPublish) {
      this._flushPendingPublish();
    }
  }

  get optionGroups() {
    return this._optionGroups;
  }

  // Default Flow mapping: {!S_01_DataManager.isApiInProgress}
  @api
  set isApiInProgress(value) {
    const nextValue = value === true || value === "true";
    const wasInProgress = this._isApiInProgress;
    this._isApiInProgress = nextValue;

    if (nextValue && !wasInProgress) {
      this._startApiTiming();
    } else if (!nextValue && wasInProgress) {
      this._finishApiTiming();
    }
  }

  get isApiInProgress() {
    return this._isApiInProgress;
  }

  // ── LMS wiring ────────────────────────────────────────────────────────────
  messageContext;

  @wire(MessageContext)
  wiredMessageContext(value) {
    this.messageContext = value;
    this._subscribe();
  }

  _subscription = null;

  // ── Private UI state ──────────────────────────────────────────────────────
  _lmsLog = [];
  _activeTab = "state";
  _activeStateSubtab = "total";
  _isCollapsed = false;
  _editPayload = PAYLOAD_SKELETON;
  _parseError = null;
  _publishSuccess = false;
  _isApiInProgress = false;
  _isInstantPricingEnabled = false;
  _isInstantPricingStateKnown = false;
  _apiTimingStartMs = null;
  _apiTimingStartedAt = null;
  _apiTimingIntervalId = null;
  _apiTimingTick = 0;
  _apiTimings = [];
  _stateSearchTerm = "";
  _stateSearchMatchIndex = 0;
  _stateSearchMatches = [];
  _stateSearchSnapshot = "";
  _stateSearchDebounceId = null;
  _isStateSearchPending = false;
  _pendingStateSearchScroll = false;
  _stateRefreshTick = 0;
  _logEntrySequence = 0;
  _hasAutoInstantPricingAttempted = false;
  _autoInstantPricingRetryCount = 0;
  _autoInstantPricingRetryTimeoutId = null;
  _favoriteData = null;
  _favoriteDataDeserialized = null;
  _contextMetadata = null;
  _contextMetadataDeserialized = null;

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  connectedCallback() {
    // MessageContext is wired asynchronously; subscription happens in wire handler.
  }

  disconnectedCallback() {
    this._clearStateSearchDebounce();
    this._clearApiTimingInterval();
    this._clearAutoInstantPricingRetry();
    this._unsubscribe();
  }

  renderedCallback() {
    if (!this._pendingStateSearchScroll) {
      return;
    }
    this._pendingStateSearchScroll = false;
    this._scrollStateSearchMatchIntoView();
  }

  // ── LMS subscribe / handle ────────────────────────────────────────────────
  _subscribe() {
    if (!this.messageContext || !CONFIGR_CHANNEL) {
      return;
    }
    if (!this._subscription) {
      try {
        this._subscription = subscribe(
          this.messageContext,
          CONFIGR_CHANNEL,
          (message) => this._handleLmsMessage(message),
          { scope: APPLICATION_SCOPE }
        );
        this._maybeAutoEnableInstantPricing();
      } catch (error) {
        this._parseError = `LMS subscribe error: ${error.message}`;
      }
    }
  }

  _unsubscribe() {
    if (this._subscription) {
      unsubscribe(this._subscription);
      this._subscription = null;
    }
  }

  _handleLmsMessage(message) {
    const payload = JSON.parse(JSON.stringify(message));
    const receivedAtMs = Date.now();
    this._logEntrySequence = (this._logEntrySequence + 1) % 1000;
    const entry = {
      id: receivedAtMs * 1000 + this._logEntrySequence,
      timestamp: new Date().toLocaleTimeString(),
      receivedAtMs,
      action: payload?.action ?? "(no action)",
      apiTimingLabel: "",
      payload,
      json: JSON.stringify(payload, null, 2),
      isExpanded: false,
    };
    this._lmsLog = [entry, ...this._lmsLog].slice(0, MAX_LOG_ENTRIES);
    // Keep State tab synced even if upstream mutates objects in place.
    this._stateRefreshTick += 1;
    this._refreshStateSearchMatchesIfNeeded();
    this._pendingStateSearchScroll = this._stateSearchMatches.length > 0;
  }

  // ── Publish with race-condition guard ─────────────────────────────────────
  _flushPendingPublish() {
    try {
      if (!this.messageContext) {
        throw new Error(
          "LMS message context is not ready yet. Wait a moment and try again."
        );
      }
      if (!CONFIGR_CHANNEL) {
        throw new Error(
          "LMS channel metadata is unavailable for this component context."
        );
      }
      const payload = JSON.parse(this._pendingPublish);
      publish(this.messageContext, CONFIGR_CHANNEL, payload);
      this._publishSuccess = true;
      // Auto-clear success banner after 3 s
      // eslint-disable-next-line @lwc/lwc/no-async-operation
      setTimeout(() => {
        this._publishSuccess = false;
      }, 3000);
    } catch (e) {
      this._parseError = `Publish error: ${e.message}`;
    } finally {
      this._waitingForDataManager = false;
      this._pendingPublish = null;
    }
  }

  // ── State snapshot (rendered on State tab) ────────────────────────────────
  get stateSnapshot() {
    // Manual refresh button increments this value to force a fresh render pass.
    this._stateRefreshTick;
    return JSON.stringify(
      {
        transactionId: this.transactionId,
        transactionLineId: this.transactionLineId,
        currentTransactionLineId: this.currentTransactionLineId,
        parentName: this.parentName,
        origin: this.origin,
        headerTitle: this.headerTitle,
        currencyCode: this.currencyCode,
        favoriteData: this.favoriteData,
        favoriteDataDeserialized: this.favoriteDataDeserialized,
        contextMetadata: this.contextMetadata,
        contextMetadataDeserialized: this.contextMetadataDeserialized,
        isApiInProgress: this.isApiInProgress,
        currentApiDuration: this.currentApiDurationLabel,
        apiTimings: this._apiTimings,
        isConfiguratorDisabled: this.isConfiguratorDisabled,
        isInstantPricingEnabled: this.isInstantPricingEnabled,
        isCompactLayoutEnabled: this.isCompactLayoutEnabled,
        showPrices: this.showPrices,
        isPriceRampEnabled: this.isPriceRampEnabled,
        header: this.header,
        summary: this.summary,
        messages: this.messages,
        optionGroups: this._optionGroups,
        attributeCategories: this.attributeCategories,
        salesTransactionItems: this.salesTransactionItems,
        addedNodes: this.addedNodes,
        transactionRecord: this.transactionRecord,
        navigationInformation: this.navigationInformation,
        navigationRoute: this.navigationRoute,
        tabs: this.tabs,
        searchInfo: this.searchInfo,
      },
      null,
      2
    );
  }

  get activeStateJson() {
    const snippets = {
      total: JSON.parse(this.stateSnapshot),
      messages: this.messages ?? null,
      optionGroups: this._optionGroups ?? null,
      attributeCategories: this.attributeCategories ?? null,
      salesTransactionItems: this.salesTransactionItems ?? null,
      addedNodes: this.addedNodes ?? null,
      navigationInformation: this.navigationInformation ?? null,
      summary: this.summary ?? null,
      favoriteData: this.favoriteDataDeserialized,
      contextMetadata: this.contextMetadataDeserialized,
    };
    return JSON.stringify(snippets[this._activeStateSubtab], null, 2);
  }

  get activeStateSubtab() {
    return this._activeStateSubtab;
  }

  get favoriteDataDeserialized() {
    return this._favoriteDataDeserialized;
  }

  get contextMetadataDeserialized() {
    return this._contextMetadataDeserialized;
  }

  // ── Tab getters ───────────────────────────────────────────────────────────
  get isStateTab() {
    return this._activeTab === "state";
  }

  get isLogTab() {
    return this._activeTab === "log";
  }

  get isEditTab() {
    return this._activeTab === "edit";
  }

  get stateTabClass() {
    return `slds-tabs_default__item${this._activeTab === "state" ? " slds-is-active" : ""}`;
  }

  get logTabClass() {
    return `slds-tabs_default__item${this._activeTab === "log" ? " slds-is-active" : ""}`;
  }

  get editTabClass() {
    return `slds-tabs_default__item${this._activeTab === "edit" ? " slds-is-active" : ""}`;
  }

  // ── Collapse getters ──────────────────────────────────────────────────────
  get isCollapsed() {
    return this._isCollapsed;
  }

  get collapseIcon() {
    return this._isCollapsed ? "utility:chevrondown" : "utility:chevronup";
  }

  get collapseLabel() {
    return this._isCollapsed ? "Expand" : "Collapse";
  }

  // ── Status getters ────────────────────────────────────────────────────────
  get hasParseError() {
    return Boolean(this._parseError);
  }

  get parseError() {
    return this._parseError;
  }

  get showPublishSuccess() {
    return this._publishSuccess;
  }

  get hasErrors() {
    return this.summary?.hasErrors === true;
  }

  get apiProgressLabel() {
    const duration = this.currentApiDurationLabel;
    return duration ? `API in Progress ${duration}` : "API in Progress";
  }

  get currentApiDurationLabel() {
    // Referencing the tick makes the getter reactive while the interval runs.
    this._apiTimingTick;
    if (!this.isApiInProgress || this._apiTimingStartMs === null) {
      return "";
    }
    return this._formatDuration(Date.now() - this._apiTimingStartMs);
  }

  get hasApiTimings() {
    return this._apiTimings.length > 0;
  }

  get apiTimings() {
    return this._apiTimings;
  }

  get hasLastApiTiming() {
    return !this.isApiInProgress && this._apiTimings.length > 0;
  }

  get lastApiTimingLabel() {
    const [lastTiming] = this._apiTimings;
    return lastTiming ? `Last API ${lastTiming.durationLabel}` : "";
  }

  // ── Log getters ───────────────────────────────────────────────────────────
  get lmsLog() {
    return this._lmsLog;
  }

  get hasLogEntries() {
    return this._lmsLog.length > 0;
  }

  get isClearDisabled() {
    return this._lmsLog.length === 0;
  }

  get logEntryCount() {
    return this._lmsLog.length;
  }

  // ── State search getters ──────────────────────────────────────────────────
  get stateSearchTerm() {
    return this._stateSearchTerm;
  }

  get stateSearchMatchCount() {
    return this._stateSearchMatches.length;
  }

  get stateSearchPosition() {
    if (!this._stateSearchTerm.trim()) {
      return "";
    }
    if (this._isStateSearchPending) {
      return "...";
    }
    const count = this.stateSearchMatchCount;
    if (count === 0) {
      return "0 / 0";
    }
    return `${this._getActiveStateSearchIndex() + 1} / ${count}`;
  }

  get isStateSearchNavigationDisabled() {
    return this._isStateSearchPending || this._stateSearchMatches.length === 0;
  }

  get isStateSearchClearDisabled() {
    return !this._stateSearchTerm.trim();
  }

  // ── Edit getters ──────────────────────────────────────────────────────────
  get editPayload() {
    return this._editPayload;
  }

  // ── Handlers: navigation ──────────────────────────────────────────────────
  handleTabClick(event) {
    this._activeTab = event.currentTarget.dataset.tab;
    this._parseError = null;
  }

  handleToggleCollapse() {
    this._isCollapsed = !this._isCollapsed;
  }

  // ── Handlers: state tab ───────────────────────────────────────────────────
  handleCopyState() {
    this._copyToClipboard(this.activeStateJson);
  }

  handleRefreshState() {
    this._stateRefreshTick += 1;
    this._refreshStateSearchMatchesIfNeeded();
    this._pendingStateSearchScroll = this._stateSearchMatches.length > 0;
    this._clearWindowSelection();
  }

  handleStateSubtabActive(event) {
    this._activeStateSubtab = event.target.value;
    this._stateSearchMatchIndex = 0;
    this._stateSearchMatches = [];
    this._stateSearchSnapshot = "";
    this._pendingStateSearchScroll = false;
    this._clearWindowSelection();
    if (this._stateSearchTerm.trim()) {
      this._indexStateSearchMatches();
    }
  }

  handleStateSearchChange(event) {
    this._stateSearchTerm = event.detail?.value ?? event.target.value ?? "";
    this._stateSearchMatchIndex = 0;
    this._pendingStateSearchScroll = false;
    this._clearStateSearchDebounce();

    if (!this._stateSearchTerm.trim()) {
      this._stateSearchMatches = [];
      this._stateSearchSnapshot = "";
      this._isStateSearchPending = false;
      return;
    }

    this._isStateSearchPending = true;
    // eslint-disable-next-line @lwc/lwc/no-async-operation
    this._stateSearchDebounceId = setTimeout(() => {
      this._indexStateSearchMatches();
      this._isStateSearchPending = false;
      this._stateSearchDebounceId = null;
    }, STATE_SEARCH_DEBOUNCE_MS);
  }

  handleClearStateSearch() {
    this._clearStateSearchDebounce();
    this._stateSearchTerm = "";
    this._stateSearchMatchIndex = 0;
    this._stateSearchMatches = [];
    this._stateSearchSnapshot = "";
    this._isStateSearchPending = false;
    this._pendingStateSearchScroll = false;
    this._clearWindowSelection();
  }

  handlePreviousStateSearch() {
    this._refreshStateSearchMatchesIfNeeded();
    const count = this._stateSearchMatches.length;
    if (count === 0) {
      return;
    }
    this._stateSearchMatchIndex =
      (this._getActiveStateSearchIndex() - 1 + count) % count;
    this._pendingStateSearchScroll = true;
  }

  handleNextStateSearch() {
    this._refreshStateSearchMatchesIfNeeded();
    const count = this._stateSearchMatches.length;
    if (count === 0) {
      return;
    }
    this._stateSearchMatchIndex = (this._getActiveStateSearchIndex() + 1) % count;
    this._pendingStateSearchScroll = true;
  }

  // ── Handlers: log tab ─────────────────────────────────────────────────────
  handleClearLog() {
    this._lmsLog = [];
  }

  handleCopyAllLogEntries() {
    const payloads = this._lmsLog.map((entry) => entry.payload);
    this._copyToClipboard(JSON.stringify(payloads, null, 2));
  }

  handleToggleLogEntry(event) {
    const id = Number(event.currentTarget.dataset.id);
    this._lmsLog = this._lmsLog.map((e) =>
      e.id === id ? { ...e, isExpanded: !e.isExpanded } : e
    );
  }

  handleCopyLogEntry(event) {
    event.stopPropagation();
    const id = Number(event.currentTarget.dataset.id);
    const entry = this._lmsLog.find((e) => e.id === id);
    if (entry) {
      this._copyToClipboard(entry.json);
    }
  }

  // ── Handlers: edit tab ────────────────────────────────────────────────────
  handleEditChange(event) {
    this._editPayload = event.detail?.value ?? event.target.value;
    this._parseError = null;
    this._publishSuccess = false;
  }

  handleApply() {
    this._parseError = null;
    this._publishSuccess = false;
    try {
      const parsedPayload = JSON.parse(this._editPayload); // validate JSON before queuing
      this._validatePublishPayload(parsedPayload);
      this._pendingPublish = this._editPayload;
      this._waitingForDataManager = true;
      // Safety fallback: if Data Manager doesn't respond within 500 ms, publish anyway
      // eslint-disable-next-line @lwc/lwc/no-async-operation
      setTimeout(() => {
        if (this._waitingForDataManager && this._pendingPublish) {
          this._flushPendingPublish();
        }
      }, 500);
    } catch (e) {
      this._parseError = `JSON parse error: ${e.message}`;
    }
  }

  handleReset() {
    this._editPayload = PAYLOAD_SKELETON;
    this._parseError = null;
    this._publishSuccess = false;
  }

  handleCopyEdit() {
    this._copyToClipboard(this._editPayload);
  }

  handleInsertSnippet(event) {
    const type = event.currentTarget.dataset.snippet;
    const snippets = {
      quantity:
        '{\n  "key": ["<transactionLineId>"],\n  "field": "Quantity",\n  "value": 1\n}',
      attribute:
        '{\n  "key": ["<transactionLineId>"],\n  "field": "AttributeField",\n  "attributeId": "<attributeDefinitionId (0tj...)>",\n  "value": "<attributeValueId (0v6...) or text>"\n}',
      select:
        '{\n  "field": "isSelected",\n  "productRelatedComponentId": "<prcId>",\n  "value": true\n}',
      custom:
        '{\n  "key": ["<transactionLineId>"],\n  "values": [{\n    "field": "<CustomField__c>",\n    "value": "<newValue>"\n  }]\n}',
      psm: '{\n  "key": ["<transactionLineId>"],\n  "field": "ProductSellingModel",\n  "value": {\n    "psmId": "<psmId>",\n    "pbeId": "<pbeId>"\n  }\n}',
    };
    const snippet = snippets[type];
    if (!snippet) return;
    try {
      const payload = this._editPayload.trim() ? this._editPayload : PAYLOAD_SKELETON;
      const parsed = JSON.parse(payload);
      if (!Array.isArray(parsed.data)) {
        parsed.data = [];
      }
      parsed.data.push(JSON.parse(snippet));
      this._editPayload = JSON.stringify(parsed, null, 2);
      this._parseError = null;
    } catch (e) {
      this._parseError = `Could not insert snippet: ${e.message}`;
    }
  }

  // ── Clipboard helper ──────────────────────────────────────────────────────
  _copyToClipboard(text) {
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(text).catch(() => {
        this._legacyCopy(text);
      });
    } else {
      this._legacyCopy(text);
    }
  }

  _legacyCopy(text) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy"); // eslint-disable-line @lwc/lwc/no-document-query
    document.body.removeChild(ta);
  }

  _getActiveStateSearchIndex() {
    const count = this._stateSearchMatches.length;
    if (count === 0) {
      return 0;
    }
    return Math.min(Math.max(this._stateSearchMatchIndex, 0), count - 1);
  }

  _indexStateSearchMatches() {
    const query = this._stateSearchTerm.trim();
    if (!query) {
      this._stateSearchMatches = [];
      this._stateSearchSnapshot = "";
      return;
    }

    const snapshot = this.activeStateJson;
    const lowerSnapshot = snapshot.toLowerCase();
    const lowerQuery = query.toLowerCase();
    const matches = [];
    let cursor = lowerSnapshot.indexOf(lowerQuery);
    while (cursor !== -1) {
      matches.push(cursor);
      cursor = lowerSnapshot.indexOf(lowerQuery, cursor + lowerQuery.length);
    }
    this._stateSearchMatches = matches;
    this._stateSearchSnapshot = snapshot;
  }

  _refreshStateSearchMatchesIfNeeded() {
    if (!this._stateSearchTerm.trim()) {
      return;
    }
    if (this.activeStateJson !== this._stateSearchSnapshot) {
      this._indexStateSearchMatches();
    }
  }

  _scrollStateSearchMatchIntoView() {
    const matchStart = this._stateSearchMatches[this._getActiveStateSearchIndex()];
    if (matchStart === undefined) {
      return;
    }

    const pre = this.template.querySelector("[data-state-json]");
    const container = this.template.querySelector(".json-container");
    if (!pre || !container) {
      return;
    }

    const lineIndex = this._stateSearchSnapshot
      .slice(0, matchStart)
      .split("\n").length - 1;
    const lineHeight =
      Number.parseFloat(window.getComputedStyle(pre).lineHeight) || 18;
    container.scrollTop = Math.max(0, lineIndex * lineHeight - container.clientHeight / 2);
    this._selectStateSearchMatch(pre, matchStart);
  }

  _selectStateSearchMatch(pre, matchStart) {
    const textNode = pre.firstChild;
    if (!textNode) {
      return;
    }

    const range = document.createRange();
    const matchEnd = matchStart + this._stateSearchTerm.trim().length;
    if (matchEnd > textNode.textContent.length) {
      return;
    }
    range.setStart(textNode, matchStart);
    range.setEnd(textNode, matchEnd);

    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
  }

  _clearWindowSelection() {
    const selection = window.getSelection?.();
    if (selection) {
      selection.removeAllRanges();
    }
  }

  _startApiTiming() {
    this._apiTimingStartMs = Date.now();
    this._apiTimingStartedAt = new Date().toLocaleTimeString();
    this._apiTimingTick += 1;
    this._clearApiTimingInterval();
    // eslint-disable-next-line @lwc/lwc/no-async-operation
    this._apiTimingIntervalId = setInterval(() => {
      this._apiTimingTick += 1;
    }, API_TIMING_TICK_MS);
  }

  _finishApiTiming() {
    if (this._apiTimingStartMs === null) {
      this._clearApiTimingInterval();
      return;
    }

    const startedAtMs = this._apiTimingStartMs;
    const endedAtMs = Date.now();
    const durationMs = endedAtMs - this._apiTimingStartMs;
    const entry = {
      id: endedAtMs,
      startedAt: this._apiTimingStartedAt,
      endedAt: new Date(endedAtMs).toLocaleTimeString(),
      durationMs,
      durationLabel: this._formatDuration(durationMs),
    };

    this._apiTimings = [entry, ...this._apiTimings].slice(0, MAX_API_TIMINGS);
    this._associateTimingWithLogEntry(entry.durationLabel, startedAtMs, endedAtMs);
    this._apiTimingStartMs = null;
    this._apiTimingStartedAt = null;
    this._clearApiTimingInterval();
  }

  _associateTimingWithLogEntry(durationLabel, startedAtMs, endedAtMs) {
    // Correlate timing to LMS entries emitted during the same API in-progress window.
    const CORRELATION_GRACE_MS = 300;
    const candidateInWindow = this._lmsLog.filter(
      (entry) =>
        !entry.apiTimingLabel &&
        entry.receivedAtMs >= startedAtMs - CORRELATION_GRACE_MS &&
        entry.receivedAtMs <= endedAtMs + CORRELATION_GRACE_MS
    );

    const candidates = candidateInWindow.length
      ? candidateInWindow
      : this._lmsLog.filter(
        (entry) =>
          !entry.apiTimingLabel &&
          entry.receivedAtMs >= startedAtMs - CORRELATION_GRACE_MS
      );

    if (!candidates.length) {
      return;
    }

    // Prefer action-based events over initialization "(no action)" noise.
    const preferredEntry =
      candidates.find((entry) => entry.action !== "(no action)") ?? candidates[0];

    this._lmsLog = this._lmsLog.map((entry) =>
      entry.id === preferredEntry.id
        ? { ...entry, apiTimingLabel: durationLabel }
        : entry
    );
  }

  _formatDuration(durationMs) {
    if (durationMs < 1000) {
      return `${durationMs}ms`;
    }
    return `${(durationMs / 1000).toFixed(2)}s`;
  }

  _clearStateSearchDebounce() {
    if (this._stateSearchDebounceId) {
      clearTimeout(this._stateSearchDebounceId);
      this._stateSearchDebounceId = null;
    }
  }

  _clearApiTimingInterval() {
    if (this._apiTimingIntervalId) {
      clearInterval(this._apiTimingIntervalId);
      this._apiTimingIntervalId = null;
    }
  }

  _coerceBoolean(value) {
    return value === true || value === "true";
  }

  _deserializeJsonString(value, propertyName) {
    if (value === null || value === undefined || value === "") {
      return null;
    }

    if (typeof value !== "string") {
      return value;
    }

    try {
      return JSON.parse(value);
    } catch (error) {
      return {
        _parseError: `Invalid serialized JSON in ${propertyName}: ${error.message}`,
        rawValue: value,
      };
    }
  }

  _maybeAutoEnableInstantPricing() {
    if (this._hasAutoInstantPricingAttempted) {
      return;
    }
    if (!this._coerceBoolean(this.automaticInstantPricing)) {
      return;
    }
    if (!this._subscription || !this.messageContext || !CONFIGR_CHANNEL) {
      return;
    }

    if (!this._isInstantPricingStateKnown) {
      this._scheduleAutoInstantPricingRetry();
      return;
    }

    this._hasAutoInstantPricingAttempted = true;
    this._clearAutoInstantPricingRetry();
    if (this.isInstantPricingEnabled) {
      return;
    }

    try {
      publish(this.messageContext, CONFIGR_CHANNEL, TOGGLE_INSTANT_PRICING_PAYLOAD);
    } catch (error) {
      this._parseError = `Auto instant pricing publish error: ${error.message}`;
    }
  }

  _scheduleAutoInstantPricingRetry() {
    if (
      this._autoInstantPricingRetryTimeoutId ||
      this._autoInstantPricingRetryCount >= MAX_AUTO_INSTANT_PRICING_RETRIES
    ) {
      return;
    }
    this._autoInstantPricingRetryCount += 1;
    // eslint-disable-next-line @lwc/lwc/no-async-operation
    this._autoInstantPricingRetryTimeoutId = setTimeout(() => {
      this._autoInstantPricingRetryTimeoutId = null;
      this._maybeAutoEnableInstantPricing();
    }, AUTO_INSTANT_PRICING_RETRY_MS);
  }

  _clearAutoInstantPricingRetry() {
    if (this._autoInstantPricingRetryTimeoutId) {
      clearTimeout(this._autoInstantPricingRetryTimeoutId);
      this._autoInstantPricingRetryTimeoutId = null;
    }
  }

  _validatePublishPayload(payload) {
    if (!payload || typeof payload !== "object") {
      throw new Error("Payload must be a JSON object.");
    }
    if (!Array.isArray(payload.data)) {
      throw new Error('Payload must include a "data" array.');
    }

    const { attributeIds, picklistIdsToAttributeId } = this._indexKnownAttributes();
    payload.data.forEach((change, index) => {
      if (change?.field !== "AttributeField") {
        return;
      }

      const attributeId = change?.attributeId;
      if (!attributeId || typeof attributeId !== "string") {
        throw new Error(
          `Attribute change at data[${index}] is missing a valid string attributeId.`
        );
      }

      if (picklistIdsToAttributeId.has(attributeId)) {
        const expectedAttributeId = picklistIdsToAttributeId.get(attributeId);
        throw new Error(
          `Attribute change at data[${index}] uses picklist id "${attributeId}" as attributeId. Use the attribute definition id "${expectedAttributeId}" (usually 0tj...), and keep the picklist value id in "value".`
        );
      }

      if (attributeIds.size > 0 && !attributeIds.has(attributeId)) {
        throw new Error(
          `Attribute change at data[${index}] uses unknown attributeId "${attributeId}". Use the attribute definition id from State > Attribute Categories (usually 0tj...).`
        );
      }
    });
  }

  _indexKnownAttributes() {
    const attributeIds = new Set();
    const picklistIdsToAttributeId = new Map();

    const categories = Array.isArray(this.attributeCategories)
      ? this.attributeCategories
      : [];

    categories.forEach((category) => {
      const attributes = Array.isArray(category?.attributes)
        ? category.attributes
        : [];
      attributes.forEach((attribute) => {
        if (typeof attribute?.id === "string" && attribute.id) {
          attributeIds.add(attribute.id);
          const picklistId = attribute?.attributePicklist?.id;
          if (typeof picklistId === "string" && picklistId) {
            picklistIdsToAttributeId.set(picklistId, attribute.id);
          }
        }
      });
    });

    return { attributeIds, picklistIdsToAttributeId };
  }
}
