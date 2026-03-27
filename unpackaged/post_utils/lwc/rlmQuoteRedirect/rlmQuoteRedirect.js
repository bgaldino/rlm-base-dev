import { LightningElement, api } from "lwc";
import { NavigationMixin } from "lightning/navigation";

/**
 * Quote Redirect Flow Screen Component
 * @property {string} quoteId - Quote Id to redirect to
 * @property {boolean} disableAutoRedirect - Disable automatic redirect for debugging
 * @description
 * - Exposed to flows (lightning__FlowScreen)
 * - Accepts a Quote Id and navigates to the Quote record page on render
 * - Shows a minimal "Redirecting..." state and handles errors
 */
export default class RlmQuoteRedirect extends NavigationMixin(LightningElement) {
  /**
   * Public property to receive Quote Id from Flow
   * The Flow should pass the Id of the created Quote into this property.
   */
  @api quoteId;

  /**
   * Optional: allow disabling automatic redirect for debugging
   */
  @api disableAutoRedirect = false;

  hasNavigated = false;
  errorMessage = null;

  renderedCallback() {
    if (this.hasNavigated || this.disableAutoRedirect) {
      return;
    }
    if (!this.quoteId) {
      this.errorMessage = "Quote Id is missing. Cannot redirect.";
      return;
    }
    this.hasNavigated = true;
    // Defer navigation to next microtask to ensure DOM is ready
    Promise.resolve().then(() => {
      try {
        this[NavigationMixin.Navigate]({
          type: "standard__recordPage",
          attributes: {
            recordId: this.quoteId,
            objectApiName: "Quote",
            actionName: "view"
          }
        });
      } catch (e) {
        this.errorMessage =
          e?.message ?? "An unexpected error occurred during navigation.";
      }
    });
  }

  get hasError() {
    return Boolean(this.errorMessage);
  }
}