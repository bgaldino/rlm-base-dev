import { LightningElement, track } from 'lwc'
import { ShowToastEvent } from 'lightning/platformShowToastEvent'
import getDecisionTables from '@salesforce/apex/RLM_DecisionTableManagerController.getDecisionTables'
import refreshTables from '@salesforce/apex/RLM_DecisionTableManagerController.refreshTables'
import getRefreshStatus from '@salesforce/apex/RLM_DecisionTableManagerController.getRefreshStatus'

const POLL_INTERVAL_MS = 4000
const MAX_POLL_ATTEMPTS = 45 // ~3 minutes; a refresh that outlives this is reported, not hidden

// Verdicts as returned by the Apex controller. Only FRESH and STALE are computed
// comparisons; the other two mean "not established", and must never be presented
// as reassurance.
const VERDICT_FRESH = 'Fresh'
const VERDICT_STALE = 'Stale'
const VERDICT_UNCOMPUTED = 'Not comparable'
const VERDICT_UNKNOWN = 'Unknown'

// A refresh is finished when RefreshStatus leaves this set. Anything unrecognised
// counts as still running so the poll keeps watching rather than declaring success.
const RUNNING_REFRESH_STATUSES = new Set(['Initiated', 'In Progress', 'Queued', 'Processing'])

// ⚠ Leaving the running set is NOT the same as succeeding. Failed and
// CompletedWithWarnings are terminal too, and treating "not running" as "done" put a
// failed refresh behind a green "Refresh complete" toast — the one outcome a user most
// needs to see.
//
// SUCCESS is the enumerated set, not failure: a status this file has never heard of
// then reports as a problem rather than as an all-clear. Enumerating failures instead
// would make every new platform status silently successful.
const SUCCESS_REFRESH_STATUSES = new Set(['Completed', 'Success', 'Succeeded'])

// Only Fresh and Stale are computed comparisons. Written as "is one of the two
// established verdicts" rather than "is one of the two unclear ones" so a verdict
// added to the controller later lands in the not-established bucket by default —
// an unrecognised value must not be able to escape every tile and go uncounted.
const isEstablished = (verdict) => verdict === VERDICT_FRESH || verdict === VERDICT_STALE

const FILTER_ALL = 'all'
// The "not established" tile covers BOTH non-committal verdicts. It is deliberately
// not keyed to one of them: the count and the filter have to select the same rows,
// and counting Unknown while filtering only Not-comparable made the tile lie about
// how many rows clicking it would show.
const FILTER_UNCLEAR = 'unclear'

// Usage types get a distinct ICON rather than a distinct colour: SLDS exposes only a
// handful of icon colours and there are more usage types than that, so shape is what
// distinguishes them at a glance. The label stays the FULL usage type on purpose —
// reading it here is how you learn which value to refresh by.
//
// ⚠ Only use icon names verified to render. An SLDS name that does not exist draws
// NOTHING and logs nothing, and the fallback below cannot save you because the key is
// mapped — the lookup succeeds and hands back a dead name. utility:product_request,
// utility:products and utility:tag all silently drew blank here before this was
// caught by looking at the rendered table.
const USAGE_ICONS = {
    DefaultPricing: 'utility:moneybag',
    PricingDiscovery: 'utility:search',
    DefaultRating: 'utility:trending',
    RatingDiscovery: 'utility:filterList',
    // Same icon as ProductCategoryQualification on purpose: they are the same
    // concept at two grains, so sharing a shape groups them rather than implying a
    // difference that is not there.
    ProductQualification: 'utility:hierarchy',
    ProductCategoryQualification: 'utility:hierarchy',
    RevenueStandardTax: 'utility:percent',
    Bre: 'utility:rules'
}

// Dates are deliberately compact: auto column sizing hands width to the widest
// content, and a full "Jul 26, 2026, 12:49 PM" starves the table-name column. Full
// precision is in the row details.
const COMPACT_DATE = {
    year: '2-digit', month: 'short', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false
}

