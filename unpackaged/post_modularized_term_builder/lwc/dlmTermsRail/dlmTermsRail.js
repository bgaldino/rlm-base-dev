import { LightningElement, api, track, wire } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { CurrentPageReference } from "lightning/navigation";
import {
  publish,
  subscribe,
  unsubscribe,
  MessageContext,
  APPLICATION_SCOPE
} from "lightning/messageService";
import DLM_CHANNEL from "@salesforce/messageChannel/DLM_TermBuilderChannel__c";
import getBuilderState from "@salesforce/apex/RLM_DeltaTermBuilderController.getBuilderState";
import addTerm from "@salesforce/apex/RLM_DeltaTermBuilderController.addTerm";
import DlmTermLibraryModal from "c/dlmTermLibraryModal";

const SOURCE = "dlmTermsRail";
const DEFAULT_MAX_ADD = 10;

/**
 * Modularized Delta Term Builder — the "Terms rail" tile.
 *
 * Renders the c/dlmTermCard chips for the open negotiation plus a bare inline "Add Term" bar (the
 * DL-TERM product is resolved server-side, so no catalog/search UI is needed). Owns term SELECTION
 * on behalf of the composed page.
 *
 * Publishes: `termSelected` (chip click / default-select after load) and `termsChanged` (after Add
 * Term, carrying the newest term id). Subscribes: `context` (new negotiation → load terms +
 * default-select) and `linesChanged` / `fareAdded` / `contractCreated` (reload — names/counts and
 * downstream state may change).
 */
export default class DlmTermsRail extends LightningElement {
  // Design-time configuration (see .js-meta.xml). Undefined-unless-set so the getters can treat
  // "unset" as on-by-default without tripping the LWC boolean-default-true lint rule.
  @api headingLabel;
  @api allowAddTerms;
  @api maxAddCount;

  @track terms = [];

  quoteId;
  selectedTermId;
  loadingState = false;
  addingTerm = false;
  addTermCount = 1;
  errorMessage = "";

  _subscription = null;
  // The ?c__quoteId= we last acted on. Tracked (not a one-shot boolean) so a re-navigation to this app
  // page with a DIFFERENT quote is honored even when Lightning reuses the cached component instance.
  _lastUrlQuoteId;

  @wire(MessageContext)
  messageContext;

  // Pick up ?c__quoteId= from URL state, re-running when the param CHANGES: a deep-link/renewal
  // fallback so the rail loads its terms even if the LMC `context` publish is missed (this tile can
  // mount after the header broadcasts it). Adopting only on a URL-param change never clobbers an
  // interactive quote switch that flows through `context` without touching the URL.
  @wire(CurrentPageReference)
  applyPageReference(pageRef) {
    if (!pageRef) {
      return;
    }
    const quoteFromUrl = (pageRef.state && pageRef.state.c__quoteId) || null;
    if (quoteFromUrl && quoteFromUrl !== this._lastUrlQuoteId) {
      this._lastUrlQuoteId = quoteFromUrl;
      if (quoteFromUrl !== this.quoteId) {
        this.quoteId = quoteFromUrl;
        this.selectedTermId = null;
        this.loadTerms(true);
      }
    }
  }

  connectedCallback() {
    this._subscribe();
  }

