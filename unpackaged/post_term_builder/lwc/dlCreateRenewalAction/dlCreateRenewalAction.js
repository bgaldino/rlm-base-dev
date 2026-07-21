import { LightningElement, api } from "lwc";
import { NavigationMixin } from "lightning/navigation";
import { CloseActionScreenEvent } from "lightning/actions";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import createRenewalFromContractViaAssets from "@salesforce/apex/RLM_DeltaTermBuilderController.createRenewalFromContractViaAssets";

/**
 * Contract quick action: renews the Contract's activated Assets into a new Renewal negotiation via
 * the STANDARD asset-based renewal (RLM_DeltaTermBuilderController.createRenewalFromContractViaAssets
 * → initiateRenewal), then navigates straight into the standalone Term Builder app with that renewal
 * already open (?c__quoteId=...). Mirrors c/dlLaunchTermBuilderAction: a ScreenAction's recordId can
 * arrive after connectedCallback, so the setter (not connectedCallback alone) kicks off the
 * renew+navigate exactly once.
 */
export default class DlCreateRenewalAction extends NavigationMixin(LightningElement) {
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
        await createRenewalFromContractViaAssets({
          inputJson: JSON.stringify({ contractId: this._recordId })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage = res.errorMessage || "Unable to create the renewal.";
        return;
      }
      this._toast("Renewal created", res.renewalName, "success");
      this._navigateToTermBuilder(res.renewalQuoteId);
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

  // Navigate straight to the Term Builder tab within whatever app is currently open, opening the
  // new renewal negotiation (?c__quoteId=...). Same pattern as c/dlLaunchTermBuilderAction — a
  // standard__app switch to the standalone appTarget was rejected by the platform there.
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