const COLUMNS = [
    {
        label: 'Decision Table',
        fieldName: 'label',
        type: 'text',
        sortable: true,
        // Never wrap the name. With auto column sizing the column is measured from
        // its widest single-line value, so the full name stays on one line instead
        // of stacking over three rows and dragging every row's height with it.
        wrapText: false
    },
    // No API Name column by design: long enough to dominate the table, rarely what
    // you scan for, still fully searchable, and shown in the row details alongside
    // the source criteria and the reason behind each freshness verdict.
    {
        label: 'Usage Type',
        fieldName: 'usageType',
        type: 'text',
        sortable: true,
        cellAttributes: {
            iconName: { fieldName: 'usageIcon' },
            iconPosition: 'left',
            class: 'slds-text-color_weak slds-current-color'
        }
    },
    {
        label: 'Freshness',
        fieldName: 'staleness',
        type: 'text',
        sortable: true,
        cellAttributes: {
            iconName: { fieldName: 'stalenessIcon' },
            iconPosition: 'left',
            class: { fieldName: 'stalenessClass' }
        }
    },
    {
        label: 'Full Sync',
        fieldName: 'lastSyncDate',
        type: 'date',
        sortable: true,
        typeAttributes: COMPACT_DATE
    },
    // No incremental-sync column while IsIncrementalSyncEnabled is false on every
    // table in a fresh build — it spends width to print the same blank on each row.
    // The timestamp and the reason it cannot be enabled from here are in the details.
    {
        label: 'Refresh',
        fieldName: 'refreshStatus',
        type: 'text',
        sortable: true,
        cellAttributes: { class: { fieldName: 'refreshStatusClass' } }
    },
    {
        type: 'button-icon',
        fixedWidth: 50,
        typeAttributes: {
            iconName: 'utility:info',
            name: 'details',
            title: 'View details',
            alternativeText: 'View details',
            variant: 'bare'
        }
    }
]

export default class RlmDecisionTableManager extends LightningElement {
    @track rows = []
    @track selectedApiNames = []
    @track detailRow

    columns = COLUMNS
    isLoading = true
    isPolling = false
    errorMessage
    searchTerm = ''
    usageTypeFilter = FILTER_ALL
    verdictFilter = FILTER_ALL
    useIncremental = false
    sortedBy = 'usageType'
    sortedDirection = 'asc'
    pollMessage = ''
    pollProgress = 0

    _pollTimer
    _pollAttempts = 0
    _watchedApiNames = []

    connectedCallback() {
        this.loadTables()
    }

    disconnectedCallback() {
        // Leaving the page mid-refresh must not leave a timer running.
        this.stopPolling()
    }

    // ---- data ----------------------------------------------------------------

    async loadTables() {
        this.isLoading = true
        try {
            const data = await getDecisionTables()
            this.rows = data.map((row) => this.decorate(row))
            this.errorMessage = undefined
        } catch (error) {
            this.rows = []
            this.errorMessage = this.readError(error)
        } finally {
            this.isLoading = false
        }
    }

    /** Adds the presentation-only fields the datatable columns bind to. */
    decorate(row) {
        const verdict = row.staleness
        let stalenessIcon = 'utility:question'
        let stalenessClass = 'slds-text-color_weak slds-current-color'
        if (verdict === VERDICT_FRESH) {
            stalenessIcon = 'utility:success'
            stalenessClass = 'slds-text-color_success slds-current-color'
        } else if (verdict === VERDICT_STALE) {
            stalenessIcon = 'utility:warning'
            stalenessClass = 'slds-text-color_error slds-current-color'
        }

        // Unmapped usage types fall back to their raw value rather than to blank,
        // so a new type added by the platform still shows something truthful.
        // An unmapped usage type still gets a neutral icon rather than a blank cell.
        const usageIcon = USAGE_ICONS[row.usageType] || 'utility:record'

        const refreshStatus = row.refreshStatus || ''
        let refreshStatusClass = 'slds-text-color_weak'
        if (refreshStatus === 'Completed') {
            refreshStatusClass = 'slds-text-color_success'
        } else if (refreshStatus.toLowerCase().indexOf('fail') > -1) {
            refreshStatusClass = 'slds-text-color_error'
        }

        return {
            ...row,
            stalenessIcon,
            stalenessClass,
            refreshStatusClass,
            incrementalLabel: row.incrementalEnabled ? 'Enabled' : 'Disabled',
            usageIcon,
            searchBlob: [row.label, row.apiName, row.sourceObject, row.usageType]
                .filter((v) => v)
                .join(' ')
                .toLowerCase()
        }
    }

    // ---- derived state -------------------------------------------------------

    get visibleRows() {
        const term = this.searchTerm.trim().toLowerCase()
        const filtered = this.rows.filter((row) => {
            if (this.usageTypeFilter !== FILTER_ALL && row.usageType !== this.usageTypeFilter) {
                return false
            }
            if (this.verdictFilter === FILTER_UNCLEAR) {
                if (isEstablished(row.staleness)) return false
            } else if (this.verdictFilter !== FILTER_ALL && row.staleness !== this.verdictFilter) {
                return false
            }
            if (term && row.searchBlob.indexOf(term) === -1) {
                return false
            }
            return true
        })
        return this.sortRows(filtered)
    }

