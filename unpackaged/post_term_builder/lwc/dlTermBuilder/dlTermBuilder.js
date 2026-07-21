import { LightningElement, api, track, wire } from "lwc";
import { CurrentPageReference } from "lightning/navigation";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { loadStyle } from "lightning/platformResourceLoader";
import DlCreateContractModal from "c/dlCreateContractModal";
import noHeader from "@salesforce/resourceUrl/DL_Term_Builder_NoHeader";
import DL_TERM_BUILDER_EMBLEM from "@salesforce/resourceUrl/DL_Term_Builder_Emblem";
import createNegotiation from "@salesforce/apex/RLM_DeltaTermBuilderController.createNegotiation";
import getNegotiationsForAccount from "@salesforce/apex/RLM_DeltaTermBuilderController.getNegotiationsForAccount";
import getBuilderState from "@salesforce/apex/RLM_DeltaTermBuilderController.getBuilderState";
import addTerm from "@salesforce/apex/RLM_DeltaTermBuilderController.addTerm";
import updateNegotiationDates from "@salesforce/apex/RLM_DeltaTermBuilderController.updateNegotiationDates";
import updateLineDiscountAndDates from "@salesforce/apex/RLM_DeltaLineController.updateLineDiscountAndDates";

// Route-attribute codes surfaced in the Term workspace's inline attribute picker, in display order.
// These are the PC-DL-TERM informational (non-price-impacting) attributes; fares have none.
const TERM_ATTRIBUTE_CODES =
  "DL_Origin,DL_Destination,DL_Directionality,DL_Measure,DL_RequirementValue,DL_SpecialConditions";

/**
 * Delta "Term Builder" — the standalone app orchestrator (placed on the DL_Term_Builder AppPage).
 * A rep selects an Account, starts a negotiation Quote, adds route-based Terms (DL-TERM bundles),
 * sets each Term's route attributes, and adds fare-class products under the selected Term.
 *
 * Composition (all children are copies owned by this package):
 *   - header: lightning-record-picker (Account) + New Negotiation + existing-Quote combobox +
 *     editable Quote name + negotiation Start/End Date defaults (seed new Term/fare lines only —
 *     see updateNegotiationDates).
 *   - terms rail: c/dlTermCard chips (one per Term) + a bare inline "Add Term" bar (the DL-TERM
 *     product is resolved server-side, so no catalog/search UI is needed).
 *   - workspace: c/dlQuoteLineGrid scoped to the selected Term (scopeRootLineId) + c/dlAddFareClass.
 *
 * Server contract: RLM_DeltaTermBuilderController's JSON-in/JSON-out methods. getBuilderState is the
 * single bulk round trip that feeds the rail, the catalog/category refs for the finder, and the
 * selected-Term default. This component owns selection + orchestration only; children own their I/O.
 */
export default class DlTermBuilder extends LightningElement {
  // Optional URL preselect: a future Account-page button can deep-link with ?c__accountId=...
  @api accountId;
  // Optional deep-link straight into an existing negotiation: ?c__quoteId=... (or the design
  // property) opens that Quote on load and back-fills its Account into the header.
  @api quoteRecordId;

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
  catalogId;
  categoryId;

  selectedTermId;
  // When the open negotiation is already related to a Contract, the server returns its id + number;
  // the header then offers "View Contract" instead of a "Create Contract" that would only fail.
  contractId = null;
  contractNumber = "";
  loadingState = false;
  creating = false;
  contracting = false;
  addingTerm = false;
  addTermCount = 1;
  errorMessage = "";

  // Term-attribute codes forwarded to the scoped grid's inline pickers.
  attributeCodes = TERM_ATTRIBUTE_CODES;

  // Delta triangle emblem shown in the header, replacing the CSS triangle stand-in.
  emblemUrl = DL_TERM_BUILDER_EMBLEM;

  _pageStateApplied = false;

  // Pick up ?c__quoteId= / ?c__accountId= from URL state once. A quoteId wins: it opens the quote
  // directly and back-fills its account. Otherwise an accountId just preselects the account.
  @wire(CurrentPageReference)
  applyPageReference(pageRef) {
    if (pageRef && !this._pageStateApplied) {
      const quoteFromUrl = pageRef.state && pageRef.state.c__quoteId;
      const acctFromUrl = pageRef.state && pageRef.state.c__accountId;
      if (quoteFromUrl) {
        this._pageStateApplied = true;
        this.openQuote(quoteFromUrl);
      } else if (acctFromUrl) {
        this._pageStateApplied = true;
        this.selectedAccountId = acctFromUrl;
        this.loadNegotiations();
      }
    }
  }