  disconnectedCallback() {
    this._unsubscribe();
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
        // A different negotiation was opened/created: adopt it and load its terms. A repeat of the
        // current quote (e.g. a header date edit) carries no term-list change, so ignore it and keep
        // the current selection.
        if (message.quoteId && message.quoteId !== this.quoteId) {
          this.quoteId = message.quoteId;
          this.selectedTermId = null;
          this.loadTerms(true);
        }
        break;
      case "linesChanged":
      case "fareAdded":
      case "contractCreated":
        // Names / fare counts / downstream state can change; reload while preserving the selection.
        if (message.quoteId && message.quoteId === this.quoteId) {
          this.loadTerms(false);
        }
        break;
      default:
        break;
    }
  }

  _publishTermSelected() {
    publish(this.messageContext, DLM_CHANNEL, {
      type: "termSelected",
      quoteId: this.quoteId,
      selectedTermId: this.selectedTermId,
      source: SOURCE
    });
  }

  _publishTermsChanged() {
    publish(this.messageContext, DLM_CHANNEL, {
      type: "termsChanged",
      quoteId: this.quoteId,
      selectedTermId: this.selectedTermId,
      source: SOURCE
    });
  }

  // ---------- design-time visibility ----------

  get effectiveHeading() {
    return this.headingLabel || "Terms";
  }

  get addTermsAllowed() {
    return this.allowAddTerms !== false;
  }

  get maxAdd() {
    const n = parseInt(this.maxAddCount, 10);
    return Number.isNaN(n) || n < 1 ? DEFAULT_MAX_ADD : n;
  }

  get maxOverflowMessage() {
    return `Add up to ${this.maxAdd} Terms at a time.`;
  }

  // ---------- rail state ----------

  get hasTerms() {
    return this.terms.length > 0;
  }

  // Decorate each term with its selected flag for the rail chips.
  get termCards() {
    return this.terms.map((t) => ({
      ...t,
      selected: t.id === this.selectedTermId
    }));
  }

  get addTermDisabled() {
    return !this.quoteId || this.addingTerm;
  }

  // Load the term list from getBuilderState. When selectDefault is true (a fresh open) the selection
  // follows the server default; otherwise the current selection is preserved if it still exists.
  async loadTerms(selectDefault) {
    if (!this.quoteId) {
      return;
    }
    this.loadingState = true;
    this.errorMessage = "";
    try {
      const res = this._parse(await getBuilderState({ quoteId: this.quoteId }));
      if (res.isSuccess === false) {
        this.errorMessage = res.errorMessage || "Unable to load the terms.";
        return;
      }
      this.terms = res.terms || [];
      const ids = new Set(this.terms.map((t) => t.id));
      if (
        selectDefault ||
        !this.selectedTermId ||
        !ids.has(this.selectedTermId)
      ) {
        this.selectedTermId =
          res.selectedTermId || (this.terms[0] && this.terms[0].id) || null;
        // Broadcast the resolved selection so the workspace scopes to it.
        this._publishTermSelected();
      }
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.loadingState = false;
    }
  }

  handleTermSelect(event) {
    const termId = event.detail.termId;
    if (termId && termId !== this.selectedTermId) {
      this.selectedTermId = termId;
      this._publishTermSelected();
    }
  }

  handleAddTermCountChange(event) {
    // Clamp to [1, maxAdd]; a blank/NaN entry falls back to 1.
    const raw = parseInt(event.target.value, 10);
    this.addTermCount = Number.isNaN(raw)
      ? 1
      : Math.min(this.maxAdd, Math.max(1, raw));
  }

  // Add N route-based Term(s) directly via the controller (the DL-TERM product is resolved
  // server-side). Reload the rail and auto-select the newest Term.
  async handleAddTerm() {
    if (!this.quoteId || this.addingTerm) {
      return;
    }
    this.addingTerm = true;
    this.errorMessage = "";
    try {
      const res = this._parse(
        await addTerm({
          inputJson: JSON.stringify({
            quoteId: this.quoteId,
            count: this.addTermCount
          })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage = res.errorMessage || "Unable to add the Term.";
        return;
      }
      const added = res.addedCount || 1;
      this._toast(
        added > 1 ? `${added} Terms added` : "Term added",
        "",
        "success"
      );
      await this.handleTermAdded();
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.addingTerm = false;
    }
  }

  // Open the Term Library modal and, on a finished add, funnel into the same refresh path as a manual
  // Add Term. The modal owns the getTermLibrary/addTermFromTemplate calls and its own busy state; here
  // we only react to its result (a real DL-TERM line was created server-side, so handleTermAdded picks
  // it up as the newest term exactly like the inline add).
  async handleAddFromLibrary() {
    if (!this.quoteId || this.addingTerm) {
      return;
    }
    this.errorMessage = "";
    try {
      const result = await DlmTermLibraryModal.open({
        quoteId: this.quoteId,
        size: "medium",
        label: "Term Library"
      });
      // The modal stays open across adds and reports its running totals when the rep finishes. A
      // clean cancel (nothing added) needs no refresh; a finished close carries the totals for the
      // toast; an ESC/X dismissal resolves with no payload but Terms may still have been created, so
      // refresh to be safe.
      if (result && result.status === "cancel") {
        return;
      }
      if (result && result.status === "finished") {
        const count = result.addedCount || 1;
        const fares = result.addedFareCount || 0;
        const termText = `${count} Term${count > 1 ? "s" : ""}`;
        const fareText = fares
          ? ` with ${fares} fare class${fares > 1 ? "es" : ""}`
          : "";
        this._toast(
          "Terms added from library",
          `${termText} added${fareText}.`,
          "success"
        );
      }
      await this.handleTermAdded(result && result.lastTermLineId);
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    }
  }

  // Reload the rail and auto-select the newest Term (the one not previously present), then broadcast
  // termsChanged so the workspace re-fetches its scoped grid (its getQuoteLines wire is keyed on
  // quoteId, which doesn't change here, so it must be told explicitly) and the header refreshes its
  // Apply-to-All / Create Contract state.
  async handleTermAdded(preferredId) {
    const before = new Set(this.terms.map((t) => t.id));
    // Reload without auto-selecting the server default; we pick the newest term explicitly below.
    await this.loadTerms(false);
    // Prefer an explicit target (e.g. the last Term added from the library across several adds);
    // otherwise fall back to whichever Term wasn't present before this reload.
    const target =
      (preferredId && this.terms.find((t) => t.id === preferredId)) ||
      this.terms.find((t) => !before.has(t.id));
    if (target) {
      this.selectedTermId = target.id;
    } else if (!this.selectedTermId && this.terms.length) {
      this.selectedTermId = this.terms[0].id;
    }
    this._publishTermsChanged();
  }

  // ---------- helpers ----------

  _parse(json) {
    try {
      return json ? JSON.parse(json) : {};
    } catch {
      return {
        isSuccess: false,
        errorMessage: "Unexpected response from server."
      };
    }
  }

  _errMessage(e) {
    return (
      (e && e.body && e.body.message) || (e && e.message) || "Unexpected error."
    );
  }

  _toast(title, message, variant) {
    this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
  }
}