    sortRows(rows) {
        const field = this.sortedBy
        const factor = this.sortedDirection === 'asc' ? 1 : -1
        // Copy first: Array.prototype.sort mutates, and the source array is
        // reactive tracked state.
        return [...rows].sort((a, b) => {
            const left = a[field]
            const right = b[field]
            if (left === right) return 0
            // Nulls sort last in both directions so "never synced" rows do not
            // masquerade as the oldest or newest depending on which way you click.
            if (left === null || left === undefined) return 1
            if (right === null || right === undefined) return -1
            return left > right ? factor : -factor
        })
    }

    get hasRows() {
        return this.visibleRows.length > 0
    }

    get usageTypeOptions() {
        const seen = new Set()
        this.rows.forEach((row) => {
            if (row.usageType) seen.add(row.usageType)
        })
        const options = [...seen].sort().map((t) => ({ label: t, value: t }))
        return [{ label: 'All usage types', value: FILTER_ALL }, ...options]
    }

    get summaryTiles() {
        const counts = { total: this.rows.length, fresh: 0, stale: 0, unclear: 0 }
        this.rows.forEach((row) => {
            if (row.staleness === VERDICT_FRESH) counts.fresh += 1
            else if (row.staleness === VERDICT_STALE) counts.stale += 1
            else counts.unclear += 1
        })
        // counts.unclear and FILTER_UNCLEAR select by the same rule, so the number
        // on the tile is the number of rows clicking it shows.
        const tile = (key, label, count, modifier, help) => ({
            key,
            label,
            count,
            help,
            // ⚠ The active filter was signalled by the is-active CLASS alone, which a
            // screen reader cannot see: the tiles are toggle buttons, so which one is
            // selected has to be in the accessibility tree too. String, not boolean —
            // aria-pressed is an attribute value.
            ariaPressed: this.verdictFilter === key ? 'true' : 'false',
            cssClass:
                `dtm-tile dtm-tile_${modifier}` +
                (this.verdictFilter === key ? ' is-active' : '')
        })
        return [
            tile(FILTER_ALL, 'Total', counts.total, 'total', 'Show every decision table'),
            tile(VERDICT_STALE, 'Stale', counts.stale, 'stale',
                'Source changed after the last full sync'),
            tile(VERDICT_FRESH, 'Fresh', counts.fresh, 'fresh',
                'Last full sync is later than the newest source change'),
            tile(FILTER_UNCLEAR, 'Not comparable', counts.unclear, 'unclear',
                `"${VERDICT_UNCOMPUTED}" or "${VERDICT_UNKNOWN}" — freshness was not ` +
                    'established, which is not the same as fresh')
        ]
    }

    get rowCountSummary() {
        const shown = this.visibleRows.length
        const total = this.rows.length
        const selected = this.selectedApiNames.length
        const base = shown === total ? `${total} decision tables` : `${shown} of ${total} decision tables`
        return selected > 0 ? `${base} · ${selected} selected` : base
    }

    get emptyMessage() {
        return this.rows.length === 0
            ? 'No decision tables were returned. You may not have read access to DecisionTable.'
            : 'No decision tables match the current filters.'
    }

    get isBusy() {
        return this.isLoading || this.isPolling
    }

    get staleRows() {
        return this.rows.filter((row) => row.staleness === VERDICT_STALE)
    }

    get refreshSelectedLabel() {
        const n = this.selectedApiNames.length
        return n > 0 ? `Refresh ${n} selected` : 'Refresh selected'
    }

    get refreshVisibleLabel() {
        return `Refresh all shown (${this.visibleRows.length})`
    }

    get isRefreshSelectedDisabled() {
        return this.isBusy || this.selectedApiNames.length === 0
    }

    get isRefreshVisibleDisabled() {
        return this.isBusy || this.visibleRows.length === 0
    }

    get isRefreshStaleDisabled() {
        return this.isBusy || this.staleRows.length === 0
    }

    // ---- events --------------------------------------------------------------

    handleReload() {
        this.loadTables()
    }

    handleSearch(event) {
        this.searchTerm = event.target.value || ''
    }

    handleUsageTypeFilter(event) {
        this.usageTypeFilter = event.detail.value
    }

    handleIncrementalToggle(event) {
        this.useIncremental = event.target.checked
    }

    handleTileFilter(event) {
        const verdict = event.currentTarget.dataset.verdict
        this.verdictFilter = this.verdictFilter === verdict ? FILTER_ALL : verdict
    }

