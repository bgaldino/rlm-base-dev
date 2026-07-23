import { LightningElement, wire } from 'lwc'
import { refreshApex } from '@salesforce/apex'
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
const MAX_JOB_POLL_ATTEMPTS = 80
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
    {
        label: 'Linked',
        fieldName: 'linkStatusText',
        type: 'text',
        sortable: true,
        sortingFieldName: 'linkSortValue',
        fixedWidth: 80,
        cellAttributes: {
            iconName: { fieldName: 'linkStatusIcon' },
            iconPosition: 'left',
            class: { fieldName: 'linkStatusClass' }
        }
    },
    {
        label: 'Status',
        fieldName: 'statusText',
        type: 'text',
        sortable: true,
        cellAttributes: {
            iconName: { fieldName: 'statusIcon' },
            iconPosition: 'left',
            class: { fieldName: 'statusClass' }
        }
    },
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
    expressionSets = []
    selectedRowIds = []
    columns = COLUMNS
    sortedByColumn = 'usageType'
    sortDirection = 'desc'
    isLoading = false
    isActing = false
    previousError = ''
    _contextData = []
    _wiredContexts
    _pollTimer
    _delayTimer
    _focusErrorOnRender = false
    _loadRequestId = 0
    _pollRequestId = 0

    @wire(getContextDefinitions)
    wiredContextDefinitions(result) {
        this._wiredContexts = result
        const { data, error } = result
        if (data) {
            this._contextData = data
            this.contextOptions = data.map(cd => ({
                label: `${cd.label} (${cd.developerName}) [${cd.expressionSetCount} linked Expression Sets]`,
                value: cd.id
            }))
        } else if (error) {
            this.showToast('Error', `Failed to load Context Definitions: ${this.reduceErrors(error)}`, 'error')
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
        // isLoading matters as well as isActing: every terminal polling path calls
        // stopPolling() (clearing isActing) *before* awaiting loadExpressionSets,
        // and the previous selection survives until that resolves. Without this
        // the buttons briefly re-enable over stale rows, allowing a duplicate
        // operation against outdated state.
        return this.isActing || this.isLoading || this.selectedRowIds.length === 0
    }

    get selectedContext() {
        return this._contextData.find(cd => cd.id === this.selectedContextId)
    }

    get contextDefUrl() {
        if (!this.selectedContext) return ''
        const idParam = btoa(`"${this.selectedContextId}"`)
        const nameParam = btoa(`"${this.selectedContext.developerName}"`)
        const tab = btoa('"details"')
        const status = btoa('"Active"')
        return `/lightning/setup/ContextManagementSetupNode/home#contextIdFromLandingPage=${idParam}&contextDefinitionNameFromLandingPage=${nameParam}&activeTab=${tab}&status=${status}`
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

    // Refreshes the rows from Apex (and clears the error banner). It does NOT
    // re-run the failed activate/deactivate operation, so it is labelled
    // "Refresh", not "Retry".
    handleRefresh() {
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
        // stopPolling (not cancelPolling): bump _pollRequestId so an already
        // in-flight poll() is invalidated too. cancelPolling only clears the
        // timers, so on an A -> B -> A switch a pending check would find both
        // requestId and contextId unchanged and could still fire its callback.
        this.stopPolling()
        this.selectedContextId = event.detail.value
        this.selectedRowIds = []
        this.loadExpressionSets()
    }

    handleRowSelection(event) {
        this.selectedRowIds = event.detail.selectedRows.map(r => r.definitionId)
    }

    handleSort(event) {
        this.sortedByColumn = event.detail.fieldName
        this.sortDirection = event.detail.sortDirection
        this.expressionSets = this.applySort([...this.expressionSets])
    }

    applySort(rows) {
        const column = this.columns.find(c => c.fieldName === this.sortedByColumn)
        const field = column?.sortingFieldName || this.sortedByColumn
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
        // Deactivation targets rows linked to THIS context (the server rejects
        // unlinked defs). A linked non-Constraint qualifies only when it has an
        // active version to deactivate; a linked Constraint qualifies regardless
        // of version state, since deactivation also removes its context junction.
        const eligible = selectedRows.filter(
            es => es.isLinked && (es.hasActiveVersion || es.usageType === 'Constraint')
        )
        if (selectedRows.length === 0) {
            this.showToast('Info', 'No Expression Sets selected.', 'info')
            return
        }
        if (eligible.length === 0) {
            this.showToast(
                'Info',
                `None of the ${selectedRows.length} selected Expression Set(s) can be deactivated for this Context Definition.`,
                'info'
            )
            return
        }

        const defIds = eligible.map(es => es.definitionId)

        // Capture the context this action was submitted against. A context switch
        // while the enqueue promise is pending cancels no timer (polling has not
        // started), so without this the continuation would read the NEW
        // selectedContextId and poll the old job/defIds against it.
        const actionContextId = this.selectedContextId

        this.isActing = true
        this.previousError = ''
        try {
            const jobId = await deactivateExpressionSets({
                contextDefinitionId: actionContextId,
                definitionIds: defIds
            })
            if (actionContextId !== this.selectedContextId) return
            this.showToast('Deactivating', `Deactivating ${defIds.length} Expression Set(s)...`, 'info')
            this.pollStatus(jobId, getDeactivateStatus, actionContextId, defIds, 0, ids => {
                this.showToast('Deactivated', `${ids.size} Expression Set(s) deactivated.`, 'success')
                // Reload from Apex: for Constraint sets the queueable deletes the
                // context junction, so the local rows' isLinked/linked count are now
                // stale. A reload reflects the removed junction and refreshed counts.
                this.refreshAfterJunctionChange()
            })
        } catch (error) {
            if (actionContextId !== this.selectedContextId) return
            this.isActing = false
            this.showToast('Error', this.reduceErrors(error), 'error')
        }
    }

    async handleActivate() {
        const selectedSet = new Set(this.selectedRowIds)
        const selectedRows = this.expressionSets.filter(es => selectedSet.has(es.definitionId))
        // Activation targets rows that need a version activated (no active
        // version) OR an unlinked Constraint that needs its context junction
        // created — the latter can already be active (linked to another context)
        // yet still needs linking here.
        const eligible = selectedRows.filter(
            es => !es.hasActiveVersion || (es.usageType === 'Constraint' && !es.isLinked)
        )
        if (selectedRows.length === 0) {
            this.showToast('Info', 'No Expression Sets selected.', 'info')
            return
        }
        if (eligible.length === 0) {
            this.showToast('Info', `All ${selectedRows.length} selected Expression Set(s) are already active and linked.`, 'info')
            return
        }

        const defIds = eligible.map(es => es.definitionId)

        // See handleDeactivate — capture the submitted context so a switch during
        // the pending enqueue promise abandons this continuation instead of
        // polling the old job against the newly selected context.
        const actionContextId = this.selectedContextId

        this.isActing = true
        this.previousError = ''
        try {
            const jobId = await activateExpressionSets({
                contextDefinitionId: actionContextId,
                definitionIds: defIds
            })
            if (actionContextId !== this.selectedContextId) return
            this.showToast('Activating', `Activating ${defIds.length} Expression Set(s)...`, 'info')
            this.pollStatus(jobId, getActivateStatus, actionContextId, defIds, ACTIVATE_DELAY, () => {
                this.showToast('Activated', 'Expression Sets activated successfully.', 'success')
                // Activation creates a context junction for unlinked Constraint sets,
                // so refresh both the row query and the cacheable Context Definition
                // wire that supplies the "[N linked Expression Sets]" combobox label.
                this.refreshAfterJunctionChange()
            })
        } catch (error) {
            if (actionContextId !== this.selectedContextId) return
            this.isActing = false
            this.showToast('Error', this.reduceErrors(error), 'error')
        }
    }

    // --- Data Loading ---

    // Re-run both data sources after an activate/deactivate that can add or
    // remove a Context Definition junction: the row query (isLinked / status)
    // and the cacheable getContextDefinitions wire (the linked-count label).
    refreshAfterJunctionChange() {
        this.loadExpressionSets()
        if (this._wiredContexts) {
            refreshApex(this._wiredContexts)
        }
    }

    async loadExpressionSets() {
        const requestId = ++this._loadRequestId
        const contextDefinitionId = this.selectedContextId
        this.isLoading = true
        try {
            const data = await getLinkedExpressionSets({ contextDefinitionId })
            if (requestId !== this._loadRequestId || contextDefinitionId !== this.selectedContextId) return
            const rows = data.map(es => this.decorateExpressionSetRow(es))
            this.expressionSets = this.applySort(rows)
            this.selectedRowIds = []
        } catch (error) {
            if (requestId !== this._loadRequestId || contextDefinitionId !== this.selectedContextId) return
            this.expressionSets = []
            this.selectedRowIds = []
            this.showToast('Error', `Failed to load Expression Sets: ${this.reduceErrors(error)}`, 'error')
        } finally {
            if (requestId === this._loadRequestId && contextDefinitionId === this.selectedContextId) {
                this.isLoading = false
            }
        }
    }

    decorateExpressionSetRow(es) {
        return {
            ...es,
            recordUrl: `/lightning/r/ExpressionSet/${es.expressionSetId}/view`,
            // Text (not icon-only) so the link state reaches screen readers and
            // unlinked rows are not blank.
            linkStatusText: es.isLinked ? 'Linked' : 'Unlinked',
            linkSortValue: es.isLinked ? 'Linked' : 'Unlinked',
            linkStatusIcon: es.isLinked ? 'utility:link' : '',
            linkStatusClass: es.isLinked ? 'slds-text-color_success' : '',
            statusText: es.hasActiveVersion ? 'Active' : 'Inactive',
            statusIcon: es.hasActiveVersion ? 'action:approval' : 'action:close',
            statusClass: es.hasActiveVersion ? 'slds-text-color_success' : 'slds-text-color_error',
            latestVersionLabel: es.latestVersionNumber ? `v${es.latestVersionNumber}` : '',
            latestVersionUrl: this.buildVersionUrl(es)
        }
    }

    buildVersionUrl(es) {
        if (!es.latestVersionId) return ''
        if (es.usageType === 'Constraint') {
            const versionName = encodeURIComponent(`${es.label} V${es.latestVersionNumber}`)
            return `/builder_industries_constraints/constraintBuilder.app?constraintId=${es.expressionSetId}&versionId=${es.latestVersionId}&versionName=${versionName}&contextId=${this.selectedContextId}`
        }
        return `/builder_industries_interaction_rule/ruleBuilder.app?ruleId=${es.latestVersionId}`
    }

    // --- Polling ---

    pollStatus(jobId, statusFn, contextId, defIds, initialDelay, onComplete) {
        this.cancelPolling()
        const requestId = ++this._pollRequestId
        this.isActing = true
        let isChecking = false
        let jobAttempts = 0
        let domainAttempts = 0
        const poll = async () => {
            if (requestId !== this._pollRequestId || contextId !== this.selectedContextId) return
            if (isChecking) return
            isChecking = true
            try {
                const jobStatus = await getJobStatus({ jobId })
                if (requestId !== this._pollRequestId || contextId !== this.selectedContextId) return
                if (jobStatus.state === 'running') {
                    jobAttempts += 1
                    if (jobAttempts >= MAX_JOB_POLL_ATTEMPTS) {
                        this.stopPolling()
                        this.setPreviousError('Operation is still running. Refresh to check status or try again later.')
                        await this.loadExpressionSets()
                    }
                    return
                }
                if (jobStatus.state === 'failed' || jobStatus.state === 'unknown') {
                    this.stopPolling()
                    this.setPreviousError(jobStatus.message || 'Operation did not complete.')
                    await this.loadExpressionSets()
                    return
                }

                const status = await statusFn({ contextDefinitionId: contextId, definitionIds: defIds })
                if (requestId !== this._pollRequestId || contextId !== this.selectedContextId) return
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
                // Recheck the stale-request guard first: the try's guards only
                // run after a successful await, so a reject after a context
                // switch / disconnect jumps straight here. Without this the
                // cancelled poll would still toast, set the banner, and reload
                // the now-current context.
                if (requestId !== this._pollRequestId || contextId !== this.selectedContextId) return
                // Terminal like the branches above: the queueable may have
                // succeeded even though this status check failed, so reload the
                // possibly-mutated rows and surface the refreshable inline banner
                // rather than leaving stale status with no Refresh affordance.
                // The toast still reports the genuine callout error.
                this.stopPolling()
                const message = `Failed to check operation status: ${this.reduceErrors(error)}`
                this.showToast('Error', message, 'error')
                this.setPreviousError(message)
                await this.loadExpressionSets()
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

    cancelPolling() {
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

    stopPolling() {
        this._pollRequestId += 1
        this.cancelPolling()
    }

    disconnectedCallback() {
        this.stopPolling()
    }

    showToast(title, message, variant) {
        const mode = variant === 'error' ? 'sticky' : 'dismissable'
        this.dispatchEvent(new ShowToastEvent({ title, message, variant, mode }))
    }

    reduceErrors(error) {
        if (!error) return 'Unknown error'
        if (Array.isArray(error.body)) {
            return error.body.map(e => e.message).filter(Boolean).join(', ')
        }
        if (typeof error.body?.message === 'string') return error.body.message
        if (typeof error.message === 'string') return error.message
        return 'Unknown error'
    }
}
