/**
 * rlmAssetRatesGrants.js
 *
 * Reusable Lightning Web Component that displays rate cards and usage entitlement
 * grants for a Revenue Cloud Asset. Can be placed standalone on Asset record pages
 * or embedded inside other components.
 *
 * Public API:
 *  - recordId: Asset Id (set automatically on record pages, or passed by parent)
 *  - usageResourceId: (optional) filter to show only a specific usage resource
 */
import { LightningElement, api, wire } from 'lwc';

import getRatesForAsset from '@salesforce/apex/RLM_UsageUploaderController.getRatesForAsset';
import getGrantsForAsset from '@salesforce/apex/RLM_UsageUploaderController.getGrantsForAsset';

const DISPLAY_CONSTANTS = {
    TIER_BASED_RATE: 'Tier-based',
    HIGH_USAGE_THRESHOLD: 80,
    CRITICAL_USAGE_THRESHOLD: 95
};

export default class RlmAssetRatesGrants extends LightningElement {
    @api recordId;
    @api usageResourceId;

    // Internal state
    rateEntries = [];
    grantEntries = [];
    ratesLoaded = false;
    grantsLoaded = false;

    // ─── Wire Adapters ────────────────────────────────────────────────

    @wire(getRatesForAsset, { assetId: '$recordId' })
    wiredRates({ data, error }) {
        if (data) {
            this.rateEntries = data;
            this.ratesLoaded = true;
        } else if (error) {
            this.rateEntries = [];
            this.ratesLoaded = true;
        }
    }

    @wire(getGrantsForAsset, { assetId: '$recordId' })
    wiredGrants({ data, error }) {
        if (data) {
            this.grantEntries = data;
            this.grantsLoaded = true;
        } else if (error) {
            this.grantEntries = [];
            this.grantsLoaded = true;
        }
    }

    // ─── Computed Properties ──────────────────────────────────────────

    get isLoading() {
        return !this.ratesLoaded || !this.grantsLoaded;
    }

    get hasRates() {
        return this.filteredRates.length > 0;
    }

    get hasGrants() {
        return this.filteredGrants.length > 0;
    }

    get hasData() {
        return this.hasRates || this.hasGrants;
    }

    get noData() {
        return !this.isLoading && !this.hasData;
    }

    /**
     * Rate entries filtered by optional usageResourceId.
     */
    get filteredRates() {
        if (this.usageResourceId) {
            return this.rateEntries.filter(r =>
                r.usageResourceId === this.usageResourceId ||
                r.usageResourceId === null ||
                r.usageResourceId === undefined
            );
        }
        return this.rateEntries;
    }

    /**
     * Grant entries filtered by optional usageResourceId.
     */
    get filteredGrants() {
        if (this.usageResourceId) {
            return this.grantEntries.filter(g => g.usageResourceId === this.usageResourceId);
        }
        return this.grantEntries;
    }

    /**
     * Rates grouped by usage resource for display.
     */
    get ratesByResource() {
        const rates = this.filteredRates;
        if (!rates.length) return [];

        const grouped = {};
        rates.forEach((rate, rateIdx) => {
            const isGlobalRate = rate.usageResourceId === null || rate.usageResourceId === undefined;
            const key = rate.usageResourceId || (this.usageResourceId ? `global-for-${this.usageResourceId}` : `unknown-resource-${rateIdx}`);
            if (!grouped[key]) {
                grouped[key] = {
                    resourceName: rate.usageResourceName || (isGlobalRate ? 'All usage resources' : 'Unknown Resource'),
                    resourceId: key,
                    cards: []
                };
            }
            const cardId = rate.rateCardEntryId || `${key}-${rate.rateCardName || 'rate-card'}-${rateIdx}`;
            const card = {
                id: cardId,
                name: rate.rateCardName || 'Rate Card',
                baseRate: rate.baseRate,
                negotiatedRate: rate.negotiatedRate,
                uom: rate.rateUomName || '',
                hasTiers: rate.tiers && rate.tiers.length > 0,
                tiers: (rate.tiers || []).map((t, idx) => ({
                    id: `tier-${cardId}-${idx}`,
                    range: this._formatTierRange(t.lowerBound, t.upperBound),
                    type: t.adjustmentType,
                    value: this._formatTierValue(t.adjustmentType, t.adjustmentValue, t.rateUomName)
                })),
                displayRate: this._formatRate(rate)
            };
            grouped[key].cards.push(card);
        });

        return Object.values(grouped);
    }