    handleSort(event) {
        this.sortedBy = event.detail.fieldName
        this.sortedDirection = event.detail.sortDirection
    }

    handleRowSelection(event) {
        this.selectedApiNames = event.detail.selectedRows.map((r) => r.apiName)
    }

    handleRowAction(event) {
        if (event.detail.action.name === 'details') {
            // Re-read from rows rather than trusting the event's row copy, so the
            // panel reflects any status merged in by the poll loop since render.
            const apiName = event.detail.row.apiName
            this.detailRow = this.rows.find((r) => r.apiName === apiName) || event.detail.row
            this._focusDialogOnRender = true
        }
    }

    handleCloseDetail() {
        this.detailRow = undefined
        // Send focus back where it came from. Without this, closing the dialog drops
        // the caret at the top of the document and a keyboard user has to tab all the
        // way back to the row they were reading.
        this._restoreFocusOnRender = true
    }

    // ---- modal focus management ----------------------------------------------
    //
    // Required by .cursor/rules/lwc-components.mdc for every custom modal: initial
    // focus, a trap while open, and restoration on close. Without them a keyboard or
    // screen-reader user stays on the controls BEHIND the overlay — the dialog is
    // announced but unreachable, and Tab wanders through the page underneath it.

    renderedCallback() {
        if (this._focusDialogOnRender) {
            this._focusDialogOnRender = false
            const dialog = this.template.querySelector('section[role="dialog"]')
            if (dialog) {
                dialog.focus()
            }
        }
        if (this._restoreFocusOnRender) {
            this._restoreFocusOnRender = false
            const table = this.template.querySelector('lightning-datatable')
            if (table) {
                table.focus()
            }
        }
    }

    /** Tab off the end wraps to the top of the dialog. */
    handleFocusEscapeStart() {
        const dialog = this.template.querySelector('section[role="dialog"]')
        if (dialog) {
            dialog.focus()
        }
    }

    /** Shift+Tab off the front wraps to the dialog's last control. */
    handleFocusEscapeEnd() {
        const closeButton = this.template.querySelector('.slds-modal__footer lightning-button')
        if (closeButton) {
            closeButton.focus()
        }
    }

    handleDetailKeydown(event) {
        if (event.key === 'Escape') {
            event.stopPropagation()
            this.handleCloseDetail()
            return
        }
        // ⚠ The sentinels cover every position INSIDE the dialog, but not the one the
        // dialog opens in. Initial focus sits on the section itself (tabindex="-1", so
        // the dialog is announced rather than a control inside it), and the leading
        // sentinel is the section's first CHILD — after it in tab order, not before.
        // Nothing focusable precedes the section, so Shift+Tab at that first moment
        // walks straight out into the page behind the overlay: the exact escape the
        // trap exists to prevent, available for as long as the user has not tabbed yet.
        // Once focus has moved inside, the sentinels take over and this is inert.
        if (event.key === 'Tab' && event.shiftKey &&
            event.target === this.template.querySelector('section[role="dialog"]')) {
            event.preventDefault()
            this.handleFocusEscapeEnd()
        }
    }

    // ---- row details ---------------------------------------------------------

    // Tints the verdict banner to match the verdict. Unlike the datatable cells,
    // this markup is ours, so component CSS reaches it and real colour is available
    // — including the amber that SLDS has no global text class for.
    get detailVerdictClass() {
        const verdict = this.detailRow && this.detailRow.staleness
        if (verdict === VERDICT_FRESH) return 'dtm-verdict dtm-verdict_fresh'
        if (verdict === VERDICT_STALE) return 'dtm-verdict dtm-verdict_stale'
        return 'dtm-verdict dtm-verdict_unclear'
    }

    get hasContributingObjects() {
        return !!(this.detailRow && this.detailRow.contributingObjects &&
            this.detailRow.contributingObjects.length > 0)
    }

    get contributingObjectsLabel() {
        return this.hasContributingObjects ? this.detailRow.contributingObjects.join(', ') : ''
    }

    get dataSourceSummary() {
        if (!this.detailRow) return ''
        const { dataSourceType, sourceObject } = this.detailRow
        return sourceObject ? `${dataSourceType} · ${sourceObject}` : dataSourceType
    }

    get tableTypeSummary() {
        if (!this.detailRow) return ''
        const { tableType, executionType } = this.detailRow
        return executionType ? `${tableType} · executes via ${executionType}` : tableType
    }

    get matchingSummary() {
        if (!this.detailRow) return ''
        const { conditionType, filterResultBy } = this.detailRow
        const base = `${conditionType} conditions`
        return filterResultBy ? `${base} · filtered by ${filterResultBy}` : base
    }

