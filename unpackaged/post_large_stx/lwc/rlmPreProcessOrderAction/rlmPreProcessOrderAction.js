import { LightningElement, api, track } from "lwc";
import { CloseActionScreenEvent } from "lightning/actions";
import getOrderInfo from "@salesforce/apex/RLM_PreProcessOrderController.getOrderInfo";
import startPreprocess from "@salesforce/apex/RLM_PreProcessOrderController.startPreprocess";
import getStatus from "@salesforce/apex/RLM_PreProcessOrderController.getStatus";
import activateOrder from "@salesforce/apex/RLM_PreProcessOrderController.activateOrder";
import getPricingStatus from "@salesforce/apex/RLM_PreProcessOrderController.getPricingStatus";
import enqueuePreprocess from "@salesforce/apex/RLM_PreProcessOrderController.enqueuePreprocess";

const POLL_INTERVAL_MS = 2500;
const MAX_POLLS = 120; // ~5 minutes (preprocess phase)
const PRICING_POLL_CAP = 60; // ~2.5 minutes per reprice leg
const MAX_REPRICE_ATTEMPTS = 2; // re-reprices after the first kick (3 total)
const STABLE_POLLS_REQUIRED = 3; // committed must hold this many consecutive polls
const BACKOFF_TICKS = [1, 2, 4]; // poll intervals to wait before each re-reprice (~2.5/5/10s)

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
  _pollInFlight = false;
  _pollCount = 0;
  _phase; // 'repricing' | 'preprocess'
  _repriceAttempt = 0;
  _stableCommittedPolls = 0;
  _backoffHandle;
  _preprocessEnqueued = false;

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
    this._repriceAttempt = 0;
    this._preprocessEnqueued = false;
    await this.kickReprice();
  }

  // Phase 1: kick the reprice (large deal) or go straight to enqueue (standard).
  async kickReprice() {
    this.clearPolling();
    this._pollCount = 0;
    this._stableCommittedPolls = 0;
    this.progressText = "Confirming pricing…";
    this.setMessage("Preparing the order for activation…", "info");
    try {
      const res = JSON.parse(await startPreprocess({ orderId: this.recordId }));
      if (!res.success) {
        // Synchronous reprice reject counts as a failed attempt (bounded retry).
        this.handleRepriceFailure(res.errorMessage || "Reprice failed to start.");
        return;
      }
      if (res.phase === "ready_to_enqueue") {
        // Standard order: no pricing wait needed.
        await this.enqueueAndPoll();
        return;
      }
      this._phase = "repricing";
      this.startPolling();
    } catch (e) {
      this.handleRepriceFailure(this.errText(e));
    }
  }

  // Bounded re-reprice with backoff; gives up after MAX_REPRICE_ATTEMPTS.
  handleRepriceFailure(msg) {
    this.clearPolling();
    this._stableCommittedPolls = 0;
    if (this._repriceAttempt < MAX_REPRICE_ATTEMPTS) {
      this._repriceAttempt += 1;
      const ticks = BACKOFF_TICKS[Math.min(this._repriceAttempt - 1, BACKOFF_TICKS.length - 1)];
      this.progressText =
        "Pricing didn't settle; retrying (" + this._repriceAttempt + "/" + MAX_REPRICE_ATTEMPTS + ")…";
      this._backoffHandle = setTimeout(() => this.kickReprice(), ticks * POLL_INTERVAL_MS);
    } else {
      this.running = false;
      this.progressText = undefined;
      this.setMessage(
        "Pricing did not settle after " +
          (MAX_REPRICE_ATTEMPTS + 1) +
          " attempts. Review the order data and try again. (" +
          msg +
          ")",
        "error",
      );
    }
  }

  // Phase 3: enqueue preprocess at most once, then poll the preprocess job.
  async enqueueAndPoll() {
    if (this._preprocessEnqueued) {
      return;
    }
    this.progressText = "Submitting preprocessing job…";
    try {
      const res = JSON.parse(await enqueuePreprocess({ orderId: this.recordId }));
      if (!res.success) {
        if (res.phase === "pricing_not_committed") {
          // Racing client — resume the pricing poll instead of erroring.
          this._stableCommittedPolls = 0;
          this._phase = "repricing";
          this._pollCount = 0;
          this.startPolling();
          return;
        }
        this.running = false;
        this.progressText = undefined;
        this.setMessage(res.errorMessage || "Preprocessing failed to start.", "error");
        return;
      }
      this._preprocessEnqueued = true;
      this._requestId = res.requestId;
      if (res.alreadyEnqueued && !res.requestId) {
        // Validation already complete server-side — surface ready, no polling.
        this.clearPolling();
        this.running = false;
        this.validationComplete = true;
        this.progressText = undefined;
        this.setMessage("This order is already preprocessed and ready to activate.", "success");
        return;
      }
      this._phase = "preprocess";
      this._pollCount = 0;
      this.progressText = "Waiting for validation to complete…";
      this.setMessage("Preprocessing started. This runs asynchronously.", "info");
      this.startPolling();
    } catch (e) {
      this.running = false;
      this.progressText = undefined;
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
    if (this._backoffHandle) {
      clearTimeout(this._backoffHandle);
      this._backoffHandle = undefined;
    }
  }

  async poll() {
    // Re-entrancy guard: setInterval can fire again while a prior poll's async
    // Apex call is still in flight (server response slower than POLL_INTERVAL_MS).
    // Skip overlapping ticks so only one poll mutates state at a time.
    if (this._pollInFlight) {
      return;
    }
    this._pollInFlight = true;
    try {
      this._pollCount += 1;
      if (this._phase === "repricing") {
        await this.pollPricing();
      } else {
        await this.pollPreprocess();
      }
    } finally {
      this._pollInFlight = false;
    }
  }

  // Phase 2 poll: wait for the reprice to commit, retry it, or surface a partial-save.
  async pollPricing() {
    if (this._pollCount > PRICING_POLL_CAP) {
      this.handleRepriceFailure("Pricing is taking longer than expected.");
      return;
    }
    try {
      const res = JSON.parse(await getPricingStatus({ orderId: this.recordId }));
      if (!res.success) {
        // A non-committed observation breaks the consecutive-committed streak.
        this._stableCommittedPolls = 0;
        return; // transient; keep polling
      }
      this.progressText =
        "Confirming pricing… (" +
        (res.calculationStatus || "…") +
        ", " +
        (res.pendingAsyncCount || 0) +
        " pending)";
      if (res.phase === "pricing_failed") {
        this.handleRepriceFailure("Pricing failed (" + (res.calculationStatus || "unknown") + ").");
        return;
      }
      if (res.phase === "pricing_investigate") {
        this.clearPolling();
        this._stableCommittedPolls = 0;
        this.running = false;
        this.progressText = undefined;
        this.setMessage(
          "Pricing returned a partial-save state (" +
            (res.calculationStatus || "unknown") +
            "). Review the order data before retrying.",
          "error",
        );
        return;
      }
      if (res.phase === "pricing_committed") {
        this._stableCommittedPolls += 1;
        if (this._stableCommittedPolls >= STABLE_POLLS_REQUIRED) {
          this.clearPolling();
          await this.enqueueAndPoll();
        }
        return;
      }
      // pricing_in_progress
      this._stableCommittedPolls = 0;
    } catch (e) {
      // Transient error — a failed observation breaks the committed streak too.
      this._stableCommittedPolls = 0;
    }
  }

  // Final poll: the existing preprocess-tracker poll (failed checked before ready).
  async pollPreprocess() {
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
