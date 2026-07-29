import { LightningElement, api, wire, track } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import { subscribe, unsubscribe } from 'lightning/empApi';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import getQuoteLines from '@salesforce/apex/RLM_HomeServices_MobileQuoteEditorCtrl.getQuoteLines';
import applyLineEdit from '@salesforce/apex/RLM_HomeServices_MobileQuoteEditorCtrl.applyLineEdit';
import removeLine from '@salesforce/apex/RLM_HomeServices_MobileQuoteEditorCtrl.removeLine';
import getConfigurableAddOns from '@salesforce/apex/RLM_HomeServices_MobileQuoteEditorCtrl.getConfigurableAddOns';
import setAddOn from '@salesforce/apex/RLM_HomeServices_MobileQuoteEditorCtrl.setAddOn';

const DISCOUNT_PERCENT = 'percent';
const DISCOUNT_AMOUNT = 'amount';

// Platform event published by RLM_HomeServices_QuoteLineItemQuoteRefresh whenever
// a QuoteLineItem changes. Subscribing lets the editor auto-refresh when pricing
// is recalculated (including changes made outside this component), matching the
// service proposal LWC behavior.
const QUOTE_REFRESH_EVENT = '/event/RLM_HomeServices_QuoteDataRefresh__e';
const REFRESH_DEBOUNCE_MS = 350;

export default class RlmHomeServicesMobileQuoteEditor extends LightningElement {
    @api recordId;
    @api quoteId;

    // Design attributes (set in App Builder).
    @api headerTitle = 'Quoted Services';
    // Retained (currently unused) App Builder attributes. Salesforce blocks removing
    // design attributes from a component that's live on a Lightning page.
    @api configFlowApiName;
    @api configOrigin;

    @track data = null;
    @track error = null;
    isSaving = false;

    // Edit sheet state.
    showEditSheet = false;
    editLine = null;
    editQuantity = null;
    editDiscountMode = DISCOUNT_PERCENT;
    editDiscountValue = null;
    editStartDate = null;
    editEndDate = null;

    // Add-ons sheet state.
    showAddOnSheet = false;
    addOnBundleLineId = null;
    addOnBundleName = '';
    addOnLoading = false;
    @track addOns = [];

    wiredResult;
    _empSubscription;
    _refreshDebounceTimer;

    get effectiveQuoteId() {
        return this.recordId || this.quoteId || null;
    }

    connectedCallback() {
        subscribe(QUOTE_REFRESH_EVENT, -1, (message) => {
            const quoteId = message?.data?.payload?.RLM_HomeServices_QuoteId__c;
            if (quoteId && quoteId === this.effectiveQuoteId) {
                this.scheduleRefresh();
            }
        }).then((subscription) => {
            this._empSubscription = subscription;
        });
    }

    disconnectedCallback() {
        clearTimeout(this._refreshDebounceTimer);
        this._refreshDebounceTimer = null;
        if (this._empSubscription) {
            unsubscribe(this._empSubscription);
            this._empSubscription = null;
        }
    }

    scheduleRefresh() {
        clearTimeout(this._refreshDebounceTimer);
        this._refreshDebounceTimer = setTimeout(() => {
            this._refreshDebounceTimer = null;
            this.refresh();
        }, REFRESH_DEBOUNCE_MS);
    }

    @wire(getQuoteLines, { quoteId: '$effectiveQuoteId' })
    wiredLines(result) {
        this.wiredResult = result;
        const { data, error } = result;
        if (error) {
            this.error = this.reduceError(error);
            this.data = null;
        } else if (data) {
            this.error = null;
            this.data = data;
        } else {
            this.data = null;
            this.error = this.effectiveQuoteId
                ? null
                : 'No quote selected. Add this component to a Quote record page.';
        }
    }

    get hasData() {
        return this.data != null;
    }

    get isReadOnly() {
        return this.data != null && this.data.editable === false;
    }

    get isEmpty() {
        return this.hasData && (!this.data.lines || this.data.lines.length === 0);
    }

