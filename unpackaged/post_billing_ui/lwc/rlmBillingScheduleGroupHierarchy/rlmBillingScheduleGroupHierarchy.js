import { LightningElement, api, wire, track } from 'lwc';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import getBillingScheduleGroups from '@salesforce/apex/RLM_BillingScheduleGroupController.getBillingScheduleGroups';
import { NavigationMixin } from 'lightning/navigation';

export default class RlmBillingScheduleGroupHierarchy extends NavigationMixin(LightningElement) {
    @api recordId;
    @api objectApiName;
    @track billingGroups = [];
    @track error;
    @track isLoading = true;
    @track showExpired = false;
    @track activeChargeType = 'all';
    @track activeStatusFilter = 'all';
    @track sortField = 'startDate';
    @track sortDirection = 'desc';

    @track totalBsgs = 0;
    @track activeBsgs = 0;
    @track expiredBsgs = 0;
    @track completelyBilledBsgs = 0;
    @track totalAmount = 0;
    @track pendingAmount = 0;

    @track chargeTypeCounts = { all: 0, recurring: 0, oneTime: 0, usage: 0, milestone: 0 };

    accountId;
    currencyCode = 'USD';
    hasInitialized = false;
    allBillingGroups = [];

    connectedCallback() {
        // For Account pages, recordId IS the accountId
        if (this.objectApiName === 'Account') {
            this.accountId = this.recordId;
            this.loadBillingGroups();
        }
        // For Order pages, we need to fetch the AccountId from the Order
        // This will be handled by the wire below
    }

    @wire(getRecord, { 
        recordId: '$recordId', 
        fields: ['Order.AccountId']
    })
    wiredRecord({ error, data }) {
        // Only process if this is an Order page
        if (this.objectApiName !== 'Order') {
            return;
        }

        if (data) {
            this.accountId = getFieldValue(data, 'Order.AccountId');
            this.loadBillingGroups();
        } else if (error) {
            this.error = 'Error loading record: ' + (error.body ? error.body.message : error);
            this.isLoading = false;
        }
    }

    classifyChargeType(bsg) {
        if (bsg.BillingTermUnit === 'BillingMilestonePlan') {
            return 'milestone';
        }
        if (bsg.BillingTermUnit === 'OneTime' || bsg.BillingTermUnit === 'Onetime' || bsg.BillingTermUnit === 'One-Time') {
            return 'oneTime';
        }
        if (bsg.BillingMethod === 'Usage') {
            return 'usage';
        }
        return 'recurring';
    }

    loadBillingGroups() {
        if (!this.accountId || this.hasInitialized) return;
        
        this.hasInitialized = true;
        this.isLoading = true;
        getBillingScheduleGroups({ accountId: this.accountId })
            .then(data => {
                try {
                    this.allBillingGroups = data;
                    this.countChargeTypes(data);
                    this.applyChargeTypeFilter();
                    this.error = undefined;
                } catch (e) {
                    this.error = 'Error processing billing schedule groups: ' + e.message;
                    this.billingGroups = [];
                }
                this.isLoading = false;
            })
            .catch(error => {
                this.error = error.body ? error.body.message : 'Unknown error occurred';
                this.billingGroups = [];
                this.isLoading = false;
            });
    }

    countChargeTypes(data) {
        const counts = { all: 0, recurring: 0, oneTime: 0, usage: 0, milestone: 0 };
        data.forEach(item => {
            if (item.bsg) {
                counts.all++;
                const ct = this.classifyChargeType(item.bsg);
                counts[ct]++;
            }
        });
        this.chargeTypeCounts = counts;
    }

    applyChargeTypeFilter() {
        let filtered = this.allBillingGroups;
        if (this.activeChargeType !== 'all') {
            filtered = this.allBillingGroups.filter(item => 
                item.bsg && this.classifyChargeType(item.bsg) === this.activeChargeType
            );
        }
        this.billingGroups = this.buildHierarchy(filtered);
        this.calculateSummary(filtered);
    }

    handleChargeTypeChange(event) {
        this.activeChargeType = event.currentTarget.dataset.type;
        this.applyChargeTypeFilter();
    }

