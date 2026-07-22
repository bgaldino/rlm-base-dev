import { LightningElement, api, track, wire } from "lwc";
import { CurrentPageReference } from "lightning/navigation";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { loadStyle } from "lightning/platformResourceLoader";
import {
  publish,
  subscribe,
  unsubscribe,
  MessageContext,
  APPLICATION_SCOPE
} from "lightning/messageService";
import DLM_CHANNEL from "@salesforce/messageChannel/DLM_TermBuilderChannel__c";
import DlmCreateContractModal from "c/dlmCreateContractModal";
import noHeader from "@salesforce/resourceUrl/DL_Term_Builder_NoHeader";
import DL_TERM_BUILDER_EMBLEM from "@salesforce/resourceUrl/DL_Term_Builder_Emblem";
import createNegotiation from "@salesforce/apex/RLM_DeltaTermBuilderController.createNegotiation";
import getNegotiationsForAccount from "@salesforce/apex/RLM_DeltaTermBuilderController.getNegotiationsForAccount";
import getBuilderState from "@salesforce/apex/RLM_DeltaTermBuilderController.getBuilderState";
import updateNegotiationDates from "@salesforce/apex/RLM_DeltaTermBuilderController.updateNegotiationDates";
import updateLineDiscountAndDates from "@salesforce/apex/RLM_DeltaLineController.updateLineDiscountAndDates";

// This tile's name, stamped on every published message so the tile can ignore its own echoes.
const SOURCE = "dlmNegotiationContext";

/**
 * Modularized Delta Term Builder — the "negotiation context" header tile.
 *
 * Owns Account selection, New Negotiation, the existing-negotiation combobox, the editable
 * negotiation name, the default Start/End Date + Apply-to-All, and the Create/View Contract action.
 * It is a page-composable sibling of c/dlmTermsRail and c/dlmTermWorkspace; the three stay in sync
 * over the DLM_TermBuilderChannel LMC rather than through a parent's @api props.
 *
 * Publishes: `context` (quote/account/dates — on open, create, or date change) and `contractCreated`.
 * Subscribes: `termsChanged` / `linesChanged` / `fareAdded` — to re-fetch the term list it needs for
 * Apply-to-All (collects every line id) and Create Contract (enablement + summary).
 *
 * Server contract is unchanged from the monolith: RLM_DeltaTermBuilderController /
 * RLM_DeltaLineController JSON-in/JSON-out methods, shared with the original post_term_builder app.
 */
export default class DlmNegotiationContext extends LightningElement {
  // Optional URL preselect: an Account-page button can deep-link with ?c__accountId=...
  @api accountId;
  // Optional deep-link straight into an existing negotiation: ?c__quoteId=... (or the design
  // property) opens that Quote on load and back-fills its Account into the header.
  @api quoteRecordId;

  // Design-time configuration (see .js-meta.xml). Left undefined unless the admin sets them, so the
  // visibility getters below can treat "unset" as the intended on-by-default without tripping the
  // LWC "boolean public property should not default to true" lint rule.
  @api headingLabel;
  @api showBranding;
  @api showContractActions;
  @api showDateDefaults;

  @track terms = [];
  @track quoteOptions = [];

  selectedAccountId;
  quoteId;
  quoteName = "";
  accountName = "";
  negotiationStartDate = "";
  negotiationEndDate = "";
  savingNegotiationDates = false;
  applyingDatesToAllLines = false;

  // When the open negotiation is already related to a Contract, the server returns its id + number;
  // the header then offers "View Contract" instead of a "Create Contract" that would only fail.
  contractId = null;
  contractNumber = "";
  loadingState = false;
  creating = false;
  contracting = false;
  errorMessage = "";

  // Delta triangle emblem shown in the header, replacing the CSS triangle stand-in.
  emblemUrl = DL_TERM_BUILDER_EMBLEM;

