import { LightningElement, api, wire, track } from 'lwc';
import getInvoiceProductSummary from '@salesforce/apex/RLM_InvoiceProductSummaryController.getInvoiceProductSummary';
import saveLineAttributes       from '@salesforce/apex/RLM_InvoiceProductSummaryController.saveLineAttributes';

const CHARGE_TYPE_PILL_MAP = {
    'Monthly'              : 'pill pill-monthly',
    'Monthly Subscription' : 'pill pill-monthly',
    'Annual'               : 'pill pill-annual',
    'Annual Subscription'  : 'pill pill-annual',
    'One-Time'             : 'pill pill-onetime',
    'One time'             : 'pill pill-onetime',
    'Onetime'              : 'pill pill-onetime',
    'OneTime'              : 'pill pill-onetime',
};

export default class RlmInvoiceProductSummary extends LightningElement {
    @api recordId;

    @track _summaryResult    = null;
    @track _expandedMap      = {};   // product row open/close
    @track _attrExpandedMap  = {};   // attribute section open/close per product
    @track _bundleExpandedMap = {};  // sub-bundle parent row open/close
    @track isLoading         = true;
    @track errorMessage      = null;

    // ─── Lifecycle ────────────────────────────────────────────────────────────

    connectedCallback() {
        if (this.recordId) {
            saveLineAttributes({ invoiceId: this.recordId })
                .then(() => console.log('Line attributes saved.'))
                .catch(err => console.warn('saveLineAttributes (non-blocking):', err));
        }
    }

    // ─── Wire ─────────────────────────────────────────────────────────────────

    @wire(getInvoiceProductSummary, { invoiceId: '$recordId' })
    wiredSummary({ data, error }) {
        this.isLoading = false;
        if (data) {
            this._summaryResult   = data;
            this.errorMessage     = null;
            this._expandedMap      = {};
            this._attrExpandedMap  = {};
            this._bundleExpandedMap = {};
        } else if (error) {
            this.errorMessage   = error.body ? error.body.message : 'Unknown error occurred.';
            this._summaryResult = null;
        }
    }

    // ─── State ────────────────────────────────────────────────────────────────

    get hasError() { return !!this.errorMessage; }

    get hasData() {
        return !this.isLoading && !this.hasError &&
               this._summaryResult?.products?.length > 0;
    }

    get isEmpty() {
        return !this.isLoading && !this.hasError &&
               (!this._summaryResult?.products?.length);
    }

    // ─── Header / footer ──────────────────────────────────────────────────────

    get headerSubtitle() {
        if (!this._summaryResult) return '';
        const p = this._summaryResult.products?.length ?? 0;
        const l = this._summaryResult.totalLines ?? 0;
        return `${p} product${p !== 1 ? 's' : ''} · ${l} line${l !== 1 ? 's' : ''}`;
    }

    get footerMeta() {
        if (!this._summaryResult) return '';
        return `${this._summaryResult.products?.length ?? 0} Products · ${this._summaryResult.totalLines ?? 0} Lines`;
    }

    get totalLines()             { return this._summaryResult?.totalLines    ?? 0; }
    get formattedGrandSubtotal() { return this.fmt(this._summaryResult?.grandSubtotal); }
    get formattedGrandTax()      { return this.fmt(this._summaryResult?.grandTax); }
    get formattedGrandTotal()    { return this.fmt(this._summaryResult?.grandTotal); }

    // ─── Product rows ─────────────────────────────────────────────────────────

    get productRows() {
        if (!this._summaryResult?.products) return [];

        return this._summaryResult.products.map(p => {
            const isExpanded  = !!this._expandedMap[p.productId];
            const attrExp     = !!this._attrExpandedMap[p.productId];
            const isNegSub    = p.subtotal     < 0;
            const isNegTax    = p.taxAmount    < 0;
            const isNegTotal  = p.totalWithTax < 0;
            const isZeroTotal = p.totalWithTax === 0;

            const assetBlocks = (p.assetBlocks ?? []).map(block => ({
                assetId    : block.assetId,
                assetName  : block.assetName ?? 'Asset',
                attributes : (block.attributes ?? []).map(a => ({
                    label        : a.label ?? '—',
                    displayValue : (a.value != null && a.value !== '') ? a.value : '—',
                })),
            }));

            return {
                productId         : p.productId,
                productName       : p.productName,
                chargeType        : p.chargeType ?? null,
                lineCount         : p.lineCount,
                lineCountLabel    : `${p.lineCount} line item${p.lineCount !== 1 ? 's' : ''}`,
                isExpanded,
                chevronIcon       : isExpanded ? 'utility:chevrondown' : 'utility:chevronright',
                attrExpanded      : attrExp,
                attrChevronIcon   : attrExp ? 'utility:chevrondown' : 'utility:chevronright',
                pillClass         : this.pillClass(p.chargeType),
                rowClass          : 'product-row',
                // isBundle: product has a single suppressed parent (it IS the bundle)
                isBundle          : !!(p.lines?.length === 1 && p.lines[0]?.isSuppressedParent),
                hasAssetBlocks    : assetBlocks.length > 0,
                assetBlocks,
                subtotalClass     : `col-amount cell-right${isNegSub ? ' amount-negative' : ' amount-positive'}`,
                taxClass          : `col-amount cell-right${isNegTax ? ' amount-negative' : ' amount-positive'}`,
                totalClass        : `col-amount cell-right${isZeroTotal ? ' amount-zero' : isNegTotal ? ' amount-negative' : ' amount-positive'}`,
                formattedSubtotal : this.fmt(p.subtotal),
                formattedTax      : this.fmt(p.taxAmount),
                formattedTotal    : this.fmt(p.totalWithTax),
                lines             : this.buildLineDetails(p.lines),
            };
        });
    }

