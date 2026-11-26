import { LightningElement, api, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import getAccountOptions from '@salesforce/apex/RLM_CollectionsDashboardController.getAccountOptions';
import searchAccounts from '@salesforce/apex/RLM_CollectionsDashboardController.searchAccounts';
import getCurrencyOptions from '@salesforce/apex/RLM_CollectionsDashboardController.getCurrencyOptions';
import getOrgDefaultCurrency from '@salesforce/apex/RLM_CollectionsDashboardController.getOrgDefaultCurrency';
import getDashboardCards from '@salesforce/apex/RLM_CollectionsDashboardController.getDashboardCards';
import getWorklist from '@salesforce/apex/RLM_CollectionsDashboardController.getWorklist';
import getCollectionPlanTasks from '@salesforce/apex/RLM_CollectionsDashboardController.getCollectionPlanTasks';
import getPaymentPromiseSummary from '@salesforce/apex/RLM_CollectionsDashboardController.getPaymentPromiseSummary';
import getMyCollectionPlans from '@salesforce/apex/RLM_CollectionsDashboardController.getMyCollectionPlans';
import getCollectionsProgress from '@salesforce/apex/RLM_CollectionsDashboardController.getCollectionsProgress';

// Figures and lists the page could not read (todo 435). The controller marks each one unavailable with a
// reason: 'refused' (the user may not read it: "You don't have access to ...", ask an administrator),
// 'tooMany' (more records than a bounded read may take: "Too many records to total/list here.", with the
// filters still free to narrow it) or 'failed' (anything else: "... could not be loaded", try again). A
// failed call (a wire or imperative error) is always 'failed'. Nothing unavailable is shown as a zero or an
// empty "none", and a short list with more rows than it shows says so.
const NOT_AVAILABLE = '\u2014';
const REFUSED = 'refused';
const FAILED = 'failed';
// More rows than a bounded read may take (the controller's ROW_CAP, or what is left of the call's query
// rows): the figure or list would be built from a cut-off read, so narrow the filters instead.
const TOO_MANY = 'tooMany';
// Amounts in another currency could not be converted (the conversion rates could not be read): not something a
// refresh fixes.
const NO_RATES = 'noRates';
const NO_RATES_TEXT = 'Amounts in other currencies cannot be converted: the conversion rates could not be read. Contact your administrator.';
const SUBJECTS = {
    accounts: 'accounts',
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
const ALL_ACCOUNTS = Object.freeze({ value: '', label: 'All Accounts' });
// The account search runs from this many characters (the controller's ACCOUNT_SEARCH_MIN).
const ACCOUNT_SEARCH_MIN = 2;

// What each section is when it has too many records: a figure is totalled and a list is listed. The filters
// that narrow it are the ones the controller reports its reads applied (a filter is listed only where the
// object read has the field, so a single-currency org never hears "choose a currency"). A scope is
// { verb, filters }, built per section by scopeOf; the text suggests only the filters not already in use
// (`active`, from the page's current selection).
const ACCOUNT = 'account';
const CURRENCY = 'currency';
const VERBS = {
    cards: 'total',
    promises: 'total',
    progress: 'total',
    tasks: 'list',
    plans: 'list',
    critical: 'list',
    highValue: 'list',
    disputed: 'list'
};

function scopeOf(section, filters) {
    return { verb: VERBS[section], filters: Array.isArray(filters) ? filters : [] };
}

// "Choose an account or currency to narrow it." for the scope's filters not yet in use; '' when none is left.
function narrowingText(scope, active) {
    const left = scope.filters.filter((filter) => !active[filter]);
    if (left.length === 0) return '';
    if (left.length === 2) return 'Choose an account or currency to narrow it.';
    return left[0] === ACCOUNT ? 'Choose an account to narrow it.' : 'Choose a currency to narrow it.';
}

// Too many records: what to do about it, or, when every filter that narrows the section is already in use,
// that it is too many even so.
function tooManyText(scope, active) {
    const narrowing = narrowingText(scope, active);
    if (narrowing) return `Too many records to ${scope.verb} here. ${narrowing}`;
    if (scope.filters.length > 0) return `Too many records to ${scope.verb} here even for this ${scope.filters.join(' and ')}.`;
    return `Too many records to ${scope.verb} here.`;
}

function unavailableText(subject, reason, scope, active) {
    if (reason === REFUSED) return `You don't have access to ${subject}.`;
    if (reason === NO_RATES) return NO_RATES_TEXT;
    if (reason === TOO_MANY) return tooManyText(scope, active);
    return `${subject.charAt(0).toUpperCase()}${subject.slice(1)} could not be loaded. Refresh the page to try again.`;
}

// A short list with more rows than it shows: "Showing the first 200 of more than 200 (latest due first).",
// then the filters still free to narrow it.
function moreText(count, order, scope, active) {
    const narrowing = narrowingText(scope, active);
    const sentence = `Showing the first ${count} of more than ${count} (${order} first).`;
    return narrowing ? `${sentence} ${narrowing}` : sentence;
}
const LIST_ORDER = {
    critical: 'most overdue',
    highValue: 'largest balance',
    disputed: 'newest open case',
    tasks: 'latest due',
    plans: 'soonest due'
};

// The total balance note's wording per reason, as the cards and tooltips word it: `alone` when every
// excluded component has that reason, `short` beside each name when the reasons are mixed, and `action`,
// said once after a mixed list, for the reasons the user can act on. Too many follows the filters the
// too-many components' reads applied (`scope`) and those in use.
function noteClauses(scope, active) {
    const tooMany = tooManyText(scope, active);
    const narrowing = narrowingText(scope, active);
    let tooManyShort = 'too many records to total';
    if (!narrowing && scope.filters.length > 0) tooManyShort += ` even for this ${scope.filters.join(' and ')}`;
    return {
        [REFUSED]: { alone: "you don't have access to them.", short: "you don't have access" },
        [TOO_MANY]: {
            alone: `${tooMany.charAt(0).toLowerCase()}${tooMany.slice(1)}`,
            short: tooManyShort,
            action: narrowing || undefined
        },
        [NO_RATES]: {
            alone: 'the conversion rates for their currencies could not be read. Contact your administrator.',
            short: 'conversion rates could not be read',
            action: 'Contact your administrator.'
        },
        [FAILED]: {
            alone: 'they could not be loaded. Refresh the page to try again.',
            short: 'could not be loaded',
            action: 'Refresh the page to try again.'
        }
    };
}
const NOTE_ORDER = [REFUSED, TOO_MANY, NO_RATES, FAILED];

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
    return reason === REFUSED || reason === TOO_MANY || reason === NO_RATES ? reason : FAILED;
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
    // The first page of accounts (getAccountOptions), restored when the search is cleared.
    listedAccountOptions = [];
    accountOptionsHaveMore = false;
    // Why the accounts could not be read (refused or failed), or null: the filter then offers only "All Accounts".
    accountOptionsUnavailableReason = null;
    accountSearch;
    accountSearchTerm = '';
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
        // Each call stands alone: a failed default-currency or currency call touches only the currency filter
        // (it falls back to "All Currencies" and the default), a failed accounts call only the account filter
        // (it says the accounts could not be loaded), and the page loads either way, with no error toast.
        Promise.all([
            getOrgDefaultCurrency().catch(() => null),
            getCurrencyOptions().catch(() => null),
            getAccountOptions().catch(() => ({ options: [ALL_ACCOUNTS], hasMore: false, unavailable: true, unavailableReason: FAILED }))
        ])
            .then(([defaultCode, currencyOpts, accountOpts]) => {
                this.orgDefaultCurrency = defaultCode || 'USD';
                this.currencyOptions = Array.isArray(currencyOpts)
                    ? currencyOpts
                    : [
                          { value: '', label: 'All Currencies' },
                          { value: this.orgDefaultCurrency, label: this.orgDefaultCurrency }
                      ];
                this.listedAccountOptions = Array.isArray(accountOpts?.options) ? accountOpts.options : [ALL_ACCOUNTS];
                this.accountOptionsHaveMore = accountOpts?.hasMore === true;
                this.accountOptionsUnavailableReason = accountOpts?.unavailable ? knownReason(accountOpts.unavailableReason) : null;
                this.accountOptions = this.listedAccountOptions;
                if (!this.selectedCurrency) {
                    this.selectedCurrency = '';
                }
                this.dispatchFilterChange();
            })
            .finally(() => {
                this.isLoadingOptions = false;
            });
    }

    // With more accounts than the filter lists, the page offers a search by name (todo 435). Each search answers
    // with "All Accounts" and its matches; the chosen account stays in the options whatever the search finds.
    handleAccountSearch(event) {
        const term = (event.target.value || '').trim();
        this.accountSearchTerm = term;
        if (term.length < ACCOUNT_SEARCH_MIN) {
            this.accountSearch = undefined;
            this.accountOptions = this.withSelectedAccount(this.listedAccountOptions);
            return;
        }
        searchAccounts({ term })
            .then((found) => {
                // A newer search has been typed since: its answer, not this one, fills the list.
                if (this.accountSearchTerm !== term) return;
                if (found?.unavailable) {
                    this.searchUnavailable(knownReason(found.unavailableReason));
                    return;
                }
                const options = Array.isArray(found?.options) ? found.options : [ALL_ACCOUNTS];
                this.accountSearch = {
                    unavailable: false,
                    hasMore: found?.hasMore === true,
                    count: options.filter((option) => option.value).length
                };
                this.accountOptions = this.withSelectedAccount(options);
            })
            .catch(() => {
                if (this.accountSearchTerm === term) this.searchUnavailable(FAILED);
            });
    }

    // A search that was refused or failed lists the first page of accounts again (keeping the chosen one), never
    // another search's matches, and says why.
    searchUnavailable(reason) {
        this.accountSearch = { unavailable: true, reason, hasMore: false, count: 0 };
        this.accountOptions = this.withSelectedAccount(this.listedAccountOptions);
    }

    withSelectedAccount(options) {
        if (!this.selectedAccountId || options.some((option) => option.value === this.selectedAccountId)) return options;
        const selected = this.accountOptions.find((option) => option.value === this.selectedAccountId);
        return selected ? [options[0], selected, ...options.slice(1)] : options;
    }

    get showAccountSearch() {
        return this.accountOptionsHaveMore && !this.accountOptionsUnavailableReason;
    }

    // What the account filter lists, when it is not every account.
    get accountFilterNotice() {
        // Accounts that could not be read are not an org with no accounts: say why there is none to choose.
        if (this.accountOptionsUnavailableReason) {
            return unavailableText(SUBJECTS.accounts, this.accountOptionsUnavailableReason, scopeOf('plans', []), {});
        }
        const search = this.accountSearch;
        // A refused search is a refusal, as the account options say; any other failure, try again.
        if (search?.unavailable) {
            return search.reason === REFUSED ? "You don't have access to accounts." : 'Accounts could not be searched. Try again.';
        }
        if (search?.hasMore) return `Showing the first ${search.count} matching accounts by name. Type more of the name to narrow it.`;
        if (search && search.count === 0) return 'No account name contains that text.';
        if (search) return '';
        if (!this.accountOptionsHaveMore) return '';
        const listed = this.listedAccountOptions.filter((option) => option.value).length;
        return `Showing the first ${listed} accounts by name. Search for an account to find another.`;
    }

    get effectiveAccountId() {
        return this.selectedAccountId && this.selectedAccountId !== '' ? this.selectedAccountId : null;
    }

    get effectiveCurrencyCode() {
        return this.selectedCurrency && this.selectedCurrency !== '' ? this.selectedCurrency : null;
    }

    // The filters in use, so a too-many or more-rows note suggests only the ones left.
    get activeFilters() {
        return { [ACCOUNT]: Boolean(this.effectiveAccountId), [CURRENCY]: Boolean(this.effectiveCurrencyCode) };
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

    @wire(getMyCollectionPlans, { currencyCode: '$effectiveCurrencyCode' })
    wiredMyCollectionPlans({ error, data }) {
        if (error) this.myCollectionPlansState = failedSection({ items: [] });
        else if (data) this.myCollectionPlansState = data;
    }

    @wire(getCollectionsProgress, { currencyCode: '$effectiveCurrencyCode' })
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

    // Every amount on the page is in one currency (the chosen one, or else the user's); on a multi-currency org,
    // amounts recorded in another currency are converted, and the page says so.
    // The currency each section's answer says its amounts are in.
    get cardsCurrency() {
        return this.dashboardData?.currencyCode;
    }

    get promisesCurrency() {
        return this.paymentPromiseState?.currencyCode;
    }

    get worklistCurrency() {
        return this.worklistData?.currencyCode;
    }

    get plansCurrency() {
        return this.myCollectionPlansState?.currencyCode;
    }

    get currencyNote() {
        const data = this.dashboardData;
        if (!data || !data.multiCurrency || !data.currencyCode) return '';
        return `Amounts in ${data.currencyCode}. Amounts recorded in another currency are converted at the org's conversion rates.`;
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
        // Progress and the user's plans are not filtered by currency, but their amounts are shown in it.
        this.collectionsProgressData = undefined;
        this.myCollectionPlansState = undefined;
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

    // Formats an amount in the currency its section's answer is in (the server's page currency). A section shows
    // amounts only once it has answered, so its currency is known; displayCurrency is only a fallback.
    formatCurrency(val, currencyCode) {
        const n = Number(val);
        if (isNaN(n)) return '0';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currencyCode || this.displayCurrency || 'USD',
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

    // A card component's scope: the filters its read applied, as the controller reports them. With several
    // keys (the total note's too-many components), the filters any of them applied.
    cardsScope(...keys) {
        const byKey = this.dashboardData?.filtersByKey || {};
        const filters = [ACCOUNT, CURRENCY].filter((filter) => keys.some((key) => (byKey[key] || []).includes(filter)));
        return scopeOf('cards', filters);
    }

    cardReason(key) {
        return knownReason(this.dashboardData?.unavailableReason?.[key]);
    }

    get invoicesUnavailableText() {
        return unavailableText(SUBJECTS.invoices, this.sections.invoices.reason, this.cardsScope('invoices'), this.activeFilters);
    }

    // Names the total's components that could not be read, and why, in the cards' words: "Excludes debit
    // memos: you don't have access to them." for one reason; for mixed reasons each name carries its reason,
    // then what the user can do ("Choose an account or currency ..." for too many, "Refresh ..." for failed).
    // Every component (debit memos, unapplied credits and payments) can be refused, failed or too many.
    get totalBalanceNote() {
        const total = this.sections.total;
        if (total.status === 'loading' || this.sections.cards !== READY) return '';
        if (total.status === 'unavailable') return unavailableText(SUBJECTS.invoices, total.reason, this.cardsScope('invoices'), this.activeFilters);
        const excluded = this.unavailableKeys.filter((key) => EXCLUDED_NAMES[key]);
        if (excluded.length === 0) return '';
        const groups = NOTE_ORDER.map((reason) => ({
            reason,
            names: excluded.filter((key) => this.cardReason(key) === reason).map((key) => EXCLUDED_NAMES[key])
        })).filter((group) => group.names.length > 0);
        const tooManyKeys = excluded.filter((key) => this.cardReason(key) === TOO_MANY);
        const clauses = noteClauses(this.cardsScope(...tooManyKeys), this.activeFilters);
        if (groups.length === 1) {
            return `Excludes ${listNames(groups[0].names)}: ${clauses[groups[0].reason].alone}`;
        }
        const parts = groups.map((group) => `${listNames(group.names)} (${clauses[group.reason].short})`);
        const actions = groups.map((group) => clauses[group.reason].action).filter(Boolean);
        return [`Excludes ${listNames(parts)}.`, ...actions].join(' ');
    }

    get invoiceCountLabel() {
        const state = this.sections.invoices;
        if (state.status === 'loading') return LOADING_TEXT;
        if (state.status === 'unavailable') return unavailableText(SUBJECTS.invoices, state.reason, this.cardsScope('invoices'), this.activeFilters);
        return `${this.invoiceCount} invoices`;
    }

    get unappliedPaymentMeta() {
        const { payments, paymentCount } = this.sections;
        if (payments.status === 'loading') return LOADING_TEXT;
        if (payments.status === 'unavailable') return unavailableText(SUBJECTS.unappliedPayments, payments.reason, this.cardsScope('unappliedPayments'), this.activeFilters);
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
            formatted: b.unavailable ? NOT_AVAILABLE : this.formatCurrency(b.amount != null ? b.amount : 0, this.cardsCurrency),
            title: b.unavailable ? unavailableText(SUBJECTS[b.unavailable] || 'this figure', this.cardReason(b.unavailable), this.cardsScope(b.unavailable), this.activeFilters) : '',
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
        return `Partially settled: ${c} (${this.formatCurrency(s, this.cardsCurrency)})`;
    }

    get notSettledLabel() {
        const c = this.dashboardData?.notSettledCount ?? 0;
        const s = this.dashboardData?.notSettledSum ?? 0;
        return `Not settled: ${c} (${this.formatCurrency(s, this.cardsCurrency)})`;
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
        return figureText(this.sections.invoices, () => this.formatCurrency(this.receivablesOutstandingValue, this.cardsCurrency));
    }

    get currentDueFormatted() {
        return figureText(this.sections.invoices, () => this.formatCurrency(this.currentDueValue, this.cardsCurrency));
    }

    get overdueFormatted() {
        return figureText(this.sections.invoices, () => this.formatCurrency(this.overdueValue, this.cardsCurrency));
    }

    get unappliedPaymentBalanceFormatted() {
        return figureText(this.sections.payments, () => this.formatCurrency(this.unappliedPaymentBalanceValue, this.cardsCurrency));
    }

    get totalBalanceFormatted() {
        return figureText(this.sections.total, () => this.formatCurrency(this.totalBalanceValue, this.cardsCurrency));
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
                formatted: this.formatCurrency(amt, this.cardsCurrency),
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
                    formatted: this.formatCurrency(amt, this.promisesCurrency),
                    itemCount: b.itemCount || 0,
                    segmentStyle: `width: ${width}%; background-color: ${bg}; min-width: 4px;`,
                    dotStyle: `background-color: ${bg};`,
                    tooltip: `${b.status}: ${this.formatCurrency(amt, this.promisesCurrency)} (${b.itemCount || 0} items)`
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
        return unavailableText(SUBJECTS.paymentSchedules, this.sections.promises.reason, scopeOf('promises', this.paymentPromiseState?.filters), this.activeFilters);
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
        return this.formatCurrency(total, this.promisesCurrency);
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
                balanceFormatted: this.formatCurrency(item.balance, this.worklistCurrency),
                invoiceUrl: item.invoiceId ? `/lightning/r/Invoice/${item.invoiceId}/view` : '#',
                // A name the user may not read (refused, or hidden by sharing) is plain text: its record would
                // open on an insufficient-privileges page.
                accountUrl: item.billingAccountId && !item.accountNameUnavailable ? `/lightning/r/Account/${item.billingAccountId}/view` : null,
                billingAccountName: item.accountNameUnavailable ? NOT_AVAILABLE_CELL : item.billingAccountName,
                // The contact's name; one the user may not read (refused, or hidden by sharing) is plain text.
                contactUrl: item.billToContactId && !item.billToContactNameUnavailable ? `/lightning/r/Contact/${item.billToContactId}/view` : null,
                billToContactLabel: this.contactLabel(item),
                collectionPlanLabel: item.collectionPlanName || NOT_AVAILABLE,
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
                accountName: item.accountNameUnavailable ? NOT_AVAILABLE_CELL : item.accountName,
                balanceFormatted: this.formatCurrency(item.balance, this.worklistCurrency),
                accountUrl: item.accountId && !item.accountNameUnavailable ? `/lightning/r/Account/${item.accountId}/view` : null,
                invoiceNumber: null,
                invoiceUrl: null,
                ptpDateFormatted,
                disputeReasonShort: disputeReasonShort || '—',
                disputeReason: disputeReason || '',
                collectionPlanUrl: item.collectionPlanId ? `/lightning/r/CollectionPlan/${item.collectionPlanId}/view` : null,
                collectionPlanLabel: item.collectionPlanName || NOT_AVAILABLE,
                caseUrl: item.caseId ? `/lightning/r/Case/${item.caseId}/view` : null,
                ...this.planCell(item)
            };
        });
    }

    // The bill-to contact column: the contact's name, "Not available" when it could not be read, "—" for none.
    contactLabel(item) {
        if (!item.billToContactId) return NOT_AVAILABLE;
        if (item.billToContactNameUnavailable || !item.billToContactName) return NOT_AVAILABLE_CELL;
        return item.billToContactName;
    }

    // The plan column of a worklist row: a plan the lookup could not read is "Not available" and offers no
    // Create (it may exist); a plan that was read and is absent is "—" with Create (a plan sharing hides from
    // the user reads as absent too: a USER_MODE read cannot tell the two apart).
    planCell(item) {
        return {
            planCellText: item.collectionPlanUnavailable ? NOT_AVAILABLE_CELL : NOT_AVAILABLE,
            showCreatePlan: !item.collectionPlanUnavailable
        };
    }

    // Each tab shows a fixed number of rows; when there are more, the tab says so. hasMore maps each such tab
    // to the filters that narrow which rows it lists.
    get worklistTabHasMore() {
        const more = this.worklistData?.hasMore || {};
        return this.sections.worklistTab === READY && Object.prototype.hasOwnProperty.call(more, this.selectedWorklistTab);
    }

    // Counts the rows the tab read, not those left after the aging selection, which narrows them on the page.
    get worklistMoreText() {
        const tab = this.selectedWorklistTab;
        const rowsByTab = {
            critical: this.worklistData.criticalFollowUpInvoices,
            highValue: this.worklistData.highValueDelinquents,
            disputed: this.worklistData.disputedInvoices
        };
        return moreText((rowsByTab[tab] || []).length, LIST_ORDER[tab], scopeOf(tab, this.worklistData.hasMore[tab]), this.activeFilters);
    }

    get worklistTabUnavailable() {
        return this.sections.worklistTab.status === 'unavailable';
    }

    get worklistTabLoading() {
        return this.sections.worklistTab === LOADING;
    }

    get worklistUnavailableText() {
        return unavailableText(SUBJECTS.worklist, this.sections.worklistTab.reason,
            scopeOf(this.selectedWorklistTab, this.worklistData?.filtersByTab?.[this.selectedWorklistTab]), this.activeFilters);
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
        return unavailableText(SUBJECTS.planTasks, this.sections.tasks.reason, scopeOf('tasks', this.cpTasksState?.filters), this.activeFilters);
    }

    get showNoCpTasks() {
        return this.sections.tasks === READY && !this.hasCpTasks;
    }

    get cpTasksCount() {
        return figureText(this.sections.tasks, () => `${this.cpTasks.length}${this.cpTasksHaveMore ? '+' : ''}`);
    }

    get cpTasksHaveMore() {
        return this.sections.tasks === READY && this.cpTasksState.hasMore === true;
    }

    get cpTasksMoreText() {
        return moreText(this.cpTasks.length, LIST_ORDER.tasks, scopeOf('tasks', this.cpTasksState?.filters), this.activeFilters);
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
            accountUrl: item.accountId && !item.accountNameUnavailable ? `/lightning/r/Account/${item.accountId}/view` : null,
            accountName: item.accountNameUnavailable ? NOT_AVAILABLE_CELL : item.accountName,
            dueDateFormatted: item.dueDate ? this.formatDateShort(item.dueDate) : '—',
            toRecoverFormatted: this.formatCurrency(item.totalInvoiceBalance, this.plansCurrency)
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
        return unavailableText(SUBJECTS.collectionPlans, this.sections.plans.reason, scopeOf('plans', this.myCollectionPlansState?.filters), this.activeFilters);
    }

    get showNoMyCollectionPlans() {
        return this.sections.plans === READY && !this.hasMyCollectionPlans;
    }

    get myCollectionPlansCount() {
        return figureText(this.sections.plans, () => `${this.myCollectionPlans.length}${this.myCollectionPlansHaveMore ? '+' : ''}`);
    }

    get myCollectionPlansHaveMore() {
        return this.sections.plans === READY && this.myCollectionPlansState.hasMore === true;
    }

    get myCollectionPlansMoreText() {
        return moreText(this.myCollectionPlans.length, LIST_ORDER.plans, scopeOf('plans', this.myCollectionPlansState?.filters), this.activeFilters);
    }

    get progressUnavailable() {
        return this.sections.progress.status === 'unavailable';
    }

    get progressUnavailableText() {
        return unavailableText(SUBJECTS.collectionPlans, this.sections.progress.reason, scopeOf('progress', this.collectionsProgressData?.filters), this.activeFilters);
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

    // No amount before the server has said which currency it is in.
    get progressRecoveredAmount() {
        const data = this.collectionsProgressData;
        if (!data || !data.currencyCode) return '';
        return this.formatCurrency(data.recoveredAmount, data.currencyCode);
    }

    get progressNotRecoveredAmount() {
        const data = this.collectionsProgressData;
        if (!data || !data.currencyCode) return '';
        return this.formatCurrency(data.notRecoveredAmount, data.currencyCode);
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