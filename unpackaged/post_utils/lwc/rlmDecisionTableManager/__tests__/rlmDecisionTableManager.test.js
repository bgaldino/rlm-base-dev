import { createElement } from 'lwc'
import RlmDecisionTableManager from 'c/rlmDecisionTableManager'
import getDecisionTables from '@salesforce/apex/RLM_DecisionTableManagerController.getDecisionTables'
import refreshTables from '@salesforce/apex/RLM_DecisionTableManagerController.refreshTables'
import getRefreshStatus from '@salesforce/apex/RLM_DecisionTableManagerController.getRefreshStatus'

jest.mock(
    '@salesforce/apex/RLM_DecisionTableManagerController.getDecisionTables',
    () => ({ default: jest.fn() }),
    { virtual: true }
)
jest.mock(
    '@salesforce/apex/RLM_DecisionTableManagerController.refreshTables',
    () => ({ default: jest.fn() }),
    { virtual: true }
)
jest.mock(
    '@salesforce/apex/RLM_DecisionTableManagerController.getRefreshStatus',
    () => ({ default: jest.fn() }),
    { virtual: true }
)

const POLL_INTERVAL_MS = 4000

const TABLE = {
    apiName: 'Derived_Pricing_Entries_Decision_Table',
    label: 'Derived Pricing Entries',
    usageType: 'PricingDiscovery',
    staleness: 'Stale',
    stalenessReason: 'A source row changed after the last sync.',
    refreshStatus: 'Completed',
    lastSyncDate: '2026-10-27T22:15:53.000Z',
    lastIncrementalSyncDate: null,
    latestSyncDate: '2026-10-27T22:15:53.000Z',
    latestSyncKind: 'full',
    contributingObjects: ['PricebookEntry'],
    readsObjects: ['PricebookEntry']
}

// Settles the microtask queue: Apex mocks resolve on it, and so do LWC re-renders. Tests
// that fake timers fake only the poll's setInterval (FAKE_POLL_ONLY), so this still resolves.
const FAKE_POLL_ONLY = { doNotFake: ['setTimeout', 'clearTimeout'] }
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0))

async function mount() {
    const element = createElement('c-rlm-decision-table-manager', { is: RlmDecisionTableManager })
    document.body.appendChild(element)
    await flushPromises()
    return element
}

async function openDetails(element, row = TABLE) {
    const table = element.shadowRoot.querySelector('lightning-datatable')
    table.dispatchEvent(
        new CustomEvent('rowaction', { detail: { action: { name: 'details' }, row } })
    )
    await flushPromises()
    return element.shadowRoot.querySelector('section[role="dialog"]')
}

