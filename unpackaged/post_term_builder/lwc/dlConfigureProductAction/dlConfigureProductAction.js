import { LightningElement, api } from 'lwc';
import { CloseActionScreenEvent } from 'lightning/actions';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { getRecordNotifyChange } from 'lightning/uiRecordApi';
import DlConfiguratorModal from 'c/dlConfiguratorModal';
import getReconfigureLaunch from '@salesforce/apex/RLM_DeltaCatalogController.getReconfigureLaunch';
import commitReconfiguredQuote from '@salesforce/apex/RLM_DeltaCatalogController.commitReconfiguredQuote';

// Type token for the configurator flow's single Apex-typed input variable. The lightning-flow
// flow-input-variables token is the LITERAL string 'Apex' (NOT an apex://Class URI) — the Flow
// runtime resolves the concrete class from the flow's own <apexClass> declaration and coerces the
// plain value object by field-name match. (Mirrors c/dlConfiguratorModal, which hosts the same
// flow inside a modal; here we host it inline in the record-page region.)
const CONFIGURATOR_CONTEXT_TYPE = 'Apex';

/**
 * Re-configures an already-added bundle line in place. It resolves the hydrating launch context
 * server-side (getReconfigureLaunch), hosts the org's native Product Configurator, and on Save &
 * Exit commits the edited tree back to the quote via commitReconfiguredQuote (PST PATCH/POST/DELETE).
 *
 * Two placements (one component, two targets), differing only in WHERE the configurator renders:
 *   - lightning__RecordAction (header screen action): AUTO-launches the configurator in a MODAL
 *     (reusing c/dlConfiguratorModal) when opened, then closes the action screen. QuoteLineItem
 *     does NOT accept custom quick actions (platform-restricted), so this target serves
 *     standard/other objects that do.
 *   - lightning__RecordPage (embedded on the QuoteLineItem record page): renders a Configure button.
 *     Launching a configurator starts a session, so it stays gated behind the button — never on page
 *     load. On click it hosts <lightning-flow> INLINE in the page region (a configurator tab), not a
 *     modal, and collapses back to the button on Save & Exit / Cancel.
 */
export default class DlConfigureProductAction extends LightningElement {
    _recordId;
    _started = false;

    // A ScreenAction's recordId can arrive AFTER connectedCallback, so auto-launching from
    // connectedCallback races an undefined id. We kick off once from the setter when a non-blank id
    // first lands (proven pattern from rlmPreProcessOrderAction). The page (button) placement waits
    // for the click instead.
    @api
    get recordId() {
        return this._recordId;
    }
    set recordId(value) {
        this._recordId = value;
        this.maybeAutoStart();
    }

    @api objectApiName;

    // Design property (RecordPage target only).
    @api buttonLabel = 'Configure';

    // The action framework injects this on the RecordAction target; the RecordPage target leaves it
    // undefined. It drives modal-auto-launch vs inline-button hosting.
    _isActionContext = false;
    @api
    get isActionContext() {
        return this._isActionContext;
    }
    set isActionContext(value) {
        this._isActionContext = value === true || value === 'true';
        this.maybeAutoStart();
    }

    // Inline-flow (page placement) state.
    flowApiName;
    configuratorContext;
    loading = false;
    running = false;
    committing = false; // reactive: drives the "Saving…" processing view
    _committing = false; // synchronous re-entrancy guard against double-fired onsave
    errorMessage = '';

    connectedCallback() {
        this.maybeAutoStart();
    }

    // ---------- placement / rendering getters ----------

    get isModalPlacement() {
        return this._isActionContext === true;
    }

    // The page placement shows the button until the configurator is launched, then the inline flow,
    // then (briefly) the processing view while the save commits. The button only returns once the
    // commit settles.
    get showButton() {
        return !this.isModalPlacement && !this.hasFlow && !this.committing;
    }

    get hasFlow() {
        return !!this.flowApiName && !!this.configuratorContext && !this.committing;
    }

    // While a Save & Exit is committing, the configurator (and its Save button) is removed from the
    // DOM and replaced by a non-interactive "Saving…" view — so a double-click can't fire a second
    // commit against a tree the first commit already mutated (PST "Delta count … does not match").
    get processing() {
        return this.committing;
    }

    get effectiveButtonLabel() {
        return this.buttonLabel || 'Configure';
    }

    get buttonDisabled() {
        return this.running || !this._recordId;
    }

    // Single Apex-typed input variable the configurator flow declares (inline-host equivalent of the
    // modal's inputVariables getter).
    get inputVariables() {
        if (!this.configuratorContext) {
            return [];
        }
        return [{ name: 'configuratorContext', type: CONFIGURATOR_CONTEXT_TYPE, value: this.configuratorContext }];
    }

    // ---------- launch ----------

    maybeAutoStart() {
        if (this.isModalPlacement && this._recordId && !this._started) {
            this._started = true;
            this.launchModal();
        }
    }

    handleConfigureClick() {
        if (this.running || this.hasFlow) {
            return;
        }
        this.launchInline();
    }

    // Resolve the launch context, shared by both placements.
    async resolveLaunch() {
        return this._parse(
            await getReconfigureLaunch({ inputJson: JSON.stringify({ quoteLineItemId: this._recordId }) })
        );
    }

