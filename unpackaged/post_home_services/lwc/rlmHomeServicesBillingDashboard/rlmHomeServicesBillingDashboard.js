import { LightningElement, api, wire, track } from 'lwc';
import getBillingScheduleGroup from '@salesforce/apex/RLM_HomeServices_BillingDashCtrl.getBillingScheduleGroup';
import getBillingScheduleGroups from '@salesforce/apex/RLM_HomeServices_BillingDashCtrl.getBillingScheduleGroups';
import getMilestonePlanItems from '@salesforce/apex/RLM_HomeServices_BillingDashCtrl.getMilestonePlanItems';
import getInvoices from '@salesforce/apex/RLM_HomeServices_BillingDashCtrl.getInvoices';
import getSavedPaymentMethods from '@salesforce/apex/RLM_HomeServices_BillingDashCtrl.getSavedPaymentMethods';

const MILESTONE_COLUMNS = [
    { label: 'Plan',             fieldName: 'PlanName',         type: 'text',     sortable: false },
    { label: 'Name',             fieldName: 'Name',             type: 'text',     sortable: true  },
    { label: 'Milestone Type',   fieldName: 'MilestoneType',    type: 'text',     sortable: false },
    { label: 'Status',           fieldName: 'Status',           type: 'text',     sortable: false },
    {
        label: 'Milestone Amount',
        fieldName: 'MilestoneAmount',
        type: 'currency',
        sortable: false,
        typeAttributes: { currencyCode: 'USD', minimumFractionDigits: 2 }
    }
];

const INVOICE_COLUMNS = [
    { label: 'Invoice Number',   fieldName: 'DocumentNumber',       type: 'text'     },
    { label: 'Status',           fieldName: 'Status',               type: 'text'     },
    { label: 'Invoice Date',     fieldName: 'InvoiceDate',          type: 'date'     },
    { label: 'Due Date',         fieldName: 'DueDate',              type: 'date'     },
    { label: 'Total Amount',     fieldName: 'TotalAmountWithTax',   type: 'currency', typeAttributes: { currencyCode: 'USD', minimumFractionDigits: 2 } },
    { label: 'Balance',          fieldName: 'Balance',              type: 'currency', typeAttributes: { currencyCode: 'USD', minimumFractionDigits: 2 } },
    { label: 'Description',      fieldName: 'Description',          type: 'text'     }
];

const PAYMENT_COLUMNS = [
    { label: 'Type',             fieldName: 'Type',                 type: 'text'    },
    { label: 'Status',           fieldName: 'Status',               type: 'text'    },
    { label: 'Default',          fieldName: 'IsDefault',            type: 'boolean' },
    { label: 'Name',             fieldName: 'Name',                 type: 'text'    },
    { label: 'Expiry Month',     fieldName: 'ExpiryMonth',          type: 'text'    },
    { label: 'Expiry Year',      fieldName: 'ExpiryYear',           type: 'text'    }
];


export default class RlmHomeServicesBillingDashboard extends LightningElement {
    @api recordId; // Account Id injected by the flexipage runtime

    @track bsgId;
    @track bsgList = [];
    @track milestoneItems = [];
    @track invoiceRecords = [];
    @track paymentRecords = [];
    @track milestoneSortedBy = 'Name';
    @track milestoneSortDirection = 'asc';
    @track isMilestonesExpanded = false;

    isLoading = true;
    hasError = false;
    errorMessage = '';
    noBsg = false;

    milestoneColumns = MILESTONE_COLUMNS;
    invoiceColumns   = INVOICE_COLUMNS;
    paymentColumns   = PAYMENT_COLUMNS;

    // ── Step 1: resolve the BillingScheduleGroup for this Account ──────────
    @wire(getBillingScheduleGroup, { accountId: '$recordId' })
    wiredBsg({ data, error }) {
        if (data) {
            if (data.Id) {
                this.bsgId = data.Id;
                this.noBsg = false;
            } else {
                this.noBsg = true;
                this.isLoading = false;
            }
        } else if (error) {
            this._handleError(error);
        }
    }

    // ── Load every BSG for the account so timelines render per plan ────────
    @wire(getBillingScheduleGroups, { accountId: '$recordId' })
    wiredBsgList({ data, error }) {
        if (data) {
            this.bsgList = data.map(b => ({ id: b.Id, productName: b.ProductName }));
        } else if (error) {
            this._handleError(error);
        }
    }

