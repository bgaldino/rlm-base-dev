import { LightningElement, api, track } from "lwc";
import { CloseActionScreenEvent } from "lightning/actions";
import getOrderInfo from "@salesforce/apex/RLM_PreProcessOrderController.getOrderInfo";
import startPreprocess from "@salesforce/apex/RLM_PreProcessOrderController.startPreprocess";
import getStatus from "@salesforce/apex/RLM_PreProcessOrderController.getStatus";
import activateOrder from "@salesforce/apex/RLM_PreProcessOrderController.activateOrder";

const POLL_INTERVAL_MS = 2500;
const MAX_POLLS = 120; // ~5 minutes

export default class RlmPreProcessOrderAction extends LightningElement {
  _recordId;
  _infoLoaded = false;

  // recordId can arrive after connectedCallback for screen actions; load when it's set.
  @api
  get recordId() {
    return this._recordId;
  }
  set recordId(value) {
    this._recordId = value;
    this.maybeLoad();
  }

  @track loading = true;
  @track running = false;
  @track orderNumber;
  @track orderStatus;
  @track preprocessingStatus;
  @track isLargeDeal = false;
  @track validationComplete = false;
  @track activated = false;
  @track autoActivate = false;
  @track message;
  @track messageVariant = "info"; // info | success | error
  @track progressText;

  _requestId;
  _pollHandle;
  _pollCount = 0;

  connectedCallback() {
    this.maybeLoad();
  }

  disconnectedCallback() {
    this.clearPolling();
  }

  maybeLoad() {
    if (this._recordId && !this._infoLoaded) {
      this._infoLoaded = true;
      this.loadInfo();
    }
  }

  async loadInfo() {
    this.loading = true;
    try {
      const res = JSON.parse(await getOrderInfo({ orderId: this.recordId }));
      if (!res.success) {
        this.setMessage(res.errorMessage || "Could not load order.", "error");
        return;
      }
      this.orderNumber = res.orderNumber;
      this.orderStatus = res.status;
      this.preprocessingStatus = res.preprocessingStatus;
      this.isLargeDeal = res.isLargeDeal === true;
      this.validationComplete = res.validationComplete === true;
      this.activated = res.activated === true;
      this.deriveInitialMessage();
    } catch (e) {
      this.setMessage(this.errText(e), "error");
    } finally {
      this.loading = false;
    }
  }

  deriveInitialMessage() {
    if (this.activated) {
      this.setMessage("This order is already activated.", "success");
    } else if (!this.isLargeDeal) {
      this.setMessage(
        "This order is not a large deal. Use the standard Activate button — no preprocessing is required.",
        "info",
      );
    } else if (this.validationComplete) {
      this.setMessage(
        "This order is already preprocessed and ready to activate.",
        "success",
      );
    } else {
      this.setMessage(
        "Large-deal orders must be preprocessed before activation. Click Prepare for Activation to run validation.",
        "info",
      );
    }
  }

  get showPrepareButton() {
    return this.isLargeDeal && !this.activated && !this.validationComplete && !this.running;
  }

  get showActivateButton() {
    return !this.activated && this.validationComplete && !this.running;
  }

  get prepareDisabled() {
    return this.running || this.loading;
  }

  get statusBadge() {
    return this.preprocessingStatus || "—";
  }

  handleAutoActivateChange(event) {
    this.autoActivate = event.target.checked;
  }

  async handlePrepare() {
    this.clearPolling();
    this.running = true;
    this.progressText = "Submitting preprocessing job…";
    this.setMessage("Preprocessing started. This runs asynchronously.", "info");
    try {
      const res = JSON.parse(await startPreprocess({ orderId: this.recordId }));
      if (!res.success) {
        this.running = false;
        this.setMessage(res.errorMessage || "Preprocessing failed to start.", "error");
        return;
      }
      this._requestId = res.requestId;
      this._pollCount = 0;
      this.progressText = "Waiting for validation to complete…";
      this.startPolling();
    } catch (e) {
      this.running = false;
      this.setMessage(this.errText(e), "error");
    }
  }

  startPolling() {
    this._pollHandle = setInterval(() => this.poll(), POLL_INTERVAL_MS);
  }

  clearPolling() {
    if (this._pollHandle) {
      clearInterval(this._pollHandle);
      this._pollHandle = undefined;
    }
  }

  async poll() {
    this._pollCount += 1;
    if (this._pollCount > MAX_POLLS) {
      this.clearPolling();
      this.running = false;
      this.setMessage(
        "Preprocessing is taking longer than expected. The job may still finish — reopen this action to check, then activate.",
        "error",
      );
      return;
    }
    try {
      const res = JSON.parse(
        await getStatus({ orderId: this.recordId, requestId: this._requestId }),
      );
      if (!res.success) {
        return; // transient; keep polling
      }
      this.preprocessingStatus = res.preprocessingStatus;
      this.orderStatus = res.orderStatus;
      if (res.failed) {
        this.clearPolling();
        this.running = false;
        this.setMessage(
          "Preprocessing failed (status: " + (res.trackerStatus || "unknown") + "). Review the order data and try again.",
          "error",
        );
        return;
      }
      if (res.ready) {
        this.clearPolling();
        this.validationComplete = true;
        if (this.autoActivate) {
          await this.doActivate();
        } else {
          this.running = false;
          this.progressText = undefined;
          this.setMessage("Validation complete. The order is ready to activate.", "success");
        }
      }
    } catch (e) {
      // Keep polling on transient errors.
    }
  }

  async handleActivate() {
    this.running = true;
    await this.doActivate();
  }

  async doActivate() {
    this.progressText = "Activating order…";
    try {
      const res = JSON.parse(await activateOrder({ orderId: this.recordId }));
      this.running = false;
      this.progressText = undefined;
      if (!res.success) {
        this.setMessage(res.errorMessage || "Activation failed.", "error");
        return;
      }
      this.activated = true;
      this.orderStatus = "Activated";
      this.setMessage("Order activated.", "success");
    } catch (e) {
      this.running = false;
      this.progressText = undefined;
      this.setMessage(this.errText(e), "error");
    }
  }

  handleClose() {
    this.clearPolling();
    this.dispatchEvent(new CloseActionScreenEvent());
  }

  setMessage(text, variant) {
    this.message = text;
    this.messageVariant = variant || "info";
  }

  get messageClass() {
    const base = "slds-box slds-box_x-small slds-m-bottom_small ";
    if (this.messageVariant === "success") return base + "msg-success";
    if (this.messageVariant === "error") return base + "msg-error";
    return base + "msg-info";
  }

  errText(e) {
    if (e && e.body && e.body.message) return e.body.message;
    if (e && e.message) return e.message;
    return "Unexpected error.";
  }
}
