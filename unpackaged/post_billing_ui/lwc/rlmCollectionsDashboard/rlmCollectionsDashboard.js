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
    dashboardData = null;
    worklistData = null;
    cpTasksData = [];
    paymentPromiseData = [];
    myCollectionPlansData = [];
    collectionsProgressData = null;
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
                this.loadWorklistImperative();
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
        if (data) this.cpTasksData = data;
        else if (error) this.cpTasksData = [];
    }

    @wire(getPaymentPromiseSummary, { accountId: '$effectiveAccountId', currencyCode: '$effectiveCurrencyCode' })
    wiredPaymentPromises({ error, data }) {
        if (data) this.paymentPromiseData = Array.isArray(data) ? data : [];
        else if (error) this.paymentPromiseData = [];
    }

    @wire(getMyCollectionPlans)
    wiredMyCollectionPlans({ error, data }) {
        if (data) this.myCollectionPlansData = Array.isArray(data) ? data : [];
        else if (error) this.myCollectionPlansData = [];
    }

    @wire(getCollectionsProgress)
    wiredCollectionsProgress({ error, data }) {
        if (data) this.collectionsProgressData = data;
        else if (error) this.collectionsProgressData = null;
    }

    @wire(getWorklist, { accountId: '$effectiveAccountId', currencyCode: '$effectiveCurrencyCode' })
    wiredWorklist({ error, data }) {
        if (data) {
            this.worklistData = data;
            this.worklistError = undefined;
        } else if (error) {
            this.worklistData = null;
            this.worklistError = this.reduceErrors(error);
            this.loadWorklistImperative();
        }
    }

    loadWorklistImperative() {
        getWorklist({ accountId: this.effectiveAccountId, currencyCode: this.effectiveCurrencyCode })
            .then((data) => {
                this.worklistData = data;
                this.worklistError = undefined;
            })
            .catch((err) => {
                this.worklistData = { criticalFollowUpInvoices: [], highValueDelinquents: [], disputedInvoices: [] };
                this.worklistError = this.reduceErrors(err);
            });
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

    handleAccountChange(event) {
        this.selectedAccountId = event.detail.value || '';
        this.dispatchFilterChange();
        this.loadWorklistImperative();
    }

    handleCurrencyChange(event) {
        this.selectedCurrency = event.detail.value || '';
        this.dispatchFilterChange();
        this.loadWorklistImperative();
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

    handleLogCall(event) {
        const accountId = event.currentTarget.dataset.accountId;
        console.log('Log Call', accountId);
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
        const d = typeof dateVal === 'string' ? new Date(dateVal) : dateVal;
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

    get totalBalanceValue() {
        return this.dashboardData?.totalBalance != null ? this.dashboardData.totalBalance : 0;
    }

    get totalBalanceBreakdown() {
        if (!this.dashboardData?.totalBalanceBreakdown) return [];
        return this.dashboardData.totalBalanceBreakdown.map((b) => ({
            ...b,
            amount: b.amount != null ? b.amount : 0,
            formatted: this.formatCurrency(b.amount != null ? b.amount : 0),
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

    get agingBuckets() {
        if (!this.dashboardData?.agingBuckets) return [];
        const total = this.dashboardData.agingBuckets.reduce((sum, b) => sum + (Number(b.amount) || 0), 0);
        const colors = { current: '#2563eb', '1-30': '#3b82f6', '31-60': '#f59e0b', '61-90': '#ef4444', '90+': '#b91c1c' };
        return this.dashboardData.agingBuckets.map((b) => {
            const amt = Number(b.amount) || 0;
            const pct = total > 0 ? (amt / total) * 100 : 0;
            const width = Math.max(pct, 0.5);
            const bg = colors[b.key] || '#64748b';
            return {
                ...b,
                amount: amt,
                formatted: this.formatCurrency(amt),
                widthPercent: width,
                segmentStyle: `width: ${width}%; background-color: ${bg}; min-width: 2px;`,
                dotStyle: `background-color: ${bg};`,
                isSelected: this.selectedAgingKey === b.key
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

    get hasPaymentPromises() {
        return this.paymentPromisesBuckets && this.paymentPromisesBuckets.length > 0;
    }

    get paymentPromisesTotalFormatted() {
        if (!this.paymentPromiseData || this.paymentPromiseData.length === 0) return this.formatCurrency(0);
        const total = this.paymentPromiseData.reduce((sum, b) => sum + (Number(b.totalRequestedAmount) || 0), 0);
        return this.formatCurrency(total);
    }

    get worklistItems() {
        if (!this.worklistData) return [];
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
                invoiceUrl: item.invoiceId ? `/lightning/r/Invoice/${item.invoiceId}/view` : '#',
                accountUrl: item.billingAccountId ? `/lightning/r/Account/${item.billingAccountId}/view` : null,
                contactUrl: item.billToContactId ? `/lightning/r/Contact/${item.billToContactId}/view` : null,
                collectionPlanUrl: item.collectionPlanId ? `/lightning/r/CollectionPlan/${item.collectionPlanId}/view` : null
            }));
        }
        return list.map((item, idx) => {
            const ptpDateFormatted = item.ptpDate ? this.formatPtpDate(item.ptpDate) : '—';
            const disputeReason = item.disputeReason || '';
            const disputeReasonShort = disputeReason.length > 60 ? disputeReason.slice(0, 57) + '...' : (disputeReason || '—');
            return {
                ...item,
                uniqueKey: `${item.accountId || 'row'}-${idx}`,
                accountUrl: `/lightning/r/Account/${item.accountId}/view`,
                invoiceNumber: null,
                invoiceUrl: null,
                ptpDateFormatted,
                disputeReasonShort: disputeReasonShort || '—',
                disputeReason: disputeReason || '',
                collectionPlanUrl: item.collectionPlanId ? `/lightning/r/CollectionPlan/${item.collectionPlanId}/view` : null,
                caseUrl: item.caseId ? `/lightning/r/Case/${item.caseId}/view` : null
            };
        });
    }

    get noWorklistItems() {
        return !this.worklistItems || this.worklistItems.length === 0;
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

    get cpTasksCount() {
        return this.cpTasks ? this.cpTasks.length : 0;
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

    get myCollectionPlansCount() {
        return this.myCollectionPlans ? this.myCollectionPlans.length : 0;
    }

    get hasCollectionsProgress() {
        return this.collectionsProgressData && this.collectionsProgressData.totalPlans > 0;
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
        if (!this.collectionsProgressData) return '0';
        return String(this.collectionsProgressData.avgDaysToClose);
    }

    get progressAvgDaysPastDue() {
        if (!this.collectionsProgressData) return '0';
        return String(this.collectionsProgressData.avgDaysPastDue);
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
        } catch (e) {
            return String(dateVal);
        }
    }
}