    get tableStatusSummary() {
        if (!this.detailRow) return ''
        return this.detailRow.isVersioned ? `${this.detailRow.status} · versioned` : this.detailRow.status
    }

    // The incremental timestamp belongs next to the full sync it is so often
    // mistaken for: incremental advances ONLY this one, leaving Last Full Sync
    // untouched, which makes a working incremental refresh look dead.
    get incrementalSyncNote() {
        if (!this.detailRow) return ''
        if (!this.detailRow.lastIncrementalSyncDate) {
            return 'No incremental sync has run.'
        }
        const when = new Date(this.detailRow.lastIncrementalSyncDate).toLocaleString()
        return `Incremental sync last ran ${when}, which does not move this date.`
    }

    get detailCriteriaClass() {
        return this.detailRow && this.detailRow.criteriaApplied
            ? 'dtm-callout dtm-callout_applied'
            : 'dtm-callout dtm-callout_muted'
    }

    // How many of the displayed criteria the check could not reproduce. Drives every
    // caption below, because `criteriaApplied` alone cannot tell "none applied and no
    // verdict" apart from "none applied, objects watched instead, verdict computed".
    get unreproducedCount() {
        return (this.detailRow && this.detailRow.unreproducedCriteria)
            ? this.detailRow.unreproducedCriteria.length
            : 0
    }

    get criteriaHeadline() {
        if (!this.detailRow) return ''
        if (this.detailRow.criteriaApplied) {
            return this.unreproducedCount > 0
                ? 'Partly applied to the freshness check'
                : 'Applied to the freshness check'
        }
        return this.unreproducedCount > 0
            ? 'Watched instead of reproduced'
            : 'Not reproduced by the freshness check'
    }

    // Plain-language note on how the selected table gets its rows. CsvUpload and
    // ContextDefinition tables have no sObject behind them at all, which is why they
    // can never carry a computed freshness verdict.
    get dataSourceExplanation() {
        if (!this.detailRow) return ''
        switch (this.detailRow.dataSourceType) {
            case 'CsvUpload':
                return 'Rows come from an uploaded CSV file. Refreshing re-reads the upload, ' +
                    'so freshness depends on when the file was last uploaded, not on any record.'
            case 'ContextDefinition':
                return 'Rows come from a Context Definition rather than records.'
            case 'MultipleSobjects':
                return 'Rows are assembled from more than one object, so the freshness check ' +
                    'compares against the newest change across the source object and every ' +
                    'other object this table reads columns from.'
            case 'SingleSobject':
                return 'Rows come from records on this object.'
            default:
                return ''
        }
    }

    get hasDetailCriteria() {
        return !!(this.detailRow && this.detailRow.sourceCriteria && this.detailRow.sourceCriteria.length > 0)
    }

    // Zero is a meaningful count, so test for a value rather than truthiness — a
    // table whose source holds nothing is exactly the case worth showing, and `if
    // (count)` would hide it.
    get hasSourceRowCount() {
        return !!this.detailRow && this.detailRow.sourceRowCount !== null &&
            this.detailRow.sourceRowCount !== undefined
    }

    // Full wording, shown on hover. The panel must not scroll, so the long form
    // lives in a title tooltip and only the short form is printed.
    // ⚠ A zero count means two different things, and only one of them licenses the
    // "a refresh would produce an empty table" prediction. When the verdict is
    // Not comparable, the controller has explicitly refused to rule out that the
    // filter was translated too narrowly — in which case rows DO feed the table and a
    // refresh would not be empty. Predicting an empty table there states exactly the
    // conclusion the verdict declined to reach.
    get sourceRowCountExplanation() {
        if (!this.detailRow) return ''
        const scope = this.detailRow.criteriaApplied
            ? 'Rows matching the criteria as this check reproduced them.'
            : 'Rows in the source object.'
        if (this.detailRow.sourceRowCount !== 0) {
            return `${scope} This is the source, not the number of rows in the decision table itself.`
        }
        return this.isVerdictEstablished
            ? `${scope} Nothing feeds this table, so a refresh would produce an empty table.`
            : `${scope} The reproduced filter matched nothing, but it may not match what the ` +
                  'decision table itself matches — so this does not mean a refresh would be empty.'
    }

    get sourceRowCountNote() {
        if (!this.detailRow) return ''
        if (!this.hasSourceRowCount) return 'Source was not counted.'
        if (this.detailRow.sourceRowCount === 0) {
            return this.isVerdictEstablished
                ? 'Nothing feeds this table.'
                : 'Nothing matched the reproduced filter.'
        }
        return this.detailRow.criteriaApplied ? 'Matching the criteria below.' : 'In the source object.'
    }

