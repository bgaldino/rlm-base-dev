import { LightningElement, track, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import getHighValueDelinquents from '@salesforce/apex/RLM_CollectionsConsoleController.getHighValueDelinquents';

export default class RlmCollectionsConsole extends NavigationMixin(LightningElement) {
    /* List-view IDs for each aging bucket — used to navigate to filtered Invoice lists */
    agingListViews = {
        current: '00BWt00000A0o0fMAB',
        '30': '00BWt00000A0mDNMAZ',
        '60': '00BWt00000A0mJpMAJ',
        '90': '00BWt00000A0mN3MAJ',
        'over90': '00BWt00000A2mM9MAJ'
    };

    selectedAccount = 'all';
    selectedCurrency = 'all';
    @track activeToggle = 'aging';
    @track activeDataTab = 'critical';

    get accountOptions() {
        return [
            { label: 'All Accounts', value: 'all' }
        ];
    }

    get currencyOptions() {
        return [
            { label: 'All Currencies', value: 'all' }
        ];
    }

    // ====================== Toggle buttons ======================
    get isAgingActive() {
        return this.activeToggle === 'aging';
    }

    get isPaymentPromisesActive() {
        return this.activeToggle === 'payment';
    }

    /* Returns SLDS-compliant CSS class string with c-* prefixed modifier */
    get agingButtonClass() {
        return this.activeToggle === 'aging' ? 'c-toggle-btn c-active' : 'c-toggle-btn';
    }

    get paymentPromisesButtonClass() {
        return this.activeToggle === 'payment' ? 'c-toggle-btn c-active' : 'c-toggle-btn';
    }

    /* Navigate to the appropriate Invoice list view when an aging bucket is clicked */
    handleAgingClick(event) {
        const bucket = event.currentTarget.dataset.bucket;
        const listViewId = this.agingListViews[bucket];
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

    /* Keyboard handler for aging bucket items — enables Enter/Space activation (WCAG 2.1.1) */
    handleAgingKeydown(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            this.handleAgingClick(event);
        }
    }

    handleToggleAging() {
        this.activeToggle = 'aging';
    }

    handleTogglePaymentPromises() {
        this.activeToggle = 'payment';
    }

    // ====================== Data tabs ======================
    get isCriticalTab() {
        return this.activeDataTab === 'critical';
    }

    get isHighValueTab() {
        return this.activeDataTab === 'highValue';
    }

    get isDisputedTab() {
        return this.activeDataTab === 'disputed';
    }

    get criticalTabClass() {
        return this.activeDataTab === 'critical' ? 'c-data-tab c-active' : 'c-data-tab';
    }

    get highValueTabClass() {
        return this.activeDataTab === 'highValue' ? 'c-data-tab c-active' : 'c-data-tab';
    }

    get disputedTabClass() {
        return this.activeDataTab === 'disputed' ? 'c-data-tab c-active' : 'c-data-tab';
    }

    handleTabCritical() {
        this.activeDataTab = 'critical';
    }

    handleTabHighValue() {
        this.activeDataTab = 'highValue';
    }

    handleTabDisputed() {
        this.activeDataTab = 'disputed';
    }

    /* ARIA tabindex pattern: only the active tab is in the tab order (tabindex 0);
       inactive tabs use tabindex -1 so arrow keys move focus, not Tab (WCAG 2.1.1). */
    get criticalTabIndex() {
        return this.activeDataTab === 'critical' ? '0' : '-1';
    }

    get highValueTabIndex() {
        return this.activeDataTab === 'highValue' ? '0' : '-1';
    }

    get disputedTabIndex() {
        return this.activeDataTab === 'disputed' ? '0' : '-1';
    }

    /* Arrow-key navigation between tabs per WAI-ARIA Authoring Practices (WCAG 2.1.1).
       Left/Right arrows cycle through tabs; Home/End jump to first/last. */
    _tabOrder = ['critical', 'highValue', 'disputed'];
    _tabIdMap = { critical: 'tab-critical', highValue: 'tab-highvalue', disputed: 'tab-disputed' };

    handleTabKeydown(event) {
        const currentIndex = this._tabOrder.indexOf(this.activeDataTab);
        let newIndex = currentIndex;

        switch (event.key) {
            case 'ArrowRight':
                newIndex = (currentIndex + 1) % this._tabOrder.length;
                break;
            case 'ArrowLeft':
                newIndex = (currentIndex - 1 + this._tabOrder.length) % this._tabOrder.length;
                break;
            case 'Home':
                newIndex = 0;
                break;
            case 'End':
                newIndex = this._tabOrder.length - 1;
                break;
            default:
                return; // Don't prevent default for other keys
        }

        event.preventDefault();
        this.activeDataTab = this._tabOrder[newIndex];
        /* Move focus to the newly activated tab after the DOM re-renders */
        const newTabId = this._tabIdMap[this._tabOrder[newIndex]];
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        requestAnimationFrame(() => {
            const newTab = this.template.querySelector(`#${newTabId}`);
            if (newTab) {
                newTab.focus();
            }
        });
    }

    handleAccountChange(event) {
        this.selectedAccount = event.detail.value;
    }

    handleCurrencyChange(event) {
        this.selectedCurrency = event.detail.value;
    }

    // ====================== Donut chart interactivity ======================
    /* Segment data — maps segment key to label and dollar amount for the floating tooltip */
    donutSegmentData = {
        recovered: { label: 'Recovered', amount: '$500', percentage: '2.4%' },
        'yet-to-recover': { label: 'Yet to Recover', amount: '$20,091.87', percentage: '97.6%' }
    };

    @track donutTooltipVisible = false;
    @track donutTooltipLabel = '';
    @track donutTooltipValue = '';
    @track donutScreenReaderText = '';

    /* CSS class for floating tooltip — hidden when no segment is active */
    get donutFloatingTooltipClass() {
        return this.donutTooltipVisible
            ? 'c-donut-floating-tooltip c-donut-floating-tooltip-visible'
            : 'c-donut-floating-tooltip';
    }

    /* Show floating tooltip on segment hover/focus */
    handleDonutHover(event) {
        const segment = event.currentTarget.dataset.segment;
        const data = this.donutSegmentData[segment];
        if (data) {
            this.donutTooltipLabel = data.label;
            this.donutTooltipValue = data.amount;
            this.donutTooltipVisible = true;
            /* Announce to screen readers so segment info is conveyed without visual-only cues */
            this.donutScreenReaderText = `${data.label}: ${data.amount}, ${data.percentage}`;
        }
    }

    /* Hide floating tooltip when cursor/focus leaves the segment */
    handleDonutLeave() {
        this.donutTooltipVisible = false;
    }

    /* Track mouse position to anchor the floating tooltip near the cursor.
       Uses the chart container as the positioning context. */
    handleDonutMouseMove(event) {
        const container = this.template.querySelector('.c-donut-chart-container');
        if (container) {
            const rect = container.getBoundingClientRect();
            /* Offset tooltip slightly from cursor so it doesn't block the segment */
            const offsetX = 12;
            const offsetY = 16;
            this._donutTooltipX = event.clientX - rect.left + offsetX;
            this._donutTooltipY = event.clientY - rect.top + offsetY;
            /* Apply position via style attribute on the tooltip element */
            const tooltip = this.template.querySelector('.c-donut-floating-tooltip');
            if (tooltip) {
                tooltip.style.left = `${this._donutTooltipX}px`;
                tooltip.style.top = `${this._donutTooltipY}px`;
            }
        }
    }

    /* Keyboard support for donut segments — Tab navigates between segments,
       Escape dismisses the tooltip (WCAG 2.1.1, 2.1.2) */
    handleDonutKeydown(event) {
        if (event.key === 'Escape') {
            event.currentTarget.blur();
            this.handleDonutLeave();
        }
    }

    // ====================== Invoice datatable ======================
    invoiceRowActions = [
        { label: 'View', name: 'view' },
        { label: 'Edit', name: 'edit' },
        { label: 'Delete', name: 'delete' },
        { label: 'Change Owner', name: 'change_owner' },
        { label: 'Change Record Type', name: 'change_record_type' },
        { label: 'Clone', name: 'clone' },
        { label: 'Print', name: 'print' }
    ];

    get invoiceColumns() {
        return [
            {
                label: 'Billing Account',
                fieldName: 'billingAccountUrl',
                type: 'url',
                typeAttributes: { label: { fieldName: 'billingAccount' }, target: '_blank' }
            },
            {
                label: 'Invoice Number',
                fieldName: 'invoiceUrl',
                type: 'url',
                typeAttributes: { label: { fieldName: 'invoiceNumber' }, target: '_blank' }
            },
            {
                label: 'Balance',
                fieldName: 'balance',
                type: 'currency',
                typeAttributes: { currencyCode: 'USD' }
            },
            {
                label: 'Overdue Days',
                fieldName: 'overdueDays',
                type: 'number'
            },
            {
                label: 'Bill To Contact',
                fieldName: 'billToContact',
                type: 'text'
            },
            {
                label: 'Collection ID',
                fieldName: 'collectionUrl',
                type: 'url',
                typeAttributes: { label: { fieldName: 'collectionId' }, target: '_blank' }
            },
            {
                type: 'action',
                typeAttributes: { rowActions: this.invoiceRowActions }
            }
        ];
    }

    get invoicesCount() {
        return this.invoiceData.length;
    }

    get invoiceData() {
        return [
            { Id: 'inv1', billingAccount: 'NovaSphere Solutions', billingAccountUrl: '#', invoiceNumber: 'INV-US-02-2026-000096', invoiceUrl: '#', balance: 2876.00, overdueDays: 69, billToContact: 'Acme USA', collectionId: 'CP-00PQ1', collectionUrl: '#' },
            { Id: 'inv2', billingAccount: 'NovaSphere Solutions', billingAccountUrl: '#', invoiceNumber: 'INV-US-02-2026-000090', invoiceUrl: '#', balance: 3476.00, overdueDays: 87, billToContact: 'Acme JAPAN', collectionId: 'CP-00AC4', collectionUrl: '#' },
            { Id: 'inv3', billingAccount: 'Acme', billingAccountUrl: '#', invoiceNumber: 'INV-US-02-2026-000872', invoiceUrl: '#', balance: 9809.00, overdueDays: 900, billToContact: 'Acme EU', collectionId: 'CP-00PLM8', collectionUrl: '#' }
        ];
    }

    handleInvoiceRowAction(event) {
        const action = event.detail.action;
        const row = event.detail.row;
        switch (action.name) {
            case 'view':
                this[NavigationMixin.Navigate]({
                    type: 'standard__recordPage',
                    attributes: {
                        recordId: row.Id,
                        objectApiName: 'Invoice',
                        actionName: 'view'
                    }
                });
                break;
            case 'edit':
                this[NavigationMixin.Navigate]({
                    type: 'standard__recordPage',
                    attributes: {
                        recordId: row.Id,
                        objectApiName: 'Invoice',
                        actionName: 'edit'
                    }
                });
                break;
            case 'delete':
                this[NavigationMixin.Navigate]({
                    type: 'standard__recordPage',
                    attributes: {
                        recordId: row.Id,
                        objectApiName: 'Invoice',
                        actionName: 'view'
                    }
                });
                break;
            case 'change_owner':
                this[NavigationMixin.Navigate]({
                    type: 'standard__objectPage',
                    attributes: {
                        objectApiName: 'Invoice',
                        actionName: 'list'
                    }
                });
                break;
            case 'clone':
                this[NavigationMixin.Navigate]({
                    type: 'standard__objectPage',
                    attributes: {
                        objectApiName: 'Invoice',
                        actionName: 'new'
                    },
                    state: {
                        defaultFieldValues: 'BillingAccountId=' + row.Id
                    }
                });
                break;
            default:
                break;
        }
    }

    handleViewAllInvoices(event) {
        event.preventDefault();
        this[NavigationMixin.Navigate]({
            type: 'standard__objectPage',
            attributes: {
                objectApiName: 'Invoice',
                actionName: 'list'
            },
            state: {
                filterName: 'All'
            }
        });
    }

    // ====================== Delinquents datatable ======================
    get delinquentColumns() {
        return [
            {
                label: 'Business Account',
                fieldName: 'accountUrl',
                type: 'url',
                typeAttributes: { label: { fieldName: 'businessAccount' }, target: '_blank' }
            },
            {
                label: 'Invoice Balance',
                fieldName: 'invoiceBalance',
                type: 'currency',
                typeAttributes: { currencyCode: 'USD' }
            },
            {
                label: 'Balance',
                fieldName: 'balance',
                type: 'currency',
                typeAttributes: { currencyCode: 'USD' }
            },
            {
                label: 'Days Overdue',
                fieldName: 'overdueDays',
                type: 'number'
            },
            {
                label: 'PTP Date',
                fieldName: 'ptpDate',
                type: 'date',
                typeAttributes: { month: '2-digit', day: '2-digit', year: 'numeric' }
            },
            {
                label: 'Dispute Reason',
                fieldName: 'disputeReason',
                type: 'text'
            },
            {
                label: 'Collection Plan ID',
                fieldName: 'collectionPlanUrl',
                type: 'url',
                typeAttributes: { label: { fieldName: 'collectionPlanId' }, target: '_blank' }
            },
            {
                type: 'action',
                typeAttributes: { rowActions: this.invoiceRowActions }
            }
        ];
    }

    @track delinquentData = [];

    @wire(getHighValueDelinquents)
    wiredDelinquents({ error, data }) {
        if (data) {
            this.delinquentData = data.map(item => ({
                Id: item.Id,
                businessAccount: item.businessAccount,
                accountUrl: item.accountId ? '/' + item.accountId : '#',
                invoiceBalance: item.invoiceBalance,
                balance: item.balance,
                overdueDays: item.overdueDays,
                ptpDate: item.ptpDate,
                disputeReason: item.disputeReason || '-',
                collectionPlanId: item.collectionPlanId || '-',
                collectionPlanUrl: item.collectionPlanRecordId ? '/' + item.collectionPlanRecordId : '#'
            }));
        } else if (error) {
            console.error('Error loading delinquents:', error);
        }
    }

    get delinquentsCount() {
        return this.delinquentData.length;
    }

    get disputedCount() {
        return this.disputedInvoices.length;
    }

    /* Column definitions for Disputed Invoices lightning-datatable */
    disputedRowActions = [
        { label: 'View', name: 'view' },
        { label: 'Edit', name: 'edit' }
    ];

    get disputedColumns() {
        return [
            { label: 'Customer', fieldName: 'customer', type: 'text' },
            { label: 'Balance', fieldName: 'balance', type: 'text' },
            { label: 'Overdue Days', fieldName: 'overdueDays', type: 'text' },
            { label: 'FTP Date', fieldName: 'ftpDate', type: 'text' },
            { label: 'Dispute Reason', fieldName: 'disputeReason', type: 'text' },
            { label: 'Case Number', fieldName: 'caseNumber', type: 'text' },
            { type: 'action', typeAttributes: { rowActions: this.disputedRowActions } }
        ];
    }

    get disputedInvoices() {
        return [
            { id: '1', customer: 'LimaHQ1', balance: '$2876.00', overdueDays: '69', ftpDate: '12/04/2026', disputeReason: '-', caseNumber: '0043982' },
            { id: '2', customer: 'NovaSphere Solutions', balance: '$3476.00', overdueDays: '87', ftpDate: '12/04/2026', disputeReason: '-', caseNumber: '0089342' },
            { id: '3', customer: 'Acme', balance: '$9809.00', overdueDays: '900', ftpDate: '12/04/2026', disputeReason: '-', caseNumber: '9608624' }
        ];
    }

    handleDisputedRowAction(event) {
        const action = event.detail.action;
        const row = event.detail.row;
        if (action.name === 'view' || action.name === 'edit') {
            console.log('Disputed invoice action:', action.name, row);
        }
    }

    get collectionPlansCount() {
        return 31;
    }

    /* Row actions for collection plans and disputed invoices */
    collectionPlanRowActions = [
        { label: 'View', name: 'view' },
        { label: 'Edit', name: 'edit' }
    ];

    /* Column definitions for My Collection Plans lightning-datatable */
    get collectionPlanColumns() {
        return [
            { label: 'CP ID', fieldName: 'customer', type: 'text' },
            { label: 'Due', fieldName: 'due', type: 'text' },
            { label: 'Account', fieldName: 'account', type: 'text' },
            { label: 'Account', fieldName: 'amount', type: 'text' },
            { type: 'action', typeAttributes: { rowActions: this.collectionPlanRowActions } }
        ];
    }

    /* Collection plans data for lightning-datatable */
    get collectionPlans() {
        return [
            { id: '1', customer: 'NovaSphere Solutions', due: 'INV-US-02-2026-000096', account: 'Acme USA', amount: '$2876.00' },
            { id: '2', customer: 'NovaSphere Solutions', due: 'INV-US-02-2026-000090', account: 'Acme JAPAN', amount: '$3476.00' },
            { id: '3', customer: 'Acme', due: 'INV-US-02-2026-000872', account: 'Acme EU', amount: '$9809.00' }
        ];
    }

    handleCollectionPlanRowAction(event) {
        const action = event.detail.action;
        const row = event.detail.row;
        if (action.name === 'view' || action.name === 'edit') {
            console.log('Collection Plan action:', action.name, row);
        }
    }

    /* Column definitions for My Tasks lightning-datatable — matches Figma sort-arrow headers */
    get taskColumns() {
        return [
            { label: 'Subject', fieldName: 'subject', type: 'text', sortable: true },
            { label: 'Due', fieldName: 'due', type: 'text', sortable: true },
            { label: 'Status', fieldName: 'status', type: 'text', sortable: true },
            { label: 'CP ID', fieldName: 'cpId', type: 'text', sortable: true }
        ];
    }

    get tasks() {
        return [
            { id: '1', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 1' },
            { id: '2', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 2' },
            { id: '3', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 3' },
            { id: '4', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 4' },
            { id: '5', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 5' },
            { id: '6', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 6' },
            { id: '7', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 7' },
            { id: '8', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 8' },
            { id: '9', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 9' },
            { id: '10', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 10' },
            { id: '11', subject: 'RTL98879', due: '03/23/2021...', status: 'Due to invo...', cpId: 'Record 11' }
        ];
    }
}