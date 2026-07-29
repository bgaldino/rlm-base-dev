import { LightningElement, api, wire, track } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import { subscribe, unsubscribe } from 'lightning/empApi';
import getQuoteData from '@salesforce/apex/RLM_HomeServices_ServiceProposalCtrl.getQuoteData';
import backgroundImage from '@salesforce/resourceUrl/RLM_HomeServices_ServicesProposalBackground';

const IPAD_WIDTH = 768;
const IPAD_HEIGHT = 1024;
const QUOTE_REFRESH_EVENT = '/event/RLM_HomeServices_QuoteDataRefresh__e';
const REFRESH_DEBOUNCE_MS = 350;

export default class Rlm_serviceProposal extends LightningElement {
    @api recordId;
    @api quoteId;

    @track proposalData = null;
    @track error = null;

    wiredQuoteResult;
    _empSubscription;
    _refreshDebounceTimer;
    _empErrorHandler;

    get effectiveQuoteId() {
        return this.recordId || this.quoteId || null;
    }

    get containerStyle() {
        return `background-image: url(${backgroundImage}); background-size: cover; background-position: center;`;
    }

    @wire(getQuoteData, { quoteId: '$effectiveQuoteId' })
    wiredQuote(result) {
        this.wiredQuoteResult = result;
        const { error, data } = result;
        if (error) {
            this.error = error.body?.message || error.message || 'Failed to load quote data.';
            this.proposalData = null;
        } else if (data) {
            this.error = null;
            this.proposalData = data;
        } else {
            this.proposalData = null;
            this.error = this.effectiveQuoteId ? null : 'No quote selected. Add this component to a Quote record page or provide a quote ID.';
        }
    }

    get hasData() {
        return this.proposalData != null;
    }

    get clientName() {
        return this.proposalData?.clientName ?? '';
    }

    get billingStreet() {
        return this.proposalData?.billingStreet ?? '';
    }

    get lineItems() {
        const items = this.proposalData?.lineItems ?? [];
        return items.map((item, idx) => ({
            ...item,
            key: `qli-${idx}`,
            formattedListPrice: this.formatCurrency(item.listPrice),
            formattedPromotion: this.formatCurrency(item.promotion, true),
            formattedCustomerDiscount: this.formatCurrency(item.customerDiscount, true),
            formattedFinalPrice: this.formatCurrency(item.finalPrice),
            hasPromotion: (item.promotion ?? 0) > 0,
            hasCustomerDiscount: (item.customerDiscount ?? 0) > 0
        }));
    }

    get formattedServicesTotal() {
        return this.formatCurrency(this.proposalData?.servicesTotal ?? 0);
    }

    get formattedPromotionsTotal() {
        return this.formatCurrency(this.proposalData?.promotionsTotal ?? 0, true);
    }

    get formattedDiscountsTotal() {
        return this.formatCurrency(this.proposalData?.discountsTotal ?? 0, true);
    }

    get formattedTax() {
        return this.formatCurrency(this.proposalData?.tax ?? 0);
    }

    get formattedGrandTotal() {
        return this.formatCurrency(this.proposalData?.grandTotal ?? 0);
    }

    get formattedMonthlyBilling() {
        const total = Number(this.proposalData?.grandTotal ?? 0);
        return this.formatCurrency(total / 12);
    }

    get formattedQuarterlyBilling() {
        const total = Number(this.proposalData?.grandTotal ?? 0);
        return this.formatCurrency(total / 4);
    }

    get formattedAnnualBilling() {
        const total = Number(this.proposalData?.grandTotal ?? 0);
        return this.formatCurrency(total);
    }

    get hasPromotionsTotal() {
        return (this.proposalData?.promotionsTotal ?? 0) > 0;
    }

    get hasDiscountsTotal() {
        return (this.proposalData?.discountsTotal ?? 0) > 0;
    }

    get hasTax() {
        return (this.proposalData?.tax ?? 0) > 0;
    }

    connectedCallback() {
        subscribe(QUOTE_REFRESH_EVENT, -1, (message) => {
            const quoteId = message?.data?.payload?.RLM_HomeServices_QuoteId__c;
            if (quoteId && quoteId === this.effectiveQuoteId) {
                this.scheduleRefreshProposal();
            }
        }).then((subscription) => {
            this._empSubscription = subscription;
        });
    }

    scheduleRefreshProposal() {
        clearTimeout(this._refreshDebounceTimer);
        this._refreshDebounceTimer = setTimeout(() => {
            this._refreshDebounceTimer = null;
            if (this.wiredQuoteResult) {
                refreshApex(this.wiredQuoteResult);
            }
        }, REFRESH_DEBOUNCE_MS);
    }

    formatCurrency(value, negative = false) {
        if (value == null) return negative ? '-$0.00' : '$0.00';
        const num = Number(value);
        const formatted = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Math.abs(num));
        return negative && num > 0 ? `-${formatted}` : formatted;
    }

    renderedCallback() {
        if (this._scaleSetup) return;
        this._scaleSetup = true;
        this.setupViewportScaling();
    }

    setupViewportScaling() {
        const viewport = this.template.querySelector('.proposal-viewport');
        if (!viewport) return;

        const wrapper = this.template.querySelector('.proposal-wrapper');
        if (!wrapper) return;

        const updateScale = () => {
            const vw = window.innerWidth;
            const vh = window.innerHeight;
            const scaleX = vw / IPAD_WIDTH;
            const scaleY = vh / IPAD_HEIGHT;
            const scale = Math.min(1, scaleX, scaleY);
            wrapper.style.transform = `scale(${scale})`;
            wrapper.style.transformOrigin = 'center center';
        };

        updateScale();
        const observer = new ResizeObserver(updateScale);
        observer.observe(viewport);

        this._resizeObserver = observer;
    }

    disconnectedCallback() {
        if (this._resizeObserver) {
            this._resizeObserver.disconnect();
        }
        clearTimeout(this._refreshDebounceTimer);
        this._refreshDebounceTimer = null;
        if (this._empSubscription) {
            unsubscribe(this._empSubscription);
            this._empSubscription = null;
        }
    }
}