    get isVerdictEstablished() {
        return !!this.detailRow && isEstablished(this.detailRow.staleness)
    }

    get incrementalShortNote() {
        if (!this.detailRow) return ''
        return this.detailRow.lastIncrementalSyncDate
            ? 'Incremental ran later; it does not move this.'
            : 'No incremental sync has run.'
    }

    get incrementalTooltip() {
        if (!this.detailRow) return ''
        return this.detailRow.incrementalEnabled
            ? 'Incremental refresh advances only the incremental timestamp, never the full sync date.'
            : 'An incremental refresh will not sync while this is disabled.'
    }

    // ⚠ Do NOT name a specific reason here. Criteria go unreproduced for several
    // different reasons — a related-record read, OR/NOT condition logic, an operator
    // with no SOQL equivalent, an ordering comparison on a type with no agreed
    // ordering, a value that does not coerce — and the freshness reason above already
    // states which one applied. A caption asserting one of them sits next to a reason
    // stating another, which is how this comment came to exist.
    get criteriaShortNote() {
        if (!this.detailRow) return ''
        if (!this.detailRow.criteriaApplied) {
            return this.unreproducedCount > 0
                ? 'None were reproduced; the objects they read are watched instead, so the ' +
                      'verdict covers more rows than the table holds.'
                : 'This check could not reproduce these, so no verdict was computed — the ' +
                      'freshness reason above says which one stopped it.'
        }
        if (!this.isVerdictEstablished) {
            return 'These were applied, but the result could not be interpreted — see the reason above.'
        }
        return this.unreproducedCount > 0
            ? `The verdict above covers these rows plus more: ${this.unreproducedCount} could ` +
                  'not be reproduced.'
            : 'The verdict above covers only these rows.'
    }

    // The same criteria mean different things depending on what the check could do
    // with them, so the panel must say which — otherwise a verdict computed over a
    // filtered subset reads as covering the whole object.
    //
    // ⚠ Three states, not two. A criterion that cannot be reproduced is DROPPED from
    // the query rather than guessed at, and the objects it reads are watched instead,
    // so a verdict still gets computed — over a SUPERSET of the table's rows. Saying
    // "freshness was not established" underneath a Fresh banner, as this did, is
    // simply false. Only a criterion that could be neither reproduced nor watched
    // stops the verdict outright.
    get criteriaExplanation() {
        if (!this.detailRow) return ''
        const widened = 'A criterion this check cannot reproduce is dropped from the query ' +
            'rather than approximated, and the objects it reads are watched instead — so the ' +
            'comparison covers MORE rows than the table holds. That can over-report Stale for a ' +
            'row the table excludes; it cannot produce a false all-clear.'
        if (this.detailRow.criteriaApplied) {
            return this.unreproducedCount > 0
                ? `${this.unreproducedCount} of these could not be reproduced. ${widened}`
                : 'These filters were applied to the freshness check, so any verdict above ' +
                      'reflects only the rows that match them.'
        }
        if (this.unreproducedCount > 0) {
            return `None of these reached the query. ${widened}`
        }
        return 'These exclude rows from the table, and this check could neither reproduce nor ' +
            'watch them, so freshness was not established. That happens when the translation ' +
            'would not be provably faithful and nothing observes the difference — condition ' +
            'logic other than plain AND, a related record that cannot be resolved, or a value ' +
            'that resolves at refresh time rather than a literal. The freshness reason above ' +
            'names the one that applied here.'
    }

    get detailCriteriaItems() {
        if (!this.hasDetailCriteria) return []
        return this.detailRow.sourceCriteria.map((text, index) => ({ key: `${index}`, text }))
    }

    handleRefreshSelected() {
        this.queueRefresh(this.selectedApiNames)
    }

    handleRefreshVisible() {
        this.queueRefresh(this.visibleRows.map((r) => r.apiName))
    }

    handleRefreshStale() {
        this.queueRefresh(this.staleRows.map((r) => r.apiName))
    }

    handleStopPolling() {
        this.stopPolling()
        this.toast('Stopped watching', 'The refresh is still running in the org. Reload to see its result.', 'info')
    }

    // ---- refresh + poll ------------------------------------------------------

