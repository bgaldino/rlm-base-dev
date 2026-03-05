import { LightningElement, api } from 'lwc';
import getAmendmentRenewalSummary from '@salesforce/apex/RLM_AmendmentRenewalController.getAmendmentRenewalSummary';
import getExpansionAttritionDetails from '@salesforce/apex/RLM_AmendmentRenewalController.getExpansionAttritionDetails';

export default class RLMAmendmentRenewalSummary extends LightningElement {
    @api recordId;

    quote;
    expansionAttritionDetails = [];
    detailsLoaded = false;

    // -------------------------
    // Lifecycle
    // -------------------------
    connectedCallback() {
        this.loadQuote();
    }

    renderedCallback() {
        if (this.recordId && !this.detailsLoaded && this.hasQuote && this.isAmendmentOrRenewal) {
            this.detailsLoaded = true;
            this.loadExpansionAttritionDetails();
        }
    }

    // -------------------------
    // Quote Summary
    // -------------------------
    async loadQuote() {
        try {
            this.quote = await getAmendmentRenewalSummary({ quoteId: this.recordId });
        } catch (e) {
            console.error('Amendment/Renewal summary load failed', e);
            this.quote = null;
        }
    }

    get hasQuote() {
        return this.quote !== undefined && this.quote !== null;
    }

    get isAmendmentOrRenewal() {
        if (!this.quote || !this.quote.originalActionType) {
            return false;
        }
        const actionType = this.quote.originalActionType.trim();
        return actionType === 'Amendment' || actionType === 'Amend' || 
               actionType === 'Renewal' || actionType === 'Renew';
    }

    // -------------------------
    // Expansion/Attrition Details
    // -------------------------
    async loadExpansionAttritionDetails() {
        try {
            const data = await getExpansionAttritionDetails({ quoteId: this.recordId });

            if (!data || data.length === 0) {
                this.expansionAttritionDetails = [];
                return;
            }

            // Convert to renderable shape
            this.expansionAttritionDetails = data.map(item => ({
                key: item.assetId,
                assetId: item.assetId,
                assetName: item.assetName || 'Unknown Asset',
                previousAmount: this.formatCurrency(item.previousAmount),
                currentAmount: this.formatCurrency(item.currentAmount),
                changeAmount: this.formatCurrency(item.changeAmount),
                changeType: item.changeType,
                assetActionType: item.assetActionType || '',
                isExpansion: item.changeType === 'Expansion',
                isAttrition: item.changeType === 'Attrition'
            }));

        } catch (e) {
            console.error('Expansion/Attrition details load failed', e);
            this.expansionAttritionDetails = [];
        }
    }

    get hasExpansionAttritionDetails() {
        return this.expansionAttritionDetails.length > 0;
    }

    // -------------------------
    // Formatting
    // -------------------------
    get formattedSubtotal() {
        return this.formatCurrency(this.quote?.subtotal);
    }

    get formattedDiscount() {
        return this.formatCurrency(this.quote?.discount);
    }

    get formattedTotal() {
        return this.formatCurrency(this.quote?.total);
    }

    get formattedRenewalAmount() {
        return this.formatCurrency(this.quote?.renewalAmount);
    }

    get formattedExpansionAmount() {
        return this.formatCurrency(this.quote?.expansionAmount);
    }

    get formattedAttritionAmount() {
        return this.formatCurrency(this.quote?.attritionAmount);
    }

    get formattedNetNewAddsAmount() {
        return this.formatCurrency(this.quote?.netNewAddsAmount);
    }

    get formattedNetChange() {
        return this.formatCurrency(this.quote?.netChange);
    }

    get isNetExpansion() {
        return this.quote && this.quote.netChange > 0;
    }

    get isNetAttrition() {
        return this.quote && this.quote.netChange < 0;
    }

    get displayActionType() {
        if (!this.quote || !this.quote.originalActionType) {
            return '';
        }
        const actionType = this.quote.originalActionType.trim();
        // Normalize "Amend" to "Amendment" and "Renew" to "Renewal" for display
        if (actionType === 'Amend') {
            return 'Amendment';
        } else if (actionType === 'Renew') {
            return 'Renewal';
        }
        return actionType;
    }

    formatCurrency(value) {
        if (value === null || value === undefined) {
            return '$0.00';
        }
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(value);
    }
}