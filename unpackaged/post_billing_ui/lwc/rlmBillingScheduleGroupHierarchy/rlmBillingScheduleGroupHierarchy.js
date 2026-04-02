import { LightningElement, api, wire, track } from 'lwc';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import getBillingScheduleGroups from '@salesforce/apex/RLM_BillingScheduleGroupController.getBillingScheduleGroups';
import { NavigationMixin } from 'lightning/navigation';

export default class RlmBillingScheduleGroupHierarchy extends NavigationMixin(LightningElement) {
    @api recordId; // Can be Account Id or Order Id
    @api objectApiName; // Object type (Account or Order)
    @track billingGroups = [];
    @track error;
    @track isLoading = true;

    // Summary statistics
    @track totalBsgs = 0;
    @track activeBsgs = 0;
    @track totalAmount = 0;
    @track pendingAmount = 0;

    accountId; // The resolved account ID to query
    hasInitialized = false;

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

    loadBillingGroups() {
        if (!this.accountId || this.hasInitialized) return;
        
        this.hasInitialized = true;
        this.isLoading = true;
        getBillingScheduleGroups({ accountId: this.accountId })
            .then(data => {
                try {
                    this.billingGroups = this.buildHierarchy(data);
                    this.calculateSummary(data);
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

    calculateSummary(data) {
        let total = 0;
        let pending = 0;
        let active = 0;
        
        data.forEach(item => {
            if (item.bsg) {
                total += item.bsg.TotalBilledAmount || 0;
                pending += item.bsg.TotalPendingAmount || 0;
                // Count active BSGs (started and not expired)
                const today = new Date();
                const startDate = item.bsg.StartDate ? new Date(item.bsg.StartDate) : null;
                const endDate = item.bsg.EndDate ? new Date(item.bsg.EndDate) : null;
                const isOneTimeOrEvergreen = item.bsg.BillingTermUnit === 'OneTime' || 
                                            item.bsg.BillingTermUnit === 'Evergreen';
                
                if (isOneTimeOrEvergreen && startDate && startDate <= today) {
                    active++;
                } else if (startDate && startDate <= today && (!endDate || endDate >= today)) {
                    active++;
                }
            }
        });

        this.totalBsgs = data.length;
        this.activeBsgs = active;
        this.totalAmount = total;
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
                
                const bsg = {
                    id: item.bsg.Id,
                    name: item.bsg.ProductName || item.bsg.ReferenceEntityId || 'Unnamed BSG',
                    startDate: item.bsg.StartDate,
                    endDate: item.bsg.EndDate,
                    hasEndDate: !isOneTimeOrEvergreen && !!item.bsg.EndDate,
                    billingTermUnit: item.bsg.BillingTermUnit,
                    billingTermLabel: this.getBillingTermLabel(item.bsg.BillingTermUnit),
                    totalAmount: item.bsg.TotalBilledAmount || 0,
                    pendingAmount: item.bsg.TotalPendingAmount || 0,
                    status: this.getStatus(bsgWithTermUnit),
                    billingPercentage: this.calculateBillingPercentage(
                        item.bsg.TotalPendingAmount,
                        item.bsg.TotalBilledAmount
                    ),
                    children: [],
                    isExpanded: true,
                    hasChildren: false,
                    level: 0,
                    childCount: 0
                };
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
        const startDate = bsg.StartDate ? new Date(bsg.StartDate) : null;
        const endDate = bsg.EndDate ? new Date(bsg.EndDate) : null;
        
        // Debug logging
        console.log('BSG Status Check:', {
            BillingTermUnit: bsg.BillingTermUnit,
            StartDate: bsg.StartDate,
            EndDate: bsg.EndDate,
            ProductName: bsg.ProductName
        });
        
        const isOneTimeOrEvergreen = bsg.BillingTermUnit === 'OneTime' || 
                                     bsg.BillingTermUnit === 'Evergreen';
        
        console.log('Is One-Time or Evergreen:', isOneTimeOrEvergreen);

        if (startDate && startDate > today) {
            return 'Pending';
        } else if (isOneTimeOrEvergreen && startDate && startDate <= today) {
            return 'Active';
        } else if (endDate && endDate < today) {
            return 'Expired';
        } else if (startDate && startDate <= today && (!endDate || endDate >= today)) {
            return 'Active';
        }
        return 'Unknown';
    }

    calculateBillingPercentage(pendingAmount, billedAmount) {
        const total = (billedAmount || 0) + (pendingAmount || 0);
        if (!total || total === 0) return 0;
        return Math.round(((billedAmount || 0) / total) * 100);
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

    get hasGroups() {
        return this.billingGroups && this.billingGroups.length > 0;
    }

    get flattenedGroups() {
        return this.flattenHierarchy(this.billingGroups);
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
            currency: 'USD',
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