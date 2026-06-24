import { LightningElement, wire } from 'lwc'
import { ShowToastEvent } from 'lightning/platformShowToastEvent'
import getContextDefinitions from '@salesforce/apex/RLM_ExpressionSetManagerController.getContextDefinitions'
import getLinkedExpressionSets from '@salesforce/apex/RLM_ExpressionSetManagerController.getLinkedExpressionSets'
import getJobStatus from '@salesforce/apex/RLM_ExpressionSetManagerController.getJobStatus'
import deactivateExpressionSets from '@salesforce/apex/RLM_ExpressionSetManagerController.deactivateExpressionSets'
import getDeactivateStatus from '@salesforce/apex/RLM_ExpressionSetManagerController.getDeactivateStatus'
import activateExpressionSets from '@salesforce/apex/RLM_ExpressionSetManagerController.activateExpressionSets'
import getActivateStatus from '@salesforce/apex/RLM_ExpressionSetManagerController.getActivateStatus'

const POLL_INTERVAL = 3000
const ACTIVATE_DELAY = 5000
const MAX_DOMAIN_POLL_ATTEMPTS = 40

const COLUMNS = [
    {
        label: 'Expression Set',
        fieldName: 'recordUrl',
        type: 'url',
        typeAttributes: { label: { fieldName: 'label' }, target: '_blank' },
        sortable: true,
        sortingFieldName: 'label',
        wrapText: true
    },
    { label: 'API Name', fieldName: 'developerName', type: 'text', sortable: true },
    { label: 'Type', fieldName: 'usageType', type: 'text', sortable: true },
    { label: 'Status', fieldName: 'statusText', type: 'text', sortable: true },
    {
        label: 'Latest Version',
        fieldName: 'latestVersionUrl',
        type: 'url',
        typeAttributes: { label: { fieldName: 'latestVersionLabel' }, target: '_blank' },
        sortable: true,
        sortingFieldName: 'latestVersionNumber'
    }
]

// Admin/setup utility — intentionally has no @api props, slots, or
// CustomEvents. It is not designed to be composed by other components.
export default class RlmExpressionSetManager extends LightningElement {
    contextOptions = []
    selectedContextId
    selectedContextDevName
    expressionSets = []
    selectedRowIds = []
    columns = COLUMNS
    sortedByColumn = 'usageType'
    sortedBy = 'usageType'
    sortDirection = 'desc'
    isLoading = false
    isActing = false
    previousError = ''
    contextDefUrl = ''
    _contextData = []
    _pollTimer
    _delayTimer
    _focusErrorOnRender = false

    @wire(getContextDefinitions)
    wiredContextDefinitions({ data, error }) {
        if (data) {
            this._contextData = data
            this.contextOptions = data.map(cd => ({
                label: `${cd.label} (${cd.developerName}) [${cd.expressionSetCount} Expression Sets]`,
                value: cd.id
            }))
        } else if (error) {
            this.showToast('Error', 'Failed to load Context Definitions', 'error')
        }
    }

    // --- Getters ---

    get hasPreviousError() {
        return !!this.previousError
    }

    get hasContext() {
        return !!this.selectedContextId
    }

    get hasExpressionSets() {
        return this.expressionSets.length > 0
    }

    get showNoResults() {
        return !this.isLoading && !this.hasExpressionSets
    }

    get bulkActionDisabled() {
        return this.isActing || this.selectedRowIds.length === 0
    }

    get statusMessage() {
        const active = this.expressionSets.filter(es => es.hasActiveVersion).length
        const inactive = this.expressionSets.length - active
        const total = this.expressionSets.length
        const parts = []
        if (active > 0) parts.push(`${active} active`)
        if (inactive > 0) parts.push(`${inactive} inactive`)
        return `${total} Expression Set(s): ${parts.join(', ')}.`
    }

    get statusVariant() {
        if (this.expressionSets.every(es => es.hasActiveVersion)) return 'success'
        return 'warning'
    }

    get statusIcon() {
        return this.statusVariant === 'success' ? 'utility:success' : 'utility:warning'
    }

    get statusAlertClass() {
        return `slds-notify slds-notify_alert slds-alert_${this.statusVariant}`
    }

    // --- Event Handlers ---

    handleDismissError() {
        this.previousError = ''
    }

    handleRetryError() {
        this.previousError = ''
        if (this.selectedContextId) {
            this.loadExpressionSets()
        }
    }

