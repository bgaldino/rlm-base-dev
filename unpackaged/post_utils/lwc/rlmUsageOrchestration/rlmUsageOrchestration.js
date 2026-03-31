/**
 * rlmUsageOrchestration.js
 *
 * Lightning Web Component for triggering and monitoring usage orchestration.
 * Provides:
 *  - Manual trigger button for usage processing
 *  - Real-time status display with 3-step progress indicator
 *  - Link to Monitor Workflow Services
 *  - Last run information display
 */
import { LightningElement, api, wire } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { NavigationMixin } from 'lightning/navigation';
import startOrchestration from '@salesforce/apex/RLM_UsageOrchestrationController.startOrchestration';
import getOrchestrationStatus from '@salesforce/apex/RLM_UsageOrchestrationController.getOrchestrationStatus';
import getLastRunInfo from '@salesforce/apex/RLM_UsageOrchestrationController.getLastRunInfo';

const POLL_INTERVAL_MS = 5000; // Poll every 5 seconds
const MAX_POLLS = 360; // 30 minutes maximum (360 * 5s)

const STEP_STATUS = {
    PENDING: 'pending',
    PROCESSING: 'processing',
    SUCCESS: 'success',
    ERROR: 'error'
};

// Flow element name patterns for status detection
const FLOW_ELEMENTS = {
    USAGE_SUMMARY: 'Usage_Summary',
    RATABLE_SUMMARY: 'Ratable_Summary',
    LIABLE_SUMMARY: 'Liable_Summary'
};

export default class RlmUsageOrchestration extends NavigationMixin(LightningElement) {
    // Configuration
    @api orchestrationFlowApiName = 'RLM_Orchestrate_Usage_Management';

    isProcessing = false;
    interviewGuid;
    pollCount = 0;
    pollInterval;

    // Step statuses
    step1Status = STEP_STATUS.PENDING;
    step2Status = STEP_STATUS.PENDING;
    step3Status = STEP_STATUS.PENDING;

    // Last run info
    lastRunInfo;

    // ─── Wire Adapters ──────────────────────────────────────────────────

    @wire(getLastRunInfo)
    wiredLastRunInfo({ data, error }) {
        if (data) {
            this.lastRunInfo = data;
        } else if (error) {
            console.error('Error loading last run info:', error);
        }
    }

    // ─── Computed Properties ────────────────────────────────────────────

    get isStartDisabled() {
        return this.isProcessing;
    }

    get processButtonLabel() {
        return this.isProcessing ? 'Processing...' : 'Process Usage';
    }

    get step1IconName() {
        return this.getStepIconName(this.step1Status);
    }

    get step1IconVariant() {
        return this.getStepIconVariant(this.step1Status);
    }

    get step2IconName() {
        return this.getStepIconName(this.step2Status);
    }

    get step2IconVariant() {
        return this.getStepIconVariant(this.step2Status);
    }

    get step3IconName() {
        return this.getStepIconName(this.step3Status);
    }

    get step3IconVariant() {
        return this.getStepIconVariant(this.step3Status);
    }

    get step1Class() {
        return this.getStepClass(this.step1Status);
    }

    get step2Class() {
        return this.getStepClass(this.step2Status);
    }

    get step3Class() {
        return this.getStepClass(this.step3Status);
    }

    get lastRunTimestamp() {
        if (!this.lastRunInfo || !this.lastRunInfo.startTime) return 'Never';
        return new Date(this.lastRunInfo.startTime).toLocaleString();
    }

    get lastRunStatus() {
        if (!this.lastRunInfo) return 'Unknown';
        if (this.lastRunInfo.status === 'Finished') return 'Success';
        if (this.lastRunInfo.status === 'Error') return 'Failed';
        return this.lastRunInfo.status;
    }

    get showLastRunInfo() {
        return this.lastRunInfo != null;
    }

    // ─── Helper Methods ─────────────────────────────────────────────────

    getStepIconName(status) {
        switch (status) {
            case STEP_STATUS.PENDING:
                return 'utility:clock';
            case STEP_STATUS.PROCESSING:
                return 'utility:sync';
            case STEP_STATUS.SUCCESS:
                return 'utility:success';
            case STEP_STATUS.ERROR:
                return 'utility:error';
            default:
                return 'utility:clock';
        }
    }

    getStepClass(status) {
        const baseClass = 'step-card slds-box slds-p-around_small slds-m-bottom_small';
        switch (status) {
            case STEP_STATUS.PROCESSING:
                return `${baseClass} step-processing`;
            case STEP_STATUS.SUCCESS:
                return `${baseClass} step-success`;
            case STEP_STATUS.ERROR:
                return `${baseClass} step-error`;
            default:
                return `${baseClass} step-pending`;
        }
    }

