import { api } from 'lwc';
import LightningModal from 'lightning/modal';

// Type token for the configurator flow's single Apex-typed input variable. For lightning-flow
// flow-input-variables, the token is the LITERAL string 'Apex' — NOT an apex://Class URI. The Flow
// runtime resolves the concrete class from the flow's own <apexClass> declaration
// (ProductConfig__ConfiguratorContext) and coerces the plain `value` object by field-name match.
// (apex://ProductConfig.ConfiguratorContext and apex://ProductConfig__ConfiguratorContext are both
// rejected at launch as "not a valid data type"; the platform's own configurator launcher uses 'Apex'.)
const CONFIGURATOR_CONTEXT_TYPE = 'Apex';

/**
 * Hosts the org's native Primary Product Configurator screen flow in a modal. The parent catalog
 * LWC builds the launch payload (flowApiName + configuratorContext) via Apex and opens this modal
 * with DlConfiguratorModal.open({ flowApiName, configuratorContext, size: 'large' }). The flow's
 * Data Manager persists the configured QuoteLineItem on finish, so closing with 'finished' signals
 * the parent to refresh.
 */
export default class DlConfiguratorModal extends LightningModal {
    @api flowApiName;
    @api configuratorContext;

    errorMessage = '';

    get hasFlow() {
        return !!this.flowApiName;
    }

    // Single Apex-typed input variable the configurator flow declares.
    get inputVariables() {
        if (!this.configuratorContext) {
            return [];
        }
        return [
            {
                name: 'configuratorContext',
                type: CONFIGURATOR_CONTEXT_TYPE,
                value: this.configuratorContext
            }
        ];
    }

    // The configurator runtime dispatches its own DOM events that bubble to <lightning-flow>:
    //   save    -> Save & Exit pressed (event.detail.transactionContextId carries the saved context)
    //   proceed -> Cancel pressed
    //   loading -> spinner toggle
    // These are NOT the classic FINISHED status-change events, so we wire them explicitly. The
    // configurator's own Data Manager (S01_DataManager) persists the configured line on Save & Exit;
    // we treat 'save' as the finished signal and let the parent catalog refresh the quote.
    handleSave(event) {
        // The configurator builds and prices the full configured tree but does NOT persist it when
        // launched standalone (the OOTB record-page container does that). It hands us the tree on the
        // save event as detail.transactionContext; we return it so the parent catalog can commit it
        // via Place Sales Transaction. Closing with an object payload (vs the 'cancel' string) is the
        // "finished, here is what to persist" signal.
        const detail = event && event.detail;
        this.close({ status: 'finished', transactionContext: detail && detail.transactionContext });
    }

    handleCancel() {
        this.close('cancel');
    }

    handleLoading() {
        // No-op: the configurator renders its own spinner. Hook retained for completeness.
    }

    // Retained for flows that still surface terminal status via statuschange (e.g. an ERROR state).
    handleStatusChange(event) {
        const status = event.detail?.status;
        if (status === 'FINISHED' || status === 'FINISHED_SCREEN') {
            this.close('finished');
        } else if (status === 'ERROR') {
            this.errorMessage = 'The product configurator encountered an error. Please try again.';
        }
    }
}