    async queueRefresh(apiNames) {
        if (!apiNames || apiNames.length === 0) {
            return
        }
        this.errorMessage = undefined
        this.isLoading = true
        try {
            const result = await refreshTables({ apiNames, incremental: this.useIncremental })
            this.isLoading = false

            if (result.errorMessage) {
                this.errorMessage = result.errorMessage
                this.toast('Refresh not started', result.errorMessage, 'error')
                return
            }

            // Report the partial outcome rather than only the happy count.
            const problems = []
            if (result.failedCount > 0) {
                problems.push(`${result.failedCount} failed to queue (${result.failedApiNames.join(', ')})`)
            }
            if (result.unknownApiNames && result.unknownApiNames.length > 0) {
                problems.push(`${result.unknownApiNames.length} not found (${result.unknownApiNames.join(', ')})`)
            }
            const mode = result.incremental ? 'Incremental' : 'Full'
            if (problems.length > 0) {
                this.toast(
                    `${mode} refresh partially queued`,
                    `${result.queuedCount} queued · ${problems.join(' · ')}`,
                    'warning',
                    'sticky'
                )
            } else {
                this.toast(`${mode} refresh queued`, `${result.queuedCount} decision table(s) queued.`, 'success')
            }

            if (result.queuedCount > 0) {
                // Watch only what was actually accepted.
                const failed = new Set(result.failedApiNames || [])
                const unknown = new Set(result.unknownApiNames || [])
                this.startPolling(apiNames.filter((n) => !failed.has(n) && !unknown.has(n)))
            }
        } catch (error) {
            this.isLoading = false
            this.errorMessage = this.readError(error)
            this.toast('Refresh failed', this.errorMessage, 'error', 'sticky')
        }
    }

    startPolling(apiNames) {
        this.stopPolling()
        if (!apiNames || apiNames.length === 0) {
            return
        }
        this._watchedApiNames = apiNames
        this._pollAttempts = 0
        this._pollInFlight = false
        // Evidence that THIS refresh ran, so a stale terminal status from a previous
        // one cannot end the watch on its own. See poll().
        this._observedRunning = new Set()
        // ⚠ Snapshot ALL THREE signals, not just the full-sync date. A fast INCREMENTAL
        // refresh advances lastIncrementalSyncDate and never lastSyncDate; a fast FAILED
        // refresh advances neither but does change the status. Watching only lastSyncDate
        // meant either of those, if it finished before the first 4s poll, sat in
        // stillRunning until the three-minute timeout — safe, but wrong, and it made the
        // component look broken on exactly the fastest cases.
        this._stateAtQueue = new Map(
            apiNames.map((name) => {
                const row = this.rows.find((t) => t.apiName === name) || {}
                return [name, {
                    sync: row.lastSyncDate || '',
                    incremental: row.lastIncrementalSyncDate || '',
                    status: row.refreshStatus || ''
                }]
            })
        )
        this.isPolling = true
        this.pollProgress = 0
        this.pollMessage = `Watching ${apiNames.length} decision table(s)…`
        // A refresh is asynchronous in the org, so reporting when it finishes needs a
        // timer. The rule this suppresses guards against leaked intervals; this one is
        // cleared on every exit path — stopPolling() (completion, timeout, error and
        // the Stop button), disconnectedCallback(), and startPolling() itself before
        // opening a new one, so a second refresh cannot strand the first one's timer.
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        this._pollTimer = setInterval(() => this.poll(), POLL_INTERVAL_MS)
    }

    stopPolling() {
        if (this._pollTimer) {
            clearInterval(this._pollTimer)
            this._pollTimer = undefined
        }
        this.isPolling = false
        this.pollProgress = 0
    }

