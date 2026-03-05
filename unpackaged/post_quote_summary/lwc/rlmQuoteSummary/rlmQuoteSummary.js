import { LightningElement, api } from 'lwc';
import getQuoteSummary from '@salesforce/apex/RLM_QuoteSummaryController.getQuoteSummary';
import getSegmentSummaries from '@salesforce/apex/RLM_QuoteSummaryController.getSegmentSummaries';

export default class RLMQuoteSummary extends LightningElement {
    @api recordId;

    quote;
    segments = [];
    segmentsLoaded = false;

    // -------------------------
    // Lifecycle
    // -------------------------
    connectedCallback() {
        this.loadQuote();
    }

    renderedCallback() {
        if (this.recordId && !this.segmentsLoaded) {
            this.segmentsLoaded = true;
            this.loadSegments();
        }
    }

    // -------------------------
    // Quote Summary
    // -------------------------
    async loadQuote() {
        try {
            this.quote = await getQuoteSummary({ quoteId: this.recordId });
        } catch (e) {
            console.error('Quote summary load failed', e);
            this.quote = null;
        }
    }

    get hasQuote() {
        return this.quote !== undefined && this.quote !== null;
    }

    // -------------------------
    // Segment Summary
    // -------------------------
    async loadSegments() {
        try {
            const data = await getSegmentSummaries({ quoteId: this.recordId });

            if (!data || data.length === 0) {
                this.segments = [];
                return;
            }

            // Group by Segment Label
            const grouped = {};

            data.forEach(row => {
                const key = row.segmentLabel;

                if (!grouped[key]) {
                    grouped[key] = {
                        segmentLabel: row.segmentLabel,
                        subtotal: 0,
                        discount: 0,
                        total: 0
                    };
                }

                grouped[key].subtotal += row.subtotal || 0;
                grouped[key].discount += row.discount || 0;
                grouped[key].total += row.total || 0;
            });

            // Build array
            const groupedArray = Object.values(grouped);

            // ---- Sort to match TLE label ordering: Base Name, then Year #
            // "New Group 1" => Year 1
            // "New Group 1 - Year 2" => Year 2
            groupedArray.sort((a, b) => {
                const pa = this.parseSegmentLabel(a.segmentLabel);
                const pb = this.parseSegmentLabel(b.segmentLabel);

                const baseCompare = (pa.base || '').localeCompare(pb.base || '');
                if (baseCompare !== 0) return baseCompare;

                return (pa.year || 1) - (pb.year || 1);
            });

            // Convert to renderable shape
            this.segments = groupedArray.map(seg => ({
                key: seg.segmentLabel,
                segmentLabel: seg.segmentLabel,
                subtotal: this.formatCurrency(seg.subtotal),
                discount: this.formatCurrency(seg.discount),
                total: this.formatCurrency(seg.total)
            }));

        } catch (e) {
            console.error('Segment load failed', e);
            this.segments = [];
        }
    }

    // Extract base + year from labels like: "New Group 1 - Year 2"
    // If no "Year X" suffix, treat as Year 1.
    parseSegmentLabel(label) {
        if (!label) return { base: '', year: 1 };

        const m = label.match(/^(.*?)(?:\s*-\s*Year\s*(\d+))\s*$/i);
        if (m) {
            return {
                base: (m[1] || '').trim(),
                year: parseInt(m[2], 10) || 1
            };
        }

        return { base: label.trim(), year: 1 };
    }

    get hasSegments() {
        return this.segments.length > 0;
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