  // The ?c__quoteId= / ?c__accountId= values we last acted on. Tracked (not a one-shot boolean) so a
  // re-navigation to this app page with a DIFFERENT quote is honored even when Lightning reuses the
  // cached component instance — otherwise the page keeps rendering the previously-opened quote.
  _lastUrlQuoteId;
  _lastUrlAccountId;
  _subscription = null;

  @wire(MessageContext)
  messageContext;

  // Pick up ?c__quoteId= / ?c__accountId= from URL state. A quoteId wins: it opens the quote directly
  // and back-fills its account. Otherwise an accountId just preselects the account. Re-runs when the
  // URL param CHANGES (compared against the last value we acted on) so navigating to a new negotiation
  // on a cached page instance is honored; an unchanged param never clobbers an interactive selection.
  @wire(CurrentPageReference)
  applyPageReference(pageRef) {
    if (!pageRef) {
      return;
    }
    const quoteFromUrl = (pageRef.state && pageRef.state.c__quoteId) || null;
    const acctFromUrl = (pageRef.state && pageRef.state.c__accountId) || null;
    if (quoteFromUrl && quoteFromUrl !== this._lastUrlQuoteId) {
      this._lastUrlQuoteId = quoteFromUrl;
      this._lastUrlAccountId = null;
      this.openQuote(quoteFromUrl);
    } else if (!quoteFromUrl && acctFromUrl && acctFromUrl !== this._lastUrlAccountId) {
      this._lastUrlAccountId = acctFromUrl;
      this.selectedAccountId = acctFromUrl;
      this.loadNegotiations();
    }
  }

