import { LightningElement, api, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import getAccountOptions from '@salesforce/apex/RLM_CollectionsDashboardController.getAccountOptions';
import getCurrencyOptions from '@salesforce/apex/RLM_CollectionsDashboardController.getCurrencyOptions';
import getOrgDefaultCurrency from '@salesforce/apex/RLM_CollectionsDashboardController.getOrgDefaultCurrency';
import getDashboardCards from '@salesforce/apex/RLM_CollectionsDashboardController.getDashboardCards';
import getWorklist from '@salesforce/apex/RLM_CollectionsDashboardController.getWorklist';
import getCollectionPlanTasks from '@salesforce/apex/RLM_CollectionsDashboardController.getCollectionPlanTasks';
import getPaymentPromiseSummary from '@salesforce/apex/RLM_CollectionsDashboardController.getPaymentPromiseSummary';
import getMyCollectionPlans from '@salesforce/apex/RLM_CollectionsDashboardController.getMyCollectionPlans';
import getCollectionsProgress from '@salesforce/apex/RLM_CollectionsDashboardController.getCollectionsProgress';

// Figures and lists the page could not read (todo 435). The controller marks each one unavailable with a
// reason: 'refused' (the user may not read it: "You don't have access to ...", ask an administrator) or
// 'failed' (anything else: "... could not be loaded", try again). A failed call (a wire or imperative
// error) is always 'failed'. Nothing unavailable is shown as a zero or an empty "none".
const NOT_AVAILABLE = '\u2014';
const REFUSED = 'refused';
const FAILED = 'failed';
// More rows than a bounded read may take (the controller's ROW_CAP, or what is left of the call's query
// rows): the figure or list would be built from a cut-off read, so narrow the filters instead.
const TOO_MANY = 'tooMany';
const SUBJECTS = {
    invoices: 'invoices',
    debitMemos: 'debit memos',
    unappliedCredits: 'payments',
    unappliedPayments: 'payments',
    paymentSchedules: 'payment schedules',
    collectionPlans: 'collection plans',
    planTasks: 'collection plan tasks',
    worklist: 'the records this list is built from'
};
const EXCLUDED_NAMES = {
    invoices: 'unpaid invoices',
    debitMemos: 'debit memos',
    unappliedCredits: 'unapplied credits',
    unappliedPayments: 'unapplied payments'
};
const WORKLIST_TABS = ['critical', 'highValue', 'disputed'];

// What each section is when it has too many records, and which of the page's filters its reads follow:
// a figure is totalled and a list is listed; `narrowBy` names the filters that narrow it (none for a
// section the filters do not reach). Every unavailableText call names its section's scope.
const ACCOUNT_OR_CURRENCY = 'an account or currency';
const ACCOUNT_ONLY = 'an account';
const SCOPES = {
    // The card figures and the total: every component follows both filters.
    cards: { verb: 'total', narrowBy: ACCOUNT_OR_CURRENCY },
    // Payment promise sums: the schedule items' account and currency.
    promises: { verb: 'total', narrowBy: ACCOUNT_OR_CURRENCY },
    // Progress covers every plan the user can read.
    progress: { verb: 'total', narrowBy: null },
    // Plan tasks follow the account only (the plans carry no currency filter).
    tasks: { verb: 'list', narrowBy: ACCOUNT_ONLY },
    // The user's own plans: no filter.
    plans: { verb: 'list', narrowBy: null },
    // The worklist tabs: Critical and High-Value read invoices by account and currency; Disputed starts from
    // open cases and its account cap, which only the account narrows.
    critical: { verb: 'list', narrowBy: ACCOUNT_OR_CURRENCY },
    highValue: { verb: 'list', narrowBy: ACCOUNT_OR_CURRENCY },
    disputed: { verb: 'list', narrowBy: ACCOUNT_ONLY }
};

function tooManyText(scope) {
    const sentence = `Too many records to ${scope.verb} here.`;
    return scope.narrowBy ? `${sentence} Choose ${scope.narrowBy} to narrow it.` : sentence;
}

function unavailableText(subject, reason, scope) {
    if (reason === REFUSED) return `You don't have access to ${subject}.`;
    if (reason === TOO_MANY) return tooManyText(scope);
    return `${subject.charAt(0).toUpperCase()}${subject.slice(1)} could not be loaded. Refresh the page to try again.`;
}

// The total balance note's wording per reason, as the cards and tooltips word it: `alone` when every
// excluded component has that reason, `short` beside each name when the reasons are mixed, and `action`,
// said once after a mixed list, for the reasons the user can act on.
const NOTE_CLAUSES = {
    [REFUSED]: { alone: "you don't have access to them.", short: "you don't have access" },
    [TOO_MANY]: {
        alone: `too many records to total here. Choose ${SCOPES.cards.narrowBy} to narrow it.`,
        short: 'too many records to total',
        action: `Choose ${SCOPES.cards.narrowBy} to narrow it.`
    },
    [FAILED]: {
        alone: 'they could not be loaded. Refresh the page to try again.',
        short: 'could not be loaded',
        action: 'Refresh the page to try again.'
    }
};
const NOTE_ORDER = [REFUSED, TOO_MANY, FAILED];

function listNames(names) {
    return names.length === 1 ? names[0] : `${names.slice(0, -1).join(', ')} and ${names[names.length - 1]}`;
}

// A section the call itself could not return: unavailable, and a failure, not a refusal.
function failedSection(empty) {
    return { ...empty, unavailable: true, unavailableReason: FAILED };
}

// One state per section, derived in one place (the `sections` getter): loading until that section's
// answer for the current filters arrives, then ready, or unavailable with its reason. Every figure, count,
// list and empty message renders from `ready` only; loading shows nothing, unavailable shows the dash
// and the reason. A filter change puts the sections it affects back to loading.
const LOADING = Object.freeze({ status: 'loading' });
const READY = Object.freeze({ status: 'ready' });
const LOADING_TEXT = 'Loading\u2026';
// A row's lookup that was refused or failed: not "none".
const NOT_AVAILABLE_CELL = 'Not available';

function knownReason(reason) {
    return reason === REFUSED || reason === TOO_MANY ? reason : FAILED;
}

function unavailableState(reason) {
    return { status: 'unavailable', reason: knownReason(reason) };
}

// A wrapper section (promises, progress, tasks, plans): undefined until the server answers.
function wrapperState(wrapper) {
    if (wrapper === undefined) return LOADING;
    if (wrapper === null || wrapper.unavailable) return unavailableState(wrapper?.unavailableReason);
    return READY;
}

// The text of a figure: the formatted value when ready, nothing while loading, the dash when unavailable.
function figureText(state, format) {
    if (state.status === 'ready') return format();
    return state.status === 'loading' ? '' : NOT_AVAILABLE;
}

// A failed worklist call: every tab is not available, next to the error banner.
const WORKLIST_FAILED = {
    criticalFollowUpInvoices: [],
    highValueDelinquents: [],
    disputedInvoices: [],
    unavailable: WORKLIST_TABS,
    unavailableReason: { critical: FAILED, highValue: FAILED, disputed: FAILED }
};

/**
 * AR Recovery Agent Mission Control – premium dashboard with Pulse (KPIs), Aging chart, and Action worklist.
 */
export default class RlmCollectionsDashboard extends NavigationMixin(LightningElement) {
    @api recordId;

    accountOptions = [];
    currencyOptions = [];
    selectedAccountId = '';
    selectedCurrency = '';
    orgDefaultCurrency = 'USD';
    isLoadingOptions = true;
    // undefined = loading, null = the call failed, else the server's answer (see `sections`).
    dashboardData;
    worklistData;
    // The task, promise and plan wrappers from the server ({ items | buckets, unavailable, unavailableReason });
    // undefined until the first answer, which is "still loading", not "none".
    cpTasksState;
    paymentPromiseState;
    myCollectionPlansState;
    collectionsProgressData;
    dataError = null;
    worklistError = null;
    selectedWorklistTab = 'critical';
    selectedAgingKey = null;

    connectedCallback() {
        this.loadOptions();
    }

    loadOptions() {
        this.isLoadingOptions = true;
        Promise.all([
            getOrgDefaultCurrency(),
            getCurrencyOptions(),
            getAccountOptions()
        ])
            .then(([defaultCode, currencyOpts, accountOpts]) => {
                this.orgDefaultCurrency = defaultCode || 'USD';
                this.currencyOptions = Array.isArray(currencyOpts) ? currencyOpts : [];
                this.accountOptions = Array.isArray(accountOpts) ? accountOpts : [];
                if (!this.selectedCurrency) {
                    this.selectedCurrency = '';
                }
                this.dispatchFilterChange();
            })
            .catch(() => {
                this.currencyOptions = [
                    { value: '', label: 'All Currencies' },
                    { value: this.orgDefaultCurrency || 'USD', label: this.orgDefaultCurrency || 'USD' }
                ];
                this.accountOptions = [{ value: '', label: 'All Accounts' }];
                this.selectedCurrency = '';
                this.dispatchFilterChange();
            })
            .finally(() => {
                this.isLoadingOptions = false;
            });
    }

    get effectiveAccountId() {
        return this.selectedAccountId && this.selectedAccountId !== '' ? this.selectedAccountId : null;
    }

    get effectiveCurrencyCode() {
        return this.selectedCurrency && this.selectedCurrency !== '' ? this.selectedCurrency : null;
    }

    @wire(getDashboardCards, { accountId: '$effectiveAccountId', currencyCode: '$effectiveCurrencyCode' })
    wiredDashboard({ error, data }) {
        if (data) {
            this.dashboardData = data;
            this.dataError = undefined;
        } else if (error) {
            this.dashboardData = null;
            this.dataError = this.reduceErrors(error);
        }
    }

    @wire(getCollectionPlanTasks, { accountId: '$effectiveAccountId' })
    wiredCpTasks({ error, data }) {
        if (error) this.cpTasksState = failedSection({ items: [] });
        else if (data) this.cpTasksState = data;
    }

    @wire(getPaymentPromiseSummary, { accountId: '$effectiveAccountId', currencyCode: '$effectiveCurrencyCode' })
    wiredPaymentPromises({ error, data }) {
        if (error) this.paymentPromiseState = failedSection({ buckets: [] });
        else if (data) this.paymentPromiseState = data;
    }

    @wire(getMyCollectionPlans)
    wiredMyCollectionPlans({ error, data }) {
        if (error) this.myCollectionPlansState = failedSection({ items: [] });
        else if (data) this.myCollectionPlansState = data;
    }

    @wire(getCollectionsProgress)
    wiredCollectionsProgress({ error, data }) {
        if (data) this.collectionsProgressData = data;
        // A failed call: not available (could not be loaded), not zero averages.
        else if (error) this.collectionsProgressData = failedSection({});
    }

    @wire(getWorklist, { accountId: '$effectiveAccountId', currencyCode: '$effectiveCurrencyCode' })
    wiredWorklist({ error, data }) {
        if (data) {
            this.worklistData = data;
            this.worklistError = undefined;
        } else if (error) {
            this.worklistData = WORKLIST_FAILED;
            this.worklistError = this.reduceErrors(error);
        }
    }

    get filterContext() {
        return {
            accountId: this.selectedAccountId || null,
            currencyCode: this.selectedCurrency || this.orgDefaultCurrency || 'USD'
        };
    }

    get displayCurrency() {
        return this.selectedCurrency || this.orgDefaultCurrency || 'USD';
    }

    get selectedAccountLabel() {
        if (!this.selectedAccountId) return 'All Accounts';
        const found = this.accountOptions.find((opt) => opt.value === this.selectedAccountId);
        return found ? found.label : 'Selected account';
    }

    get selectedCurrencyLabel() {
        if (!this.selectedCurrency) return 'All Currencies';
        const found = this.currencyOptions.find((opt) => opt.value === this.selectedCurrency);
        return found ? found.label : this.selectedCurrency;
    }

    // A filter change puts every section that reads it back to loading, so the previous filter's figures
    // never show under the new "Viewing:" label. Choosing the same value again changes nothing (the wires
    // would not answer again).
    handleAccountChange(event) {
        const value = event.detail.value || '';
        if (value === this.selectedAccountId) return;
        this.selectedAccountId = value;
        this.resetFilteredSections();
        this.cpTasksState = undefined;
        this.dispatchFilterChange();
    }

    handleCurrencyChange(event) {
        const value = event.detail.value || '';
        if (value === this.selectedCurrency) return;
        this.selectedCurrency = value;
        this.resetFilteredSections();
        this.dispatchFilterChange();
    }

    resetFilteredSections() {
        this.dashboardData = undefined;
        this.dataError = undefined;
        this.paymentPromiseState = undefined;
        this.worklistData = undefined;
        this.worklistError = undefined;
    }

    // Every section's state, in one place.
    get sections() {
        const data = this.dashboardData;
        let cards = READY;
        if (data === undefined) cards = LOADING;
        else if (data === null) cards = unavailableState(FAILED);
        const component = (key) => {
            if (cards !== READY) return cards;
            return (data.unavailable || []).includes(key) ? unavailableState(data.unavailableReason?.[key]) : READY;
        };
        // No total without the unpaid invoices (the controller returns none): it is unavailable for the
        // invoices' reason. Without debit memos, credits or payments it is a partial total, labelled.
        let total = cards;
        if (cards === READY && data.totalBalance == null) {
            const invoices = component('invoices');
            total = invoices === READY ? unavailableState(FAILED) : invoices;
        }
        const worklist = (tab) => {
            if (this.worklistData === undefined) return LOADING;
            return (this.worklistData.unavailable || []).includes(tab)
                ? unavailableState(this.worklistData.unavailableReason?.[tab])
                : READY;
        };
        return {
            cards,
            invoices: component('invoices'),
            payments: component('unappliedPayments'),
            paymentCount: component('unappliedPaymentCount'),
            total,
            promises: wrapperState(this.paymentPromiseState),
            progress: wrapperState(this.collectionsProgressData),
            tasks: wrapperState(this.cpTasksState),
            plans: wrapperState(this.myCollectionPlansState),
            worklistTab: worklist(this.selectedWorklistTab)
        };
    }

    handleWorklistTab(event) {
        const tab = event.currentTarget?.dataset?.tab;
        if (tab) this.selectedWorklistTab = tab;
    }

    handleWorklistTabKeydown(event) {
        const key = event.key;
        if (key === 'Enter' || key === ' ') {
            event.preventDefault();
            const tab = event.currentTarget?.dataset?.tab;
            if (tab) this.selectedWorklistTab = tab;
        }
    }

    agingListViewMap = {
        'current': '00BWt00000A0o0fMAB',
        '1-30':    '00BWt00000A0mDNMAZ',
        '31-60':   '00BWt00000A0mJpMAJ',
        '61-90':   '00BWt00000A0mN3MAJ',
        '90+':     '00BWt00000A2mM9MAJ'
    };

    psiListViewMap = {
        'Failed':                '00BWt00000A2mnZMAR',
        'Ready for Processing':  '00BWt00000A2mUDMAZ',
        'Processing':            '00BWt00000A2mqnMAB',
        'Draft':                 '00BWt00000A2mnaMAB'
    };

    handlePaymentPromiseKeydown(event) {
        if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
            event.preventDefault();
            this.handlePaymentPromiseClick(event);
        }
    }

    handlePaymentPromiseClick(event) {
        const status = event.currentTarget.dataset.status;
        const listViewId = this.psiListViewMap[status];
        if (listViewId) {
            this[NavigationMixin.Navigate]({
                type: 'standard__objectPage',
                attributes: {
                    objectApiName: 'PaymentScheduleItem',
                    actionName: 'list'
                },
                state: {
                    filterName: listViewId
                }
            });
        }
    }

    handleAgingBucketKeydown(event) {
        if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
            event.preventDefault();
            this.handleAgingBucketClick(event);
        }
    }

    handleAgingBucketClick(event) {
        const key = event.currentTarget.dataset.key;
        this.selectedAgingKey = this.selectedAgingKey === key ? null : key;
        const listViewId = this.agingListViewMap[key];
        if (listViewId) {
            this[NavigationMixin.Navigate]({
                type: 'standard__objectPage',
                attributes: {
                    objectApiName: 'Invoice',
                    actionName: 'list'
                },
                state: {
                    filterName: listViewId
                }
            });
        }
    }

    handleSendReminder(event) {
        const accountId = event.currentTarget.dataset.accountId;
        // Placeholder: navigate to record or fire flow
        console.log('Send Reminder', accountId);
    }

    handleRaiseDispute(event) {
        const accountId = event.currentTarget.dataset.accountId;
        if (accountId) {
            this[NavigationMixin.Navigate]({
                type: 'standard__objectPage',
                attributes: {
                    objectApiName: 'Case',
                    actionName: 'new'
                },
                state: {
                    defaultFieldValues: `AccountId=${accountId}`
                }
            });
        }
    }

    handleResolve(event) {
        const caseId = event.currentTarget.dataset.caseId;
        if (caseId) {
            this[NavigationMixin.Navigate]({
                type: 'standard__recordPage',
                attributes: {
                    recordId: caseId,
                    objectApiName: 'Case',
                    actionName: 'view'
                }
            });
        }
    }

    handleCreateCollectionPlan(event) {
        const accountId = event.currentTarget.dataset.accountId;
        if (accountId) {
            this[NavigationMixin.Navigate]({
                type: 'standard__objectPage',
                attributes: {
                    objectApiName: 'CollectionPlan',
                    actionName: 'new'
                },
                state: {
                    defaultFieldValues: `AccountId=${accountId}`
                }
            });
        }
    }

    handleCreateNewCollectionPlan() {
        this[NavigationMixin.Navigate]({
            type: 'standard__objectPage',
            attributes: {
                objectApiName: 'CollectionPlan',
                actionName: 'new'
            }
        });
    }

    handleWriteOff(event) {
        const accountId = event.currentTarget.dataset.accountId;
        console.log('Write Off', accountId);
    }

    handleLogTask(event) {
        const accountId = event.currentTarget.dataset.accountId;
        if (accountId) {
            this[NavigationMixin.Navigate]({
                type: 'standard__objectPage',
                attributes: {
                    objectApiName: 'Task',
                    actionName: 'new'
                },
                state: {
                    defaultFieldValues: `WhoId=${accountId}`
                }
            });
        }
    }

    dispatchFilterChange() {
        this.dispatchEvent(
            new CustomEvent('filterchange', {
                detail: {
                    accountId: this.selectedAccountId || null,
                    currencyCode: this.selectedCurrency || null,
                    displayCurrency: this.displayCurrency
                },
                bubbles: true,
                composed: true
            })
        );
    }

    formatCurrency(val) {
        const n = Number(val);
        if (isNaN(n)) return '0';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: this.displayCurrency || 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(n);
    }

    formatPtpDate(dateVal) {
        if (!dateVal) return '—';
        // A date-only 'YYYY-MM-DD' is a calendar date: read it as local midnight, never as UTC midnight,
        // which the browser would show as the day before west of UTC (todo 435).
        let d = dateVal;
        if (typeof dateVal === 'string') {
            d = new Date(/^\d{4}-\d{2}-\d{2}$/.test(dateVal) ? `${dateVal}T00:00:00` : dateVal);
        }
        if (isNaN(d.getTime())) return '—';
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    }

    reduceErrors(error) {
        if (typeof error === 'string') return error;
        if (error.body) {
            if (typeof error.body.message === 'string') return error.body.message;
            if (error.body.pageErrors && error.body.pageErrors.length > 0) {
                return error.body.pageErrors.map((e) => e.message).join(', ');
            }
        }
        if (error.message) return error.message;
        return 'Unknown error';
    }

    get unavailableKeys() {
        return this.dashboardData?.unavailable || [];
    }

    get invoicesUnavailable() {
        return this.sections.invoices.status === 'unavailable';
    }

    cardReason(key) {
        return knownReason(this.dashboardData?.unavailableReason?.[key]);
    }

    get invoicesUnavailableText() {
        return unavailableText(SUBJECTS.invoices, this.sections.invoices.reason, SCOPES.cards);
    }

    // Names the total's components that could not be read, and why, in the cards' words: "Excludes debit
    // memos: you don't have access to them." for one reason; for mixed reasons each name carries its reason,
    // then what the user can do ("Choose an account or currency ..." for too many, "Refresh ..." for failed).
    // Every component (debit memos, unapplied credits and payments) can be refused, failed or too many.
    get totalBalanceNote() {
        const total = this.sections.total;
        if (total.status === 'loading' || this.sections.cards !== READY) return '';
        if (total.status === 'unavailable') return unavailableText(SUBJECTS.invoices, total.reason, SCOPES.cards);
        const excluded = this.unavailableKeys.filter((key) => EXCLUDED_NAMES[key]);
        if (excluded.length === 0) return '';
        const groups = NOTE_ORDER.map((reason) => ({
            reason,
            names: excluded.filter((key) => this.cardReason(key) === reason).map((key) => EXCLUDED_NAMES[key])
        })).filter((group) => group.names.length > 0);
        if (groups.length === 1) {
            return `Excludes ${listNames(groups[0].names)}: ${NOTE_CLAUSES[groups[0].reason].alone}`;
        }
        const parts = groups.map((group) => `${listNames(group.names)} (${NOTE_CLAUSES[group.reason].short})`);
        const actions = groups.map((group) => NOTE_CLAUSES[group.reason].action).filter(Boolean);
        return [`Excludes ${listNames(parts)}.`, ...actions].join(' ');
    }

    get invoiceCountLabel() {
        const state = this.sections.invoices;
        if (state.status === 'loading') return LOADING_TEXT;
        if (state.status === 'unavailable') return unavailableText(SUBJECTS.invoices, state.reason, SCOPES.cards);
        return `${this.invoiceCount} invoices`;
    }

    get unappliedPaymentMeta() {
        const { payments, paymentCount } = this.sections;
        if (payments.status === 'loading') return LOADING_TEXT;
        if (payments.status === 'unavailable') return unavailableText(SUBJECTS.unappliedPayments, payments.reason, SCOPES.cards);
        return `${figureText(paymentCount, () => String(this.unappliedPaymentCount))} records · Action required`;
    }

    get totalBalanceValue() {
        return this.dashboardData?.totalBalance != null ? this.dashboardData.totalBalance : 0;
    }

    get totalBalanceBreakdown() {
        if (this.sections.cards !== READY || !this.dashboardData.totalBalanceBreakdown) return [];
        return this.dashboardData.totalBalanceBreakdown.map((b) => ({
            ...b,
            amount: b.amount != null ? b.amount : 0,
            formatted: b.unavailable ? NOT_AVAILABLE : this.formatCurrency(b.amount != null ? b.amount : 0),
            title: b.unavailable ? unavailableText(SUBJECTS[b.unavailable] || 'this figure', this.cardReason(b.unavailable), SCOPES.cards) : '',
            lineClass: `breakdown-line breakdown-${b.color || 'blue'}`
        }));
    }

    get receivablesOutstandingValue() {
        return this.dashboardData?.receivablesOutstanding != null ? this.dashboardData.receivablesOutstanding : 0;
    }

    get invoiceCount() {
        return this.dashboardData?.invoiceCount != null ? this.dashboardData.invoiceCount : 0;
    }

    get partiallySettledLabel() {
        const c = this.dashboardData?.partiallySettledCount ?? 0;
        const s = this.dashboardData?.partiallySettledSum ?? 0;
        return `Partially settled: ${c} (${this.formatCurrency(s)})`;
    }

    get notSettledLabel() {
        const c = this.dashboardData?.notSettledCount ?? 0;
        const s = this.dashboardData?.notSettledSum ?? 0;
        return `Not settled: ${c} (${this.formatCurrency(s)})`;
    }

    get currentDueValue() {
        return this.dashboardData?.currentDue != null ? this.dashboardData.currentDue : 0;
    }

    get overdueValue() {
        return this.dashboardData?.overdue != null ? this.dashboardData.overdue : 0;
    }

    get unappliedPaymentBalanceValue() {
        return this.dashboardData?.unappliedPaymentBalance != null ? this.dashboardData.unappliedPaymentBalance : 0;
    }

    get unappliedPaymentCount() {
        return this.dashboardData?.unappliedPaymentCount != null ? this.dashboardData.unappliedPaymentCount : 0;
    }

    get totalOutstandingValue() {
        return this.dashboardData?.totalOutstanding != null ? this.dashboardData.totalOutstanding : 0;
    }

    // Pre-formatted KPI values: LWC templates can't call methods in bindings (LWC1060),
    // so currency formatting is done here and bound as plain properties.
    get receivablesOutstandingFormatted() {
        return figureText(this.sections.invoices, () => this.formatCurrency(this.receivablesOutstandingValue));
    }

    get currentDueFormatted() {
        return figureText(this.sections.invoices, () => this.formatCurrency(this.currentDueValue));
    }

    get overdueFormatted() {
        return figureText(this.sections.invoices, () => this.formatCurrency(this.overdueValue));
    }

    get unappliedPaymentBalanceFormatted() {
        return figureText(this.sections.payments, () => this.formatCurrency(this.unappliedPaymentBalanceValue));
    }

    get totalBalanceFormatted() {
        return figureText(this.sections.total, () => this.formatCurrency(this.totalBalanceValue));
    }

    get agingBuckets() {
        if (this.sections.invoices !== READY || !this.dashboardData.agingBuckets) return [];
        const total = this.dashboardData.agingBuckets.reduce((sum, b) => sum + (Number(b.amount) || 0), 0);
        const colors = { current: '#2563eb', '1-30': '#3b82f6', '31-60': '#f59e0b', '61-90': '#ef4444', '90+': '#b91c1c' };
        return this.dashboardData.agingBuckets.map((b) => {
            const amt = Number(b.amount) || 0;
            const pct = total > 0 ? (amt / total) * 100 : 0;
            const width = Math.max(pct, 0.5);
            const bg = colors[b.key] || '#64748b';
            const isSelected = this.selectedAgingKey === b.key;
            return {
                ...b,
                amount: amt,
                formatted: this.formatCurrency(amt),
                widthPercent: width,
                segmentStyle: `width: ${width}%; background-color: ${bg}; min-width: 2px;`,
                dotStyle: `background-color: ${bg};`,
                isSelected,
                segmentClass: isSelected ? 'aging-segment aging-segment-selected' : 'aging-segment',
                legendClass: isSelected ? 'legend-item legend-item-selected' : 'legend-item'
            };
        });
    }

    /** Payment Promises: segments by PSI status (same colors as Payment Plans screen). */
    get paymentPromisesBuckets() {
        if (!this.paymentPromiseData || this.paymentPromiseData.length === 0) return [];
        const total = this.paymentPromiseData.reduce((sum, b) => sum + (Number(b.totalRequestedAmount) || 0), 0);
        if (total <= 0) return [];
        const colors = {
            'Failed': '#ea001e',
            'Ready for Processing': '#fe9339',
            'Draft': '#0176d3',
            'Processing': '#5a1ba9'
        };
        return this.paymentPromiseData
            .filter(b => (Number(b.totalRequestedAmount) || 0) > 0 || (b.itemCount || 0) > 0)
            .map(b => {
                const amt = Number(b.totalRequestedAmount) || 0;
                const pct = total > 0 ? (amt / total) * 100 : 0;
                const width = Math.max(pct, 0.5);
                const bg = colors[b.status] || '#706e6b';
                return {
                    key: b.status,
                    status: b.status,
                    label: b.status,
                    amount: amt,
                    formatted: this.formatCurrency(amt),
                    itemCount: b.itemCount || 0,
                    segmentStyle: `width: ${width}%; background-color: ${bg}; min-width: 4px;`,
                    dotStyle: `background-color: ${bg};`,
                    tooltip: `${b.status}: ${this.formatCurrency(amt)} (${b.itemCount || 0} items)`
                };
            });
    }

    get paymentPromiseData() {
        return this.sections.promises === READY ? this.paymentPromiseState.buckets || [] : [];
    }

    get paymentPromisesUnavailable() {
        return this.sections.promises.status === 'unavailable';
    }

    get paymentPromisesUnavailableText() {
        return unavailableText(SUBJECTS.paymentSchedules, this.sections.promises.reason, SCOPES.promises);
    }

    // "No payment promises." only once the server answered with none.
    get showNoPaymentPromises() {
        return this.sections.promises === READY && !this.hasPaymentPromises;
    }

    get paymentPromisesLabel() {
        const state = this.sections.promises;
        if (state.status === 'loading') return 'Payment Promises';
        return `Payment Promises (${figureText(state, () => this.paymentPromisesTotal)})`;
    }

    get hasPaymentPromises() {
        return this.paymentPromisesBuckets && this.paymentPromisesBuckets.length > 0;
    }

    get paymentPromisesTotal() {
        const total = this.paymentPromiseData.reduce((sum, b) => sum + (Number(b.totalRequestedAmount) || 0), 0);
        return this.formatCurrency(total);
    }

    get worklistItems() {
        if (this.sections.worklistTab !== READY) return [];
        const isCritical = this.selectedWorklistTab === 'critical';
        let list = [];
        if (isCritical) list = this.worklistData.criticalFollowUpInvoices || [];
        else if (this.selectedWorklistTab === 'highValue') list = this.worklistData.highValueDelinquents || [];
        else list = this.worklistData.disputedInvoices || [];
        if (!isCritical && this.selectedAgingKey) {
            const key = this.selectedAgingKey;
            list = list.filter((item) => {
                const d = item.daysOverdue;
                if (key === 'current') return d == null || d === 0;
                if (key === '1-30') return d != null && d >= 1 && d <= 30;
                if (key === '31-60') return d != null && d >= 31 && d <= 60;
                if (key === '61-90') return d != null && d >= 61 && d <= 90;
                if (key === '90+') return d != null && d > 90;
                return true;
            });
        }
        if (isCritical) {
            return list.map((item, idx) => ({
                ...item,
                uniqueKey: `critical-inv-${item.invoiceId || idx}`,
                balanceFormatted: this.formatCurrency(item.balance),
                invoiceUrl: item.invoiceId ? `/lightning/r/Invoice/${item.invoiceId}/view` : '#',
                accountUrl: item.billingAccountId ? `/lightning/r/Account/${item.billingAccountId}/view` : null,
                contactUrl: item.billToContactId ? `/lightning/r/Contact/${item.billToContactId}/view` : null,
                collectionPlanUrl: item.collectionPlanId ? `/lightning/r/CollectionPlan/${item.collectionPlanId}/view` : null,
                ...this.planCell(item)
            }));
        }
        return list.map((item, idx) => {
            let ptpDateFormatted = item.ptpDate ? this.formatPtpDate(item.ptpDate) : '—';
            if (item.ptpUnavailable) ptpDateFormatted = NOT_AVAILABLE_CELL;
            const disputeReason = item.disputeReason || '';
            const disputeReasonShort = disputeReason.length > 60 ? disputeReason.slice(0, 57) + '...' : (disputeReason || '—');
            return {
                ...item,
                uniqueKey: `${item.accountId || 'row'}-${idx}`,
                balanceFormatted: this.formatCurrency(item.balance),
                accountUrl: `/lightning/r/Account/${item.accountId}/view`,
                invoiceNumber: null,
                invoiceUrl: null,
                ptpDateFormatted,
                disputeReasonShort: disputeReasonShort || '—',
                disputeReason: disputeReason || '',
                collectionPlanUrl: item.collectionPlanId ? `/lightning/r/CollectionPlan/${item.collectionPlanId}/view` : null,
                caseUrl: item.caseId ? `/lightning/r/Case/${item.caseId}/view` : null,
                ...this.planCell(item)
            };
        });
    }

    // The plan column of a worklist row: a plan the lookup could not read is "Not available" and offers no
    // Create (it may exist); a plan that was read and is absent is "—" with Create.
    planCell(item) {
        return {
            planCellText: item.collectionPlanUnavailable ? NOT_AVAILABLE_CELL : NOT_AVAILABLE,
            showCreatePlan: !item.collectionPlanUnavailable
        };
    }

    get worklistTabUnavailable() {
        return this.sections.worklistTab.status === 'unavailable';
    }

    get worklistTabLoading() {
        return this.sections.worklistTab === LOADING;
    }

    get worklistUnavailableText() {
        return unavailableText(SUBJECTS.worklist, this.sections.worklistTab.reason, SCOPES[this.selectedWorklistTab]);
    }

    get loadingText() {
        return LOADING_TEXT;
    }

    get noWorklistItems() {
        return this.sections.worklistTab === READY && this.worklistItems.length === 0;
    }

    get worklistTabCriticalActive() {
        return this.selectedWorklistTab === 'critical';
    }

    get worklistTabHighValueActive() {
        return this.selectedWorklistTab === 'highValue';
    }

    get worklistTabDisputedActive() {
        return this.selectedWorklistTab === 'disputed';
    }

    get showActionButtons() {
        return this.selectedWorklistTab === 'critical' || this.selectedWorklistTab === 'highValue';
    }

    get criticalTabIndex() {
        return this.selectedWorklistTab === 'critical' ? 0 : -1;
    }

    get highValueTabIndex() {
        return this.selectedWorklistTab === 'highValue' ? 0 : -1;
    }

    get disputedTabIndex() {
        return this.selectedWorklistTab === 'disputed' ? 0 : -1;
    }

    get worklistPanelLabelledBy() {
        if (this.selectedWorklistTab === 'critical') return 'tab-critical';
        if (this.selectedWorklistTab === 'highValue') return 'tab-highValue';
        return 'tab-disputed';
    }

    get cpTasks() {
        if (!this.cpTasksData || !Array.isArray(this.cpTasksData)) return [];
        return this.cpTasksData.map((t, idx) => {
            const subj = t.subject || '';
            const subjectShort = subj.length > 18 ? subj.slice(0, 15) + '...' : subj;
            const cpIdShort = t.collectionPlanId ? String(t.collectionPlanId).slice(-8) : '—';
            return {
                ...t,
                uniqueKey: `cptask-${t.taskId || idx}`,
                taskUrl: t.taskId ? `/lightning/r/Task/${t.taskId}/view` : '#',
                activityDateFormatted: t.activityDate ? this.formatPtpDate(t.activityDate) : '—',
                cpUrl: t.collectionPlanId ? `/lightning/r/CollectionPlan/${t.collectionPlanId}/view` : '#',
                subjectShort,
                cpIdShort
            };
        });
    }

    get cpTasksData() {
        return this.sections.tasks === READY ? this.cpTasksState.items || [] : [];
    }

    get cpTasksUnavailable() {
        return this.sections.tasks.status === 'unavailable';
    }

    get cpTasksUnavailableText() {
        return unavailableText(SUBJECTS.planTasks, this.sections.tasks.reason, SCOPES.tasks);
    }

    get showNoCpTasks() {
        return this.sections.tasks === READY && !this.hasCpTasks;
    }

    get cpTasksCount() {
        return figureText(this.sections.tasks, () => String(this.cpTasks.length));
    }

    get hasCpTasks() {
        return this.cpTasks && this.cpTasks.length > 0;
    }

    get myCollectionPlans() {
        if (!this.myCollectionPlansData || this.myCollectionPlansData.length === 0) return [];
        return this.myCollectionPlansData.map((item, idx) => ({
            ...item,
            uniqueKey: `mycp-${item.collectionPlanId || idx}`,
            cpUrl: item.collectionPlanId ? `/lightning/r/CollectionPlan/${item.collectionPlanId}/view` : '#',
            accountUrl: item.accountId ? `/lightning/r/Account/${item.accountId}/view` : null,
            dueDateFormatted: item.dueDate ? this.formatDateShort(item.dueDate) : '—',
            toRecoverFormatted: this.formatCurrency(item.totalInvoiceBalance)
        }));
    }

    get hasMyCollectionPlans() {
        return this.myCollectionPlans && this.myCollectionPlans.length > 0;
    }

    get myCollectionPlansData() {
        return this.sections.plans === READY ? this.myCollectionPlansState.items || [] : [];
    }

    get myCollectionPlansUnavailable() {
        return this.sections.plans.status === 'unavailable';
    }

    get myCollectionPlansUnavailableText() {
        return unavailableText(SUBJECTS.collectionPlans, this.sections.plans.reason, SCOPES.plans);
    }

    get showNoMyCollectionPlans() {
        return this.sections.plans === READY && !this.hasMyCollectionPlans;
    }

    get myCollectionPlansCount() {
        return figureText(this.sections.plans, () => String(this.myCollectionPlans.length));
    }

    get progressUnavailable() {
        return this.sections.progress.status === 'unavailable';
    }

    get progressUnavailableText() {
        return unavailableText(SUBJECTS.collectionPlans, this.sections.progress.reason, SCOPES.progress);
    }

    get showNoProgress() {
        return this.sections.progress === READY && !(this.collectionsProgressData.totalPlans > 0);
    }

    get hasCollectionsProgress() {
        return this.sections.progress === READY && this.collectionsProgressData.totalPlans > 0;
    }

    get progressRecoveredPercent() {
        if (!this.collectionsProgressData) return 0;
        return Number(this.collectionsProgressData.recoveredPercent) || 0;
    }

    get progressNotRecoveredPercent() {
        if (!this.collectionsProgressData) return 0;
        return Number(this.collectionsProgressData.notRecoveredPercent) || 0;
    }

    get progressRecoveredAmount() {
        if (!this.collectionsProgressData) return this.formatCurrency(0);
        return this.formatCurrency(this.collectionsProgressData.recoveredAmount);
    }

    get progressNotRecoveredAmount() {
        if (!this.collectionsProgressData) return this.formatCurrency(0);
        return this.formatCurrency(this.collectionsProgressData.notRecoveredAmount);
    }

    get progressAvgDaysToClose() {
        return figureText(this.sections.progress, () => String(this.collectionsProgressData.avgDaysToClose ?? 0));
    }

    get progressAvgDaysPastDue() {
        return figureText(this.sections.progress, () => String(this.collectionsProgressData.avgDaysPastDue ?? 0));
    }

    get pieSvgRecoveredPath() {
        const pct = this.progressRecoveredPercent / 100;
        if (pct <= 0) return '';
        if (pct >= 1) return 'M 50 10 A 40 40 0 1 1 49.99 10 Z';
        const angle = pct * 2 * Math.PI;
        const x = 50 + 40 * Math.sin(angle);
        const y = 50 - 40 * Math.cos(angle);
        const largeArc = pct > 0.5 ? 1 : 0;
        return `M 50 10 A 40 40 0 ${largeArc} 1 ${x.toFixed(2)} ${y.toFixed(2)} L 50 50 Z`;
    }

    get pieSvgNotRecoveredPath() {
        const recoveredPct = this.progressRecoveredPercent / 100;
        const pct = this.progressNotRecoveredPercent / 100;
        if (pct <= 0) return '';
        if (pct >= 1) return 'M 50 10 A 40 40 0 1 1 49.99 10 Z';
        const startAngle = recoveredPct * 2 * Math.PI;
        const endAngle = startAngle + pct * 2 * Math.PI;
        const x1 = 50 + 40 * Math.sin(startAngle);
        const y1 = 50 - 40 * Math.cos(startAngle);
        const x2 = 50 + 40 * Math.sin(endAngle);
        const y2 = 50 - 40 * Math.cos(endAngle);
        const largeArc = pct > 0.5 ? 1 : 0;
        return `M ${x1.toFixed(2)} ${y1.toFixed(2)} A 40 40 0 ${largeArc} 1 ${x2.toFixed(2)} ${y2.toFixed(2)} L 50 50 Z`;
    }

    get progressRecoveredPercentFormatted() {
        return Math.round(this.progressRecoveredPercent) + '%';
    }

    get progressNotRecoveredPercentFormatted() {
        return Math.round(this.progressNotRecoveredPercent) + '%';
    }

    formatDateShort(dateVal) {
        if (!dateVal) return '—';
        try {
            const d = new Date(dateVal + 'T00:00:00');
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        } catch {
            return String(dateVal);
        }
    }
}