  connectedCallback() {
    // Hide the standard flexipage page-header band (a redundant "Term Builder" title + tab icon)
    // so only this component's navy Delta header shows. Failure is non-fatal — ignore and continue.
    loadStyle(this, noHeader).catch(() => {
      /* header-hiding stylesheet is cosmetic; ignore load failures */
    });
    // A design-property quoteId deep-links straight into that negotiation; else an accountId
    // preselects the account. The URL-state wire (above) takes precedence when present.
    if (this.quoteRecordId && !this.quoteId) {
      this.openQuote(this.quoteRecordId);
    } else if (this.accountId && !this.selectedAccountId) {
      this.selectedAccountId = this.accountId;
      this.loadNegotiations();
    }
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

  // Relative Lightning URL to the related Contract record, for the header "View Contract" link.
  get contractRecordUrl() {
    return this.contractId
      ? `/lightning/r/Contract/${this.contractId}/view`
      : null;
  }

  // Title/label for the "View Contract" link, including the contract number when known.
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
    this.selectedTermId = null;
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
      await this._saveNegotiationDates(this._isoDate(start), this._isoDate(end));
      await this.refreshState(true);
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
      this._refreshGrid();
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.applyingDatesToAllLines = false;
    }
  }

  // Open the Create Contract modal (hosts the DL_CreateContractFromQuote screen flow) for the open
  // negotiation. On finish the flow returns isSuccess / contractId / errorMessage; we toast the
  // outcome, deep-link to the new Contract, and refresh the rail (contracting a quote can change
  // downstream state). Cancel closes with no side effect.
  async handleCreateContract() {
    if (this.contractDisabled) {
      return;
    }
    this.contracting = true;
    this.errorMessage = "";
    try {
      const result = await DlCreateContractModal.open({
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
  }

  // Reload the whole rail from getBuilderState. When selectFirst is true (a fresh open) the default
  // selection follows the server; otherwise the current selection is preserved if it still exists.
  async refreshState(selectFirst) {
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
      this.catalogId = res.catalogId;
      this.categoryId = res.categoryId;
      this.terms = res.terms || [];
      this.contractId = res.contractId || null;
      this.contractNumber = res.contractNumber || "";

      // Deep-link back-fill: when opened straight into a quote (no account chosen yet), seed the
      // header's Account picker + negotiation list from the quote's own account.
      if (quote.accountId && this.selectedAccountId !== quote.accountId) {
        this.selectedAccountId = quote.accountId;
        this.loadNegotiations();
      }

      // Resolve the selected Term: keep the current one if still present, else fall back to the
      // server default / first Term.
      const ids = new Set(this.terms.map((t) => t.id));
      if (
        selectFirst ||
        !this.selectedTermId ||
        !ids.has(this.selectedTermId)
      ) {
        this.selectedTermId =
          res.selectedTermId || (this.terms[0] && this.terms[0].id) || null;
      }
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.loadingState = false;
    }
  }

  // ---------- terms rail ----------

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

  get selectedTerm() {
    return this.terms.find((t) => t.id === this.selectedTermId) || null;
  }

  get selectedTermName() {
    const t = this.selectedTerm;
    return t ? t.displayName : "";
  }

  get showWorkspace() {
    return !!this.quoteId && !!this.selectedTermId;
  }

  get addTermDisabled() {
    return !this.quoteId || this.addingTerm;
  }

  handleTermSelect(event) {
    this.selectedTermId = event.detail.termId;
  }

  handleAddTermCountChange(event) {
    // Clamp to [1, 10]; a blank/NaN entry falls back to 1.
    const raw = parseInt(event.target.value, 10);
    this.addTermCount = Number.isNaN(raw) ? 1 : Math.min(10, Math.max(1, raw));
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

  // Reload the rail and auto-select the newest Term (the one not previously present). The scoped
  // grid's own getQuoteLines wire is keyed on quoteId, which doesn't change here, so it must be
  // told explicitly to refetch — otherwise it re-scopes to the new Term against stale cached lines
  // that don't include it yet, rendering an empty "No quote lines yet" until a full page reload.
  async handleTermAdded() {
    const before = new Set(this.terms.map((t) => t.id));
    await this.refreshState(false);
    const added = this.terms.find((t) => !before.has(t.id));
    if (added) {
      this.selectedTermId = added.id;
    } else if (!this.selectedTermId && this.terms.length) {
      this.selectedTermId = this.terms[0].id;
    }
    this._refreshGrid();
  }

  // ---------- workspace: grid + fares ----------

  // A fare was added under the selected Term: refresh the rail counts and the scoped grid.
  async handleFareAdded() {
    await this.refreshState(false);
    this._refreshGrid();
  }

  // The grid edited/removed/renamed a line: refresh the rail (name + counts may change) but leave
  // the grid to manage its own refresh (it already called refreshApex).
  handleLinesUpdated() {
    this.refreshState(false);
  }

  _refreshGrid() {
    const grid = this.template.querySelector("c-dl-quote-line-grid");
    if (grid) {
      grid.refresh();
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

  // Build the Create Contract modal's summary from the already-loaded rail state: each Term with its
  // negotiated discount, its fares (each with their own discount), and a total count of lines that
  // will be saved as contracted prices. Every Term + fare line is contracted (the DISCOUNT_ONLY path
  // saves each line's discount, defaulting to 0% where none was negotiated), so lineCount is the full
  // Term + fare line count — matching what the service actually creates.
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
