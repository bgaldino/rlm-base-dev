import { LightningElement, api } from "lwc";
import { NavigationMixin } from "lightning/navigation";
import { CloseActionScreenEvent } from "lightning/actions";

/**
 * Quote quick action: navigates straight into the standalone Term Builder app with this
 * Quote already open (?c__quoteId=...) — no negotiation creation needed since the Quote
 * already exists, unlike c/dlLaunchTermBuilderAction on Account.
 *
 * Auto-launches on open: a ScreenAction's recordId can arrive after connectedCallback, so
 * the setter (not connectedCallback alone) kicks off the navigate exactly once.
 */
export default class DlOpenTermBuilderAction extends NavigationMixin(LightningElement) {
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

  connectedCallback() {
    this.maybeStart();
  }

  maybeStart() {
    if (this._recordId && !this._started) {
      this._started = true;
      this._navigateToTermBuilder(this._recordId);
      this._closeAction();
    }
  }

  // See c/dlLaunchTermBuilderAction: no standard__app switch here — the app is added to
  // the org's Lightning apps directly, so navigating to the tab within the current app works.
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
}
