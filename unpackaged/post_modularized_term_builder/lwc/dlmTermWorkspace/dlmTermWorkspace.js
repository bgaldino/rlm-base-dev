import { LightningElement, api, wire } from "lwc";
import {
  publish,
  subscribe,
  unsubscribe,
  MessageContext,
  APPLICATION_SCOPE
} from "lightning/messageService";
import DLM_CHANNEL from "@salesforce/messageChannel/DLM_TermBuilderChannel__c";

const SOURCE = "dlmTermWorkspace";
// Route + geography scope attribute codes surfaced in the scoped grid's inline attribute picker.
// Extends the monolith dlTermBuilder default with the G2 geography-scope codes (DL_ScopeType /
// DL_MarketGroup — definitions live in the org as data). Includes/Excludes is NOT here: it is a
// transient UI toggle on the Term rail card, never a persisted attribute. Only codes whose
// AttributeDefinition exists in the org render; overridable per placement via the attributeCodes
// design property.
const DEFAULT_ATTRIBUTE_CODES =
  "DL_ScopeType,DL_MarketGroup,DL_Origin,DL_Destination,DL_Directionality,DL_Measure,DL_RequirementValue,DL_SpecialConditions";

/**
 * Modularized Delta Term Builder — the "term workspace" tile.
 *
 * Hosts the scoped c/dlmQuoteLineGrid (the selected Term + its fares) and the c/dlmAddFareClass bar.
 * Holds no term data of its own: it learns the open negotiation from the header's `context` message
 * and the chosen Term from the rail's `termSelected` / `termsChanged` messages, then scopes the grid
 * to `quoteId` + `selectedTermId`.
 *
 * Publishes: `linesChanged` (grid line edit / removal / term rename) and `fareAdded` (a fare class
 * was added). Subscribes: `context` (new negotiation → adopt quoteId, clear selection),
 * `termSelected` (adopt selected Term), `termsChanged` (adopt the newest Term + refetch, since the
 * grid's quoteId-keyed cache doesn't yet include it), and `linesChanged` from other tiles (refetch).
 */
export default class DlmTermWorkspace extends LightningElement {
  // Design-time configuration (see .js-meta.xml). Booleans are left undefined unless the admin sets
  // them so the getters can treat "unset" as on-by-default without tripping the LWC
  // boolean-default-true lint rule.
  @api headingLabel;
  @api attributeCodes;
  @api hideGroupColumn;
  @api showAddFareClass;

  quoteId;
  selectedTermId;

  _subscription = null;
  // Set when an inbound message requires the grid to refetch (not just re-scope its cache); acted on
  // in renderedCallback once the grid is guaranteed present.
  _needsGridRefresh = false;

  @wire(MessageContext)
  messageContext;

  connectedCallback() {
    this._subscribe();
  }

  disconnectedCallback() {
    this._unsubscribe();
  }

  renderedCallback() {
    if (this._needsGridRefresh) {
      const grid = this.template.querySelector("c-dlm-quote-line-grid");
      if (grid) {
        this._needsGridRefresh = false;
        grid.refresh();
      }
    }
  }

  // ---------- LMC wiring ----------

  _subscribe() {
    if (this._subscription) {
      return;
    }
    this._subscription = subscribe(
      this.messageContext,
      DLM_CHANNEL,
      (message) => this.handleMessage(message),
      { scope: APPLICATION_SCOPE }
    );
  }

  _unsubscribe() {
    if (this._subscription) {
      unsubscribe(this._subscription);
      this._subscription = null;
    }
  }

  handleMessage(message) {
    if (!message || message.source === SOURCE) {
      return;
    }
    switch (message.type) {
      case "context":
        // A different negotiation was opened/created: adopt it and drop any prior Term selection so
        // the workspace shows its empty prompt until the rail broadcasts a selection.
        if (message.quoteId !== this.quoteId) {
          this.quoteId = message.quoteId;
          this.selectedTermId = null;
        }
        break;
      case "termSelected":
        // Plain chip selection: the term already exists in the grid's cache, so the grid's
        // scopeRootLineId setter re-scopes without a server round trip.
        if (message.quoteId === this.quoteId) {
          this.selectedTermId = message.selectedTermId || null;
        }
        break;
      case "termsChanged":
        // A Term was just added: adopt the newest selection AND refetch, because the grid's
        // getQuoteLines cache is keyed on quoteId (unchanged) and doesn't include the new line yet.
        if (message.quoteId === this.quoteId) {
          this.selectedTermId = message.selectedTermId || null;
          this._needsGridRefresh = true;
        }
        break;
      case "linesChanged":
        // Another tile changed line data (e.g. the header's Apply-to-All). Our own edits are
        // suppressed by the source guard above, so this is always someone else's change.
        if (message.quoteId === this.quoteId) {
          this._needsGridRefresh = true;
        }
        break;
      default:
        break;
    }
  }

  _publishLinesChanged() {
    publish(this.messageContext, DLM_CHANNEL, {
      type: "linesChanged",
      quoteId: this.quoteId,
      source: SOURCE
    });
  }

  _publishFareAdded() {
    publish(this.messageContext, DLM_CHANNEL, {
      type: "fareAdded",
      quoteId: this.quoteId,
      selectedTermId: this.selectedTermId,
      source: SOURCE
    });
  }

  // ---------- design-time config ----------

  get effectiveHeading() {
    return this.headingLabel || this.selectedTermName || "Term Workspace";
  }

  // The grid/add-fare heading falls back to a generic label; the Term's identity is visible in the
  // grid's own root row, so no extra Apex call for the term name is needed here.
  get selectedTermName() {
    return "";
  }

  get effectiveAttributeCodes() {
    return this.attributeCodes || DEFAULT_ATTRIBUTE_CODES;
  }

  get groupColumnHidden() {
    return this.hideGroupColumn !== false;
  }

  get addFareVisible() {
    return this.showAddFareClass !== false;
  }

  // Show the grid + fares only once a negotiation is open and a Term is selected; otherwise a prompt.
  get showWorkspace() {
    return !!this.quoteId && !!this.selectedTermId;
  }

  // ---------- child events → LMC pulses ----------

  // The grid edited/removed a line or renamed the Term. The grid manages its own refreshApex, so we
  // just broadcast linesChanged for the rail (counts/name) and header (Apply-to-All / summary).
  handleLinesUpdated() {
    this._publishLinesChanged();
  }

  // A fare class was added under the selected Term. Refresh our own scoped grid (its cache predates
  // the new fare line) and broadcast fareAdded so the rail counts and header refresh.
  handleFareAdded() {
    const grid = this.template.querySelector("c-dlm-quote-line-grid");
    if (grid) {
      grid.refresh();
    }
    this._publishFareAdded();
  }
}