    get displayLines() {
        const lines = this.data?.lines ?? [];
        return lines.map((line) => this.decorateLine(line, false));
    }

    decorateLine(line, isChild) {
        const discountPercent = Number(line.discountPercent ?? 0);
        const discountAmount = Number(line.discountAmount ?? 0);
        let discountLabel = null;
        if (discountPercent > 0) {
            discountLabel = `${this.formatNumber(discountPercent)}% off`;
        } else if (discountAmount > 0) {
            discountLabel = `${this.formatCurrency(discountAmount)} off`;
        }
        return {
            ...line,
            isChild,
            cardClass: isChild ? 'line-card line-card_child' : 'line-card',
            formattedListPrice: this.formatCurrency(line.grossTotalPrice ?? line.listPrice),
            formattedNetTotal: this.formatCurrency(line.netTotalPrice),
            formattedQuantity: this.formatNumber(line.quantity),
            hasDiscount: discountLabel != null,
            discountLabel,
            hasDates: !!line.startDate || !!line.endDate,
            dateRange: this.formatDateRange(line.startDate, line.endDate),
            children: (line.children ?? []).map((child) => this.decorateLine(child, true))
        };
    }

    get formattedServicesTotal() {
        return this.formatCurrency(this.data?.servicesTotal ?? 0);
    }

    get formattedDiscountsTotal() {
        return this.formatCurrency(this.data?.discountsTotal ?? 0, true);
    }

    get formattedTax() {
        return this.formatCurrency(this.data?.tax ?? 0);
    }

    get formattedGrandTotal() {
        return this.formatCurrency(this.data?.grandTotal ?? 0);
    }

    get hasDiscountsTotal() {
        return (this.data?.discountsTotal ?? 0) > 0;
    }

    get hasTax() {
        return (this.data?.tax ?? 0) > 0;
    }

    // ── Edit sheet ───────────────────────────────────────────────────────────

    handleEditLine(event) {
        const lineId = event.currentTarget.dataset.id;
        const line = this.findLine(lineId);
        if (!line) return;
        this.editLine = line;
        this.editQuantity = line.quantity;
        this.editStartDate = line.startDate;
        this.editEndDate = line.endDate;
        if (Number(line.discountAmount ?? 0) > 0) {
            this.editDiscountMode = DISCOUNT_AMOUNT;
            this.editDiscountValue = line.discountAmount;
        } else {
            this.editDiscountMode = DISCOUNT_PERCENT;
            this.editDiscountValue = line.discountPercent;
        }
        this.showEditSheet = true;
    }

    closeEditSheet() {
        this.showEditSheet = false;
        this.editLine = null;
    }

    get discountModeOptions() {
        return [
            { label: 'Percent (%)', value: DISCOUNT_PERCENT },
            { label: 'Amount ($)', value: DISCOUNT_AMOUNT }
        ];
    }

    get isPercentMode() {
        return this.editDiscountMode === DISCOUNT_PERCENT;
    }

    get discountStep() {
        return this.isPercentMode ? '0.01' : '0.01';
    }

    get discountFormatter() {
        return this.isPercentMode ? undefined : 'currency';
    }

    handleQuantityChange(event) {
        this.editQuantity = event.detail.value;
    }

    handleDiscountModeChange(event) {
        this.editDiscountMode = event.detail.value;
    }

    handleDiscountValueChange(event) {
        this.editDiscountValue = event.detail.value;
    }

    handleStartDateChange(event) {
        this.editStartDate = event.detail.value;
    }

    handleEndDateChange(event) {
        this.editEndDate = event.detail.value;
    }

    async handleSaveEdit() {
        if (!this.editLine) return;
        this.isSaving = true;
        try {
            const qty = this.editQuantity != null && this.editQuantity !== ''
                ? Number(this.editQuantity)
                : null;
            const discountValue = this.editDiscountValue != null && this.editDiscountValue !== ''
                ? Number(this.editDiscountValue)
                : null;
            await applyLineEdit({
                lineId: this.editLine.id,
                quantity: qty,
                discountValue,
                discountMode: discountValue != null ? this.editDiscountMode : null,
                startDate: this.editStartDate || null,
                endDate: this.editEndDate || null
            });
            this.showToast('Updated', 'Line updated and repriced.', 'success');
            this.closeEditSheet();
            await this.refresh();
        } catch (e) {
            this.showToast('Could not save', this.reduceError(e), 'error');
        } finally {
            this.isSaving = false;
        }
    }

