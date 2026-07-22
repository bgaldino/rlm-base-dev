import { api, track } from "lwc";
import LightningModal from "lightning/modal";
import getTermLibrary from "@salesforce/apex/RLM_DeltaTermBuilderController.getTermLibrary";
import addTermFromTemplate from "@salesforce/apex/RLM_DeltaTermBuilderController.addTermFromTemplate";

/**
 * Delta "Term Library" modal. The Terms rail opens this with
 * DlmTermLibraryModal.open({ quoteId, size: 'medium', label: 'Term Library' }). On open it loads the
 * pre-defined term templates (getTermLibrary) and lists them with their scope chips + fare classes.
 * Choosing one calls addTermFromTemplate, which creates a real DL-TERM line, stamps the template's
 * scope attributes, and attaches its fare classes. The modal stays open so the rep can add several
 * Terms in one sitting; the footer button ("Done" once anything is added) reports the running totals
 * to the rail on close. The rep can still dismiss via ESC/X — the rail refreshes after any close, so
 * added Terms are never left stale even without a totals payload. Cancelling before any add closes
 * with no effect.
 */
export default class DlmTermLibraryModal extends LightningModal {
  @api quoteId;

  @track templates = [];
  loading = true;
  addingId = null; // productId currently being added (drives per-row spinner + disable)
  errorMessage = "";
  searchKey = ""; // lower-cased, trimmed search filter (name / fares / scope values)

  // Running totals across this modal session; reported to the rail on Close.
  addedCount = 0;
  addedFareCount = 0;
  lastTermLineId = null;

  connectedCallback() {
    this.loadLibrary();
  }

  get hasTemplates() {
    return this.templates.length > 0;
  }

  // The templates matching the current search. Matches template name, fare summary, and scope chip
  // values so a rep can find a term by route/market/fare, not just its name. Empty search shows all.
  get visibleTemplates() {
    const key = this.searchKey;
    if (!key) {
      return this.templates;
    }
    return this.templates.filter((t) => this._matches(t, key));
  }

  get hasVisibleTemplates() {
    return this.visibleTemplates.length > 0;
  }

  // A search is entered but filtered every template out — show the "no matches" note (distinct from
  // showEmpty, which means the library itself is empty).
  get showNoMatches() {
    return this.hasTemplates && !!this.searchKey && !this.hasVisibleTemplates;
  }

  get busy() {
    return !!this.addingId;
  }

  get hasAdds() {
    return this.addedCount > 0;
  }

  // Running confirmation shown while the modal stays open across multiple adds.
  get addedSummary() {
    const word = this.addedCount === 1 ? "Term" : "Terms";
    return `${this.addedCount} ${word} added to this negotiation.`;
  }

  // Once the rep has added something, the footer button reads "Done" — it both closes the modal and
  // hands the rail the running totals.
  get closeLabel() {
    return this.hasAdds ? "Done" : "Close";
  }

  get closeVariant() {
    return this.hasAdds ? "brand" : "neutral";
  }

  get showEmpty() {
    return !this.loading && !this.hasTemplates && !this.errorMessage;
  }

  // Load the library once on open. getTermLibrary is cacheable, but we call it imperatively so the
  // modal controls its own loading/error UI (a wire would fire before the spinner is shown).
  async loadLibrary() {
    this.loading = true;
    this.errorMessage = "";
    try {
      const res = this._parse(await getTermLibrary());
      if (res.isSuccess === false) {
        this.errorMessage =
          res.errorMessage || "Unable to load the term library.";
        return;
      }
      this.templates = (res.templates || []).map((t) => this._decorate(t));
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.loading = false;
    }
  }

  // Shape a raw template for the list: iterable scope chips (with keys), a joined fare summary, and
  // the per-row adding/disabled flags the buttons bind to.
  _decorate(t) {
    const chips = t.scopeChips || [];
    const fareNames = t.fareNames || [];
    return {
      productId: t.productId,
      name: t.name,
      description: t.description,
      hasScope: chips.length > 0,
      scopeChips: chips.map((c, i) => ({
        key: (c.code || "chip") + i,
        label: c.label,
        value: c.value
      })),
      hasFares: fareNames.length > 0,
      fareText: fareNames.join(", "),
      adding: this.addingId === t.productId,
      disabled: this.busy
    };
  }

  // Re-derive the per-row flags after addingId changes (LWC re-renders on the reassignment).
  _syncRowFlags() {
    this.templates = this.templates.map((t) => ({
      ...t,
      adding: this.addingId === t.productId,
      disabled: this.busy
    }));
  }

  async handleAdd(event) {
    const productId = event.currentTarget.dataset.id;
    if (!productId || this.busy || !this.quoteId) {
      return;
    }
    this.addingId = productId;
    this.errorMessage = "";
    this._syncRowFlags();
    try {
      const res = this._parse(
        await addTermFromTemplate({
          inputJson: JSON.stringify({
            quoteId: this.quoteId,
            templateProductId: productId
          })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage = res.errorMessage || "Unable to add the Term.";
        return;
      }
      // Keep the modal open: tally this add and let the rep keep adding. The footer reports these
      // totals on Close, and the rail refreshes after any close (including ESC/X) so the additions
      // aren't lost even when the open() promise resolves with no payload.
      this.addedCount += 1;
      this.addedFareCount += res.addedFareCount || 0;
      this.lastTermLineId = res.termLineId || this.lastTermLineId;
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.addingId = null;
      this._syncRowFlags();
    }
  }

  handleSearch(event) {
    this.searchKey = (event.target.value || "").trim().toLowerCase();
  }

  handleClose() {
    if (this.addedCount > 0) {
      this.close({
        status: "finished",
        addedCount: this.addedCount,
        addedFareCount: this.addedFareCount,
        lastTermLineId: this.lastTermLineId
      });
      return;
    }
    this.close({ status: "cancel" });
  }

  // ---------- helpers ----------

  // True when the search key appears in the template's name, fare summary, or any scope chip value.
  _matches(t, key) {
    if ((t.name || "").toLowerCase().includes(key)) {
      return true;
    }
    if ((t.fareText || "").toLowerCase().includes(key)) {
      return true;
    }
    return (t.scopeChips || []).some((c) =>
      (c.value || "").toLowerCase().includes(key)
    );
  }

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
}
