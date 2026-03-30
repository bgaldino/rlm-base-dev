import { LightningElement, api } from "lwc";
import { NavigationMixin } from "lightning/navigation";

/**
 * Order Redirect Flow Screen Component
 * @property {string} orderId - Order Id to redirect to
 * @property {string} quoteId - Quote Id to use for the list view
 * @property {boolean} disableAutoRedirect - Disable automatic redirect for debugging
 * @description
 * - Exposed to flows (lightning__FlowScreen)
 * - Accepts an Order Id and navigates to the Order record page on render
 * - Shows a minimal "Redirecting..." state and handles errors
 */
export default class RlmOrderRedirect extends NavigationMixin(LightningElement) {
  /**
   * Public property to receive Order Id from Flow
   * The Flow should pass the Id of the created Order into this property.
   */
  @api orderId;
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
    if (!this.orderId && !this.quoteId) {
      this.errorMessage = "Order Id or Quote Id is missing. Cannot redirect.";
      return;
    }
    this.hasNavigated = true;
    // Defer navigation to next microtask to ensure DOM is ready
    Promise.resolve().then(() => {
      try {
        if (this.quoteId) {
          this[NavigationMixin.Navigate]({
            type: "standard__recordRelationshipPage",
            attributes: {
              recordId: this.quoteId,
              objectApiName: "Quote",
              relationshipApiName: "Orders",
              actionName: "view"
            }
          });
        } else {
          this[NavigationMixin.Navigate]({
            type: "standard__recordPage",
            attributes: {
              recordId: this.orderId,
              objectApiName: "Order",
              actionName: "view"
            }
          });
        }
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
