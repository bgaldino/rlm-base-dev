import { LightningElement, api, wire } from "lwc";
import { CurrentPageReference } from "lightning/navigation";
import {
  publish,
  subscribe,
  unsubscribe,
  MessageContext,
  APPLICATION_SCOPE
} from "lightning/messageService";
import DLM_CHANNEL from "@salesforce/messageChannel/DLM_TermBuilderChannel__c";

const SOURCE = "dlmTermWorkspace";
// Route/requirement attribute codes surfaced in the scoped grid's inline attribute picker, in
// display order. These are the PC-DL-TERM informational (non-price-impacting) attributes; fares
// have none. The geography-scope codes (DL_ScopeType / DL_MarketGroup) are intentionally NOT
// listed: those attributes are unassigned from the Term Workspace so they neither render nor
// persist — matching the monolith dlTermBuilder default and this bundle's attributeCodes meta
// default. Includes/Excludes is likewise not here: it is a transient UI toggle on the Term rail
// card, never a persisted attribute. Only codes whose AttributeDefinition exists in the org render;
// overridable per placement via the attributeCodes design property.
const DEFAULT_ATTRIBUTE_CODES =
  "DL_Origin,DL_Destination,DL_Directionality,DL_Measure,DL_RequirementValue,DL_SpecialConditions";

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

  // quoteId + selectedTermId are BOTH an inbound prop AND LMC-derived. When embedded in
  // c/dlmWorkspaceShell they are handed down as props (the props-down fix: this tile mounts inside a
  // tab AFTER the header published its one-shot `context` message, so it can never learn the quote
  // from LMC alone). The first prop write latches `_propDriven`, after which the LMC context /
  // termSelected / termsChanged handlers no longer clobber the selection — they still pulse grid
  // refetches. Standalone (props never set), LMC drives selection exactly as before.
  _quoteId;
  _selectedTermId;
  _propDriven = false;

  @api
  get quoteId() {
    return this._quoteId;
  }
  set quoteId(value) {
    // The template binds this before the shell resolves the quote; ignore the undefined pre-write so
    // we don't latch prop-driven for a standalone tile that never gets a real value.
    if (value === undefined) {
      return;
    }
    this._propDriven = true;
    this._quoteId = value || null;
  }

  @api
  get selectedTermId() {
    return this._selectedTermId;
  }
  set selectedTermId(value) {
    if (value === undefined) {
      return;
    }
    this._propDriven = true;
    this._selectedTermId = value || null;
  }

  // Latest action state reported by the scoped grid (drives the header Save/Cancel controls hoisted
  // onto the card title row). Defaults keep the buttons hidden/disabled until the grid emits.
  _gridHasRows = false;
  _gridSaveDisabled = true;
  // The Add Fare Class panel starts open (its prior always-shown behavior); the header toggles it.
  faresExpanded = true;

  _subscription = null;
  // Set when an inbound message requires the grid to refetch (not just re-scope its cache); acted on
  // in renderedCallback once the grid is guaranteed present.
  _needsGridRefresh = false;
  // The ?c__quoteId= we last acted on (standalone fallback; see the CurrentPageReference wire below).
  _lastUrlQuoteId;

  @wire(MessageContext)
  messageContext;

  // Pick up ?c__quoteId= from URL state — the standalone-tile fallback for renewals, re-running when
  // the param CHANGES. When embedded in c/dlmWorkspaceShell the shell hands quoteId down as a prop
  // (latching _propDriven), so this is a no-op there; only a standalone placement with a missed
  // `context` message adopts the URL quote. Sets _quoteId directly (not via the prop setter) so a
  // later shell prop still wins.
  @wire(CurrentPageReference)
  applyPageReference(pageRef) {
    if (!pageRef || this._propDriven) {
      return;
    }
    const quoteFromUrl = (pageRef.state && pageRef.state.c__quoteId) || null;
    if (quoteFromUrl && quoteFromUrl !== this._lastUrlQuoteId) {
      this._lastUrlQuoteId = quoteFromUrl;
      if (quoteFromUrl !== this._quoteId) {
        this._quoteId = quoteFromUrl;
        this._selectedTermId = null;
      }
    }
  }

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

  // Refresh the scoped grid now if it's already mounted; otherwise latch so renderedCallback fires it
  // once the grid appears. This must NOT rely on a re-render to consume the latch: when the first Term
  // is added, a `termSelected` (published by the rail during Add Term, before `termsChanged`) already
  // pushed the selection through the shell and mounted the grid, so the later `termsChanged` doesn't
  // change any prop — no re-render follows, renderedCallback never re-runs, and a latch-only refresh
  // would be stranded. Refreshing imperatively here closes that gap; the latch still covers the case
  // where the grid isn't mounted yet (standalone mode, or termsChanged winning the race).
  _requestGridRefresh() {
    const grid = this.template.querySelector("c-dlm-quote-line-grid");
    if (grid) {
      this._needsGridRefresh = false;
      grid.refresh();
    } else {
      this._needsGridRefresh = true;
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
        // the workspace shows its empty prompt until the rail broadcasts a selection. Skipped when
        // prop-driven — the shell owns the selection there.
        if (!this._propDriven && message.quoteId !== this._quoteId) {
          this._quoteId = message.quoteId;
          this._selectedTermId = null;
        }
        break;
      case "termSelected":
        // Plain chip selection: the term already exists in the grid's cache, so the grid's
        // scopeRootLineId setter re-scopes without a server round trip.
        if (!this._propDriven && message.quoteId === this._quoteId) {
          this._selectedTermId = message.selectedTermId || null;
        }
        break;
      case "termsChanged":
        // A Term was just added: adopt the newest selection (unless prop-driven) AND refetch, because
        // the grid's getQuoteLines cache is keyed on quoteId (unchanged) and doesn't include the new
        // line yet. The refetch pulse fires in both modes.
        if (message.quoteId === this._quoteId) {
          if (!this._propDriven) {
            this._selectedTermId = message.selectedTermId || null;
          }
          this._requestGridRefresh();
        }
        break;
      case "linesChanged":
        // Another tile changed line data (e.g. the header's Apply-to-All). Our own edits are
        // suppressed by the source guard above, so this is always someone else's change.
        if (message.quoteId === this._quoteId) {
          this._requestGridRefresh();
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

  // Header Save/Cancel controls (aligned with the card title) render only once the scoped grid has
  // rows, and follow the grid's own dirty/saving gate.
  get showGridActions() {
    return this._gridHasRows;
  }

  get gridSaveDisabled() {
    return this._gridSaveDisabled;
  }

  // Collapsible Add Fare Class panel state for the disclosure button.
  get faresExpandedStr() {
    return this.faresExpanded ? "true" : "false";
  }

  get faresChevron() {
    return this.faresExpanded ? "utility:chevrondown" : "utility:chevronright";
  }

  toggleFares() {
    this.faresExpanded = !this.faresExpanded;
  }

  // ---------- child events → LMC pulses ----------

  // The grid edited/removed a line or renamed the Term. The grid manages its own refreshApex, so we
  // just broadcast linesChanged for the rail (counts/name) and header (Apply-to-All / summary).
  handleLinesUpdated() {
    this._publishLinesChanged();
  }

  // The grid reports its action state (row count + save gate) so the hoisted header buttons stay in
  // lockstep with its dirty/saving state.
  handleGridState(event) {
    const detail = event.detail || {};
    this._gridHasRows = !!detail.hasRows;
    // Default to disabled unless the grid explicitly reports it can save.
    this._gridSaveDisabled = detail.saveDisabled !== false;
  }

  // Header Save/Cancel delegate to the scoped grid's public controls.
  handleGridSave() {
    const grid = this.template.querySelector("c-dlm-quote-line-grid");
    if (grid) {
      grid.save();
    }
  }

  handleGridCancel() {
    const grid = this.template.querySelector("c-dlm-quote-line-grid");
    if (grid) {
      grid.cancel();
    }
  }

  // A fare class was added under the selected Term. Refresh our own scoped grid (its cache predates
  // the new fare line) and broadcast fareAdded so the rail counts and header refresh.
  handleFareAdded() {
    this._requestGridRefresh();
    this._publishFareAdded();
  }
}