    async handleRemoveLine() {
        if (!this.editLine) return;
        this.isSaving = true;
        try {
            await removeLine({ lineId: this.editLine.id });
            this.showToast('Removed', 'Service removed from the quote.', 'success');
            this.closeEditSheet();
            await this.refresh();
        } catch (e) {
            this.showToast('Could not remove', this.reduceError(e), 'error');
        } finally {
            this.isSaving = false;
        }
    }

    // ── Native configurator launch ────────────────────────────────────────────

    handleReconfigure(event) {
        const { id, name } = event.currentTarget.dataset;
        this.openAddOnSheet(id, name);
    }

    async openAddOnSheet(bundleLineId, bundleName) {
        this.addOnBundleLineId = bundleLineId;
        this.addOnBundleName = bundleName || '';
        this.addOns = [];
        this.showAddOnSheet = true;
        this.addOnLoading = true;
        try {
            const rows = await getConfigurableAddOns({ bundleLineId });
            this.addOns = (rows ?? []).map((r) => this.decorateAddOn(r));
        } catch (error) {
            this.showToast('Could not load add-ons', this.reduceError(error), 'error');
        } finally {
            this.addOnLoading = false;
        }
    }

    decorateAddOn(row) {
        return {
            ...row,
            saving: false,
            disabled: !row.available,
            formattedPrice: row.unitPrice != null ? `${this.formatCurrency(row.unitPrice)}/mo` : ''
        };
    }

    async handleAddOnToggle(event) {
        const productId = event.currentTarget.dataset.id;
        const selected = event.target.checked;
        this.setAddOnRow(productId, { saving: true });
        try {
            const result = await setAddOn({
                bundleLineId: this.addOnBundleLineId,
                componentProductId: productId,
                selected
            });
            if (result) {
                this.data = result;
            }
            this.setAddOnRow(productId, { saving: false, selected });
        } catch (error) {
            // Revert the toggle on failure.
            this.setAddOnRow(productId, { saving: false });
            this.showToast('Could not update add-on', this.reduceError(error), 'error');
        }
    }

    setAddOnRow(productId, patch) {
        this.addOns = this.addOns.map((a) =>
            a.productId === productId ? { ...a, ...patch } : a
        );
    }

    closeAddOnSheet() {
        this.showAddOnSheet = false;
        this.addOnBundleLineId = null;
        this.addOns = [];
        this.refresh();
    }

    get hasAddOns() {
        return this.addOns && this.addOns.length > 0;
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    async refresh() {
        if (this.wiredResult) {
            await refreshApex(this.wiredResult);
        }
    }

    findLine(lineId) {
        const lines = this.data?.lines ?? [];
        for (const line of lines) {
            if (line.id === lineId) return line;
            for (const child of line.children ?? []) {
                if (child.id === lineId) return child;
            }
        }
        return null;
    }

    formatCurrency(value, negative = false) {
        if (value == null) return negative ? '-$0.00' : '$0.00';
        const num = Number(value);
        const formatted = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(Math.abs(num));
        return negative && num > 0 ? `-${formatted}` : formatted;
    }

    formatNumber(value) {
        if (value == null) return '0';
        return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(Number(value));
    }

    formatDateRange(start, end) {
        if (!start && !end) return '';
        const fmt = (d) => (d ? new Date(d).toLocaleDateString('en-US') : '');
        if (start && end) return `${fmt(start)} – ${fmt(end)}`;
        return fmt(start || end);
    }

    showToast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }

    reduceError(error) {
        if (!error) return 'Unknown error';
        if (Array.isArray(error.body)) {
            return error.body.map((e) => e.message).join(', ');
        }
        return error.body?.message || error.message || 'Unexpected error';
    }
}