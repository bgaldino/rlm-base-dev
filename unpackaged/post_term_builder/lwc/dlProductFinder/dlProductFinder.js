import { LightningElement, api, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { getRecordNotifyChange } from 'lightning/uiRecordApi';
import getCatalogContext from '@salesforce/apex/RLM_DeltaCatalogController.getCatalogContext';
import searchProducts from '@salesforce/apex/RLM_DeltaCatalogController.searchProducts';
import getRecommendations from '@salesforce/apex/RLM_DeltaCatalogController.getRecommendations';
import addLinesToQuote from '@salesforce/apex/RLM_DeltaCatalogController.addLinesToQuote';

const SEARCH_DEBOUNCE_MS = 300;
const PAGE_SIZE = 50;
const MAX_INSTANCES_PER_LINE = 50; // must match RLM_DeltaCatalogController.MAX_INSTANCES_PER_LINE

// Discovery columns: Product, Code, an optional Bundle marker, a quantity stepper (the number of
// separate Quantity-1 lines the product becomes on add), and a per-row Add button. Keyed/reordered
// via the baseColumns attribute (product,code,bundle).
const BASE_COLUMN_DEFS = {
    product: { label: 'Product', fieldName: 'name', type: 'text' },
    code: { label: 'Code', fieldName: 'code', type: 'text' },
    bundle: {
        label: 'Bundle',
        fieldName: 'bundleLabel',
        type: 'text',
        cellAttributes: { class: { fieldName: 'bundleClass' } }
    }
};
const DEFAULT_BASE_COLUMNS = ['product', 'code'];

// The quantity-stepper column (custom cell type registered in c/dlCatalogDatatable). Its composed
// `quantitychange` event escapes the datatable shadow root and is handled by handleQuantityChange.
const QUANTITY_COLUMN = {
    label: 'Instances',
    type: 'quantityStepper',
    fixedWidth: 130,
    typeAttributes: {
        rowKey: { fieldName: 'rowKey' },
        value: { fieldName: 'instanceCount' },
        max: MAX_INSTANCES_PER_LINE
    }
};

// A standard datatable button column — clicking it fires `onrowaction` with the full row (which
// already carries the row's current instanceCount) and immediately persists just that row to the
// quote via handleRowAction.
const ADD_COLUMN = {
    type: 'button',
    fixedWidth: 90,
    typeAttributes: {
        label: 'Add',
        name: 'add',
        variant: 'brand',
        title: 'Add to quote'
    }
};

/**
 * Product discovery + immediate add for a Quote. Search/recommend products, set an instance count
 * per product, then click Add on a row to persist it to the quote right away (no staging cart, no
 * checkout). Lines are added flat to the quote (no group targeting). On a successful add it emits a
 * composed `linesadded` event so a host (e.g. c/dlQuoteWorkspace) can refresh the line grid.
 *
 * Reuses the same PST-backed Apex as c/dlProductCart via the JSON-in/JSON-out contract
 * (one `inputJson` string param + a `_parse` helper). No Apex changes.
 */
export default class DlProductFinder extends LightningElement {
    @api recordId;
    @api objectApiName;

    // Admin-configurable design attributes (forwarded from the workspace; mirror the cart).
    @api cardTitle;
    @api defaultMode = 'search';
    @api contextDefinition;
    @api configuredCatalogId;
    @api categoryId;
    @api displayFields;
    @api baseColumns;

    @track columns = [];
    @track results = [];
    @track catalogs = [];
    @track selectedRowKeys = [];
    selectedRows = [];

    searchTerm = '';
    catalogId = '';
    cursor = null;
    hasMore = false;
    mode = 'search';

    loading = false;
    adding = false;
    errorMessage = '';
    _initialized = false;
    _searchTimeout;
    pricebook2Id;

    connectedCallback() {
        this.columns = this._buildColumns([]);
        if (this.recordId && !this._initialized) {
            this._initialized = true;
            this.init();
        }
    }

    get effectiveCardTitle() {
        return this.cardTitle || 'Add Products';
    }

    get baseColumnList() {
        const tokens = (this.baseColumns || '')
            .split(',')
            .map((t) => t.trim().toLowerCase())
            .filter((t) => BASE_COLUMN_DEFS[t]);
        const ordered = tokens.length ? tokens : DEFAULT_BASE_COLUMNS;
        return ordered.map((t) => BASE_COLUMN_DEFS[t]);
    }

    async init() {
        this.loading = true;
        this.errorMessage = '';
        try {
            const ctx = this._parse(await getCatalogContext({ quoteId: this.recordId }));
            if (ctx.isSuccess === false) {
                this.errorMessage = ctx.errorMessage || 'Unable to load catalog context.';
                return;
            }
            this.pricebook2Id = ctx.pricebook2Id;
            this.catalogs = Array.isArray(ctx.catalogs) ? ctx.catalogs : [];
            if (this.defaultMode === 'recommend') {
                this.mode = 'recommend';
                await this.runRecommendations(true);
            } else {
                this.mode = 'search';
                await this.runSearch(true);
            }
        } catch (e) {
            this.errorMessage = this._errMessage(e);
        } finally {
            this.loading = false;
        }
    }

    get effectiveCatalogId() {
        return this.catalogId || this.configuredCatalogId || null;
    }

    get displayFieldList() {
        if (!this.displayFields) {
            return [];
        }
        return this.displayFields
            .split(',')
            .map((f) => f.trim())
            .filter((f) => f.length > 0);
    }

    get displayFieldsParam() {
        const fields = this.displayFieldList;
        return fields.length ? { Product2: { fields } } : null;
    }

    get hasCatalogs() {
        return this.catalogs.length > 0;
    }

    get catalogOptions() {
        const opts = [{ label: 'All catalogs', value: '' }];
        this.catalogs.forEach((c) => opts.push({ label: c.name, value: c.id }));
        return opts;
    }

    get hasResults() {
        return this.results.length > 0;
    }

    get addSelectedDisabled() {
        return this.loading || this.adding || this.selectedRows.length === 0;
    }

    get loadMoreDisabled() {
        return this.loading || !this.hasMore;
    }

    handleSearchTermChange(event) {
        this.searchTerm = event.target.value;
        clearTimeout(this._searchTimeout);
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        this._searchTimeout = setTimeout(() => this.runSearch(true), SEARCH_DEBOUNCE_MS);
    }

    handleCatalogChange(event) {
        this.catalogId = event.detail.value;
        this.runSearch(true);
    }

    handleRowSelection(event) {
        this.selectedRows = event.detail.selectedRows;
        this.selectedRowKeys = this.selectedRows.map((r) => r.rowKey);
    }

    // The in-row stepper sets a row's instance count. Update `results` (so the control reflects it and
    // "Add selected" uses it) and keep any selected-row snapshot in sync.
    handleQuantityChange(event) {
        const { rowKey, value } = event.detail;
        const apply = (r) => (r.rowKey === rowKey ? { ...r, instanceCount: value } : r);
        this.results = this.results.map(apply);
        this.selectedRows = this.selectedRows.map(apply);
    }

    // The per-row "Add" button immediately persists just that row (at its current instance count) to
    // the quote. The row payload already carries the up-to-date instanceCount (kept in sync by
    // handleQuantityChange).
    handleRowAction(event) {
        if (event.detail.action.name !== 'add') {
            return;
        }
        this._addRows([event.detail.row]);
    }

    // "Add selected" persists all checked rows in one add.
    handleAddSelected() {
        if (this.selectedRows.length === 0) {
            return;
        }
        this._addRows(this.selectedRows);
    }

    handleLoadMore() {
        if (!this.hasMore) {
            return;
        }
        if (this.mode === 'recommend') {
            this.runRecommendations(false);
        } else {
            this.runSearch(false);
        }
    }

    async runSearch(resetCursor) {
        await this._discover(
            () =>
                searchProducts({
                    inputJson: JSON.stringify(this._baseRequest(resetCursor, { searchTerm: this.searchTerm }))
                }),
            resetCursor
        );
    }

    async runRecommendations(resetCursor) {
        await this._discover(
            () =>
                getRecommendations({
                    inputJson: JSON.stringify(this._baseRequest(resetCursor))
                }),
            resetCursor
        );
    }

    _baseRequest(resetCursor, extra) {
        return {
            quoteId: this.recordId,
            catalogId: this.effectiveCatalogId,
            categoryId: this.categoryId || null,
            contextDefinition: this.contextDefinition || null,
            displayFields: this.displayFieldsParam,
            pageSize: PAGE_SIZE,
            cursor: resetCursor ? null : this.cursor,
            ...(extra || {})
        };
    }

    async _discover(invoke, resetCursor) {
        if (resetCursor) {
            this.cursor = null;
        }
        this.loading = true;
        this.errorMessage = '';
        try {
            const res = this._parse(await invoke());
            if (res.isSuccess === false) {
                this.errorMessage = res.errorMessage || 'Discovery failed.';
                if (resetCursor) {
                    this.results = [];
                }
                return;
            }
            this.columns = this._buildColumns(res.fields);
            const mapped = (res.products || []).map((p) => this._mapRow(p));
            this.results = resetCursor ? mapped : [...this.results, ...mapped];
            this.cursor = res.cursor || null;
            this.hasMore = !!res.cursor;
        } catch (e) {
            this.errorMessage = this._errMessage(e);
            if (resetCursor) {
                this.results = [];
            }
        } finally {
            this.loading = false;
        }
    }

    // One row per product (keyed by productId); seed instanceCount 1 and flatten server display fields.
    _mapRow(p) {
        const row = {
            ...p,
            rowKey: p.productId,
            instanceCount: 1,
            bundleLabel: p.isBundle ? 'Bundle' : '',
            bundleClass: p.isBundle ? 'slds-text-color_success' : ''
        };
        if (p.fields && typeof p.fields === 'object') {
            Object.keys(p.fields).forEach((k) => {
                row[`f_${k}`] = p.fields[k];
            });
        }
        return row;
    }

    _buildColumns(fields) {
        const base = this.baseColumnList;
        const dynamic =
            Array.isArray(fields) && fields.length
                ? fields.map((name) => ({ label: name, fieldName: `f_${name}`, type: 'text' }))
                : [];
        return [...base, ...dynamic, QUANTITY_COLUMN, ADD_COLUMN];
    }

    // Immediately persist the given discovery rows to the quote in one addLinesToQuote call. Each
    // row's pbeId (not just productId) is sent so the row's default/effective price is used, and
    // instanceCount so each product becomes that many separate Quantity-1 lines. Lines are added
    // flat to the quote — no group targeting.
    async _addRows(rows) {
        // Merge by pbeId so re-adding a product in the same click accumulates its instance count.
        const byPbe = new Map();
        for (const r of rows) {
            if (!r.pbeId) {
                continue; // a row with no resolvable PBE can't be added
            }
            const add = Number(r.instanceCount) > 0 ? Math.floor(Number(r.instanceCount)) : 1;
            const existing = byPbe.get(r.pbeId);
            if (existing) {
                existing.instanceCount = Math.min(existing.instanceCount + add, MAX_INSTANCES_PER_LINE);
            } else {
                byPbe.set(r.pbeId, {
                    pbeId: r.pbeId,
                    productId: r.productId,
                    instanceCount: Math.min(add, MAX_INSTANCES_PER_LINE)
                });
            }
        }
        const lines = Array.from(byPbe.values());
        if (lines.length === 0) {
            this.errorMessage = 'This product has no resolvable price and cannot be added.';
            return;
        }

        this.adding = true;
        this.errorMessage = '';
        try {
            // Preserve the JSON-wrapper Apex contract: addLinesToQuote takes ONE inputJson string param.
            const res = this._parse(
                await addLinesToQuote({
                    inputJson: JSON.stringify({
                        quoteId: this.recordId,
                        lines,
                        newGroupName: null
                    })
                })
            );
            if (res.isSuccess === false) {
                this.errorMessage = res.errorMessage || 'Unable to add products to the quote.';
                return;
            }
            const added = Array.isArray(res.addedLines) ? res.addedLines : [];
            // Prefer addedLines.length: addedCount counts emitted POSTs, which undercounts if a bundle
            // product expanded into components on commit.
            const count = added.length || res.addedCount || 0;
            this._toast('Products added', `${count} line(s) added to the quote.`, 'success');
            this._clearSelection();
            // Notify the host so it can refresh the line grid, then invalidate LDS getRecord caches.
            this.dispatchEvent(
                new CustomEvent('linesadded', {
                    detail: { quoteId: this.recordId, addedCount: count, groupIds: res.groupIds || [] },
                    bubbles: true,
                    composed: true
                })
            );
            getRecordNotifyChange([{ recordId: this.recordId }]);
        } catch (e) {
            this.errorMessage = this._errMessage(e);
        } finally {
            this.adding = false;
        }
    }

    _clearSelection() {
        this.selectedRows = [];
        this.selectedRowKeys = [];
    }

    @api
    reset() {
        this._clearSelection();
    }

    _parse(json) {
        try {
            return json ? JSON.parse(json) : {};
        } catch {
            return { isSuccess: false, errorMessage: 'Unexpected response from server.' };
        }
    }

    _errMessage(e) {
        return (e && e.body && e.body.message) || (e && e.message) || 'Unexpected error.';
    }

    _toast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
}
