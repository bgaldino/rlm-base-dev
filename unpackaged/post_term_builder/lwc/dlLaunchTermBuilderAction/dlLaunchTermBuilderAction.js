import { LightningElement, api } from "lwc";
import { NavigationMixin } from "lightning/navigation";
import { CloseActionScreenEvent } from "lightning/actions";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import createNegotiation from "@salesforce/apex/RLM_DeltaTermBuilderController.createNegotiation";

/**
 * Account quick action: creates a new Delta negotiation (Quote) for the Account via
 * RLM_DeltaTermBuilderController.createNegotiation, then navigates straight into the standalone
 * Term Builder app with that negotiation already open (?c__quoteId=...) — skipping the manual
 * "New Negotiation" step inside Term Builder.
 *
 * Auto-launches on open, mirroring c/dlConfigureProductAction's modal placement: a ScreenAction's
 * recordId can arrive after connectedCallback, so the setter (not connectedCallback alone) kicks
 * off the create+navigate exactly once.
 */
export default class DlLaunchTermBuilderAction extends NavigationMixin(LightningElement) {
  _recordId;
  _started = false;

  @api
  get recordId() {
    return this._recordId;
  }
  set recordId(value) {
    this._recordId = value;
    this.maybeStart();
  }

  @api objectApiName;

  loading = false;
  errorMessage = "";

  connectedCallback() {
    this.maybeStart();
  }

  get hasError() {
    return !!this.errorMessage;
  }

  maybeStart() {
    if (this._recordId && !this._started) {
      this._started = true;
      this.launch();
    }
  }

  async launch() {
    this.loading = true;
    this.errorMessage = "";
    try {
      const res = this._parse(
        await createNegotiation({
          inputJson: JSON.stringify({ accountId: this._recordId })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage =
          res.errorMessage || "Unable to create the negotiation.";
        return;
      }
      this._toast("Negotiation created", res.quoteName, "success");
      this._navigateToTermBuilder(res.quoteId);
      this._closeAction();
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.loading = false;
    }
  }

  handleClose() {
    this._closeAction();
  }

  // Navigate straight to the Term Builder tab within whatever app is currently open (it's added to
  // the org's Lightning apps directly, so no app-switch is needed). Forcing a standard__app switch
  // to a standalone appTarget here caused "The app you're trying to view is invalid or inaccessible"
  // — the platform rejected the app-switch and fell back to the default app before landing on this
  // same tab, so the switch was both unnecessary and noisy.
  _navigateToTermBuilder(quoteId) {
    this[NavigationMixin.Navigate]({
      type: "standard__navItemPage",
      attributes: { apiName: "DL_Term_Builder" },
      state: { c__quoteId: quoteId }
    });
  }

  _closeAction() {
    this.dispatchEvent(new CloseActionScreenEvent());
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