    renderedCallback() {
        if (this._focusErrorOnRender && this.previousError) {
            this._focusErrorOnRender = false
            const alert = this.template.querySelector('[data-error-alert]')
            if (alert) {
                alert.focus()
            }
        }
    }

    setPreviousError(message) {
        this.previousError = message
        this._focusErrorOnRender = true
    }

    handleContextChange(event) {
        this.selectedContextId = event.detail.value
        const selected = this._contextData.find(cd => cd.id === this.selectedContextId)
        this.selectedContextDevName = selected ? selected.developerName : ''
        this.contextDefUrl = this.buildContextDefUrl()
        this.selectedRowIds = []
        this.loadExpressionSets()
    }

    buildContextDefUrl() {
        const idParam = btoa(`"${this.selectedContextId}"`)
        const nameParam = btoa(`"${this.selectedContextDevName}"`)
        const tab = btoa('"details"')
        const status = btoa('"Active"')
        return `/lightning/setup/ContextManagementSetupNode/home#contextIdFromLandingPage=${idParam}&contextDefinitionNameFromLandingPage=${nameParam}&activeTab=${tab}&status=${status}`
    }

    handleRowSelection(event) {
        this.selectedRowIds = event.detail.selectedRows.map(r => r.definitionId)
    }

    handleSort(event) {
        const column = this.columns.find(c => c.fieldName === event.detail.fieldName)
        this.sortedByColumn = event.detail.fieldName
        this.sortedBy = column?.sortingFieldName || event.detail.fieldName
        this.sortDirection = event.detail.sortDirection
        this.expressionSets = this.applySort([...this.expressionSets])
    }

    applySort(rows) {
        const field = this.sortedBy
        const dir = this.sortDirection === 'asc' ? 1 : -1
        return rows.sort((a, b) => {
            const av = a[field]
            const bv = b[field]
            if (av == null && bv == null) return 0
            if (av == null) return 1
            if (bv == null) return -1
            if (typeof av === 'number' && typeof bv === 'number') {
                return (av - bv) * dir
            }
            return String(av).localeCompare(String(bv)) * dir
        })
    }

    async handleDeactivate() {
        const selectedSet = new Set(this.selectedRowIds)
        const selectedRows = this.expressionSets.filter(es => selectedSet.has(es.definitionId))
        const active = selectedRows.filter(es => es.hasActiveVersion)
        if (selectedRows.length === 0) {
            this.showToast('Info', 'No Expression Sets selected.', 'info')
            return
        }
        if (active.length === 0) {
            this.showToast(
                'Info',
                `All ${selectedRows.length} selected Expression Set(s) are already inactive.`,
                'info'
            )
            return
        }

        const defIds = active.map(es => es.definitionId)

        this.isActing = true
        this.previousError = ''
        try {
            const jobId = await deactivateExpressionSets({
                contextDefinitionId: this.selectedContextId,
                definitionIds: defIds
            })
            this.showToast('Deactivating', `Deactivating ${defIds.length} Expression Set(s)...`, 'info')
            this.pollStatus(jobId, getDeactivateStatus, this.selectedContextId, defIds, 0, ids => {
                this.expressionSets = this.expressionSets.map(es =>
                    ids.has(es.definitionId) ? { ...es, hasActiveVersion: false, statusText: 'Inactive' } : es
                )
                this.selectedRowIds = this.selectedRowIds.filter(id => !ids.has(id))
                this.showToast('Deactivated', `${ids.size} Expression Set(s) deactivated.`, 'success')
            })
        } catch (error) {
            this.isActing = false
            this.showToast('Error', error.body?.message || error.message, 'error')
        }
    }

    async handleActivate() {
        const selectedSet = new Set(this.selectedRowIds)
        const selectedRows = this.expressionSets.filter(es => selectedSet.has(es.definitionId))
        const inactive = selectedRows.filter(es => !es.hasActiveVersion)
        if (selectedRows.length === 0) {
            this.showToast('Info', 'No Expression Sets selected.', 'info')
            return
        }
        if (inactive.length === 0) {
            this.showToast('Info', `All ${selectedRows.length} selected Expression Set(s) are already active.`, 'info')
            return
        }

        const defIds = inactive.map(es => es.definitionId)

        this.isActing = true
        this.previousError = ''
        try {
            const jobId = await activateExpressionSets({
                contextDefinitionId: this.selectedContextId,
                definitionIds: defIds
            })
            this.showToast('Activating', `Activating ${defIds.length} Expression Set(s)...`, 'info')
            this.pollStatus(jobId, getActivateStatus, this.selectedContextId, defIds, ACTIVATE_DELAY, () => {
                this.showToast('Activated', 'Expression Sets activated successfully.', 'success')
                this.loadExpressionSets()
            })
        } catch (error) {
            this.isActing = false
            this.showToast('Error', error.body?.message || error.message, 'error')
        }
    }

