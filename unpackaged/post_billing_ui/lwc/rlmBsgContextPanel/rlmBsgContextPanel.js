import { LightningElement, api, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import getBSGContext from '@salesforce/apex/RLM_BSGContextController.getBSGContext';

export default class RlmBsgContextPanel extends NavigationMixin(LightningElement) {
    @api recordId;

    context;
    error;
    isLoading = true;

    @wire(getBSGContext, { recordId: '$recordId' })
    wiredContext({ error, data }) {
        if (data) {
            this.context = data;
            this.error = undefined;
            this.isLoading = false;
        } else if (error) {
            this.error = error.body?.message || 'Error loading context';
            this.context = undefined;
            this.isLoading = false;
        }
    }

    get hasData() { return !this.isLoading && this.context != null; }
    get isMilestoneView() { return this.context?.viewType === 'milestone'; }
    get isBundleView() { return this.context?.viewType === 'bundle'; }
    get isUsageView() { return this.context?.viewType === 'usage'; }
    get isStandardView() { return this.context?.viewType === 'standard'; }

    get cardTitle() { return 'Billing Model'; }
    get cardIcon() { return 'standard:metrics'; }

    // ─── Human-language summary ─────────────────────────────────────────────

    get billingSummaryText() {
        const c = this.context;
        if (!c) return '';
        const product = c.productName || 'this product';
        const arrSuffix = '';

        switch (c.viewType) {
            case 'milestone': {
                const planName = c.milestonePlan?.planName || 'a milestone plan';
                return `This charge is billed based on the milestones defined in "${planName}" plan. Each milestone is invoiced upon completion for a percentage or fixed amount of the total billings.${arrSuffix}`;
            }
            case 'bundle': {
                const bd = c.bundle;
                if (bd?.isMainBundle) {
                    const count = bd.components?.length || 0;
                    return `${product} is a bundle with ${count} component product${count !== 1 ? 's' : ''} included. Each component may have its own billing frequency and charge type.${arrSuffix}`;
                }
                const chargeType = c.billingTermUnit?.toLowerCase() === 'onetime'
                    ? 'a one-time billing charge'
                    : c.billingMethod === 'Usage'
                        ? 'a usage-based charge'
                        : (c.billingTerm && c.billingTermUnit
                            ? `a ${c.billingTerm} ${c.billingTermUnit.toLowerCase()} subscription charge`
                            : 'a recurring charge');
                return `${product} is ${chargeType}, part of the "${bd?.mainBsgProduct || ''}" bundle.${arrSuffix}`;
            }
            case 'usage': {
                const resource = c.usage?.currentResourceName || 'a usage resource';
                const anchor = c.usage?.anchorProductName || 'the anchor product';
                const arrears = c.billingType === 'Arrears' ? 'in arrears ' : '';
                return `This is a usage-based charge for the ${resource} resource, linked to anchor product ${anchor}. Billing is ${arrears}based on actual consumption.${arrSuffix}`;
            }
            default: {
                const unit = (c.billingTermUnit || '').toLowerCase();
                if (unit === 'onetime' || unit === 'one time' || unit === 'one-time') {
                    return `${product} is billed as a one-time charge${c.billingType ? ' in ' + c.billingType.toLowerCase() : ''}.${arrSuffix}`;
                }
                const freq = c.billingTerm && c.billingTermUnit
                    ? `every ${c.billingTerm} ${c.billingTermUnit.toLowerCase()}`
                    : 'on a recurring basis';
                return `${product} is billed as a subscription charge ${freq} (${c.billingType || 'Advance'} billing).${arrSuffix}`;
            }
        }
    }

    // ─── Milestone helpers ──────────────────────────────────────────────────

    get milestonePlan() { return this.context?.milestonePlan; }

    get milestoneItems() {
        const items = this.milestonePlan?.items || [];
        return items.map(item => {
            const amt = item.milestoneAmount || 0;

            let statusClass = 'ctx-badge ctx-badge-default';
            let iconClass = 'ms-icon-pending';
            let statusIcon = 'utility:clock';
            let displayStatus = item.status || '';

            if (displayStatus === 'Waiting for Milestone Accomplishment') {
                displayStatus = 'Waiting';
                statusClass = 'ctx-badge ctx-badge-waiting';
                statusIcon = 'utility:clock';
                iconClass = 'ms-icon-waiting';
            } else if (displayStatus === 'Invoiced') {
                statusClass = 'ctx-badge ctx-badge-billed';
                statusIcon = 'utility:check';
                iconClass = 'ms-icon-invoiced';
            } else if (displayStatus === 'Ready for Invoicing') {
                statusClass = 'ctx-badge ctx-badge-ready';
                statusIcon = 'utility:check';
                iconClass = 'ms-icon-ready';
            } else if (displayStatus === 'Cancelled') {
                statusClass = 'ctx-badge ctx-badge-cancelled';
                statusIcon = 'utility:close';
                iconClass = 'ms-icon-cancelled';
            }

            const pctLabel = item.itemType === 'Percentage'
                ? `${item.percentage}%`
                : (item.itemType === 'Remainder' ? 'Remainder' : '--');

            return {
                ...item,
                formattedAmount: this._formatCurrency(amt),
                pctLabel,
                displayStatus,
                statusClass,
                statusIcon,
                iconClass,
                formattedDate: item.accomplishmentDate ? this._formatDate(item.accomplishmentDate) : '--'
            };
        });
    }

    get milestoneBilledPct() {
        const billed = this.contextData?.bsBilledAmount || 0;
        const pending = this.contextData?.bsPendingAmount || 0;
        const total = billed + pending;
        if (total <= 0) return '0';
        return Math.round((billed / total) * 100);
    }

    get milestoneProgressStyle() {
        return `width: ${this.milestoneBilledPct}%`;
    }

    get formattedRefAmount() {
        const billed = this.contextData?.bsBilledAmount || 0;
        const pending = this.contextData?.bsPendingAmount || 0;
        return this._formatCurrency(billed + pending);
    }

    get formattedBilledAmount() {
        return this._formatCurrency(this.contextData?.bsBilledAmount || 0);
    }

    get planStatusClass() {
        const s = this.milestonePlan?.planStatus;
        if (s === 'Active') return 'ctx-badge ctx-badge-active';
        if (s === 'Completed') return 'ctx-badge ctx-badge-billed';
        return 'ctx-badge ctx-badge-default';
    }

    // ─── Bundle helpers ─────────────────────────────────────────────────────

    get bundleData() { return this.context?.bundle; }

    get bundleComponents() {
        return (this.bundleData?.components || []).map(comp => {
            const depth = comp.depth || 1;
            let rowClass = 'tree-child';
            if (comp.isCurrent) rowClass += ' tree-current';
            if (comp.isSubBundle) rowClass += ' tree-sub-bundle';

            return {
                ...comp,
                rowClass,
                chargeTypeClass: this._chargeTypeBadgeClass(comp.chargeType),
                indentStyle: `padding-left: ${depth * 1.5}rem`
            };
        });
    }

    _chargeTypeBadgeClass(chargeType) {
        switch (chargeType) {
            case 'Evergreen':           return 'tree-charge-type tree-ct-evergreen';
            case 'Termed Subscription': return 'tree-charge-type tree-ct-termed';
            case 'One-Time':            return 'tree-charge-type tree-ct-onetime';
            case 'Usage':               return 'tree-charge-type tree-ct-usage';
            case 'Milestone':           return 'tree-charge-type tree-ct-milestone';
            default:                    return 'tree-charge-type';
        }
    }

    // ─── Usage helpers ──────────────────────────────────────────────────────

    get usageData() { return this.context?.usage; }

    get usageSiblings() {
        return (this.usageData?.siblings || []).map(s => {
            let rowClass = 'bt-row';
            if (s.isCurrent) rowClass += ' usage-current-row';
            return {
                ...s,
                rowClass,
                formattedBilledAmount: this._formatCurrency(s.billedAmount || 0)
            };
        });
    }

    get hasSiblings() {
        return this.usageSiblings.length > 0;
    }

    // ─── Billing Arrangement helpers ────────────────────────────────────────

    get hasArrangement() {
        return this.context?.arrangement?.lines?.length > 0;
    }

    get arrangementParts() {
        const lines = this.context?.arrangement?.lines || [];
        if (lines.length === 0) return [];
        const sorted = [...lines].sort((a, b) => (b.shouldBillRemainder ? 1 : 0) - (a.shouldBillRemainder ? 1 : 0) || (b.billingPercentage || 0) - (a.billingPercentage || 0));
        return sorted.map((l, idx) => {
            const remainder = l.shouldBillRemainder ? ' (including remainder)' : '';
            const separator = idx < sorted.length - 1 ? ', ' : '';
            return {
                key: l.lineId || String(idx),
                pct: `${l.billingPercentage}%${remainder}`,
                account: l.accountName,
                separator
            };
        });
    }

    get arrangementStatusClass() {
        const s = this.arrangement?.status;
        if (s === 'Active') return 'ctx-badge ctx-badge-active';
        return 'ctx-badge ctx-badge-default';
    }

    // ─── Navigation ─────────────────────────────────────────────────────────

    navigateToBsg(event) {
        const bsgId = event.currentTarget.dataset.id;
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: { recordId: bsgId, objectApiName: 'BillingScheduleGroup', actionName: 'view' }
        });
    }

    navigateToMilestonePlan() {
        if (this.milestonePlan?.planId) {
            this[NavigationMixin.Navigate]({
                type: 'standard__recordPage',
                attributes: { recordId: this.milestonePlan.planId, objectApiName: 'BillingMilestonePlan', actionName: 'view' }
            });
        }
    }

    // ─── Utilities ──────────────────────────────────────────────────────────

    _formatCurrency(amount) {
        if (amount === null || amount === undefined) return '$0.00';
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(amount);
    }

    _formatDate(dateString) {
        if (!dateString) return '--';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(date);
    }

    _humanize(value) {
        if (!value) return '';
        return value.replace(/([a-z])([A-Z])/g, '$1 $2')
                     .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2');
    }
}