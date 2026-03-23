import { LightningElement, api } from 'lwc';
import { CloseActionScreenEvent } from 'lightning/actions';

const MODAL_STYLE_ID = 'ramp-schedule-flow-modal-style';

export default class RlmRampScheduleFlowModalAction extends LightningElement {
    @api recordId;
    @api objectApiName;
    @api flowApiName = 'RLM_Create_Ramp_Schedule_V4';

    _ownsStyle = false;

    connectedCallback() {
        this.injectModalStyles();
    }

    disconnectedCallback() {
        this.removeModalStyles();
    }

    get modalTitle() {
        return 'Create Ramp Schedule';
    }

    get hasRecordId() {
        return !!this.recordId;
    }

    get flowInputVariables() {
        if (!this.recordId) {
            return [];
        }
        return [
            {
                name: 'recordId',
                type: 'String',
                value: this.recordId
            }
        ];
    }

    handleFlowStatusChange(event) {
        const status = event.detail?.status;

        if (status === 'FINISHED' || status === 'FINISHED_SCREEN') {
            this.dispatchEvent(new CloseActionScreenEvent());
        }
    }

    injectModalStyles() {
        if (this._ownsStyle) {
            return;
        }

        // Only create and own the style element if it doesn't exist yet.
        // If another instance already injected it, we leave it alone and do not
        // take ownership — so our disconnectedCallback won't remove it prematurely.
        if (!document.getElementById(MODAL_STYLE_ID)) {
            const styleEl = document.createElement('style');
            styleEl.id = MODAL_STYLE_ID;
            styleEl.textContent = `
                .uiModal--medium .modal-container {
                    width: 70% !important;
                    max-width: 70% !important;
                    min-width: 900px !important;
                }

                .slds-modal__container {
                    width: 70% !important;
                    max-width: 70% !important;
                    min-width: 900px !important;
                }

                @media (max-width: 1200px) {
                    .uiModal--medium .modal-container,
                    .slds-modal__container {
                        width: 95% !important;
                        max-width: 95% !important;
                        min-width: 0 !important;
                    }
                }
            `;
            document.head.appendChild(styleEl);
            this._ownsStyle = true;
        }
    }

    removeModalStyles() {
        // Only remove the style element if this instance was the one that created it.
        if (this._ownsStyle) {
            const styleEl = document.getElementById(MODAL_STYLE_ID);
            if (styleEl) {
                styleEl.remove();
            }
            this._ownsStyle = false;
        }
    }
}