    // ── Step 2: load milestone plan items across all of the account's BSGs ──
    @wire(getMilestonePlanItems, { accountId: '$recordId' })
    wiredMilestones({ data, error }) {
        if (data) {
            const flattened = data.map(item => ({
                ...item,
                PlanName: item.BillingScheduleGroup
                    ? item.BillingScheduleGroup.ProductName
                    : ''
            }));
            this.milestoneItems = this._sortByNameNumeric(flattened);
            this.isLoading = false;
        } else if (error) {
            this._handleError(error);
        }
    }

    // ── Invoices via Apex ───────────────────────────────────────────────────
    @wire(getInvoices, { accountId: '$recordId' })
    wiredInvoices({ data, error }) {
        if (data) {
            this.invoiceRecords = data;
        } else if (error) {
            console.error('Invoice query error:', error);
        }
    }

    // ── Saved Payment Methods via Apex ──────────────────────────────────────
    @wire(getSavedPaymentMethods, { accountId: '$recordId' })
    wiredPayments({ data, error }) {
        if (data) {
            this.paymentRecords = data;
        } else if (error) {
            console.error('Saved payment methods query error:', error);
        }
    }

    // ── Computed properties ────────────────────────────────────────────────
    get hasMilestoneItems() {
        return this.milestoneItems && this.milestoneItems.length > 0;
    }

    get hasMoreMilestones() {
        return this.milestoneItems
            && this.milestoneItems.length > this._collapsedMilestoneCount;
    }

    // Show all "Month 1 Service" rows (across every plan) when collapsed;
    // all rows when expanded.
    get visibleMilestoneItems() {
        if (this.isMilestonesExpanded) return this.milestoneItems;
        if (!this.milestoneItems || this.milestoneItems.length === 0) return [];
        const firstMonth = this._extractMonth(this.milestoneItems[0].Name);
        return this.milestoneItems.filter(
            item => this._extractMonth(item.Name) === firstMonth
        );
    }

    get _collapsedMilestoneCount() {
        if (!this.milestoneItems || this.milestoneItems.length === 0) return 0;
        const firstMonth = this._extractMonth(this.milestoneItems[0].Name);
        return this.milestoneItems.filter(
            item => this._extractMonth(item.Name) === firstMonth
        ).length;
    }

    get milestoneToggleLabel() {
        if (this.isMilestonesExpanded) {
            return 'Collapse';
        }
        const remaining = this.milestoneItems.length - this._collapsedMilestoneCount;
        return `View all ${this.milestoneItems.length} items (${remaining} more)`;
    }

    get milestoneToggleIcon() {
        return this.isMilestonesExpanded ? 'utility:chevronup' : 'utility:chevrondown';
    }

    get hasInvoices() {
        return this.invoiceRecords && this.invoiceRecords.length > 0;
    }

    get hasPaymentMethods() {
        return this.paymentRecords && this.paymentRecords.length > 0;
    }

    get sortedMilestoneItems() {
        return this.milestoneItems;
    }

    // ── Expand / Collapse toggle ───────────────────────────────────────────
    toggleMilestones() {
        this.isMilestonesExpanded = !this.isMilestonesExpanded;
    }

    // ── Column sort handler (Name column) ──────────────────────────────────
    handleMilestoneSort(event) {
        const { fieldName, sortDirection } = event.detail;
        this.milestoneSortedBy = fieldName;
        this.milestoneSortDirection = sortDirection;

        if (fieldName === 'Name') {
            const sorted = this._sortByNameNumeric(this.milestoneItems);
            this.milestoneItems = sortDirection === 'asc' ? sorted : [...sorted].reverse();
        }
    }

    // ── Numeric Name sort ──────────────────────────────────────────────────
    // Extracts the month integer from strings like "Month 1 Service",
    // "Month 12 Service" so ordering is 1, 2, 3 … 12 rather than 1, 10, 11 …
    // Ties (same month across multiple plans) fall back to plan name.
    _sortByNameNumeric(items) {
        if (!items || items.length === 0) return [];
        return [...items].sort((a, b) => {
            const diff = this._extractMonth(a.Name) - this._extractMonth(b.Name);
            if (diff !== 0) return diff;
            return (a.PlanName || '').localeCompare(b.PlanName || '');
        });
    }

    // Extracts the first integer found in a milestone name (e.g. "Month 1 Service" -> 1).
    _extractMonth(name) {
        const match = name && name.match(/(\d+)/);
        return match ? parseInt(match[1], 10) : Infinity;
    }

    // ── Error handler ──────────────────────────────────────────────────────
    _handleError(error) {
        this.isLoading = false;
        this.hasError = true;
        if (error && error.body && error.body.message) {
            this.errorMessage = error.body.message;
        } else if (error && error.message) {
            this.errorMessage = error.message;
        } else {
            this.errorMessage = 'An unexpected error occurred loading the billing dashboard.';
        }
    }
}