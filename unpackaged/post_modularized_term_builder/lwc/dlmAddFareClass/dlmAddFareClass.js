import { LightningElement, api, track } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import getFareChoices from "@salesforce/apex/RLM_DeltaTermBuilderController.getFareChoices";
import addFareClassesToTerm from "@salesforce/apex/RLM_DeltaTermBuilderController.addFareClassesToTerm";

/**
 * The primary custom "Add Fare Class" path for c/dlTermBuilder. Lists the fare-class products
 * (classification PC-DL-FARE, resolved server-side) with a valid active PricebookEntry on the
 * quote's price book. A rep checks one or more products and clicks the single top "Add Selected"
 * button; that posts one Quantity-1 child QLI + a QuoteLineRelationship per selected fare under the
 * selected Term in ONE Place Sales Transaction (RLM_DeltaTermBuilderController.addFareClassesToTerm).
 *
 * Duplicate fares are allowed by design: each add is an independent Quantity-1 line, so previously
 * added fares are NOT disabled and the same fare may be added again. On success it emits a single
 * composed `fareadded` event ({ termLineId, addedLineIds }) so the host refreshes the rail + grid.
 *
 * Public API:
 *   @api quoteId      (required) — the negotiation quote.
 *   @api termLineId   (required) — the selected Term root the fares hang under. Changing it reloads
 *                                  nothing (fare choices are quote-scoped, not term-scoped) but
 *                                  re-targets the Add.
 */
export default class DlmAddFareClass extends LightningElement {
  @api quoteId;

  _termLineId;
  @api
  get termLineId() {
    return this._termLineId;
  }
  set termLineId(value) {
    this._termLineId = value;
  }

  @track fares = [];
  // Selected productIds. Sets aren't reactive on mutation in LWC, so reassign on every change.
  @track selectedIds = new Set();
  loading = false;
  // True while an "Add Selected" round trip is in flight (drives the button's disabled/spinner).
  adding = false;
  errorMessage = "";
  _loaded = false;

  connectedCallback() {
    if (this.quoteId && !this._loaded) {
      this.load();
    }
  }

  get hasFares() {
    return this.fares.length > 0;
  }

  get showEmpty() {
    return !this.loading && !this.errorMessage && this.fares.length === 0;
  }

  // No Term selected ⇒ Add is disabled everywhere (the fare would have nothing to hang under).
  get addDisabledReason() {
    if (!this._termLineId) {
      return "Select a Term first.";
    }
    return "";
  }

  get addBlocked() {
    return !this._termLineId;
  }

  @api
  async reload() {
    await this.load();
  }

  async load() {
    if (!this.quoteId) {
      return;
    }
    this._loaded = true;
    this.loading = true;
    this.errorMessage = "";
    try {
      const res = this._parse(
        await getFareChoices({
          inputJson: JSON.stringify({ quoteId: this.quoteId })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage = res.errorMessage || "Unable to load fare classes.";
        this.fares = [];
        return;
      }
      this.fares = (res.fares || []).map((f) => this._mapFare(f));
      // Drop any stale selection that no longer maps to a listed fare.
      this._pruneSelection();
    } catch (e) {
      this.errorMessage = this._errMessage(e);
      this.fares = [];
      this.selectedIds = new Set();
    } finally {
      this.loading = false;
    }
  }

  _mapFare(f) {
    return {
      productId: f.productId,
      productName: f.productName,
      productCode: f.productCode,
      pbeId: f.pbeId
    };
  }

  // Rows carry a computed `selected` flag derived here so the template stays declarative.
  get rows() {
    return this.fares.map((f) => ({
      ...f,
      selected: this.selectedIds.has(f.productId)
    }));
  }

  get selectedCount() {
    return this.selectedIds.size;
  }

  get hasSelection() {
    return this.selectedIds.size > 0;
  }

  // "N selected" hint next to the Add Selected button (empty when nothing is checked).
  get selectionLabel() {
    return this.hasSelection ? `${this.selectedCount} selected` : "";
  }

  // Add Selected needs a Term to hang the fares under, at least one checked fare, and no add in
  // flight.
  get addSelectedDisabled() {
    return this.addBlocked || !this.hasSelection || this.adding;
  }

  // Select-all checkbox reflects "every listed fare is checked" and drives a bulk toggle.
  get allSelected() {
    return this.fares.length > 0 && this.selectedIds.size === this.fares.length;
  }

  handleCheckboxChange(event) {
    const productId = event.target.dataset.productId;
    if (!productId) {
      return;
    }
    const next = new Set(this.selectedIds);
    if (event.target.checked) {
      next.add(productId);
    } else {
      next.delete(productId);
    }
    this.selectedIds = next;
  }

  handleSelectAll(event) {
    this.selectedIds = event.target.checked
      ? new Set(this.fares.map((f) => f.productId))
      : new Set();
  }

  async handleAddSelected() {
    if (this.addSelectedDisabled) {
      return;
    }
    // Collect the checked fares in list order as { pbeId, productId } entries for the batch add.
    const fares = this.fares
      .filter((f) => this.selectedIds.has(f.productId))
      .map((f) => ({ pbeId: f.pbeId, productId: f.productId }));
    if (!fares.length) {
      return;
    }
    this.adding = true;
    this.errorMessage = "";
    try {
      const res = this._parse(
        await addFareClassesToTerm({
          inputJson: JSON.stringify({
            quoteId: this.quoteId,
            termLineId: this._termLineId,
            fares
          })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage =
          res.errorMessage || "Unable to add the selected fare classes.";
        return;
      }
      const added = res.addedCount || fares.length;
      this._toast(
        added > 1 ? `${added} fares added` : "Fare added",
        added > 1
          ? `${added} fare classes added to the Term.`
          : "Fare class added to the Term.",
        "success"
      );
      this.selectedIds = new Set();
      this.dispatchEvent(
        new CustomEvent("fareadded", {
          detail: {
            termLineId: this._termLineId,
            addedLineIds: res.addedLineIds || []
          },
          bubbles: true,
          composed: true
        })
      );
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.adding = false;
    }
  }

  // Drop selected ids that no longer correspond to a listed fare (e.g. after a reload).
  _pruneSelection() {
    if (this.selectedIds.size === 0) {
      return;
    }
    const live = new Set(this.fares.map((f) => f.productId));
    const next = new Set();
    this.selectedIds.forEach((id) => {
      if (live.has(id)) {
        next.add(id);
      }
    });
    this.selectedIds = next;
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

  _toast(title, message, variant) {
    this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
  }
}