    calculateSummary(data) {
        let billed = 0;
        let pending = 0;
        let active = 0;
        let expired = 0;
        let completelyBilled = 0;
        
        data.forEach(item => {
            if (item.bsg) {
                // Detect the org/data currency once (multi-currency support)
                if (!this.currencyCode || this.currencyCode === 'USD') {
                    this.currencyCode = item.bsg.CurrencyIsoCode || 'USD';
                }
                const billedAmt = item.bsg.TotalBilledAmount || 0;
                const pendingAmt = item.bsg.TotalPendingAmount || 0;
                billed += billedAmt;
                pending += pendingAmt;

                const status = this.getStatus(item.bsg);
                if (status === 'Active') {
                    active++;
                } else if (status === 'Expired') {
                    expired++;
                }

                if (billedAmt > 0 && pendingAmt === 0 && this.classifyChargeType(item.bsg) !== 'usage') {
                    completelyBilled++;
                }
            }
        });

        this.totalBsgs = data.length;
        this.activeBsgs = active;
        this.expiredBsgs = expired;
        this.completelyBilledBsgs = completelyBilled;
        this.totalAmount = billed;
        this.pendingAmount = pending;
    }

    buildHierarchy(data) {
        const bsgMap = new Map();
        const relationships = [];

        // Parse the data and separate BSGs and relationships
        data.forEach(item => {
            if (item.bsg) {
                const isOneTimeOrEvergreen = item.bsg.BillingTermUnit === 'OneTime' || 
                                            item.bsg.BillingTermUnit === 'Evergreen';
                
                // Create temp object with BillingTermUnit for getStatus
                const bsgWithTermUnit = {
                    ...item.bsg,
                    BillingTermUnit: item.bsg.BillingTermUnit
                };
                
                const chargeType = this.classifyChargeType(item.bsg);
                const bsg = {
                    id: item.bsg.Id,
                    name: item.bsg.ProductName || item.bsg.ReferenceEntityId || 'Unnamed Subscription',
                    startDate: item.bsg.StartDate || '—',
                    endDate: (chargeType === 'oneTime' && !item.bsg.EndDate)
                        ? (item.bsg.StartDate || '—')
                        : (item.bsg.EndDate || '—'),
                    nextBillingDate: item.bsg.EffectiveNextBillingDate || null,
                    billingTermUnit: item.bsg.BillingTermUnit,
                    billingTermLabel: this.getBillingTermLabel(item.bsg.BillingTermUnit),
                    chargeType: chargeType,
                    chargeTypeLabel: this.getChargeTypeLabel(chargeType),
                    totalAmount: item.bsg.TotalBilledAmount || 0,
                    pendingAmount: item.bsg.TotalPendingAmount || 0,
                    status: this.getStatus(bsgWithTermUnit),
                    isUsage: chargeType === 'usage',
                    billingPercentage: this.calculateBillingPercentage(
                        item.bsg.TotalBilledAmount,
                        item.bsg.TotalPendingAmount
                    ),
                    isCompletelyBilled: (item.bsg.TotalBilledAmount || 0) > 0 && 
                                        (item.bsg.TotalPendingAmount || 0) === 0 && 
                                        chargeType !== 'usage',
                    rawStartDate: item.bsg.StartDate,
                    rawEndDate: item.bsg.EndDate,
                    rawNextBillingDate: item.bsg.EffectiveNextBillingDate,
                    children: [],
                    isExpanded: true,
                    hasChildren: false,
                    level: 0,
                    childCount: 0
                };
                const pct = bsg.billingPercentage;
                let barColor = '#fe9339';
                if (pct === 100) barColor = '#2e844a';
                else if (pct >= 50) barColor = '#0176d3';
                bsg.progressStyle = `width: ${pct}%; background: ${barColor}; height: 100%; border-radius: 4px;`;

                bsg.nextBillingDateDisplay = bsg.nextBillingDate 
                    ? bsg.nextBillingDate 
                    : (bsg.isCompletelyBilled ? 'Completely Billed' : '—');
                bsg.nextBillingIsComplete = !bsg.nextBillingDate && bsg.isCompletelyBilled;

                bsgMap.set(item.bsg.Id, bsg);
            }

            if (item.relationships && item.relationships.length > 0) {
                relationships.push(...item.relationships);
            }
        });

        // Build parent-child relationships
        const rootBsgs = [];
        const childBsgIds = new Set();

        relationships.forEach(rel => {
            const parentBsg = bsgMap.get(rel.MainBsgId);
            const childBsg = bsgMap.get(rel.AssociatedBsgId);

            if (parentBsg && childBsg) {
                parentBsg.children.push(childBsg);
                parentBsg.hasChildren = true;
                parentBsg.childCount = parentBsg.children.length;
                childBsgIds.add(childBsg.id);
            }
        });

        // Identify root BSGs
        bsgMap.forEach((bsg, id) => {
            if (!childBsgIds.has(id)) {
                rootBsgs.push(bsg);
            }
        });

        // Set levels for hierarchy
        this.setLevels(rootBsgs, 0);

        return rootBsgs;
    }