    /**
     * Grants grouped by usage resource for display.
     */
    get grantsByResource() {
        const grants = this.filteredGrants;
        if (!grants.length) return [];

        const grouped = {};
        grants.forEach((grant, grantIdx) => {
            const key = grant.usageResourceId || `unknown-grant-resource-${grantIdx}`;
            if (!grouped[key]) {
                grouped[key] = {
                    resourceName: grant.usageResourceName || 'Unknown Resource',
                    resourceId: key,
                    grants: []
                };
            }
            const remaining = grant.bucketBalance != null ? grant.bucketBalance : grant.entitlementQuantity;
            const consumed = grant.totalConsumedEntitlement || 0;
            const total = grant.entitlementQuantity || 0;
            const pct = total > 0 ? Math.round((consumed / total) * 100) : 0;

            grouped[key].grants.push({
                id: grant.entitlementId || `${key}-grant-${grantIdx}`,
                name: grant.entitlementName,
                modelType: this._formatModelType(grant.usageModelType),
                grantType: grant.grantType || 'Grant',
                overage: grant.chargeForOverage || 'N/A',
                overageLabel: `Overage: ${grant.chargeForOverage || 'N/A'}`,
                total: total,
                consumed: consumed,
                remaining: remaining,
                percentUsed: pct,
                isHighUsage: pct >= DISPLAY_CONSTANTS.HIGH_USAGE_THRESHOLD,
                isCriticalUsage: pct >= DISPLAY_CONSTANTS.CRITICAL_USAGE_THRESHOLD
            });
        });

        return Object.values(grouped);
    }

    // ─── Formatting Helpers ───────────────────────────────────────────

    _formatRate(rate) {
        if (rate.negotiatedRate != null) {
            return `${rate.negotiatedRate} ${rate.rateUomName || ''}`.trim();
        }
        if (rate.baseRate != null) {
            return `${rate.baseRate} ${rate.rateUomName || ''}`.trim();
        }
        return DISPLAY_CONSTANTS.TIER_BASED_RATE;
    }

    _formatTierRange(lower, upper) {
        const hasLower = lower !== null && lower !== undefined;
        const hasUpper = upper !== null && upper !== undefined;

        if (!hasLower && !hasUpper) {
            return 'All usage';
        }

        if (hasLower && !hasUpper) {
            return `${this._formatNumber(lower)}+`;
        }

        if (!hasLower && hasUpper) {
            return `Up to ${this._formatNumber(upper)}`;
        }

        if (upper >= 999999999) {
            return `${this._formatNumber(lower)}+`;
        }
        return `${this._formatNumber(lower)} – ${this._formatNumber(upper)}`;
    }

    _formatTierValue(type, value, uom) {
        if (type === 'Override') {
            return `${value} ${uom || ''}`.trim();
        }
        if (type === 'Percentage') {
            return `${value}%`;
        }
        return `${value}`;
    }

    _formatModelType(type) {
        if (!type) return 'N/A';
        // Convert camelCase/PascalCase to friendly labels
        const map = {
            'Anchor': 'Anchor',
            'CommitmentQuantity': 'Qty Commit',
            'Commit': 'Commit',
            'Pack': 'Pack'
        };
        return map[type] || type;
    }

    _formatNumber(num) {
        if (num === null || num === undefined || Number.isNaN(num)) {
            return '';
        }
        if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
        return String(num);
    }
}