describe('c-rlm-decision-table-manager', () => {
    // Every mock gets a default, so no test inherits another's implementation (a hung
    // promise, say) and passes or fails by run order.
    beforeEach(() => {
        getDecisionTables.mockResolvedValue([TABLE])
        refreshTables.mockResolvedValue({ queuedCount: 0, failedCount: 0, failedApiNames: [], unknownApiNames: [] })
        getRefreshStatus.mockResolvedValue([])
    })

    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild)
        }
        // Reset, not clear: implementations and spies too, even when an assertion failed
        // before a test could restore its own.
        jest.resetAllMocks()
        jest.restoreAllMocks()
        jest.useRealTimers()
    })

    describe('detail dialog focus', () => {
        it('moves focus to the dialog section when it opens, so the dialog is announced', async () => {
            const element = await mount()
            const focus = jest.spyOn(HTMLElement.prototype, 'focus')

            const dialog = await openDetails(element)

            expect(dialog).not.toBeNull()
            expect(dialog.getAttribute('tabindex')).toBe('-1')
            expect(focus.mock.contexts).toContain(dialog)
        })

        // The round-15 bug: as the section's first child, the leading sentinel was the next
        // stop after the section on a forward Tab, so Tab bounced to the footer and skipped
        // every help control in between.
        it('keeps the leading sentinel outside the section, immediately before it', async () => {
            const element = await mount()
            const dialog = await openDetails(element)

            const leading = dialog.previousElementSibling
            expect(leading).not.toBeNull()
            expect(leading.classList.contains('dtm-focus-sentinel')).toBe(true)
            expect(dialog.firstElementChild.classList.contains('dtm-focus-sentinel')).toBe(false)
        })

        it('keeps the trailing sentinel as the last child inside the section', async () => {
            const element = await mount()
            const dialog = await openDetails(element)

            const sentinels = dialog.querySelectorAll('.dtm-focus-sentinel')
            expect(sentinels).toHaveLength(1)
            expect(dialog.lastElementChild).toBe(sentinels[0])
        })

        it('wraps Tab off the end back to the section', async () => {
            const element = await mount()
            const dialog = await openDetails(element)
            const focusDialog = jest.spyOn(dialog, 'focus')

            dialog.lastElementChild.dispatchEvent(new CustomEvent('focusin'))

            expect(focusDialog).toHaveBeenCalled()
        })

        it('wraps Shift+Tab off the front to the Close button', async () => {
            const element = await mount()
            const dialog = await openDetails(element)
            const close = dialog.querySelector('.slds-modal__footer lightning-button')
            const focusClose = jest.spyOn(close, 'focus')

            dialog.previousElementSibling.dispatchEvent(new CustomEvent('focusin'))

            expect(focusClose).toHaveBeenCalled()
        })

        it('handles Shift+Tab from the section itself as a backstop', async () => {
            const element = await mount()
            const dialog = await openDetails(element)
            const close = dialog.querySelector('.slds-modal__footer lightning-button')
            const focusClose = jest.spyOn(close, 'focus')
            const event = new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, cancelable: true })

            dialog.dispatchEvent(event)

            expect(event.defaultPrevented).toBe(true)
            expect(focusClose).toHaveBeenCalled()
        })

        it('closes on Escape and returns focus to the table', async () => {
            const element = await mount()
            const dialog = await openDetails(element)
            const table = element.shadowRoot.querySelector('lightning-datatable')
            const focusTable = jest.spyOn(table, 'focus')

            dialog.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
            await flushPromises()

            expect(element.shadowRoot.querySelector('section[role="dialog"]')).toBeNull()
            expect(focusTable).toHaveBeenCalled()
        })
    })

    // The dialog's row is derived from this.rows on every read. A captured reference froze
    // at open time while the poll and the reload after it replaced the list behind it.
    it('shows a refresh failure in the open dialog once the poll reports it', async () => {
        jest.useFakeTimers(FAKE_POLL_ONLY)
        const failed = { ...TABLE, refreshStatus: 'Failed', refreshFailureReason: 'Source query timed out.' }
        getDecisionTables.mockResolvedValueOnce([TABLE]).mockResolvedValue([failed])
        refreshTables.mockResolvedValue({ queuedCount: 1, failedCount: 0, failedApiNames: [], unknownApiNames: [] })
        getRefreshStatus.mockResolvedValue([failed])

        const element = await mount()
        const dialog = await openDetails(element)
        expect(dialog.textContent).not.toContain('Source query timed out.')

        const stale = [...element.shadowRoot.querySelectorAll('lightning-button')]
            .find((b) => b.label === 'Refresh stale only')
        stale.click()
        await flushPromises()
        jest.advanceTimersByTime(POLL_INTERVAL_MS)
        await flushPromises()

        expect(getRefreshStatus).toHaveBeenCalledTimes(1)
        const open = element.shadowRoot.querySelector('section[role="dialog"]')
        expect(open.textContent).toContain('Last refresh failed')
        expect(open.textContent).toContain('Source query timed out.')
    })

    // Each await resumes whether or not the component still exists. Without the guard,
    // queueRefresh went on to open a poll interval that nothing would ever clear.
    it('does not start polling when removed while a refresh request is in flight', async () => {
        jest.useFakeTimers(FAKE_POLL_ONLY)
        let resolveRefresh
        refreshTables.mockReturnValue(new Promise((resolve) => { resolveRefresh = resolve }))
        getRefreshStatus.mockResolvedValue([TABLE])

        const element = await mount()
        const stale = [...element.shadowRoot.querySelectorAll('lightning-button')]
            .find((b) => b.label === 'Refresh stale only')
        stale.click()
        await flushPromises()
        expect(refreshTables).toHaveBeenCalledTimes(1)
        document.body.removeChild(element)

        resolveRefresh({ queuedCount: 1, failedCount: 0, failedApiNames: [], unknownApiNames: [] })
        await flushPromises()
        jest.advanceTimersByTime(POLL_INTERVAL_MS * 3)
        await flushPromises()

        expect(getRefreshStatus).not.toHaveBeenCalled()
    })

    // The poll's continuation has the same guard. Removing the component clears the
    // interval, so only the guard stops a status that lands afterwards from reloading the
    // table and toasting on a component nobody can see. (loadTables has the third guard;
    // its unguarded path only assigns state on the dead component, which nothing observes.)
    it('does not reload when removed while a poll is in flight', async () => {
        jest.useFakeTimers(FAKE_POLL_ONLY)
        refreshTables.mockResolvedValue({ queuedCount: 1, failedCount: 0, failedApiNames: [], unknownApiNames: [] })
        let resolveStatus
        getRefreshStatus.mockReturnValue(new Promise((resolve) => { resolveStatus = resolve }))

        const element = await mount()
        const toasts = jest.fn()
        element.addEventListener('lightning__showtoast', toasts)
        const stale = [...element.shadowRoot.querySelectorAll('lightning-button')]
            .find((b) => b.label === 'Refresh stale only')
        stale.click()
        await flushPromises()
        jest.advanceTimersByTime(POLL_INTERVAL_MS)
        await flushPromises()
        expect(getRefreshStatus).toHaveBeenCalledTimes(1)
        // The "queued" toast proves the listener hears toasts, so the count below means something.
        expect(toasts).toHaveBeenCalledTimes(1)
        document.body.removeChild(element)

        resolveStatus([{ ...TABLE, refreshStatus: 'Failed' }])
        await flushPromises()

        expect(getDecisionTables).toHaveBeenCalledTimes(1)
        expect(toasts).toHaveBeenCalledTimes(1)
    })

    describe('reads-object filter', () => {
        const RATES = { ...TABLE, apiName: 'Rate_Card_Entries_2', label: 'Rate Card Entries', readsObjects: ['RateCardEntry'] }
        const ASSET_RATES = { ...TABLE, apiName: 'Asset_Rate_Decision_Table_V2', label: 'Asset Rate', readsObjects: ['AssetRateCardEntry'] }
        // Reads RateCardEntry only through a column, and its verdict could not be computed, so
        // contributingObjects is empty: the case the filter exists for.
        const RESOLUTION = {
            ...TABLE, apiName: 'Pricebook_Rate_Card_Decision_Table', label: 'Pricebook Rate Card',
            staleness: 'Not comparable', contributingObjects: [], readsObjects: ['PriceBookRateCard', 'RateCardEntry']
        }

        async function filterTo(element, objectName) {
            const combo = [...element.shadowRoot.querySelectorAll('lightning-combobox')]
                .find((c) => c.label === 'Reads object')
            combo.dispatchEvent(new CustomEvent('change', { detail: { value: objectName } }))
            await flushPromises()
        }

        beforeEach(() => {
            getDecisionTables.mockResolvedValue([RATES, ASSET_RATES, RESOLUTION, TABLE])
        })

        it('offers each object some table reads, by exact name', async () => {
            const element = await mount()
            const combo = [...element.shadowRoot.querySelectorAll('lightning-combobox')]
                .find((c) => c.label === 'Reads object')
            expect(combo.options.map((o) => o.value)).toEqual(
                ['all', 'AssetRateCardEntry', 'PriceBookRateCard', 'PricebookEntry', 'RateCardEntry'])
            expect(combo.options[4].label).toBe('Reads: RateCardEntry')
        })

        it('shows every table that reads the object, Not comparable included, and no near-namesake', async () => {
            const element = await mount()
            await filterTo(element, 'RateCardEntry')

            const shown = element.shadowRoot.querySelector('lightning-datatable').data.map((r) => r.apiName)
            expect(shown.sort()).toEqual(['Pricebook_Rate_Card_Decision_Table', 'Rate_Card_Entries_2'])
        })

        it('refreshes exactly those tables with Refresh all shown', async () => {
            const element = await mount()
            await filterTo(element, 'RateCardEntry')
            const refreshShown = [...element.shadowRoot.querySelectorAll('lightning-button')]
                .find((b) => b.label.startsWith('Refresh all shown'))
            expect(refreshShown.label).toBe('Refresh all shown (2)')

            refreshShown.click()
            await flushPromises()

            expect(refreshTables).toHaveBeenCalledTimes(1)
            expect(refreshTables.mock.calls[0][0].apiNames.sort())
                .toEqual(['Pricebook_Rate_Card_Decision_Table', 'Rate_Card_Entries_2'])
        })
    })

    it('refreshes only the selected rows the filters still show', async () => {
        const OTHER = { ...TABLE, apiName: 'Other_Table', label: 'Other', usageType: 'DefaultRating', readsObjects: ['RateCardEntry'] }
        getDecisionTables.mockResolvedValue([TABLE, OTHER])
        refreshTables.mockResolvedValue({ queuedCount: 1, failedCount: 0, failedApiNames: [], unknownApiNames: [] })
        const element = await mount()
        const table = element.shadowRoot.querySelector('lightning-datatable')
        table.dispatchEvent(new CustomEvent('rowselection', { detail: { selectedRows: [TABLE, OTHER] } }))
        await flushPromises()
        const combo = [...element.shadowRoot.querySelectorAll('lightning-combobox')]
            .find((c) => c.label === 'Reads object')
        combo.dispatchEvent(new CustomEvent('change', { detail: { value: 'RateCardEntry' } }))
        await flushPromises()

        const selected = [...element.shadowRoot.querySelectorAll('lightning-button')]
            .find((b) => b.label.startsWith('Refresh') && b.label.endsWith('selected'))
        expect(selected.label).toBe('Refresh 1 selected')
        selected.click()
        await flushPromises()

        expect(refreshTables.mock.calls[0][0].apiNames).toEqual(['Other_Table'])
    })

    describe('load errors', () => {
        it('shows the Apex message', async () => {
            getDecisionTables.mockRejectedValue({ body: { message: 'Insufficient access to DecisionTable' } })

            const element = await mount()

            expect(element.shadowRoot.textContent).toContain('Insufficient access to DecisionTable')
        })

        it('shows the message of a thrown Error', async () => {
            getDecisionTables.mockRejectedValue(new Error('Network unreachable'))

            const element = await mount()

            expect(element.shadowRoot.textContent).toContain('Network unreachable')
        })

        it('shows a recovery message, not the raw error, for an unrecognised shape', async () => {
            const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {})
            getDecisionTables.mockRejectedValue({ fault: { code: 'X-123', detail: 'internal' } })

            const element = await mount()

            const text = element.shadowRoot.textContent
            expect(text).toContain('Reload the page and try again')
            expect(text).not.toContain('X-123')
            expect(text).not.toContain('{')
            // The raw shape still reaches someone who can act on it.
            expect(consoleError).toHaveBeenCalled()
        })
    })
})
