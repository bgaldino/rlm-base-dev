/**
 * @description Dynamic FieldSet-driven datatable for displaying usage data on Account and Asset record pages.
 *              Queries TransactionJournal, UsageSummary, or UsageBillingPeriodItem records
 *              associated with the current Account or Asset using columns defined by a FieldSet.
 *
 *              Features:
 *              - Columns and fields are driven by FieldSet metadata (configurable without code changes)
 *              - Name and lookup fields render as clickable hyperlinks
 *              - Client-side sorting on all columns with type-aware comparison
 *              - Client-side pagination with fixed page size (10 records per page)
 *              - Setup-required state when component properties are not configured
 */
import { LightningElement, api } from 'lwc';
import getFieldSetData from '@salesforce/apex/RLM_UsageDataController.getFieldSetData';

/** Number of records displayed per page in the datatable */
const PAGE_SIZE = 10;

export default class RlmUsageDataTable extends LightningElement {
    /** @api Record Id (Account or Asset), auto-populated by the record page */
    @api recordId;
    /** @api SObject API name to query (TransactionJournal, UsageSummary, or UsageBillingPeriodItem) */
    @api usageObject;
    /** @api Developer name of the FieldSet defining which columns to display */
    @api fieldSetName;
    /** @api Optional card title override; defaults to the usageObject API name */
    @api cardTitle;

    columns;
    allData;
    error;
    isTruncated = false;
    isLoading = true;
    sortedBy;
    sortDirection = 'asc';
    page = 1;
    contextObject; // 'Account' or 'Asset'

    /**
     * Maps URL column fieldNames to their label fieldNames for sort resolution.
     * e.g. { 'Name__url': 'Name', 'AssetId__url': 'AssetId__name' }
     * Built after data load from the column definitions returned by Apex.
     */
    _sortFieldMap = {};

    /** Falls back to the SObject API name if no custom title is provided */
    get displayTitle() {
        return this.cardTitle || this.usageObject;
    }

    /** usageObject, fieldSetName, and recordId must all be set before loading data */
    get isConfigured() {
        return this.usageObject && this.fieldSetName && this.recordId;
    }

    get hasData() {
        return this.allData && this.allData.length > 0;
    }

    get isEmpty() {
        return !this.isLoading && !this.error && (!this.allData || this.allData.length === 0);
    }

    get errorMessage() {
        return this.error?.body?.message || this.error?.message || 'An error occurred loading data.';
    }

    /** Returns the current page slice of data for the datatable */
    get tableData() {
        if (!this.allData) return [];
        const start = (this.page - 1) * PAGE_SIZE;
        return this.allData.slice(start, start + PAGE_SIZE);
    }

    get totalPages() {
        if (!this.allData || this.allData.length === 0) return 1;
        return Math.ceil(this.allData.length / PAGE_SIZE);
    }

    get showPagination() {
        return this.hasData && this.totalPages > 1;
    }

    get isFirstPage() {
        return this.page <= 1;
    }

    get isLastPage() {
        return this.page >= this.totalPages;
    }

    /** Displays range and total, e.g. "1-10 of 42" */
    get pageInfo() {
        const start = (this.page - 1) * PAGE_SIZE + 1;
        const end = Math.min(this.page * PAGE_SIZE, this.allData.length);
        return `${start}\u2013${end} of ${this.allData.length}`;
    }

    /**
     * Determines which field to use for filtering based on context and object type.
     * Account context always uses AccountId.
     * Asset context uses object-specific fields:
     * - TransactionJournal: ReferenceRecordId (polymorphic)
     * - UsageSummary: AssetId (direct lookup)
     * - UsageBillingPeriodItem: AssetId (direct lookup)
     */
    get filterField() {
        if (this.contextObject === 'Account') {
            return 'AccountId';
        }

        // Asset context — different objects use different fields
        if (this.usageObject === 'TransactionJournal') {
            return 'ReferenceRecordId';  // Polymorphic — points to Asset
        } else if (this.usageObject === 'UsageSummary') {
            return 'AssetId';            // Direct lookup to Asset
        } else if (this.usageObject === 'UsageBillingPeriodItem') {
            return 'AssetId';            // Direct lookup to Asset
        }

        return 'AccountId';  // Fallback
    }

    connectedCallback() {
        // Detect context by object key prefix (Account: 001, Asset: 02i)
        if (this.recordId) {
            const prefix = this.recordId.substring(0, 3);
            this.contextObject = prefix === '001' ? 'Account' :
                               prefix === '02i' ? 'Asset' : 'Unknown';
        }

        if (this.isConfigured) {
            this.loadData();
        } else {
            this.isLoading = false;
        }
    }

    /** Imperatively calls the Apex controller to fetch column definitions and record data */
    async loadData() {
        this.isLoading = true;
        this.isTruncated = false;
        try {
            const result = await getFieldSetData({
                recordId: this.recordId,
                filterField: this.filterField,
                objectApiName: this.usageObject,
                fieldSetName: this.fieldSetName
            });
            this.columns = result.columns;
            this.allData = result.records;
            this.isTruncated = result.truncated === true;
            this._buildSortFieldMap(result.columns);
            this.page = 1;
            this.error = undefined;
        } catch (e) {
            this.error = e;
            this.allData = undefined;
            this.isTruncated = false;
        }
        this.isLoading = false;
    }

    /**
     * Builds a mapping from URL column fieldNames to the data key that should be used for sorting.
     * URL columns display a label from a different field (e.g. Name__url displays the 'Name' value),
     * so sorting must use the label field rather than the URL string.
     */
    _buildSortFieldMap(columns) {
        this._sortFieldMap = {};
        for (const col of columns) {
            if (col.type === 'url' && col.typeAttributes?.label?.fieldName) {
                this._sortFieldMap[col.fieldName] = col.typeAttributes.label.fieldName;
            }
        }
    }

    /**
     * Handles column header sort clicks. Resolves URL columns to their label field for sorting.
     * Uses type-aware comparison: numbers sort numerically, strings use localeCompare,
     * and null values sort to the end regardless of direction.
     */
    handleSort(event) {
        const { fieldName, sortDirection } = event.detail;
        this.sortedBy = fieldName;
        this.sortDirection = sortDirection;

        // Resolve URL columns to their display label field for meaningful sorting
        const sortField = this._sortFieldMap[fieldName] || fieldName;
        const reverse = sortDirection === 'desc' ? -1 : 1;

        this.allData = [...this.allData].sort((a, b) => {
            const valA = a[sortField];
            const valB = b[sortField];
            if (valA == null && valB == null) return 0;
            if (valA == null) return 1;
            if (valB == null) return -1;
            if (typeof valA === 'number' && typeof valB === 'number') {
                return (valA - valB) * reverse;
            }
            return String(valA).localeCompare(String(valB)) * reverse;
        });
        this.page = 1;
    }

    handlePrevious() {
        if (this.page > 1) this.page--;
    }

    handleNext() {
        if (this.page < this.totalPages) this.page++;
    }

    handleRefresh() {
        this.loadData();
    }
}