    // --- Data Loading ---

    async loadExpressionSets() {
        this.isLoading = true
        try {
            const data = await getLinkedExpressionSets({ contextDefinitionId: this.selectedContextId })
            const rows = data.map(es => {
                const latest = es.versions[0]
                return {
                    ...es,
                    recordUrl: `/lightning/r/ExpressionSet/${es.expressionSetId}/view`,
                    statusText: es.hasActiveVersion ? 'Active' : 'Inactive',
                    latestVersionNumber: latest ? latest.versionNumber : null,
                    latestVersionLabel: latest ? `v${latest.versionNumber}` : '',
                    latestVersionUrl: latest ? this.buildVersionUrl(es, latest) : ''
                }
            })
            this.expressionSets = this.applySort(rows)
            this.selectedRowIds = []
        } catch (error) {
            this.expressionSets = []
            this.selectedRowIds = []
            this.showToast('Error', 'Failed to load Expression Sets', 'error')
        } finally {
            this.isLoading = false
        }
    }

    buildVersionUrl(es, v) {
        if (es.usageType === 'Constraint') {
            const versionName = encodeURIComponent(`${es.label} V${v.versionNumber}`)
            return `/builder_industries_constraints/constraintBuilder.app?constraintId=${es.expressionSetId}&versionId=${v.versionId}&versionName=${versionName}&contextId=${this.selectedContextId}`
        }
        return `/builder_industries_interaction_rule/ruleBuilder.app?ruleId=${v.versionId}`
    }

    // --- Polling ---

    pollStatus(jobId, statusFn, contextId, defIds, initialDelay, onComplete) {
        this.stopPolling()
        this.isActing = true
        let isChecking = false
        let domainAttempts = 0
        const poll = async () => {
            if (isChecking) return
            isChecking = true
            try {
                const jobStatus = await getJobStatus({ jobId })
                if (jobStatus.state === 'running') {
                    return
                }
                if (jobStatus.state === 'failed' || jobStatus.state === 'unknown') {
                    this.stopPolling()
                    this.setPreviousError(jobStatus.message || 'Operation did not complete.')
                    await this.loadExpressionSets()
                    return
                }

                const status = await statusFn({ contextDefinitionId: contextId, definitionIds: defIds })
                if (status === 'complete') {
                    this.stopPolling()
                    onComplete(new Set(defIds))
                    return
                }

                domainAttempts += 1
                if (domainAttempts >= MAX_DOMAIN_POLL_ATTEMPTS) {
                    this.stopPolling()
                    this.setPreviousError(
                        'Operation job completed, but the Expression Set status did not finish updating. Refresh and try again.'
                    )
                    await this.loadExpressionSets()
                }
            } catch (error) {
                this.stopPolling()
                this.showToast('Error', 'Failed to check operation status.', 'error')
            } finally {
                isChecking = false
            }
        }
        const startPolling = () => {
            // eslint-disable-next-line @lwc/lwc/no-async-operation
            this._pollTimer = setInterval(poll, POLL_INTERVAL)
        }

        if (initialDelay > 0) {
            // eslint-disable-next-line @lwc/lwc/no-async-operation
            this._delayTimer = setTimeout(startPolling, initialDelay)
        } else {
            startPolling()
        }
    }

    stopPolling() {
        if (this._delayTimer) {
            clearTimeout(this._delayTimer)
            this._delayTimer = null
        }
        if (this._pollTimer) {
            clearInterval(this._pollTimer)
            this._pollTimer = null
        }
        this.isActing = false
    }

    disconnectedCallback() {
        this.stopPolling()
    }

    showToast(title, message, variant) {
        const mode = variant === 'error' ? 'sticky' : 'dismissable'
        this.dispatchEvent(new ShowToastEvent({ title, message, variant, mode }))
    }
}
