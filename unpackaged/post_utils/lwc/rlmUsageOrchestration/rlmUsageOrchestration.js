/**
 * rlmUsageOrchestration.js
 *
 * Lightning Web Component for triggering usage orchestration.
 * Provides:
 *  - Manual trigger button for usage processing
 *  - Static display of the 3-step workflow
 *  - Link to Monitor Workflow Services
 */
import { LightningElement, api, wire } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { NavigationMixin } from 'lightning/navigation';
import startOrchestration from '@salesforce/apex/RLM_UsageOrchestrationController.startOrchestration';

export default class RlmUsageOrchestration extends NavigationMixin(LightningElement) {
    // Configuration
    @api orchestrationFlowApiName = 'RLM_Orchestrate_Usage_Management';

    isStarting = false;

    // ─── Computed Properties ────────────────────────────────────────────

    get isStartDisabled() {
        return this.isStarting;
    }

    get processButtonLabel() {
        return this.isStarting ? 'Starting...' : 'Process Usage';
    }

    // ─── Event Handlers ─────────────────────────────────────────────────

    async handleProcessUsage() {
        if (this.isStarting) return;
        this.isStarting = true;

        try {
            await startOrchestration({ flowApiName: this.orchestrationFlowApiName });

            this.showToast('Processing Started', 'Usage orchestration has been initiated.', 'success');

        } catch (error) {
            this.showToast('Error', error.body?.message || error.message, 'error');
        } finally {
            this.isStarting = false;
        }
    }

    handleMonitorWorkflow() {
        // Open Setup page in a new tab so users keep their current record context.
        window.open('/lightning/setup/MonitorWorkflowServices/home', '_blank');
    }

    // ─── Utilities ──────────────────────────────────────────────────────

    showToast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
}