    // Page placement: render <lightning-flow> inline in the region.
    async launchInline() {
        this.loading = true;
        this.running = true;
        this.errorMessage = '';
        try {
            const launch = await this.resolveLaunch();
            if (launch.isSuccess === false) {
                this._fail(launch.errorMessage || 'Unable to launch the product configurator.');
                return;
            }
            this._launch = launch; // retain quoteId + rootQuoteLineItemId for the commit
            this.flowApiName = launch.flowApiName;
            this.configuratorContext = launch.configuratorContext;
        } catch (e) {
            this._fail(this._errMessage(e));
        } finally {
            this.loading = false;
            this.running = false;
        }
    }

    // Action placement: auto-launch the configurator in the shared modal, then close the action.
    async launchModal() {
        this.loading = true;
        this.running = true;
        this.errorMessage = '';
        try {
            const launch = await this.resolveLaunch();
            if (launch.isSuccess === false) {
                this._toast('RLM Contracted Pricing', launch.errorMessage || 'Unable to launch the product configurator.', 'error');
                this._closeAction();
                return;
            }
            const result = await DlConfiguratorModal.open({
                size: 'large',
                flowApiName: launch.flowApiName,
                configuratorContext: launch.configuratorContext
            });
            const finished = result === 'finished' || (result && result.status === 'finished');
            if (!finished) {
                this._closeAction();
                return;
            }
            const transactionContext = result && result.transactionContext;
            const ok = await this.commit(launch, transactionContext);
            if (ok) {
                this._toast('RLM Contracted Pricing', 'Configuration changes saved to the quote.', 'success');
                getRecordNotifyChange([{ recordId: this._recordId }]);
            }
            this._closeAction();
        } catch (e) {
            this._toast('RLM Contracted Pricing', this._errMessage(e), 'error');
            this._closeAction();
        } finally {
            this.loading = false;
            this.running = false;
        }
    }

    // ---------- inline flow event handlers ----------
    // The configurator runtime dispatches its own DOM events that bubble to <lightning-flow>:
    //   onsave -> Save & Exit (event.detail.transactionContext is the built/priced tree)
    //   onproceed -> Cancel
    //   onloading -> spinner toggle (the configurator renders its own spinner; no-op)

    async handleFlowSave(event) {
        // Re-entrancy guard. The configurator can fire `onsave` twice on a fast double-click; the
        // second commit would re-submit DELETE nodes the first already applied, so PST rejects it with
        // "Delta count N does not match with input size M" (no-op deletes still count as inputs).
        // _committing is set SYNCHRONOUSLY here — JS is single-threaded, so the second handler call
        // sees it before the first `await` resolves and bails. Flipping `committing` also removes the
        // flow (and its Save button) from the DOM, replacing it with the "Saving…" view.
        if (this._committing) {
            return;
        }
        this._committing = true;
        this.committing = true;
        this.running = true;

        const detail = event && event.detail;
        const transactionContext = detail && detail.transactionContext;
        try {
            const ok = await this.commit(this._launch, transactionContext);
            if (ok) {
                this._toast('RLM Contracted Pricing', 'Configuration changes saved to the quote.', 'success');
                getRecordNotifyChange([{ recordId: this._recordId }]);
            }
        } catch (e) {
            this.errorMessage = this._errMessage(e);
            this._toast('RLM Contracted Pricing', this.errorMessage, 'error');
        } finally {
            this.running = false;
            this._committing = false;
            this.committing = false;
            // Collapse the inline configurator back to the button after the save settles.
            this.teardownFlow();
        }
    }

    handleFlowCancel() {
        this.teardownFlow();
    }

    handleFlowLoading() {
        // No-op: the configurator renders its own spinner.
    }

    handleFlowStatusChange(event) {
        const status = event && event.detail && event.detail.status;
        if (status === 'ERROR') {
            this.errorMessage = 'The product configurator encountered an error. Please try again.';
        }
    }

    teardownFlow() {
        this.flowApiName = undefined;
        this.configuratorContext = undefined;
        this._launch = undefined;
    }

    // ---------- commit (shared) ----------

    // Returns true on success (or no-op), false on a handled commit error.
    async commit(launch, transactionContext) {
        if (!transactionContext || !launch) {
            return true;
        }
        const commit = this._parse(
            await commitReconfiguredQuote({
                inputJson: JSON.stringify({
                    quoteId: launch.quoteId,
                    rootQuoteLineItemId: launch.rootQuoteLineItemId,
                    transactionContext
                })
            })
        );
        if (commit.isSuccess === false) {
            this.errorMessage = commit.errorMessage || 'Unable to save the configuration changes.';
            this._toast('RLM Contracted Pricing', this.errorMessage, 'error');
            return false;
        }
        return true;
    }

    // ---------- helpers ----------

    _fail(message) {
        this.errorMessage = message;
        this._toast('RLM Contracted Pricing', message, 'error');
    }

    // CloseActionScreenEvent closes the action screen behind the modal. Only fired in the action
    // placement (launchModal); harmless if it ever bubbled with no action host to catch it.
    _closeAction() {
        this.dispatchEvent(new CloseActionScreenEvent());
    }

    _parse(json) {
        try {
            return json ? JSON.parse(json) : {};
        } catch {
            return { isSuccess: false, errorMessage: 'Unexpected response from server.' };
        }
    }

    _errMessage(e) {
        return (e && e.body && e.body.message) || (e && e.message) || 'Unexpected error.';
    }

    _toast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
}