  connectedCallback() {
    // Hide the standard flexipage page-header band (a redundant title + tab icon) so only this
    // tile's navy Delta header shows. Failure is non-fatal — ignore and continue.
    loadStyle(this, noHeader).catch(() => {
      /* header-hiding stylesheet is cosmetic; ignore load failures */
    });
    this._subscribe();
    // A design-property quoteId deep-links straight into that negotiation; else an accountId
    // preselects the account. The URL-state wire (above) takes precedence when present.
    if (this.quoteRecordId && !this.quoteId) {
      this.openQuote(this.quoteRecordId);
    } else if (this.accountId && !this.selectedAccountId) {
      this.selectedAccountId = this.accountId;
      this.loadNegotiations();
    }
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

  // React to structural/data changes published by the rail or workspace by re-fetching the term
  // list (Apply-to-All and Create Contract both read it). Ignore our own echoes and messages for a
  // different negotiation.
  handleMessage(message) {
    if (!message || message.source === SOURCE) {
      return;
    }
    if (
      (message.type === "termsChanged" ||
        message.type === "linesChanged" ||
        message.type === "fareAdded") &&
      message.quoteId &&
      message.quoteId === this.quoteId
    ) {
      this.refreshState(false);
    }
  }

  _publishContext() {
    publish(this.messageContext, DLM_CHANNEL, {
      type: "context",
      quoteId: this.quoteId,
      accountId: this.selectedAccountId,
      negotiationStartDate: this.negotiationStartDate || null,
      negotiationEndDate: this.negotiationEndDate || null,
      source: SOURCE
    });
  }

  _publishContractCreated() {
    publish(this.messageContext, DLM_CHANNEL, {
      type: "contractCreated",
      quoteId: this.quoteId,
      source: SOURCE
    });
  }

  _publishLinesChanged() {
    publish(this.messageContext, DLM_CHANNEL, {
      type: "linesChanged",
      quoteId: this.quoteId,
      source: SOURCE
    });
  }

  // ---------- design-time visibility ----------

  get effectiveHeading() {
    return this.headingLabel || "Term Builder";
  }

  get brandingVisible() {
    return this.showBranding !== false;
  }

  get contractActionsVisible() {
    return this.showContractActions !== false;
  }

  get dateDefaultsVisible() {
    return this.showDateDefaults !== false;
  }

  // ---------- header: account + quote selection ----------

  get accountMatchingInfo() {
    return { primaryField: { fieldPath: "Name" } };
  }

  get accountDisplayInfo() {
    return { primaryField: "Name" };
  }

  get newNegotiationDisabled() {
    return this.creating || !this.selectedAccountId;
  }

  get hasQuoteOptions() {
    return this.quoteOptions.length > 0;
  }

  get quoteSelectDisabled() {
    return this.quoteOptions.length === 0;
  }

  get hasQuote() {
    return !!this.quoteId;
  }

  get hasTerms() {
    return this.terms.length > 0;
  }

  // Relative Lightning URL to the open negotiation's Quote record, for the header "Open record"
  // link. Relative so it resolves in whatever domain the app is hosted (production or sandbox).
  get quoteRecordUrl() {
    return this.quoteId ? `/lightning/r/Quote/${this.quoteId}/view` : null;
  }

  get quoteNameDisabled() {
    return !this.quoteId;
  }

  // True once the open negotiation is already related to a Contract. The Quote can then only be
  // contracted once (the standard createContract action rejects a second), so the header shows a
  // "View Contract" link instead of "Create Contract".
  get hasContract() {
    return !!this.contractId;
  }

  get contractRecordUrl() {
    return this.contractId
      ? `/lightning/r/Contract/${this.contractId}/view`
      : null;
  }

  get viewContractTitle() {
    return this.contractNumber
      ? `Open Contract ${this.contractNumber}`
      : "Open the related Contract";
  }

  // The header "Create Contract" button needs an open negotiation and at least one Term to contract;
  // it is also latched off while a create-contract modal round trip is in flight.
  get contractDisabled() {
    return !this.quoteId || !this.hasTerms || this.contracting;
  }

  handleAccountChange(event) {
    const recordId = event.detail && event.detail.recordId;
    this.selectedAccountId = recordId || null;
    // Reset the current negotiation when the account changes.
    this.quoteId = null;
    this.quoteName = "";
    this.negotiationStartDate = "";
    this.negotiationEndDate = "";
    this.terms = [];
    this.quoteOptions = [];
    this.contractId = null;
    this.contractNumber = "";
    this.errorMessage = "";
    if (this.selectedAccountId) {
      this.loadNegotiations();
    }
  }

  async loadNegotiations() {
    if (!this.selectedAccountId) {
      return;
    }
    try {
      const res = this._parse(
        await getNegotiationsForAccount({
          inputJson: JSON.stringify({ accountId: this.selectedAccountId })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage = res.errorMessage || "Unable to load negotiations.";
        return;
      }
      this.quoteOptions = (res.quotes || []).map((q) => ({
        label: q.name,
        value: q.id
      }));
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    }
  }

  handleQuoteSelect(event) {
    const quoteId = event.detail.value;
    if (quoteId) {
      this.openQuote(quoteId);
    }
  }

  async handleNewNegotiation() {
    if (!this.selectedAccountId) {
      return;
    }
    this.creating = true;
    this.errorMessage = "";
    try {
      const res = this._parse(
        await createNegotiation({
          inputJson: JSON.stringify({ accountId: this.selectedAccountId })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage =
          res.errorMessage || "Unable to create the negotiation.";
        return;
      }
      this._toast("Negotiation created", res.quoteName, "success");
      await this.loadNegotiations();
      this.quoteId = res.quoteId;
      // Default the header dates to a clean 1-year term: today through (today + 1 year - 1 day),
      // so the term spans exactly 365/366 days rather than 1 year + 1 day.
      const start = new Date();
      const end = new Date(start);
      end.setFullYear(end.getFullYear() + 1);
      end.setDate(end.getDate() - 1);
      await this._saveNegotiationDates(
        this._isoDate(start),
        this._isoDate(end)
      );
      await this.refreshState(true);
      // Broadcast the freshly-created (empty) negotiation so the rail + workspace switch to it.
      this._publishContext();
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.creating = false;
    }
  }

  handleQuoteNameInput(event) {
    this.quoteName = event.target.value;
  }

  get negotiationDatesDisabled() {
    return !this.quoteId || this.savingNegotiationDates;
  }

  // Header default Start/End Date: persisted on change via updateNegotiationDates. These only seed
  // NEW Term/fare lines as they're added (see buildTermLineFields/buildFareLineFields server-side) —
  // changing them never rewrites dates already on existing lines.
  handleNegotiationStartDateChange(event) {
    this._saveNegotiationDates(event.target.value, this.negotiationEndDate);
  }

  handleNegotiationEndDateChange(event) {
    this._saveNegotiationDates(this.negotiationStartDate, event.target.value);
  }

  async _saveNegotiationDates(startDate, endDate) {
    if (!this.quoteId) {
      return;
    }
    this.savingNegotiationDates = true;
    this.errorMessage = "";
    try {
      const res = this._parse(
        await updateNegotiationDates({
          inputJson: JSON.stringify({
            quoteId: this.quoteId,
            negotiationStartDate: startDate || null,
            negotiationEndDate: endDate || null
          })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage =
          res.errorMessage || "Unable to save the negotiation dates.";
        return;
      }
      this.negotiationStartDate = startDate || "";
      this.negotiationEndDate = endDate || "";
      // A standalone date edit updates the shared context. During New Negotiation the flow publishes
      // context once at the end (this.creating latched), so skip the redundant broadcast here.
      if (!this.creating) {
        this._publishContext();
      }
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.savingNegotiationDates = false;
    }
  }

  // "Apply to All Lines" needs an open negotiation with at least one Term line to touch, and is
  // latched off while a save is already in flight (including the per-field negotiation-date save,
  // since both write the same underlying dates).
  get applyDatesToAllLinesDisabled() {
    return (
      !this.quoteId ||
      !this.hasTerms ||
      this.savingNegotiationDates ||
      this.applyingDatesToAllLines
    );
  }

  // Mass-apply the header's Default Start/End Date to every Term and fare line already on the
  // negotiation (the per-field onchange handlers above only ever seed NEW lines as they're added).
  // Applies immediately — no confirmation — then reports how many lines were touched via toast.
  async handleApplyDatesToAllLines() {
    if (this.applyDatesToAllLinesDisabled) {
      return;
    }
    const lineIds = [];
    this.terms.forEach((term) => {
      lineIds.push(term.id);
      (term.fares || []).forEach((fare) => lineIds.push(fare.id));
    });
    if (!lineIds.length) {
      return;
    }
    this.applyingDatesToAllLines = true;
    this.errorMessage = "";
    try {
      const res = this._parse(
        await updateLineDiscountAndDates({
          inputJson: JSON.stringify({
            quoteId: this.quoteId,
            lines: lineIds.map((id) => ({
              id,
              startDate: this.negotiationStartDate || null,
              endDate: this.negotiationEndDate || null
            }))
          })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage =
          res.errorMessage || "Unable to apply the dates to all lines.";
        return;
      }
      const updatedCount = res.updatedCount || lineIds.length;
      this._toast(
        "Dates applied",
        `Updated ${updatedCount} line${updatedCount === 1 ? "" : "s"}.`,
        "success"
      );
      await this.refreshState(false);
      // Tell the workspace grid (and rail) that line data changed so they re-fetch the new dates.
      this._publishLinesChanged();
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.applyingDatesToAllLines = false;
    }
  }

  // Open the Create Contract modal (hosts the DL_CreateContractFromQuote screen flow) for the open
  // negotiation. On finish the flow returns isSuccess / contractId / errorMessage; we toast the
  // outcome, deep-link to the new Contract, refresh locally, and broadcast contractCreated so the
  // rail refreshes (contracting a quote can change downstream state). Cancel closes with no effect.
  async handleCreateContract() {
    if (this.contractDisabled) {
      return;
    }
    this.contracting = true;
    this.errorMessage = "";
    try {
      const result = await DlmCreateContractModal.open({
        quoteId: this.quoteId,
        summary: this._buildContractSummary(),
        size: "small",
        label: "Create Contract"
      });
      if (!result || result.status !== "finished") {
        return;
      }
      if (result.isSuccess) {
        this._toast("Contract created", "", "success");
        if (result.contractId) {
          this._openRecord("Contract", result.contractId);
        }
        await this.refreshState(false);
        this._publishContractCreated();
      } else {
        this.errorMessage =
          result.errorMessage || "Unable to create the contract.";
      }
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.contracting = false;
    }
  }

  // ---------- builder state ----------

  async openQuote(quoteId) {
    this.quoteId = quoteId;
    await this.refreshState(true);
    this._publishContext();
  }

  // Reload the header's own view of the negotiation from getBuilderState. Unlike the monolith this
  // tile doesn't own term selection, so it only keeps the quote/date/contract/term-list state it
  // needs for its own controls.
  async refreshState() {
    if (!this.quoteId) {
      return;
    }
    this.loadingState = true;
    this.errorMessage = "";
    try {
      const res = this._parse(await getBuilderState({ quoteId: this.quoteId }));
      if (res.isSuccess === false) {
        this.errorMessage =
          res.errorMessage || "Unable to load the negotiation.";
        return;
      }
      const quote = res.quote || {};
      this.quoteName = quote.name || this.quoteName;
      this.accountName = quote.accountName || this.accountName;
      this.negotiationStartDate = quote.negotiationStartDate || "";
      this.negotiationEndDate = quote.negotiationEndDate || "";
      this.terms = res.terms || [];
      this.contractId = res.contractId || null;
      this.contractNumber = res.contractNumber || "";

      // Deep-link back-fill: when opened straight into a quote (no account chosen yet), seed the
      // header's Account picker + negotiation list from the quote's own account.
      if (quote.accountId && this.selectedAccountId !== quote.accountId) {
        this.selectedAccountId = quote.accountId;
        this.loadNegotiations();
      }
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.loadingState = false;
    }
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

  // Format a JS Date as a local yyyy-MM-dd string (not toISOString, which is UTC and can shift the
  // date by a day depending on the browser's timezone offset).
  _isoDate(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, "0");
    const d = String(date.getDate()).padStart(2, "0");
    return `${y}-${m}-${d}`;
  }

  _errMessage(e) {
    return (
      (e && e.body && e.body.message) || (e && e.message) || "Unexpected error."
    );
  }

  _toast(title, message, variant) {
    this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
  }

  // Navigate to a record in the current tab via a relative Lightning URL so it resolves in
  // whatever domain the app is hosted.
  _openRecord(objectApiName, recordId) {
    window.open(`/lightning/r/${objectApiName}/${recordId}/view`, "_self");
  }

  // Build the Create Contract modal's summary from the already-loaded term state: each Term with its
  // negotiated discount, its fares (each with their own discount), and a total count of lines that
  // will be saved as contracted prices.
  _buildContractSummary() {
    let lineCount = 0;
    const terms = this.terms.map((t) => {
      lineCount += 1;
      const fares = (t.fares || []).map((f) => {
        lineCount += 1;
        return {
          id: f.id,
          name: f.productName || f.productCode || "Fare",
          discountText: this._discountText(f.discount)
        };
      });
      return {
        id: t.id,
        name: t.displayName || t.productName || "Term",
        discountText: this._discountText(t.discount),
        fares,
        hasFares: fares.length > 0
      };
    });
    return {
      quoteName: this.quoteName,
      termCount: terms.length,
      lineCount,
      terms
    };
  }

  _discountText(discount) {
    const hasDiscount =
      discount !== null && discount !== undefined && Number(discount) > 0;
    return hasDiscount ? `${discount}% off` : "No discount";
  }
}