    setLevels(bsgs, level) {
        bsgs.forEach(bsg => {
            bsg.level = level;
            bsg.indentClass = `indent-level-${level}`;
            if (bsg.children && bsg.children.length > 0) {
                this.setLevels(bsg.children, level + 1);
            }
        });
    }

    getChargeTypeLabel(chargeType) {
        const labels = {
            recurring: 'Recurring',
            oneTime: 'One-Time',
            usage: 'Usage',
            milestone: 'Milestone'
        };
        return labels[chargeType] || chargeType;
    }

    get chargeTypeTabs() {
        const tabs = [
            { type: 'all', label: 'All', count: this.chargeTypeCounts.all },
            { type: 'recurring', label: 'Recurring', count: this.chargeTypeCounts.recurring },
            { type: 'oneTime', label: 'One-Time', count: this.chargeTypeCounts.oneTime },
            { type: 'usage', label: 'Usage', count: this.chargeTypeCounts.usage },
            { type: 'milestone', label: 'Milestone', count: this.chargeTypeCounts.milestone }
        ];
        return tabs.map(t => ({
            ...t,
            isActive: t.type === this.activeChargeType,
            cssClass: 'charge-type-tab' + (t.type === this.activeChargeType ? ' active' : '')
        }));
    }

    getBillingTermLabel(billingTermUnit) {
        const termMap = {
            'Month':        'Monthly',
            'Year':         'Yearly',
            'Quarterly':    'Quarterly',
            'Semi-Annual':  'Semi-Annually',
            'OneTime':      'One-Time',
            'Onetime':      'One-Time',
            'One-Time':     'One-Time'
        };
        return termMap[billingTermUnit] || billingTermUnit || '—';
    }

    getStatus(bsg) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const startDate = bsg.StartDate ? new Date(bsg.StartDate) : null;
        const endDate = bsg.EndDate ? new Date(bsg.EndDate) : null;
        
        const isOneTime = bsg.BillingTermUnit === 'OneTime' || 
                          bsg.BillingTermUnit === 'Onetime' || 
                          bsg.BillingTermUnit === 'One-Time';
        const isEvergreen = bsg.BillingTermUnit === 'Evergreen';

        if (startDate && startDate > today) {
            return 'Pending';
        }

        if (isOneTime && startDate) {
            const effectiveEnd = endDate || startDate;
            return effectiveEnd < today ? 'Expired' : 'Active';
        }

        if (isEvergreen && startDate && startDate <= today) {
            return 'Active';
        }