    getStepIconVariant(status) {
        switch (status) {
            case STEP_STATUS.SUCCESS:
                return 'success';
            case STEP_STATUS.ERROR:
                return 'error';
            case STEP_STATUS.PROCESSING:
                return 'warning';
            default:
                return 'inverse';
        }
    }

    // ─── Event Handlers ─────────────────────────────────────────────────

    async handleProcessUsage() {
        if (this.isProcessing) return;

        this.isProcessing = true;
        this.resetStepStatuses();

        try {
            // Start orchestration
            this.interviewGuid = await startOrchestration({ flowApiName: this.orchestrationFlowApiName });

            this.showToast('Processing Started', 'Usage orchestration has been initiated. This may take up to 15 minutes.', 'info');

            // Start polling for status
            this.pollCount = 0;
            this.startPolling();

        } catch (error) {
            this.isProcessing = false;
            this.showToast('Error', error.body?.message || error.message, 'error');
        }
    }

    handleMonitorWorkflow() {
        // Open Setup page in a new tab so users keep their current record context.
        window.open('/lightning/setup/MonitorWorkflowServices/home', '_blank');
    }

    // ─── Status Polling ─────────────────────────────────────────────────

    startPolling() {
        this.step1Status = STEP_STATUS.PROCESSING;

        this.pollInterval = setInterval(() => {
            this.checkStatus();
        }, POLL_INTERVAL_MS);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async checkStatus() {
        this.pollCount++;

        if (this.pollCount > MAX_POLLS) {
            this.stopPolling();
            this.isProcessing = false;
            this.showToast('Timeout', 'Orchestration polling timed out. Check Monitor Workflow Services for status.', 'warning');
            return;
        }

        try {
            const status = await getOrchestrationStatus({ interviewId: this.interviewGuid });

            // Update step statuses based on current element
            this.updateStepStatusesFromInterview(status);

            // Check if complete
            if (status.status === 'Finished') {
                this.stopPolling();
                this.isProcessing = false;
                this.step1Status = STEP_STATUS.SUCCESS;
                this.step2Status = STEP_STATUS.SUCCESS;
                this.step3Status = STEP_STATUS.SUCCESS;
                this.showToast('Success', 'Usage orchestration completed successfully!', 'success');

                // Refresh last run info
                this.lastRunInfo = await getLastRunInfo();
                return;
            } else if (status.status === 'Error') {
                this.stopPolling();
                this.isProcessing = false;
                this.markCurrentStepAsError(status.currentElement);
                this.showToast('Error', 'Usage orchestration failed. Check debug logs for details.', 'error');
            }

        } catch (error) {
            console.error('Error checking status:', error);
            this.stopPolling();
            this.isProcessing = false;
            this.showToast('Error', 'Failed to check orchestration status', 'error');
        }
    }

    updateStepStatusesFromInterview(status) {
        // Based on current element, update which step is processing
        const element = status.currentElement;

        if (!element) return;

        if (element.includes(FLOW_ELEMENTS.USAGE_SUMMARY)) {
            this.step1Status = STEP_STATUS.PROCESSING;
        } else if (element.includes(FLOW_ELEMENTS.RATABLE_SUMMARY)) {
            this.step1Status = STEP_STATUS.SUCCESS;
            this.step2Status = STEP_STATUS.PROCESSING;
        } else if (element.includes(FLOW_ELEMENTS.LIABLE_SUMMARY)) {
            this.step1Status = STEP_STATUS.SUCCESS;
            this.step2Status = STEP_STATUS.SUCCESS;
            this.step3Status = STEP_STATUS.PROCESSING;
        }
    }

    markCurrentStepAsError(currentElement) {
        if (!currentElement) {
            this.step1Status = STEP_STATUS.ERROR;
            return;
        }

        if (currentElement.includes(FLOW_ELEMENTS.USAGE_SUMMARY)) {
            this.step1Status = STEP_STATUS.ERROR;
        } else if (currentElement.includes(FLOW_ELEMENTS.RATABLE_SUMMARY)) {
            this.step2Status = STEP_STATUS.ERROR;
        } else if (currentElement.includes(FLOW_ELEMENTS.LIABLE_SUMMARY)) {
            this.step3Status = STEP_STATUS.ERROR;
        }
    }

    resetStepStatuses() {
        this.step1Status = STEP_STATUS.PENDING;
        this.step2Status = STEP_STATUS.PENDING;
        this.step3Status = STEP_STATUS.PENDING;
    }

    // ─── Lifecycle ──────────────────────────────────────────────────────

    disconnectedCallback() {
        this.stopPolling();
    }

    // ─── Utilities ──────────────────────────────────────────────────────

    showToast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
}