    buildLineDetails(lines) {
        if (!lines) return [];
        const result = [];
        for (const l of lines) {
            if (l.isSuppressedParent) {
                // Product IS the bundle — skip parent row, promote children to top level
                for (const child of (l.components ?? [])) {
                    result.push(this.buildOneLine(child, 0));
                }
            } else {
                result.push(this.buildOneLine(l, 0));
            }
        }
        return result;
    }

    // depth: 0 = top-level line, 1 = first-level component, 2+ = nested bundle component
    buildOneLine(l, depth) {
        const isNegCharge = l.chargeAmount < 0;
        const isNegTax    = l.taxAmount    < 0;
        const isNegTotal  = l.totalWithTax < 0;
        const isZeroTotal = l.totalWithTax === 0;
        const isComp      = depth > 0;

        // Usage overage label
        let usageLabel = null;
        if (l.isUsage && l.overageQty != null) {
            const qty    = l.overageQty;
            const uom    = l.unitOfMeasure ?? '';
            const symbol = this.currencySymbol(l.currencyCode);
            let ratePart = '';
            if (l.rate != null) {
                const rateStr = Number(l.rate) % 1 === 0
                    ? Number(l.rate).toFixed(0)
                    : Number(l.rate).toFixed(2).replace(/0+$/, '').replace(/\.$/, '');
                ratePart = ` @ ${symbol}${rateStr}/${uom}`;
            }
            usageLabel = `Overage: ${qty} ${uom}${ratePart}`.trim();
        }

        // Recursively build children at depth+1
        const components = (l.components ?? []).map(c => this.buildOneLine(c, depth + 1));

        // Indent glyph: deeper nesting gets more indentation via CSS class
        const indentClass = isComp ? `component-depth-${Math.min(depth, 4)}` : '';

        const bundleExp = l.isParent ? !!this._bundleExpandedMap[l.lineId] : false;
        return {
            lineId          : l.lineId,
            name            : l.name ?? '—',
            nameClass       : l.isParent && !isComp ? 'sub-line-name parent-name'
                            : isComp               ? 'sub-line-name component-name'
                            :                        'sub-line-name',
            description     : (l.description?.trim()) ? l.description.trim() : null,
            dateRange       : this.formatDateRange(l.periodStartDate, l.periodEndDate),
            isParent        : !!l.isParent,
            isComp,
            depth,
            indentClass,
            hasComponents   : components.length > 0,
            bundleExpanded  : bundleExp,
            bundleChevron   : bundleExp ? 'utility:chevrondown' : 'utility:chevronright',
            components,
            usageLabel,
            lineRowClass    : [
                'sub-line',
                l.isParent ? 'parent-line' : '',
                isComp ? 'component-line' : '',
                indentClass
            ].filter(Boolean).join(' '),
            chargeClass     : `col-amount cell-right sub-cell${isNegCharge ? ' amount-negative' : ''}`,
            taxClass        : `col-amount cell-right sub-cell${isNegTax    ? ' amount-negative' : ''}`,
            totalClass      : `col-amount cell-right sub-cell${isZeroTotal ? ' amount-zero' : isNegTotal ? ' amount-negative' : ''}`,
            formattedCharge : this.fmt(l.chargeAmount, l.currencyCode),
            formattedTax    : this.fmt(l.taxAmount,    l.currencyCode),
            formattedTotal  : this.fmt(l.totalWithTax, l.currencyCode),
        };
    }

    // ─── Handlers ─────────────────────────────────────────────────────────────

    handleToggle(event)       { this.toggleRow(event.currentTarget.dataset.id); }
    handleChevronClick(event) { event.stopPropagation(); this.toggleRow(event.currentTarget.dataset.id); }
    handleKeydown(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            this.toggleRow(event.currentTarget.dataset.keyid);
        }
    }
    toggleRow(id) {
        this._expandedMap = { ...this._expandedMap, [id]: !this._expandedMap[id] };
    }

    handleAttrToggle(event) {
        event.stopPropagation();
        const id = event.currentTarget.dataset.id;
        this._attrExpandedMap = { ...this._attrExpandedMap, [id]: !this._attrExpandedMap[id] };
    }

    handleBundleToggle(event) {
        event.stopPropagation();
        const id = event.currentTarget.dataset.id;
        this._bundleExpandedMap = { ...this._bundleExpandedMap, [id]: !this._bundleExpandedMap[id] };
    }

    // ─── Helpers ──────────────────────────────────────────────────────────────

    pillClass(chargeType) {
        return CHARGE_TYPE_PILL_MAP[chargeType] ?? 'pill pill-default';
    }

    fmt(value, currencyOverride) {
        if (value == null) return '$0.00';
        const currency = currencyOverride
            ?? this._summaryResult?.currencyCode
            ?? 'USD';
        return new Intl.NumberFormat('en-US', {
            style: 'currency', currency,
            minimumFractionDigits: 2, maximumFractionDigits: 2,
        }).format(value);
    }

    currencySymbol(code) {
        try {
            const parts = new Intl.NumberFormat('en-US', {
                style: 'currency', currency: code ?? 'USD'
            }).formatToParts(0);
            return parts.find(p => p.type === 'currency')?.value ?? '$';
        } catch (e) { return '$'; }
    }

    formatDateRange(startDate, endDate) {
        if (!startDate && !endDate) return null;
        const f = d => d ? new Date(d).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric'
        }) : '?';
        if (startDate && endDate) return `${f(startDate)} → ${f(endDate)}`;
        return startDate ? `From ${f(startDate)}` : `Until ${f(endDate)}`;
    }
}