        if (endDate && endDate < today) {
            return 'Expired';
        }
        if (startDate && startDate <= today && (!endDate || endDate >= today)) {
            return 'Active';
        }
        return 'Unknown';
    }

    calculateBillingPercentage(billedAmount, pendingAmount) {
        const billed = billedAmount || 0;
        const pending = pendingAmount || 0;
        const total = billed + pending;
        if (total === 0) return 0;
        return Math.round((billed / total) * 100);
    }

    handleToggle(event) {
        const bsgId = event.currentTarget.dataset.id;
        this.toggleExpansion(this.billingGroups, bsgId);
    }

    toggleExpansion(bsgs, targetId) {
        for (let bsg of bsgs) {
            if (bsg.id === targetId) {
                bsg.isExpanded = !bsg.isExpanded;
                this.billingGroups = [...this.billingGroups]; // Trigger reactivity
                return true;
            }
            if (bsg.children && bsg.children.length > 0) {
                if (this.toggleExpansion(bsg.children, targetId)) {
                    return true;
                }
            }
        }
        return false;
    }

    handleNavigate(event) {
        event.preventDefault();
        const recordId = event.currentTarget.dataset.id;
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: {
                recordId: recordId,
                objectApiName: 'BillingScheduleGroup',
                actionName: 'view'
            }
        });
    }

    handleToggleExpired(event) {
        this.showExpired = event.target.checked;
    }

    handleStatusFilterKeydown(event) {
        if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
            event.preventDefault();
            this.handleStatusFilter(event);
        }
    }

    handleStatusFilter(event) {
        const filter = event.currentTarget.dataset.filter;
        if (filter === 'all') {
            this.activeStatusFilter = 'all';
            this.showExpired = true;
        } else {
            this.activeStatusFilter = this.activeStatusFilter === filter ? 'all' : filter;
            if (this.activeStatusFilter === 'expired') {
                this.showExpired = true;
            } else if (this.activeStatusFilter === 'all') {
                this.showExpired = false;
            }
        }
    }

    handleSortChange(event) {
        this.sortField = event.target.value;
    }

    get sortOptions() {
        return [
            { label: 'Start Date (Newest)', value: 'startDate' },
            { label: 'End Date (Nearest)', value: 'endDate' },
            { label: 'Next Billing Date', value: 'nextBillingDate' }
        ];
    }

    get hasData() {
        return this.allBillingGroups && this.allBillingGroups.length > 0;
    }

    get hasGroups() {
        return this.billingGroups && this.billingGroups.length > 0;
    }

    get filteredGroups() {
        if (!this.billingGroups || this.billingGroups.length === 0) {
            return [];
        }

        let result = this.applyStatusAndExpiredFilter(this.billingGroups);
        result = this.sortBsgs(result);
        return result;
    }

    applyStatusAndExpiredFilter(bsgs) {
        return bsgs.reduce((filtered, bsg) => {
            let include = true;

            if (!this.showExpired && bsg.status === 'Expired') {
                include = false;
            }

            if (this.activeStatusFilter === 'active' && bsg.status !== 'Active') {
                include = false;
            } else if (this.activeStatusFilter === 'expired' && bsg.status !== 'Expired') {
                include = false;
            } else if (this.activeStatusFilter === 'completelyBilled' && !bsg.isCompletelyBilled) {
                include = false;
            }

            if (include) {
                const filteredBsg = { ...bsg };
                if (filteredBsg.children && filteredBsg.children.length > 0) {
                    filteredBsg.children = this.applyStatusAndExpiredFilter(filteredBsg.children);
                    filteredBsg.hasChildren = filteredBsg.children.length > 0;
                    filteredBsg.childCount = filteredBsg.children.length;
                }
                filtered.push(filteredBsg);
            }
            return filtered;
        }, []);
    }

    sortBsgs(bsgs) {
        const field = this.sortField;
        const rawField = field === 'startDate' ? 'rawStartDate' : 
                         field === 'endDate' ? 'rawEndDate' : 'rawNextBillingDate';
        
        return [...bsgs].sort((a, b) => {
            const aVal = a[rawField] || '';
            const bVal = b[rawField] || '';
            if (!aVal && !bVal) return 0;
            if (!aVal) return 1;
            if (!bVal) return -1;
            return bVal.localeCompare(aVal);
        });
    }

    get flattenedGroups() {
        return this.flattenHierarchy(this.filteredGroups);
    }

    flattenHierarchy(bsgs) {
        let result = [];
        bsgs.forEach(bsg => {
            result.push(bsg);
            if (bsg.isExpanded && bsg.children && bsg.children.length > 0) {
                result = result.concat(this.flattenHierarchy(bsg.children));
            }
        });
        return result;
    }

    get totalCardSelected() {
        return this.activeStatusFilter === 'all' && this.showExpired;
    }
    get activeCardSelected() {
        return this.activeStatusFilter === 'active';
    }
    get expiredCardSelected() {
        return this.activeStatusFilter === 'expired';
    }
    get totalCardClass() {
        return 'summary-card clickable' + (this.totalCardSelected ? ' card-selected' : '');
    }
    get activeCardClass() {
        return 'summary-card clickable' + (this.activeCardSelected ? ' card-selected' : '');
    }
    get expiredCardClass() {
        return 'summary-card clickable' + (this.expiredCardSelected ? ' card-selected' : '');
    }
    get completelyBilledCardClass() {
        return 'summary-card clickable' + (this.activeStatusFilter === 'completelyBilled' ? ' card-selected' : '');
    }

    get formattedTotalAmount() {
        return this.formatCurrency(this.totalAmount);
    }

    get formattedPendingAmount() {
        return this.formatCurrency(this.pendingAmount);
    }

    get summaryText() {
        return `${this.totalBsgs} items • Billed: ${this.formattedTotalAmount} • Pending: ${this.formattedPendingAmount}`;
    }

    formatCurrency(value) {
        if (value === null || value === undefined) return '$0.00';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: this.currencyCode || 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
}