    async poll() {
        // ⚠ Re-entrancy guard. setInterval fires again whether or not the previous
        // tick's Apex call has returned, so a server slower than POLL_INTERVAL_MS put
        // two polls in flight at once — both incrementing the attempt count, both able
        // to stop polling, reload and toast. Matches the pattern already used by
        // rlmPreProcessOrderAction.
        if (this._pollInFlight) {
            return
        }
        this._pollInFlight = true
        this._pollAttempts += 1
        try {
            const statuses = await getRefreshStatus({ apiNames: this._watchedApiNames })
            this.mergeStatuses(statuses)

            // Iterate the WATCHED names, not the returned rows: a name the query
            // did not return cannot be confirmed finished, and treating it as done
            // would end the watch on an unverified table.
            const byApiName = new Map(statuses.map((s) => [s.apiName, s]))
            const succeeded = []
            const failed = []
            const stillRunning = []
            this._watchedApiNames.forEach((name) => {
                const row = byApiName.get(name)
                // A name the query did not return cannot be confirmed finished.
                if (!row) {
                    stillRunning.push(name)
                    return
                }
                if (RUNNING_REFRESH_STATUSES.has(row.refreshStatus)) {
                    this._observedRunning.add(name)
                    stillRunning.push(name)
                    return
                }
                // ⚠ A terminal status is only THIS refresh's outcome if this refresh
                // actually started. A table sitting on a previous run's "Completed"
                // looks finished on the very first poll, which ended the watch before
                // the queued job had moved. Require evidence: either we saw it running,
                // or its full-sync timestamp advanced past the snapshot taken at queue
                // time. Neither means keep waiting.
                const before = this._stateAtQueue.get(name) || {}
                const started =
                    this._observedRunning.has(name) ||
                    (row.lastSyncDate || '') !== (before.sync || '') ||
                    (row.lastIncrementalSyncDate || '') !== (before.incremental || '') ||
                    (row.refreshStatus || '') !== (before.status || '')
                if (!started) {
                    stillRunning.push(name)
                    return
                }
                if (SUCCESS_REFRESH_STATUSES.has(row.refreshStatus)) {
                    succeeded.push(name)
                } else {
                    // Failed, CompletedWithWarnings, or anything unrecognised that got
                    // this far — reported as not-success rather than folded into it.
                    failed.push(`${name} (${row.refreshStatus || 'no status'})`)
                }
            })

            const done = succeeded.length + failed.length
            this.pollProgress = Math.round((done / this._watchedApiNames.length) * 100)
            this.pollMessage = `Refreshing — ${done} of ${this._watchedApiNames.length} finished`

            if (stillRunning.length === 0) {
                this.stopPolling()
                if (failed.length === 0) {
                    this.toast('Refresh complete', 'All watched decision tables finished.', 'success')
                } else {
                    this.toast(
                        'Refresh finished with problems',
                        `${succeeded.length} completed · ${failed.length} did not: ${failed.join(', ')}. ` +
                            'Open the table in Setup for the failure reason.',
                        'error',
                        'sticky'
                    )
                }
                this.loadTables()
                return
            }

            if (this._pollAttempts >= MAX_POLL_ATTEMPTS) {
                this.stopPolling()
                // Timing out is reported, never silently swallowed.
                const alsoFailed = failed.length > 0 ? ` ${failed.length} failed: ${failed.join(', ')}.` : ''
                this.toast(
                    'Still refreshing',
                    `Stopped watching after ${MAX_POLL_ATTEMPTS} checks. ` +
                        `${stillRunning.length} table(s) were not confirmed finished: ${stillRunning.join(', ')}.` +
                        `${alsoFailed} The refresh continues in the org — reload to see the result.`,
                    'warning',
                    'sticky'
                )
                this.loadTables()
            }
        } catch (error) {
            this.stopPolling()
            this.errorMessage = this.readError(error)
            this.toast('Lost track of the refresh', this.errorMessage, 'error', 'sticky')
        } finally {
            this._pollInFlight = false
        }
    }

    /** Applies polled status onto the existing rows without refetching everything. */
    mergeStatuses(statuses) {
        if (!statuses || statuses.length === 0) {
            return
        }
        const byApiName = new Map(statuses.map((s) => [s.apiName, s]))
        this.rows = this.rows.map((row) => {
            const fresh = byApiName.get(row.apiName)
            if (!fresh) {
                return row
            }
            // Keep every field the full load computed that getRefreshStatus does not:
            // copying its defaults would erase them. criteriaApplied would fall back to
            // false and flip the row details to the wrong explanation of its own
            // criteria; lookupType would go undefined and the Lookup Type row would
            // silently vanish from the pane after the first poll.
            //
            // ⚠ Anything added to DecisionTableInfo that getDecisionTables populates
            // but getRefreshStatus does not belongs in this list. Forgetting one does
            // not fail loudly — the value just disappears mid-refresh.
            return this.decorate({
                ...fresh,
                staleness: row.staleness,
                stalenessReason: row.stalenessReason,
                sourceCriteria: row.sourceCriteria,
                criteriaApplied: row.criteriaApplied,
                sourceRowCount: row.sourceRowCount,
                sourceNewestChange: row.sourceNewestChange,
                lookupType: row.lookupType,
                contributingObjects: row.contributingObjects,
                unreproducedCriteria: row.unreproducedCriteria
            })
        })
    }

    // ---- helpers -------------------------------------------------------------

    readError(error) {
        if (!error) return 'Unknown error.'
        if (error.body && error.body.message) return error.body.message
        if (error.message) return error.message
        return JSON.stringify(error)
    }

    toast(title, message, variant, mode) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant, mode: mode || 'dismissable' }))
    }
}
